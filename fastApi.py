# main.py
from http.client import HTTPException
import json
import webbrowser
from fastapi import FastAPI, UploadFile, Query
from fastapi.params import File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import uvicorn
from handleBertConfig import process_yaml
from model import *
from autoslice import diarizeAndSlice
from fastapi.staticfiles import StaticFiles
from config import config, updateConfig
from audioUtils import combineAudioWithSilence, splitAudio, getAudioItems, moveItem, deleteFolder, deleteFiles, renamePath, renameSingleFile
from fastapi.middleware.cors import CORSMiddleware
from filelist import TextListManager

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return FileResponse("./Web/index.html")


@app.post("/createFolder")
async def createFolder(request: FolderRequest):
    baseDir = f"{config.get('speakerFolderPath')}"
    folderPath = os.path.join(baseDir, request.folderName)

    if os.path.exists(folderPath):
        return ResponseModel.unknownError()

    os.makedirs(folderPath, exist_ok=True)
    return ResponseModel.success()


@app.get("/getConfig")
async def getConfig():
    return ResponseModel.success(config)


@app.post("/updateConfig")
async def updateConfigFn(request: ConfigRequest):
    try:
        newConfig = json.loads(request.config)
        updateConfig(newConfig)
    except json.JSONDecodeError as e:
        print(f"Error: not correct Json Schema {e}")
        return ResponseModel.unknownError()
    except Exception as e:
        return ResponseModel.unknownError()
    return ResponseModel.success(config)


@app.get("/listTempFolders")
async def listTempFolders():
    baseDir = config.get('tempSlicePath')
    folders = []
    if not os.path.exists(baseDir) or not os.path.isdir(baseDir):
        return ResponseModel.notFoundError()

    for item in os.listdir(baseDir):
        if os.path.isdir(os.path.join(baseDir, item)):
            folders.append(item)

    return ResponseModel.success(folders)


@app.get("/listAlreadyHandledFolders")
async def listAlreadyHandledFolders():
    baseDir = config.get('speakerFolderPath')
    folders = []
    if not os.path.exists(baseDir) or not os.path.isdir(baseDir):
        return ResponseModel.notFoundError()
    for item in os.listdir(baseDir):
        if os.path.isdir(os.path.join(baseDir, item)):
            folders.append(item)
    return ResponseModel.success(folders)


@app.post("/listAllTempAudioItems")
async def listAllTempAudioItemsByPageParams(request: PageParams):
    baseDir = f"{config.get('tempSlicePath')}/{request.folderName}"
    return ResponseModel.success(
        getAudioItems(audioFolderPath=baseDir, pageParams=request))


@app.post("/listAllHandledAudioItems")
async def listAllHandledAudioItems(request: PageParams):
    baseDir = f"{config.get('speakerFolderPath')}/{request.folderName}"
    return ResponseModel.success(
        getAudioItems(audioFolderPath=baseDir, pageParams=request))


@app.post("/startSliceHandle")
async def startSliceHandle(
        file: UploadFile = File(...),
        subFile: Optional[UploadFile] = None,
        subOffset: Optional[int] = Query(0),
        language: Optional[str] = Query(1),
):
    os.makedirs(f"{config.get('uploadPath')}/", exist_ok=True)
    filePath = f"{config.get('uploadPath')}/{file.filename}"
    subPath = None  # 初始化为 None

    with open(filePath, "wb") as buffer:
        for chunk in iter(lambda: file.file.read(4096), b""):
            buffer.write(chunk)
    if subFile:
        subPath = f"{config.get('uploadPath')}/{subFile.filename}"
        with open(subPath, "wb") as buffer:
            for chunk in iter(lambda: subFile.file.read(4096), b""):
                buffer.write(chunk)
    print('Process start!')
    diarizeAndSlice(filePath,
                    subPath=subPath,
                    subOffset=subOffset,
                    language=language)
    return ResponseModel.success()


@app.post("/mergeAudio")
async def mergeAudio(params: MergeRequest):
    if not combineAudioWithSilence(params.paths, params.interval):
        return ResponseModel.notFoundError()
    return ResponseModel.success()


@app.post("/splitAudio")
def splitAudioFn(params: SpliceRequest):
    if not splitAudio(params.path, params.splitPoint):
        return ResponseModel.unknownError()
    return ResponseModel.success()


@app.post("/moveAudio")
def moveAudioFn(params: MoveAudio):
    targetPath = f"{config.get('speakerFolderPath')}/{params.targetFolderName}"
    flag = True
    if not os.path.exists(targetPath):
        return ResponseModel.notFoundError()
    for path in params.paths:
        if not moveItem(originFilePath=path, targetFolder=targetPath):
            flag = False
            break
    if not flag:
        return ResponseModel.notFoundError()
    return ResponseModel.success()


@app.post("/deleteSpeakerFolder")
def deleteSpeakerFolder(params: FolderRequest):
    targetPath = f"{config.get('speakerFolderPath')}/{params.folderName}"
    if not os.path.exists(targetPath):
        return ResponseModel.notFoundError()
    if (deleteFolder(targetFolder=targetPath)):
        return ResponseModel.success()
    else:
        return ResponseModel.notFoundError()


@app.post("/deleteAudios")
def deleteAudios(params: MoveAudio):
    if (deleteFiles(filePaths=params.paths)):
        return ResponseModel.success()
    else:
        return ResponseModel.notFoundError()


@app.post("/renamePathAllFiles")
def renamePathAllFiles(params: RenamePath):
    if (renamePath(folderPath=params.folderPath,
                   customName=params.customName)):
        return ResponseModel.success()
    else:
        return ResponseModel.unknownError()


@app.post("/renameOneFile")
def renameOneFile(params: RenameOnePath):
    if (renameSingleFile(filePath=params.filePath,
                         customName=params.customName)):
        return ResponseModel.success()
    else:
        return ResponseModel.unknownError()


@app.post("/updateTextOrLanguage")
def updateTextOrLanguage(params: UpdateText):
    if os.path.exists(params.filePath):
        dirName = os.path.dirname(params.filePath)
        manager = TextListManager(dirName)
        dictTemp = {}
        if params.language:
            dictTemp['language'] = params.language
        if params.text:
            dictTemp['text'] = params.text
        manager.updateEntry(params.filePath, dictTemp)
    else:
        return ResponseModel.unknownError()


@app.post("/exportByBertConfig")
async def exportByBertConfig(file: UploadFile = File(...),
                             folderName=Query(0)):
    os.makedirs(f"{config.get('uploadPath')}/", exist_ok=True)
    fileLocation = f"{config.get('uploadPath')}/{file.filename}"
    with open(fileLocation, "wb+") as file_object:
        file_object.write(file.file.read())

    return await process_yaml(fileLocation, folderName)


@app.get("/files/{filePath:path}")
def readFile(filePath: str):
    print(filePath)
    if not os.path.isfile(filePath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filePath)


if __name__ == "__main__":
    staticDir = './Web'
    dirs = [fir.name for fir in os.scandir(staticDir) if fir.is_dir()]
    files = [fir.name for fir in os.scandir(staticDir) if fir.is_dir()]
    if os.path.exists(staticDir):
        for dirName in dirs:
            app.mount(
                f"/{dirName}",
                StaticFiles(directory=f"./{staticDir}/{dirName}"),
                name=dirName,
            )
    else:
        print(
            '挂载静态资源出错，请前往github:https://github.com/ADKcodeXD/Anime-Audio-Dataset-Maker-WEBUI/releases 下载最新打包好的WebUI解压放在根目录下'
        )
    webbrowser.open_new("http://localhost:7896")
    uvicorn.run(app, host="localhost", port=7896)
