import json

import os
import sys

def loadJson(jsonPath: str) -> dict:
    if not jsonPath.endswith(".json"):
        raise ValueError(f"The file {jsonPath} must be a json file.")
    # 检查文件是否存在
    if not os.path.exists(jsonPath):
        raise FileNotFoundError(f"The file {jsonPath} does not exist.")

    with open(jsonPath, "r", encoding="utf-8") as f:
        return json.load(f)



def argDict() -> dict:
    argDict = {}
    for arg in sys.argv:
        if "=" in arg:
            key, value = arg.split("=")
            argDict[key] = value
    return argDict

def getConfigPath():
    return argDict().get("config", "config.json")