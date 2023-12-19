import shutil
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import os
import re
from model import PageParams


def naturalSortKey(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', s)
    ]


def combineAudioWithSilence(audioPaths, interval=200):
    try:
        combinedAudio = None
        silence = AudioSegment.silent(duration=interval)
        # 遍历所有音频文件路径
        baseDir = os.path.dirname(audioPaths[0])
        for path in audioPaths:
            # 加载当前音频文件
            audio = AudioSegment.from_file(path)
            if combinedAudio is None:
                combinedAudio = audio
            else:
                combinedAudio += silence + audio
        firstAudioIndex = re.search(r'(\d+)',
                                    os.path.basename(audioPaths[0])).group()
        outputFileName = f"{baseDir}/{firstAudioIndex}_merge({os.path.basename(path[0])}).wav"
        combinedAudio.export(outputFileName, format="wav")
        print(f"Saved {outputFileName}")
        for path in audioPaths:
            os.remove(path)
        return True
    except CouldntDecodeError:
        print(f"无法解码文件。请确保文件路径正确且为支持的音频格式")
        return None
    except FileNotFoundError:
        print("File Not Found!!")
        return None
    except Exception as e:
        print(f"unknownerror: {e}")
        return None


def splitAudio(audioPath, splitPoint):
    try:
        audio = AudioSegment.from_file(audioPath)
        baseDir = os.path.dirname(audioPath)
        firstPart = audio[:splitPoint]
        secondPart = audio[splitPoint:]
        # 获取文件名和扩展名
        filename, fileExtension = os.path.splitext(os.path.basename(audioPath))
        # 生成分割后的文件名
        firstPartFilename = os.path.join(
            baseDir, f"{filename}(split)_1{fileExtension}")
        secondPartFilename = os.path.join(
            baseDir, f"{filename}(split)_2{fileExtension}")
        # 导出音频文件
        firstPart.export(firstPartFilename, format=fileExtension.strip('.'))
        secondPart.export(secondPartFilename, format=fileExtension.strip('.'))
        os.remove(audioPath)
        print(f"音频文件已被分割并保存为 {firstPartFilename} 和 {secondPartFilename}")
        return True
    except Exception as e:
        print(f"发生错误: {e}")
        return False


def getAudioItems(audioFolderPath, pageParams):
    extensions = ('.mp3', '.wav', '.ogg')
    if not os.path.exists(audioFolderPath) or not os.path.isdir(
            audioFolderPath):
        return None

    audioFiles = [
        os.path.join(audioFolderPath, f) for f in os.listdir(audioFolderPath)
        if f.lower().endswith(extensions)
    ]

    total = len(audioFiles)
    result = []
    totalLength = 0

    for item in audioFiles:
        try:
            audio = AudioSegment.from_file(item)
            duration = len(audio)
            totalLength += duration
            result.append({
                'source': item,
                'fileName': os.path.basename(item),
                'duration': duration
            })
        except Exception as e:
            print(f"Error processing file {item}: {e}")
            return None

    # 根据音频时长排序
    if pageParams.order == 'ascend':
        result = sorted(result, key=lambda x: x['duration'])
    elif pageParams.order == 'descend':
        result = sorted(result, key=lambda x: x['duration'], reverse=True)
    else:
        # 如果没有指定排序方式或排序方式无效，则按文件名排序
        result = sorted(result, key=lambda x: naturalSortKey(x['fileName']))
    # 分页处理
    if (pageParams.page - 1) * pageParams.pageSize > len(audioFiles):
        return []

    pageFiles = result[(pageParams.page - 1) *
                       pageParams.pageSize:pageParams.page *
                       pageParams.pageSize]

    return {'results': pageFiles, 'total': total, 'totalLength': totalLength}


def moveItem(originFilePath, targetFolder):
    if not os.path.exists(originFilePath) or not os.path.isfile(
            originFilePath):
        return None
    fileName = os.path.basename(originFilePath)
    if os.path.exists(os.path.join(targetFolder, fileName)):
        return None
    else:
        shutil.move(originFilePath, targetFolder)
        return True


def deleteFolder(targetFolder):
    if not os.path.exists(targetFolder) or not os.path.isdir(targetFolder):
        return None
    else:
        shutil.rmtree(targetFolder)
        return True


def renamePath(folderPath, customName=""):
    if not os.path.isdir(folderPath):
        print("Provided path is not a directory.")
        return False
    dirName = os.path.basename(folderPath)
    print(dirName)
    customName = customName or dirName
    files = sorted(os.listdir(folderPath),
                   key=lambda x: naturalSortKey(os.path.basename(x)))
    index = 1
    print(files)
    for filename in files:
        name, ext = os.path.splitext(filename)
        newFilename = f"{index}_{customName}{ext}"
        # 生成完整的旧文件路径和新文件路径
        oldFilePath = os.path.join(folderPath, filename)
        newFilePath = os.path.join(folderPath, newFilename)
        # 重命名文件
        try:
            os.rename(oldFilePath, newFilePath)
            index += 1
        except OSError as e:
            print(f"Error renaming file {filename}: {e}")
            return False
    return True


def renameSingleFile(filePath, customName):
    if not os.path.isfile(filePath):
        print("Provided path is not a file.")
        return False

    folderPath, _ = os.path.split(filePath)
    _, ext = os.path.splitext(filePath)

    # 生成新文件名
    newFilename = f"{customName}{ext}"

    # 生成新文件的完整路径
    newFilePath = os.path.join(folderPath, newFilename)

    try:
        os.rename(filePath, newFilePath)
        return True
    except OSError as e:
        print(f"Error renaming file: {e}")
        return False


def deleteFiles(filePaths):
    for path in filePaths:
        if not os.path.exists(path) or not os.path.isfile(path):
            raise FileNotFoundError
        else:
            os.remove(path)
    return True
