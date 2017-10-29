#coding:utf-8
import codecs

import requests, yaml, json, sys, logging
from yaml import Loader
from requests_toolbelt import MultipartEncoder
from shutil import copyfile
import os

log = logging.getLogger("UPDATE")

class POEditorUpdate:
    def __init__(self, translation, api_token, project_id, language):
        Loader.add_constructor(u'tag:yaml.org,2002:float', lambda self, node: self.construct_yaml_str(node))
        log.debug("file %s", translation)
        self.translation = translation
        self.api_token = api_token
        self.project_id = project_id
        self.language = language
        self.download()

        if self.translation.endswith(".yml") or self.translation.endswith(".yaml") or self.translation.endswith(".yml.txt"):
            log.info("Save yaml")
            with codecs.open(self.translation, 'w', "utf-8") as f:
                yaml.safe_dump(self.data, f, default_flow_style=False, allow_unicode=True)
        elif self.translation.endswith(".json"):
            log.info("Save json")
            with codecs.open(self.translation, 'w', "utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, encoding='utf8')
        else:
            log.error("Only yaml or json supported")
            sys.exit(7)
        pass


    @staticmethod
    def getLanguageList(translation, api_token, project_id, exlang):
        payload = {
            "api_token": api_token,
            "id": project_id,
        }
        log.info("Get languages")
        r = requests.post("https://api.poeditor.com/v2/languages/list", data=payload)
        resp = r.json()
        if not(resp["response"]["code"] == '200'):
            log.error(resp["response"]["message"])
            sys.exit(2)
        for lang in resp["result"]["languages"]:
            if lang["code"] == exlang:
                continue
            log.info("%(name)s(%(code)s) Translate:%(percentage)d%% LastUpdate:%(updated)s", lang)
            POEditorUpdate(translation % lang["code"], api_token, project_id, lang["code"])


    def download(self):
        payload = {
                "api_token": self.api_token,
                "id": self.project_id,
                "updating": "terms_translations",
                "language": self.language,
                "type": "key_value_json"
        }
        r = requests.post("https://api.poeditor.com/v2/projects/export", data=payload)
        resp = r.json()
        if not(resp["response"]["code"] == '200'):
            log.error(resp["response"]["message"])
            sys.exit(2)
        log.info("Download %s", resp["result"]["url"])
        r = requests.get(resp["result"]["url"])
        if r.status_code != 200:
            log.error("Status code: %d", r.status_code)
            sys.exit(7)
        self.data = r.json()
