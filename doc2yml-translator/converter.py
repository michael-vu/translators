import docx2txt
import difflib
import re
import yaml

DEBUG = False
OUT_DIRECTORY = "output"
INPUT_DIR = "input"
EN_DOC = "EN - SDK Landing Page - English.docx"
EN_YML = "static_pages.en.yml"
languages = ["de", "es", "fr", "it", "ja", "ko", "ru", "zh-CN", "zh-TW"]

cannotFind = []

def readFile(name):
    en_Text = docx2txt.process("./" + INPUT_DIR + "/" + name)
    en_Text = re.sub(r"\n+", "\n", en_Text)
    en_Text = en_Text.replace("Title: ", "", 1)
    en_Text = en_Text.replace("Meta description: ", "", 1)
    en_Text = en_Text.replace("Top nav bar link name: ", "", 1)
    en_Text = re.sub(r"<|>", "", en_Text)
    splitText = en_Text.split("\n")
    return splitText

def readYML(name):
    with open("./" + INPUT_DIR + "/" + name) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

enDoc = readFile(EN_DOC)
enXml = readYML(EN_YML)

otherDoc = []
otherXMLText = []
print("Reading files")
for lang in languages:
    # Read all doc languages
    fileName = EN_DOC.replace("EN", lang.upper())
    if fileName.startswith("CN") or fileName.startswith("TW"):
        fileName = "zh-" + fileName
    doc = readFile(fileName)
    otherDoc.append(doc)

with open(INPUT_DIR + "/" + EN_YML, "r") as file:
    texts = file.read()
    for i in range(len(languages)):
        lang = languages[i]
        otherXMLText.append(texts.replace("en", lang, 1))

def findStringWithStart(input, doc):
    for i in range(len(doc)):
        if doc[i].lower().startswith(input.lower()):
            return i
    return -1

def getTranslations(index):
    translations = []
    for doc in otherDoc:
        if index < len(doc):
            t = doc[index]
            translations.append(t)
    return translations

def writeTranslations(original, translations):
    for i in range(len(translations)):
        translation = translations[i]
        otherXMLText[i] = otherXMLText[i].replace(original, translation)

def findMatch(input, doc):
    # Nearest string find
    matches = difflib.get_close_matches(input, doc)
    if len(matches) > 0:
        match = matches[0]
        matchIndex = doc.index(match)
    else:
        matchIndex = findStringWithStart(input, doc)
    return matchIndex

# What the fuck is happening here i have no clue
print("Parsing English YML")
translationFoundCount = 0
def parseYML(input):
    global translationFoundCount
    if input == None:
        return
    if type(input) == list:
        for element in input:
            parseYML(element)
    elif type(input) == dict:
        for key in input:
            parseYML(input[key])
    elif type(input) == str:
        matchIndex = findMatch(input, enDoc)
        if matchIndex > -1:
            translations = getTranslations(matchIndex)
            writeTranslations(input, translations)
            translationFoundCount = translationFoundCount + 1
        else:
            cannotFind.append(input)

parseYML(enXml)

print("Writing XML files")
for i in range(len(languages)):
    lang = languages[i]
    textOut = otherXMLText[i]
    outName = EN_YML.replace("en", lang)
    with open(OUT_DIRECTORY + "/" + outName, "w") as file:
        file.write(textOut)

print("Found %d translations!" % translationFoundCount)
print("Cannot find %d items"%len(cannotFind))

if DEBUG:
    print("=============CANNOT FIND:=============")
    for c in cannotFind:
        print(c)
    print("=============END CANNOT FIND LIST=============")