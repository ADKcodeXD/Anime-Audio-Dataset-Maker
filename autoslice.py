import os
from pydub import AudioSegment
from pyannote.audio import Pipeline
import torch
from pyannote.audio.pipelines.utils.hook import ProgressHook
from config import config
import shutil
import os
import pysubs2
from filelist import TextListManager


def loadsub(filePath, subOffset=0):
    subs = pysubs2.load(filePath)
    segments = []
    noCommentSubs = [sub for sub in subs if not sub.is_comment]
    for sub in noCommentSubs:
        start = sub.start + subOffset
        end = sub.end + subOffset
        text = sub.plaintext
        sameItem = next((item for item in segments if item['start'] == start),
                        None)
        if sameItem:
            continue
        segments.append({
            'start': start,
            'end': end,
            'text': text,
        })
    return segments


def splitAudioBySubtle(arr, audioPath):
    # 分割好的
    audio = AudioSegment.from_wav(audioPath)
    result = []
    for item in arr:
        start = item.get('start')
        end = item.get('end')
        audioPart = audio[start:end]
        result.append({
            'audioPart': audioPart,
            'text': item.get('text'),
            'start': start,
            'end': end
        })

    return result


def convertMillisecondsToHMS(milliseconds):
    seconds = milliseconds // 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    # 格式化输出为两位数字，不足两位数的前面补0
    return f"{hours:02d}h{minutes:02d}m{seconds:02d}s"


def saveSpeakerAudio(speaker,
                     speakerAudio,
                     speakerMap,
                     start,
                     end,
                     textManager=None,
                     text=None,
                     language='JP'):
    speakFolderPath = f"{config.get('tempSlicePath')}/speaker_{speaker}"
    os.makedirs(speakFolderPath, exist_ok=True)
    if speakerMap.get(speaker) is None:
        speakerMap[speaker] = 0
    else:
        speakerMap[speaker] += 1

    speakerFile = f"{speakFolderPath}/{speakerMap.get(speaker)}_{speaker}_{convertMillisecondsToHMS(start)}-{convertMillisecondsToHMS(end)}.wav"
    speakerAudio.export(speakerFile, format="wav")

    if text:
        if textManager.get(speakFolderPath):
            textManager.get(speakFolderPath).addNewEntry(
                speakerFile, text, speaker, language)
        else:
            textManager['speakFolderPath'] = TextListManager(speakFolderPath)
            textManager['speakFolderPath'].addNewEntry(speakerFile, text,
                                                       speaker, language)


def loadAudioEverPartBySub(audioPath, subPath, subOffset):
    arr = loadsub(subPath, subOffset)
    subList = splitAudioBySubtle(arr, audioPath=audioPath)
    return subList


def findBestSpeaker(start, end, speakerMap):
    bestSpeaker = None
    longestOverlap = -1

    for speaker, intervals in speakerMap.items():
        for interval in intervals:
            overlap = min(end, interval[1]) - max(start, interval[0])
            if overlap > longestOverlap:
                longestOverlap = overlap
                bestSpeaker = speaker

    return bestSpeaker


def diarizeAndSlice(audioPath, subPath=None, subOffset=0, language='JP'):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                        use_auth_token=config.get('hfToken'))

    newParams = config.get('pyannoteModelSetting')
    pipeline.instantiate(newParams)
    pipeline.to(torch.device("cuda"))

    with ProgressHook() as hook:
        diarization = pipeline(
            audioPath,
            min_speakers=config.get('pyannoteSetting').get('min_speakers'),
            max_speakers=config.get('pyannoteSetting').get('max_speakers'),
            hook=hook)

    audio = AudioSegment.from_wav(audioPath)
    speakerMap = {}

    if os.path.exists(config.get('tempSlicePath')):
        shutil.rmtree(config.get('tempSlicePath'))
        os.makedirs(config.get('tempSlicePath'))

    if subPath:
        subList = loadAudioEverPartBySub(audioPath, subPath, subOffset)
        speakerMap2 = {}
        fileMap = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start = int(turn.start * 1000)
            end = int(turn.end * 1000)
            if speakerMap2.get(speaker):
                speakerMap2.get(speaker).append([start, end])
            else:
                speakerMap2.setdefault(speaker, [[start, end]])

        for item in subList:
            audioPart = item.get('audioPart')
            start = item.get('start')
            end = item.get('end')
            text = item.get('text')
            bestSpeaker = findBestSpeaker(start=start,
                                          end=end,
                                          speakerMap=speakerMap2)
            saveSpeakerAudio(speaker=bestSpeaker or 'unset',
                             speakerAudio=audioPart,
                             speakerMap=speakerMap,
                             start=start,
                             end=end,
                             textManager=fileMap,
                             text=text,
                             language=language)
    else:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start = int(turn.start * 1000)
            end = int(turn.end * 1000)
            speaker_audio = audio[start:end]
            if (end - start < int(config.get('minAudioLength'))):
                continue
            else:
                saveSpeakerAudio(speaker, speaker_audio, speakerMap, start,
                                 end)


if __name__ == "__main__":
    audioPath = "./final.wav"
    srtPath = "./subtitle.srt"
    diarizeAndSlice(audioPath, srtPath)
