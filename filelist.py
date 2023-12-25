import os
from typing import Dict


class TextListManager:

    def __init__(self, folderPath):
        self.folderPath = folderPath
        self.filePath = f"{folderPath}/templist.list"
        self.data = self.readData()

    def readData(self):
        data = {}
        if not os.path.isfile(self.filePath):
            open(self.filePath, 'w', encoding='utf-8').close()
        with open(self.filePath, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) == 4:
                    data[parts[0]] = {
                        'speaker': parts[1],
                        'language': parts[2],
                        'text': parts[3]
                    }
        return data

    def getData(self, filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            filenameKey = filename.replace('\\', '/')
            if filenameKey in self.data:
                return self.data.get(filenameKey)
            return None
        return None

    def saveToMap(self, targetMap):
        targetMap.update(self.data)

    def deleteEntry(self, filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            filename = filename.replace('\\', '/')
        else:
            return None
        if filename in self.data:
            del self.data[filename]
            self.writeData()

    def updateEntry(self, filename, newData: Dict[str, any]):
        if os.path.exists(filename) and os.path.isfile(filename):
            filename = filename.replace('\\', '/')
        else:
            return None
        if filename in self.data:
            self.data[filename].update(newData)
            self.writeData()
        else:
            speaker = os.path.basename(os.path.dirname(filename))
            language = newData.get('language') or 'JP'
            text = newData.get('text') or ''
            self.addNewEntry(filename, text, speaker, language)

    def renameEntry(self, oldName, newFileName):
        if os.path.exists(oldName) and os.path.isfile(oldName):
            oldName = oldName.replace('\\', '/')
        else:
            return None
        if oldName in self.data:
            target = self.getData(oldName)
            self.addNewEntry(newFileName, target['text'], target['speaker'],
                             target['language'])
            self.deleteEntry(oldName)

    def addNewEntry(
        self,
        filename,
        text,
        speaker='SPAKER0',
        language='JP',
    ):
        filename = filename.replace('\\', '/')
        self.data[filename] = {
            'text': text,
            'speaker': speaker,
            'language': language
        }
        self.writeData()
        return True

    def mergeSentences(self, filenames, newFilename):
        mergedText = ''
        speaker = ''
        language = ''
        filenames = map(lambda name: name.replace('\\', '/'), filenames)
        newFilename = newFilename.replace('\\', '/')
        for filename in filenames:
            if filename in self.data:
                mergedText += (self.data[filename]['text'] + ' ')
                if not speaker:
                    speaker = self.data[filename]['speaker']
                if not language:
                    language = self.data[filename]['language']
                self.deleteEntry(filename)
        if mergedText:
            newEntry = {
                'speaker': speaker,
                'language': language,
                'text': mergedText.strip()  # 删除末尾的空格
            }
            self.data[newFilename] = newEntry
            self.writeData()

    def splitSentence(self, filename, newFilenames):
        newFilenames = map(lambda name: name.replace('\\', '/'), newFilenames)
        filename = filename.replace('\\', '/')
        if filename in self.data:
            originalEntry = self.data[filename]
            for newFilename in newFilenames:
                newEntry = {
                    'speaker': originalEntry['speaker'],
                    'language': originalEntry['language'],
                    'text': originalEntry['text']
                }
                self.data[newFilename] = newEntry
            # 删除原始文件名对应的条目
            del self.data[filename]
            # 将更改写入文件
            self.writeData()

    def cleanSentence(self):
        keysToDelete = []
        for filename in self.data:
            if not os.path.exists(filename) or not os.path.isfile(filename):
                keysToDelete.append(filename)
        for key in keysToDelete:
            del self.data[key]
        if keysToDelete:
            self.writeData()

    def writeData(self):
        with open(self.filePath, 'w', encoding='utf-8') as file:
            for path, info in self.data.items():
                line = f"{path}|{info['speaker']}|{info['language']}|{info['text']}\n"
                file.write(line)
        self.readData()
