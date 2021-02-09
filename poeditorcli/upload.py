#coding:utf-8
import codecs, requests, yaml, json, sys, os, logging
from yaml import Loader
from shutil import copyfile
from StringIO import StringIO
from utils import deepmerge, nested_get, multipart_post

real_raw_input = vars(__builtins__).get('raw_input',input)
log = logging.getLogger("UPLOAD")

class POEditorUpload:
    def __init__(self, translation, api_token, project_id, language, collect_path, cleanup):
        Loader.add_constructor(u'tag:yaml.org,2002:float', lambda self, node: self.construct_yaml_str(node))
        Loader.add_constructor(u'tag:yaml.org,2002:bool', lambda self, node: self.construct_yaml_str(node))
        log.debug("file %s", translation)
        self.translation = translation
        self.translation_name = os.path.basename(translation)
        self.api_token = api_token
        self.project_id = project_id
        self.language = language
        self.data = self.read(self.translation)
        if collect_path is not None: 
            self.collect(collect_path)
        if cleanup:
            self.cleanup()
        self.upload()

    def read(self, name):
        if not os.path.exists(name):
            log.error("File %s not exist", (name,))
            sys.exit(2)

        if name.endswith(".yml") or name.endswith(".yaml") or name.endswith(".yml.txt"):
            with codecs.open(name, 'r', "utf-8") as f:
                log.debug("Reading format %s", name)
                return yaml.load(f.read(), Loader=Loader)
        elif name.endswith(".json"):
            with codecs.open(name, 'r', "utf-8") as f:
                log.debug("Reading format %s", name)
                return json.load(f.read())
        else:
            log.error("Only yaml or json supported")
            sys.exit(7)

    def collect(self, collect_path):
        collected = []
        for (dirpath, dirnames, filenames) in os.walk(collect_path):
            if self.translation_name in filenames:
                collected.append(os.path.join(dirpath, self.translation_name))

        if self.data.get('app') is None:
            self.data['app'] = {}

        for file in collected:
            data = self.read(file)
            log.debug("Base joins %s", file)
            self.data['app']['slots'] = deepmerge(self.data['app'].get('slots', {}), data.get('app', {}).get('slots', {}))


    def cleanup(self):
        resp = multipart_post("https://api.poeditor.com/v2/projects/export", {
            "api_token": self.api_token,
            "id": self.project_id,
            "language": self.language,
            "type": "json"
        })

        if resp["response"]["code"] == '200':
            r = requests.get(resp["result"]["url"])
            if r.status_code != 200:
                log.error("Status code: %d", r.status_code)
                sys.exit(7)

            data = r.json()
        else:
            log.error("Error: %s", resp["response"]["message"])
            sys.exit(4)

        cleanup_list = []
        for term in data:
            if nested_get(self.data, term) is None:
                cleanup_list.append({"term": term["term"], "context": term["context"]})

        if len(cleanup_list):
            print("Terms: some term will be removed, sure?")
            for clean in cleanup_list:
                print("Term: %(term)s (%(context)s)" % clean)
            r = real_raw_input("Press Enter to confirm or Ctrl-C to break operation")

            resp = multipart_post("https://api.poeditor.com/v2/terms/delete", {
                    "api_token": self.api_token,
                    "id": self.project_id,
                    "data": json.dumps(cleanup_list, ensure_ascii=False).encode("utf-8")
                })            

            if resp["response"]["code"] == '200':
                log.info("Terms: Deleted:%(deleted)s Parsed:%(parsed)s", resp["result"]["terms"])
            else:
                log.error("Error: " + resp["response"]["message"])
                sys.exit(4)

    def upload(self):
        data = json.dumps(self.data, ensure_ascii=False).encode("utf-8")
        resp = multipart_post("https://api.poeditor.com/v2/projects/upload", {
            "api_token": self.api_token,
            "id": self.project_id,
            "updating": "terms_translations",
            "overwrite": "1",
            "language": self.language,
            "file": ("upload_me.json", StringIO(data), "text/plain")
        })            

        if resp["response"]["code"] == '200':
            log.info("Translation: Updated:%(updated)s Added:%(added)s Parsed:%(parsed)s", resp["result"]["translations"])
            log.info("Terms: Deleted:%(deleted)s Added:%(added)s Parsed:%(parsed)s",
                     resp["result"]["terms"])
        else:
            log.error("Error: " + resp["response"]["message"])
            sys.exit(4)