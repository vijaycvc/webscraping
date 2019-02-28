import bs4 as bs
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
import codecs
import datetime
import os
import json
import regex as re
import sys
from textblob import TextBlob

rootFolder = "D:\\Nesh\\Now\\data"
headers = {'User-Agent': 'Mozzila/5.0'}
only_transcripts = SoupStrainer(sasource="qp_analysis")
finEndPoints = {'OXY':'https://www.fool.com/quote/nyse/occidental-petroleum/oxy',
                'EOG':'https://www.fool.com/quote/nyse/eog-resources/eog',
                'APC':'https://www.fool.com/quote/nyse/anadarko-petroleum/apc',
                'APA':'https://www.fool.com/quote/nyse/apache/apa',
                'COP':'https://www.fool.com/quote/nyse/conocophillips/cop',
                'PXD':'https://www.fool.com/quote/nyse/pioneer-natural-resources/pxd'}

symToNameMap = {'OXY':'Occidental Petroleum',
                'EOG':'EOG Resources',
                'APC':'Anadarko Petroleum',
                'APA':'Apache',
                'COP':'Conocophillips',
                'PXD':'Pioneer Natural Resources'}

headings = re.compile(r"\L<words>", words=['Executive','Analyst','Participant'])
months = re.compile(r"\L<words>.*", words=['January','February','March','April','May','June','July','August','September','October','November','December'])

class EarningCall:
    def __init__(self, participantsDetail, participantWordCount, participantMaxCount, callDate, symbol):
        self.participantsDetail = participantsDetail
        self.participantWordCount = participantWordCount
        self.participantMaxCount = participantMaxCount
        self.callDate = callDate
        self.symbol = symbol

class News:
    def __init__(self, newsArticles, symbol):
        self.newsArticles =newsArticles;
        self.symbol = symbol
        
class FinData:
    def __init__(self, dataDict, symbol):
        self.dataDict =dataDict;
        self.symbol = symbol
        
def GetTranscriptsData(symbol):
    allTranscripts = "{0}\\{1}\\{2}".format(rootFolder,symbol,"transcripts.html")
    allTranscriptsData = codecs.open(allTranscripts, "r")
    allTsoup = BeautifulSoup(allTranscriptsData, 'html.parser')
    
    transLocData=allTsoup.find("a", {"sasource": "qp_analysis"})
    transFile = transLocData['href']+'.html'
    transFile = transFile.replace('/','\\')
    transFile = "{0}\\{1}{2}".format(rootFolder,symbol,transFile)
    
    transData = codecs.open(transFile, "r")
    tsoup = BeautifulSoup(transData, 'html.parser')
    
    participants=tsoup.find_all("p", {"class": lambda L: L and L.startswith('p p')})

    dict = {}
    part=[]
    flag = 0
    count=0
    spkr=""
    callDate=""
    for name in participants:
        namestr = str(name)
        if flag < 2:
            if not headings.search(namestr) and flag == 0:
                out = months.search(name.text)
                if out:
                    callDate = out.group(0)
                continue
            elif headings.search(namestr):
                flag = 1
            elif not headings.search(name.text) and "<strong>" in namestr and flag == 1:
                flag = 2
                spkr = name.text
                count = 0
            else:
                dict[name.text.split(' - ')[0]]=0
                part.append(name.text)
        else:
          if "<strong>" in namestr:
              if spkr in dict.keys():
                  dict[spkr] += count
              spkr = name.text
              count = 0
          else:
              count+=len(name.text.split())
    return dict,part,callDate

def GetNewsData(symbol):
    sauce = urllib.request.urlopen('https://www.nasdaq.com/symbol/{0}'.format(symbol))
    soup = bs.BeautifulSoup(sauce,'lxml')

    dict={}
    articles = soup.find("div", {"id": "CompanyNewsCommentary"}).find_all('a')
    for art in articles:
        dict[art.text.strip()] = art['href']
    return dict

def GetSentimentOfNewsData(dict): 
    articles=[]
    for art in dict.values():
        if not 'symbol' in art:
            sauce = urllib.request.urlopen(art)
            soup = bs.BeautifulSoup(sauce,'lxml')
            print(art)
            paras = soup.find("div", {"id": "articlebody"}).find_all('p')
            
            article=''
            for para in paras:
                article+=para.text
            articles.append(article)
    
    pol=[]
    for art in articles:
        blb = TextBlob(art)
        pol.append(blb.sentiment.polarity)

    return(sum(pol)/len(pol))

def GetFinancialNumbers(symbol):
    sauce = urllib.request.urlopen(finEndPoints[symbol])
    soup = bs.BeautifulSoup(sauce,'lxml')
    
    currentPriceTrend=soup.find("h2", {"class": lambda L: L and L.startswith('price-change-percent')})
    currentTrend = currentPriceTrend.text.strip().replace('%','').replace('(','').replace(')','')
   
    data = []
    dataDict = {}
    table = soup.find('table', attrs={'class':'key-data-points data-table key-data-table1'})
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    data.append(['Current Trend',currentTrend])
    
    for item in data:
        dataDict[item[0].replace(':','')]=item[1]
    
    return dataDict

def main(symbol):    
    runDate = datetime.datetime.now()
    fileName = "{0}{1}.json".format(runDate.strftime('%Y%m%d'),symbol)
    outputJsonPath = ("{0}\\{1}\\{2}\\{3}\\{4}".
                      format(runDate.year, '%02d'%runDate.month, '%02d'%runDate.day, '%02d'%runDate.hour, fileName))
    
    ecallDict,ecallFullNames,callDate = GetTranscriptsData(symbol)
    maxSpkr = max(ecallDict,key=ecallDict.get)
    
    newsDict = GetNewsData(symbol)
    finData = GetFinancialNumbers(symbol)
    
    senNewsData = round(GetSentimentOfNewsData(newsDict),2)
    finData['sentiment'] = str(senNewsData)
    
    finDataObject = FinData(finData,symbol)
    newsDataObject = News(newsDict, symbol)
    ecallDataObject = EarningCall(ecallFullNames, ecallDict, maxSpkr, callDate, symbol) 
    
    os.makedirs(os.path.dirname(outputJsonPath), exist_ok=True)
    with open(outputJsonPath, "w") as outfile:
        json.dump({
        "symbol":symbol,
        "companyName": symToNameMap[symbol],
        "findata":finDataObject.__dict__,
        "news": newsDataObject.__dict__,
        "earningcall":ecallDataObject.__dict__
         }, outfile)

if __name__ == '__main__':
    fileName = sys.argv[1:][0]
    symbols=open(fileName).read().split(',')
    for sym in symbols:
        main(sym)