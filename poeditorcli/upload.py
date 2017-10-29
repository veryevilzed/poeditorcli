#coding:utf-8
import codecs

import requests, yaml, json, sys, logging
from requests_toolbelt import MultipartEncoder
from shutil import copyfile
import os

log = logging.getLogger("UPLOAD")

class POEditorUpload:
    def __init__(self, translation, api_token, project_id, language):
        log.debug("file %s", translation)
        self.translation = translation
        self.api_token = api_token
        self.project_id = project_id
        self.language = language
        if self.translation.endswith(".yml") or self.translation.endswith(".yaml"):
            self.convert()
        elif self.translation.endswith(".json"):
            copyfile(translation, "upload_me.json")
        else:
            log.error("Only yaml or json supported")
            sys.exit(7)
        self.upload()

        pass

    def convert(self):
        if os.path.exists(self.translation):
            with codecs.open(self.translation, 'r', "utf-8") as f:
                log.debug("Converting yaml to json")
                s = f.read()
                data = yaml.load(s)
                json.dump(data,  codecs.open("upload_me.json", 'w', "utf-8"), ensure_ascii=False)
                self.data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        else:
            self.log.error("File %s not exist", (self.translation,))
            sys.exit(2)


    def upload(self):
        multipart_data = MultipartEncoder(
            fields = {
                "api_token": self.api_token,
                "id": self.project_id,
                "updating": "terms_translations",
                "language": self.language,
                "file": ("upload_me.json", open("upload_me.json", "rb"), "text/plain")
            }
        )
        files = {"file": open('upload_me.json', 'rb')}
        r = requests.post("https://api.poeditor.com/v2/projects/upload", data=multipart_data, headers={'Content-Type': multipart_data.content_type})
        os.remove('upload_me.json')
        resp = r.json()
        if (resp["response"]["code"] == '200'):
            log.info("Translation: Updated:%(updated)s Added:%(added)%s Parsed:%(parsed)s", resp["result"]["translations"])
            log.info("Terms: Deleted:%(deleted)s Added:%(added)s Parsed:%(parsed)s",
                     resp["result"]["terms"])
        else:
            log.error("Error: " + resp["response"]["message"])
            sys.exit(4)