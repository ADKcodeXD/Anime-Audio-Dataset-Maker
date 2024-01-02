from fastapi.responses import FileResponse
import yaml
import os
import shutil
from zipfile import ZipFile
from filelist import TextListManager
from config import config
import librosa
import soundfile as sf


def zip_directory(folder_path, zip_name):
    with ZipFile(zip_name, 'w') as zipf:
        abs_folder_path = os.path.abspath(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                abs_file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(abs_file_path, abs_folder_path)
                zipf.write(abs_file_path, rel_file_path)


def process_yaml(filepath, folderName):
    with open(filepath, 'r') as file:
        data = yaml.safe_load(file)
    dataSetPath = data['dataset_path']
    dataSetPath = dataSetPath.replace('\\', '/')
    outDir = data['resample']['out_dir']
    speakerPath = os.path.join(dataSetPath, outDir, folderName)
    os.makedirs(speakerPath, exist_ok=True)
    manager = TextListManager(
        f"{config.get('speakerFolderPath')}/{folderName}")
    trainPath = data['preprocess_text']['transcription_path']
    trainFilePath = os.path.join(dataSetPath, trainPath)
    os.makedirs(os.path.dirname(trainFilePath), exist_ok=True)
    index = 1
    for filename in os.listdir(
            f"{config.get('speakerFolderPath')}/{folderName}"):
        name, ext = filename.split('.')
        if ext not in ('wav', 'ogg', 'mp3'):
            continue
        keyName = os.path.join(
            f"{config.get('speakerFolderPath')}/{folderName}", filename)
        newKeyName = f'{folderName}_{index}.wav'
        with open(trainFilePath, 'a', encoding='utf-8') as file:
            audioTextData = manager.getData(keyName)
            if audioTextData:
                filterText = audioTextData['text'].replace('\u3000', '、')
                line = f"./{dataSetPath}/{outDir}/{folderName}/{newKeyName}|{folderName}|{audioTextData['language']}|{filterText}\n"
                file.write(line)
        y, sr = librosa.load(keyName, sr=None)
        y_resampled = librosa.resample(
            y, orig_sr=sr, target_sr=data['resample']['sampling_rate'])
        sf.write(os.path.join(speakerPath, newKeyName), y_resampled,
                 data['resample']['sampling_rate'])
        index += 1

    zipName = f'{folderName}.zip'
    zip_directory(dataSetPath, zipName)

    return FileResponse(zipName,
                        media_type='application/octet-stream',
                        filename=zipName)
