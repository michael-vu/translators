from os import name
import pandas as pd
import difflib
import yaml

DEBUG = True
EXCEL_FILE = "Application forms translations (GC-72055) from vendor.xlsx"
EN_XML = "static_pages.en.yml"

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
START_ROW = 6
MAX_ROW = 50
languages = ["en", "de", "es", "fr", "it", "ru", "ja", "ko", "zh-CN", "zh-TW"]

# "de", "es", "fr", "it", "ja", "ko", "ru", "zh-CN", "zh-TW"

engXmlValues = []
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
        engXmlValues.append(input)

def readExcelData(name):
    excelTranslation = pd.read_excel(INPUT_DIR + "/" + name, header=START_ROW, nrows=MAX_ROW)
    data = excelTranslation.values
    cleanOutput = []
    for rows in data:
        isClean = False
        for i in range(len(rows)):
            if type(rows[i]) == str:
                rows[i] = str(rows[i]).replace(u'\xa0', u' ')
                isClean = True
            if type(rows[3]) == float:
                isClean = False
        if isClean:
            cleanOutput.append(rows)
    return cleanOutput

def readXML(name):
    with open(INPUT_DIR + "/" + name) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

enXml = readXML(EN_XML)
print("Parsing English XML")
parseXML(enXml)
otherXMLText = []

with open(INPUT_DIR + "/" + EN_XML, "r") as file:
    texts = file.read()
    for i in range(len(languages)):
        lang = languages[i]
        otherXMLText.append(texts.replace("en", lang, 1))

excelData = readExcelData(EXCEL_FILE)
engTexts = []
for row in excelData:
    engTexts.append(row[0])

def findMatch(input, doc):
    matches = difflib.get_close_matches(input, doc)
    # Nearest string find
    if len(matches) > 0:
        match = matches[0]
        matchIndex = doc.index(match)
        return matchIndex
    return -1

notFoundCount = 0
foundCount = 0

notFoundList = []

for text in engXmlValues:
    matchIndex = findMatch(text, engTexts)
    if matchIndex > -1:
        for i in range(len(otherXMLText)):
            data = otherXMLText[i]
            translatedText = excelData[matchIndex][i].strip()
            otherXMLText[i] = data.replace(text, translatedText)
        foundCount = foundCount + 1
    else:
        notFoundCount = notFoundCount + 1
        notFoundList.append(text)

print("Found %d translations!" % foundCount)
print("Cannot find %d translations!" % notFoundCount)

print("=====================NOTFOUND========================")
if DEBUG:
    for i in notFoundList:
        print(i)
print("=====================NOTFOUND========================")

for lang in languages:
    EN_XML.replace("en", lang)

print("Writing XML files")
for i in range(len(languages)):
    lang = languages[i]
    textOut = otherXMLText[i]
    outName = EN_XML.replace("en", lang)
    with open(OUTPUT_DIR + "/" + outName, "w") as file:
        file.write(textOut)