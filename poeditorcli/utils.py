import requests
from requests_toolbelt import MultipartEncoder

def deepmerge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            deepmerge(value, destination.setdefault(key, {}))
        elif not destination.get(key):
            destination[key] = value
    return destination

def nested_get(input_dict, nested_key):
    internal_dict_value = input_dict
    if isinstance(nested_key, dict):
        nested_key = map(lambda x: x.strip('"'), nested_key["context"].split(".")) + [nested_key["term"]]
    if not isinstance(nested_key, list) and not isinstance(nested_key, tuple):
        nested_key = nested_key.split(".")
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value

def multipart_post(url, fields):
    multipart_data = MultipartEncoder(fields = fields)
    return requests.post(url, data=multipart_data, 
            headers={'Content-Type': multipart_data.content_type}).json()
