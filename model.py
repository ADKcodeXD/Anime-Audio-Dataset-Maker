from pydantic import BaseModel
from typing import Generic, List, TypeVar, Optional

T = TypeVar("T")


class ResponseModel(Generic[T], BaseModel):
    code: int
    msg: str
    data: Optional[T] = None

    @staticmethod
    def success(data: T = None) -> 'ResponseModel[T]':
        return ResponseModel(code=200, msg='访问成功', data=data)

    @staticmethod
    def unknownError(data: T = None) -> 'ResponseModel[T]':
        return ResponseModel(code=500, msg='访问失败', data=data)

    @staticmethod
    def paramsError(data: T = None) -> 'ResponseModel[T]':
        return ResponseModel(code=501, msg='参数错误', data=data)

    @staticmethod
    def notFoundError(data: T = None) -> 'ResponseModel[T]':
        return ResponseModel(code=404, msg='文件或文件夹未找到', data=data)

    @staticmethod
    def customError(msg='访问失败') -> 'ResponseModel[T]':
        return ResponseModel(code=404, msg=msg, data=None)


class FolderRequest(BaseModel):
    folderName: str


class ConfigRequest(BaseModel):
    config: str


class PageParams(BaseModel):
    pageSize: int = 100
    page: int = 1
    folderName: str | None
    keyword: str | None
    order: str | None


class AudioData(BaseModel):
    description: str


class MergeRequest(BaseModel):
    paths: List[str]
    interval: int = 200


class SpliceRequest(BaseModel):
    path: str
    splitPoint: int  # ms 毫秒


class MoveAudio(BaseModel):
    paths: List[str]
    targetFolderPath: str | None


class RenamePath(BaseModel):
    folderPath: str
    customName: str | None


class RenameOnePath(BaseModel):
    filePath: str
    customName: str


class UpdateText(BaseModel):
    text: str | None
    language: str | None
    filePath: str
