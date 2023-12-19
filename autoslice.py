import os
from pydub import AudioSegment
from pyannote.audio import Pipeline
import torch
from pyannote.audio.pipelines.utils.hook import ProgressHook
from config import config
import shutil
import os


def convertMillisecondsToHMS(milliseconds):
    seconds = milliseconds // 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    # 格式化输出为两位数字，不足两位数的前面补0
    return f"{hours:02d}h{minutes:02d}m{seconds:02d}s"


def saveSpeakerAudio(speaker, speakerAudio, speakerMap, start, end):
    speakFolderPath = f"{config.get('tempSlicePath')}/speaker_{speaker}"
    os.makedirs(speakFolderPath, exist_ok=True)
    if speakerMap.get(speaker) is None:
        speakerMap[speaker] = 0
    else:
        speakerMap[speaker] += 1

    speakerFile = f"{speakFolderPath}/{speakerMap.get(speaker)}_{speaker}_{convertMillisecondsToHMS(start)}-{convertMillisecondsToHMS(end)}.wav"
    speakerAudio.export(speakerFile, format="wav")


def diarizeAndSlice(audio_path):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                        use_auth_token=config.get('hfToken'))

    newParams = config.get('pyannoteModelSetting')
    pipeline.instantiate(newParams)
    pipeline.to(torch.device("cuda"))

    with ProgressHook() as hook:
        diarization = pipeline(
            audio_path,
            min_speakers=config.get('pyannoteSetting').get('min_speakers'),
            max_speakers=config.get('pyannoteSetting').get('max_speakers'),
            hook=hook)

    audio = AudioSegment.from_wav(audio_path)
    speakerMap = {}

    if os.path.exists(config.get('tempSlicePath')):
        shutil.rmtree(config.get('tempSlicePath'))
        os.makedirs(config.get('tempSlicePath'))

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * 1000)
        end = int(turn.end * 1000)
        speaker_audio = audio[start:end]

        if (end - start < int(config.get('minAudioLength'))):
            continue
        else:
            saveSpeakerAudio(speaker, speaker_audio, speakerMap, start, end)


if __name__ == "__main__":
    filePath = "./test_01.wav"
    diarizeAndSlice(filePath)
