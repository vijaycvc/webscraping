from elasticsearch import Elasticsearch 
import requests
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import json
import sys

#es=Elasticsearch([{'host':'localhost','port':9200}])

def pushToES(symbol):
    #symbol="OXY"
    runDate = datetime.datetime.now()
    fileName = "{0}{1}.json".format(runDate.strftime('%Y%m%d'),symbol)
    outputJsonPath = ("{0}\\{1}\\{2}\\{3}\\{4}".
                      format(runDate.year, '%02d'%runDate.month, '%02d'%runDate.day, '%02d'%runDate.hour, fileName))
    
    jsonData=open(outputJsonPath).read()
    docId = "{0}{1}".format(runDate.strftime('%Y%m%d'),symbol)
    
    url = "http://localhost:9200/nesh/data/{0}".format(docId)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    #print(jsonData)
    requests.put(url, data=jsonData, headers=headers)
    data=requests.get(url)
    print(data.content)

if __name__ == '__main__':
    fileName = sys.argv[1:][0]
    symbols=open(fileName).read().split(',')
    for sym in symbols:
        pushToES(sym)