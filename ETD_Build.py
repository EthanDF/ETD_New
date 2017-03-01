from pymarc import *
import csv
import codecs
import unicodedata
from urllib import request
from urllib import error
import datetime

def readRawData():
    """Read in the CSV file from digital library"""

    rawData = 'Z:\\FenichelE\\ETDs\\2016_03FA_etd.csv'
    etdData = []
    with open(rawData, 'r', encoding='utf-8') as c:
        reader = csv.reader(c)
        for row in reader:
            etdData.append(row)

    return etdData

def createRecord():

    etdData = readRawData()

    rec = Record()
    #update Leader data
    ldrData = rec.leader
    rec.leader = ldrData[:4]+'nam'+ldrData[7:9]+'a'+ldrData[10:17]+'Li'+ldrData[19:]

    #create MARC 008
    date1 = '2016'
    date2 = '2016'
    DtST = 'd'
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

    #create nowtime
    year = str(datetime.datetime.now().year)
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
    marc008 = enteredDate+DtST+date1+date2+Ctry+ills+Audn+form+cont+gPub+conf+fest+indx+marc00832+litf+biog

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
    author = 'Abazari Aghdam, Sajjad'
    rec.add_field(
        Field(
            tag= '100',
            indicators= ['1',''],
            subfields = [
                'a', author.rstrip()+',',
                'e', 'author.'
            ]))

    # add main title
    title = 'A Systematic Review and Quantitative Meta-Analysis of the Accuracy of Visual Inspection for Cervical Cancer Screening: Does Provider Type or Training Matter?'
    titleA = ''
    titleB = ''
    if ':' in title:
        titleBreak = title.find(':')
        titleA =  title[:titleBreak].rstrip()+' :'
        titleB = title[titleBreak+1:].rstrip() + ' /'
    else:
        titleA = title.rstrip()+' /'
    marc245ind2 = '0'
    byAuthor = 'Sajjad Abazari Aghdam'
    rec.add_field(
        Field(
            tag='245',
            indicators=['1',marc245ind2],
            subfields=[
                'a', titleA.rstrip(),
                'b', titleB,
                'c', 'by '+byAuthor+'.'
            ]))

    #add MARC 264 - twice, once for copyright and one for regular
    # non copyright
    rec.add_field(
        Field(
            tag='264',
            indicators=[' ','1'],
            subfields=[
                'a', 'Boca Raton, Florida :',
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

    # add summary note, MARC 520
    abstact = etdData[1][14].rstrip()
    print(abstact)
    rec.add_field(
        Field(
            tag='520',
            indicators=['3', ' '],
            subfields=[
                'a', abstact
            ]))

    return rec