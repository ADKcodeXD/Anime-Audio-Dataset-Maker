# main.py
from http.client import HTTPException
from fastapi import FastAPI, UploadFile
from fastapi.params import File
from pydantic import BaseModel
from typing import List
import os
import uvicorn
from model import *
from autoslice import diarize_and_slice

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/createFolder")
def createFolder(request: FolderRequest):
    base_dir = "./speakers"
    folder_path = os.path.join(base_dir, request.folderName)

    if os.path.exists(folder_path):
        raise ResponseModel(code=501, data=None, msg='已存在文件夹')

    os.makedirs(folder_path, exist_ok=True)
    return ResponseModel(code=200, data=None, msg='访问成功')


@app.get("/listTempFolders")
async def listTempFolders():
    base_dir = "./tempSlice"
    folders = []
    # 确保 base_dir 存在
    if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
        return ResponseModel(code=404, data=None, msg='文件夹不存在')
    # 遍历 base_dir 下的所有项
    for item in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, item)):
            folders.append(item)

    return ResponseModel(code=200, data=folders, msg='访问成功')


@app.get("/listWavItems")
def listWavItems(request: PageParams):
    baseDir = f"./tempSlice/{request.folderName}"
    wavItems = []
    extensions = ('.mp3', '.wav', '.ogg', '.flac')
    # 确保 base_dir 存在
    if not os.path.exists(baseDir) or not os.path.isdir(baseDir):
        return ResponseModel(code=404, data=None, msg='文件夹不存在')
    # 遍历 base_dir 下的所有项
    for item in os.listdir(baseDir):
        filePath = os.path.join(baseDir, item)
        if os.path.isfile(filePath) and filePath.endswith(extensions):
            wavItems.append(
                {'name': item, 'source': os.path.abspath(filePath)})

    return ResponseModel(code=200, data=wavItems, msg='访问成功')


@app.post("/startSliceHandle")
async def startSliceHandle(file: UploadFile = File(...)):
    os.makedirs(f"./uploadedFile/", exist_ok=True)
    filePath = f"./uploadedFile/{file.filename}"
    with open(filePath, "wb") as buffer:
        for chunk in iter(lambda: file.file.read(4096), b""):
            buffer.write(chunk)

    print('Process start!')
    diarize_and_slice(filePath)
    return ResponseModel(code=200, data=None, msg='访问成功')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7896)
