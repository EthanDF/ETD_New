from pymarc import *
import csv
import codecs
import unicodedata
from urllib import request
from urllib import error
import datetime

outputFile = 'processing_files\\results.dat'
nonFilingCharacters = []
nfcList = 'processing_files\\non-filing_characters.txt'

with open(nfcList) as f:
    tempF = f.readlines()
    for line in tempF:
        nonFilingCharacters.append(line.strip('\n'))

def readRawData():
    """Read in the CSV file from digital library"""

    rawData = 'processing_files\\2016_03FA_etd.csv'
    etdData = []
    with open(rawData, 'r', encoding='utf-8') as c:
        reader = csv.reader(c)
        for row in reader:
            etdData.append(row)

    return etdData

def reverseAuthorName(author):

    comma = author.find(',')
    reverseAuthor = author[comma+1:]+' '+author[:comma]
    return reverseAuthor

def determineNFChars(title):

    title = title.upper()
    ind2 = 0
    for nfc in nonFilingCharacters:
        # print(nfc, len(nfc))
        if title[:len(nfc.upper())] == nfc.upper():
            ind2 = len(nfc)
            break

    return ind2

def determineCampus(location):
    campus = 'Boca Raton'
    if location == 'Florida Atlantic University Digital Library: Boca Raton, Fla.':
        campus = 'Boca Raton'
    else:
        print("no location found")
        return
    return campus

def createRecord(testList):

    author = testList[0]
    title = testList[1]
    date = testList[2]
    date2 = testList[3]
    location = testList[4]
    degree = testList[5]
    description = testList[6]
    language = testList[7]
    purl = testList[8]

    rec = Record()
    ldrData = rec.leader
    #update Leader data

    type6 = 'a'
    BLvl7 = 'm'
    ELvl17 = 'I'
    Desc18 = 'i'

    ldrData = rec.leader
    rec.leader = ldrData[0:6]+type6+BLvl7+ldrData[8:10]+ldrData[10:17]+ELvl17+Desc18+ldrData[19:]

    #create MARC 008
    date1 = date
    date2 = date2
    DtST = 't'
    Ctry = 'flu'
    ills = '    '
    Audn = ' '
    form = 'o'
    cont = 'bm  '
    gPub = ' '
    conf = '0'
    fest = '0'
    indx = '0'
    marc00832 = ' '
    litf = '0'
    biog = ' '

    # establish language
    lang = 'eng'
    if language == 'English':
        lang = 'eng'
    elif language == 'Spanish':
        lang = 'spa'
    elif language == 'French':
        lang = 'fra'

    marc00838 = ' '
    Srce = 'd'


    #create nowtime
    year = str(datetime.datetime.now().year)[2:]
    month = datetime.datetime.now().month
    if month < 10:
        month = '0'+str(month)
    else:
        month = str(month)
    day = datetime.datetime.now().day
    if day < 10:
        day = '0'+str(day)
    else:
        day = str(day)
    enteredDate = year+month+day

    #put together the MARC 008 field
    marc008 = enteredDate+DtST+date1+date2+Ctry+ills+Audn+form+cont+gPub+conf+fest+indx+marc00832+litf+biog+\
              lang+marc00838+Srce

    field008 = Field(tag='008', data = marc008)
    rec.add_field(field008)

    #add MARC 040
    rec.add_field(
        Field(
            tag='040',
            indicators= [' ',' '],
            subfields=[
                'a', 'FGM',
                'b', 'eng',
                'c', 'FGM',
                'e', 'rda'
            ]))

    # add author data

    rec.add_field(
        Field(
            tag= '100',
            indicators= ['1',' '],
            subfields = [
                'a', author.rstrip()+',',
                'e', 'author.'
            ]))

    # add main title

    titleA = ''
    titleB = ''
    if ':' in title:
        titleBreak = title.find(':')
        titleA =  title[:titleBreak].rstrip()+' :'
        titleB = title[titleBreak+1:].rstrip() + ' /'
    else:
        titleA = title.rstrip()+' /'
    marc245ind2 = determineNFChars(title)
    byAuthor = reverseAuthorName(author.rstrip())
    rec.add_field(
        Field(
            tag='245',
            indicators=['1',marc245ind2],
            subfields=[
                'a', titleA.rstrip(),
                'b', titleB,
                'c', 'by '+byAuthor.lstrip().rstrip()+'.'
            ]))

    #add MARC 264 - twice, once for copyright and one for regular
    # non copyright

    #get campus
    campus = determineCampus(location)

    rec.add_field(
        Field(
            tag='264',
            indicators=[' ','1'],
            subfields=[
                'a', campus+', Florida :',
                'b', 'Florida Atlantic University,',
                'c', date1+'.'
            ]))
    # copyright date
    rec.add_field(
        Field(
            tag='264',
            indicators=[' ', '4'],
            subfields=[
                'c', '©'+date2
            ]))

    #add Physical Description

    #add RDA 33X Fields
    #MARC 336
    rec.add_field(
        Field(
            tag='336',
            indicators=[' ', ' '],
            subfields=[
                'a', 'text',
                'b', 'txt',
                '2', 'rdacontent'
            ]))
    # MARC 337
    rec.add_field(
        Field(
            tag='337',
            indicators=[' ', ' '],
            subfields=[
                'a', 'computer',
                'b', 'c',
                '2', 'rdamedia'
            ]))
    # MARC 338
    rec.add_field(
        Field(
            tag='338',
            indicators=[' ', ' '],
            subfields=[
                'a', 'online resource',
                'b', 'cr',
                '2', 'rdacarrier'
            ]))

    # add Dissertation Note, MARC 502
    #get date for subfield....

    # add summary note, MARC 520
    abstact = description.replace('\n',' ')

    rec.add_field(
        Field(
            tag='520',
            indicators=['3', ' '],
            subfields=[
                'a', abstact
            ]))

    # add URL to Digital Library, MARC 856
    rec.add_field(
        Field(
            tag='856',
            indicators=['4','0'],
            subfields=[
                'z', 'Full text available:',
                'u', purl
            ]))

    return rec

def writeNewMARC(record):
    with open(outputFile, 'ab') as x:
        try:
            x.write((record.as_marc()))
        except UnicodeEncodeError:
            print ("couldn't write")

def runTest(recNum):
    etdData = readRawData()

    etdRecForTest = recNum
    testList = [etdData[etdRecForTest][3],etdData[etdRecForTest][2],etdData[etdRecForTest][7],etdData[etdRecForTest][7],
                etdData[etdRecForTest][16],'Degree TBD', etdData[etdRecForTest][14], etdData[etdRecForTest][13],
                etdData[etdRecForTest][20]]
    r = createRecord(testList)
    writeNewMARC(r)
    print("Done!")
    return r