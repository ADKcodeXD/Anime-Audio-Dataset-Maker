import os
import shutil
from pydub import AudioSegment
from pyannote.audio import Pipeline
import torch
import numpy as np
from pyannote.audio.pipelines import VoiceActivityDetection
from pyannote.audio import Model
from pyannote.audio.pipelines.utils.hook import ProgressHook


def convert_seconds_with_decimal(seconds):
    sec = int(seconds) // 1000
    hours = int(sec) // 3600
    seconds %= 3600
    minutes = int(seconds) // 60
    seconds %= 60
    return f"{hours}h{minutes}m{seconds:.2f}s"


def save_speaker_audio(speaker, speaker_audio, speakerMap, start, end):
    speaker_folder = f"tempSlice/speaker_{speaker}"
    os.makedirs(speaker_folder, exist_ok=True)

    if speakerMap.get(speaker) is None:
        speakerMap[speaker] = 0
    else:
        speakerMap[speaker] += 1

    speaker_file = f"{speaker_folder}/{speakerMap.get(speaker)}_{speaker}_{convert_seconds_with_decimal(start)}-{convert_seconds_with_decimal(end)}.wav"
    speaker_audio.export(speaker_file, format="wav")


def diarize_and_slice(audio_path):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token="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")

    new_parameters = {'segmentation': {'min_duration_off': 0},
                      'clustering': {'method': 'centroid',
                                     'min_cluster_size': 15,
                                     'threshold': 0.522}
                      }
    pipeline.instantiate(new_parameters)
    pipeline.to(torch.device("cuda"))

    with ProgressHook() as hook:
        diarization = pipeline(
            audio_path, min_speakers=2, max_speakers=16, hook=hook)

    audio = AudioSegment.from_wav(audio_path)

    speakerMap = {}

    # Process each detected speaker turn
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * 1000)
        end = int(turn.end * 1000)
        speaker_audio = audio[start:end]

        if (end - start < 300):
            continue
        else:
            save_speaker_audio(speaker, speaker_audio, speakerMap, start, end)


# Path to your audio file
# audio_file_path = "./test.wav"

# Run the diarization and slicing process
# diarize_and_slice(audio_file_path)
