from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ResponseModel(Generic[T], BaseModel):
    code: int
    msg: str
    data: Optional[T] = None


class FolderRequest(BaseModel):
    folderName: str


class PageParams(BaseModel):
    pageSize: int = 100
    page: int = 1
    folderName: str
    keyword: str


class AudioData(BaseModel):
    description: str
