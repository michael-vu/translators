import docx2txt
import difflib
import re
import yaml

DEBUG = False
OUT_DIRECTORY = "output"
DIRECTORY = "GC-71401_attachments"
EN_DOC = "EN - SDK Landing Page - English.docx"
EN_XML = "static_pages.en.yml"
languages = ["de", "es", "fr", "it", "ja", "ko", "ru", "zh-CN", "zh-TW"]

cannotFind = []

def readFile(name):
    en_Text = docx2txt.process(DIRECTORY + "/" + name)
    en_Text = re.sub(r"\n+", "\n", en_Text)
    en_Text = en_Text.replace("Title: ", "", 1)
    en_Text = en_Text.replace("Meta description: ", "", 1)
    en_Text = en_Text.replace("Top nav bar link name: ", "", 1)
    # en_Text = re.sub(r"<|>", "", en_Text)
    splitText = en_Text.split("\n")
    return splitText

def readXML(name):
    with open(DIRECTORY + "/" + name) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

enDoc = readFile(EN_DOC)
enXml = readXML(EN_XML)

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

with open(DIRECTORY + "/" + EN_XML, "r") as file:
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
        t = doc[index]
        translations.append(t)
        if DEBUG:
            print("\t" + t)
    return translations

def writeTranslations(original, translations):
    for i in range(len(translations)):
        translation = translations[i]
        text = otherXMLText[i]
        otherXMLText[i] = text.replace(original, translation)

def findMatch(input, doc):
    # Nearest string find
    matches = difflib.get_close_matches(input, doc)
    if len(matches) > 0:
        match = matches[0]
        matchIndex = doc.index(match)
        translations = getTranslations(matchIndex)
        if DEBUG:
            print(translations)
        writeTranslations(input, translations)
    else:
            matchIndex = findStringWithStart(input, doc)
            if matchIndex > -1:
                if DEBUG:
                    print("EN: " + input)
                translations = getTranslations(matchIndex)
                writeTranslations(input, translations)
            else:
                cannotFind.append(input)

# What the fuck is happening here i have no clue
print("Parsing English XML")
def parseXML(input):
    if input == None:
        return
    if type(input) == list:
        for element in input:
            parseXML(element)
    elif type(input) == dict:
        for key in input:
            parseXML(input[key])
    elif type(input) == str:
        # I somehow broke this

        match = findMatch(input, enDoc)
        # writeTranslations(match, None)
        # print(match)


parseXML(enXml)
print("Writing XML files")
for i in range(len(languages)):
    lang = languages[i]
    textOut = otherXMLText[i]
    outName = EN_XML.replace("en", lang);
    with open(OUT_DIRECTORY + "/" + outName, "w") as file:
        file.write(textOut)

print("Cannot find %d items"%len(cannotFind))
