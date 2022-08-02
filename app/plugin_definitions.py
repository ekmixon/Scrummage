import json, os

def Get(Scrummage_Working_Directory):
    JSON_File = open(os.path.join(Scrummage_Working_Directory, "static/protected/json/plugin_definitions.json"), "r")
    return json.load(JSON_File)