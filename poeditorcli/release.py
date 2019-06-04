#coding:utf-8
import codecs

import requests, yaml, json, sys, logging
from yaml import Loader
from requests_toolbelt import MultipartEncoder
from shutil import copyfile
import os
from utils import deepmerge, multipart_post

log = logging.getLogger("RELEASE")

class POEditorRelease:
    def __init__(self, api_token, project_id, languages, languages_used, upload, upload_token, upload_version):
        Loader.add_constructor(u'tag:yaml.org,2002:float', lambda self, node: self.construct_yaml_str(node))
        Loader.add_constructor(u'tag:yaml.org,2002:bool', lambda self, node: self.construct_yaml_str(node))
        self.api_token = api_token
        self.project_id = project_id
        self.upload_url = upload
        self.upload_token = upload_token
        self.upload_version = upload_version

        self.all_langs = {}
        languages_avalable = self.getLanguageList()
        for language in languages_used:
            if language not in languages_avalable:
                log.error("Wrong used language code %s", language)
                sys.exit(10)

        for language in languages_used:
            self.all_langs[language] = self.download(language)
            if self.all_langs[language] is None:
                log.error("Wrong used language code %s", language)
                sys.exit(10)

        for language in languages:
            base_language, data = language[0], self.all_langs[language[0]]
            if len(language) > 1:
                for merge_language in language[1:]:
                    data = deepmerge(self.all_langs[merge_language], data)
            data = yaml.safe_dump(data, default_flow_style=False, default_style='\"', allow_unicode=True)
            self.upload(language, data)

    def getLanguageList(self):
        log.info("Get languages")
        resp = requests.post("https://api.poeditor.com/v2/languages/list", data={
                "api_token": self.api_token,
                "id": self.project_id,
            }).json()

        if resp["response"]["code"] != '200':
            log.error(resp["response"]["message"])
            sys.exit(2)

        languages = []
        for lang in resp["result"]["languages"]:
            log.info("%(name)s(%(code)s) Translate:%(percentage)d%% LastUpdate:%(updated)s", lang)
            languages.append(lang["code"])
            
        return languages

    def download(self, language):
        resp = requests.post("https://api.poeditor.com/v2/projects/export", data={
                "api_token": self.api_token,
                "id": self.project_id,
                "updating": "terms_translations",
                "language": language,
                "type": "key_value_json"
            }).json()
        if resp["response"]["code"] != '200':
            return None

        log.info("Download %s", resp["result"]["url"])
        r = requests.get(resp["result"]["url"])
        if r.status_code != 200:
            return None

        return r.json()

    def upload(self, language, data):
        payload = {
            "auth_key": self.upload_token,
            "language": language[0],
            "version": self.upload_version,
            "content": data
        }
        log.info("Uploading %s (%s)", language[0], " <= ".join(language))

        resp = requests.post(self.upload_url, data=json.dumps(payload))
        if resp.status_code != 200:
            log.error(resp.text)
            sys.exit(2)
