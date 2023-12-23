# config.py

import json
from typing import Any, Dict
import os

# 指定你的JSON文件路径
filePath = './config.json'
config: Dict[str, Any] = {}
defaultConfig = {
    "hfToken": "",
    "pyannoteModelSetting": {
        "clustering": {
            "method": "centroid",
            "min_cluster_size": 15,
            "threshold": 0.522
        },
        "segmentation": {
            "min_duration_off": 0
        }
    },
    "pyannoteSetting": {
        "min_speakers": 2,
        "max_speakers": 16
    },
    "minAudioLength": "300",
    "tempSlicePath": "./tempSlice",
    "uploadPath": "./uploadedPath",
    "speakerFolderPath": "./speakerDataSet"
}


def loadJson(filePath: str) -> Dict[str, Any]:
    if os.path.exists(filePath):
        try:
            with open(filePath, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print('错误的json格式 将初始该文件')
            with open(filePath, 'w') as file:
                json.dump(defaultConfig, file, indent=4)
            return defaultConfig
    else:
        with open(filePath, 'w') as file:
            json.dump(defaultConfig, file, indent=4)
        print(f"本地配置文件路径 {filePath} 不存在，将自动生成新配置")
        return defaultConfig


def updateConfig(jsonObj: Dict[str, Any]):
    with open(filePath, 'w') as file:
        json.dump(jsonObj, file, indent=4)
    config.update(jsonObj)
    return


config.update(loadJson(filePath))
