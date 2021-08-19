from os import system
import yaml

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
EN_YML = "static_pages.en.yml"

languages = ["de", "es", "fr", "it", "ja", "ko", "ru", "zh-CN", "zh-TW"]

system("clear")
def readYML(name):
    with open(INPUT_DIR + "/" + name) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

translationMap = {}

def parseYML(ymlInput):
    global translationFoundCount
    if ymlInput == None:
        return
    if type(ymlInput) == list:
        for element in ymlInput:
            parseYML(element)
    elif type(ymlInput) == dict:
        for key in ymlInput:
            parseYML(ymlInput[key])
    elif type(ymlInput) == str:
        if not len(ymlInput) < 1:
            if not ymlInput in translationMap:
                print(ymlInput)
                translations = []
                for lang in languages:
                    translation = input(lang.upper() + ": ")
                    translations.append(translation)
                translationMap[ymlInput] = translations
                system("clear")

outputs = []
with open(INPUT_DIR + "/" + EN_YML, "r") as file:
    texts = file.read()
    for i in range(len(languages)):
        lang = languages[i]
        outputs.append(texts.replace("en", lang, 1))

engYML = readYML(EN_YML)
parseYML(engYML)

print("Writing to translation data")
for key in translationMap:
    translations = translationMap[key]
    for i in range(len(translations)):
        translation = translations[i]
        outputs[i] = outputs[i].replace(key, translation)

print("Files output")
i = 0
for lang in languages:
    outName = EN_YML.replace("en", lang)
    with open("./" + OUTPUT_DIR + "/" + outName, "w") as file:
        file.write(outputs[i])
    i = i + 1