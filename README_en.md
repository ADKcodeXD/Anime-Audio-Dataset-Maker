# Anime Audio DataSet Maker 

- [English README](README_en.md)
- [中文说明](README.md)

<a href="https://www.bilibili.com/video/BV1VC4y1q7iX">使用演示和说明</a>

## Install

- First install pytorch accroding your cuda version

example for cuda11.8
```sh
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
if you want to see each version cuda install way can go to <a href="https://pytorch.org/get-started/locally/">pytorch</a>

- Second: install requirement.txt

```sh
pip3 install -r requirement.txt
```

## Introduce

This project is designed for anime and similar media, aiming to extract character audio quickly and efficiently.

We utilize pyannote and fastapi in our solution.

Additionally, a user-friendly web interface has been developed for this backend system.

WEBUI Download link: 
<a href="https://github.com/ADKcodeXD/Anime-Audio-Dataset-Maker-WEBUI/releases">Anime-Audio-Dataset-Maker-WEBUI Release</a>

## Usage

- First Step: Ensure Python3 is installed on your system. We recommend a version greater than Python 3.10.
- Second Step: Download this repository.
- Third Step: Download the WEBUI, unzip it, and place the Web folder in the same directory as this repository.
- Final Step: Run launch.bat. After the completion of pip installations, if there are no port conflicts, the website should open automatically.

## How it work

This project is a straightforward Python script. 
I employ pyannote.audio for splitting and classifying audio speakers.

This allows us to isolate each audio clip and categorize it into individual speaker folders.
But the accuracy is not yet ideal.

By incorporating subtitles, we can enhance the accuracy. The process involves obtaining the subtitle timeline for segmentation.
Subsequently, pyannote.audio is rerun to classify the audio clips segmented by the subtitle timeline.

We determine the best match for each speaker by calculating the longest overlap time.
Moreover, the integration of subtitles enables efficient audio text extraction!

## Feature

- Support automaticly split long audio by each speaker
- Support sub upload and slice by sub timeline.
- Support edit the sub text and export it by bert-vits config
- Support split ever single audio (WebUI)
- Support merge audio with interval (WebUI)
- Support management folders or files (WebUI)
- Support use Arrow key to handle data (WebUI)
- Support batch rename (WebUI)
- Support batch move or remove (WebUI)

