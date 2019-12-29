import requests
from bs4 import BeautifulSoup, SoupStrainer
import time

seriesName = 'Shinchou Yuusha'
selectedQuality = '1080p'
isfindMagnet = 1
isfindTorrent = 1

url = 'https://nyaa.si/user/HorribleSubs'
tag = 'a'
torrentId = ''
torrentUrl = 'https://nyaa.si/'

torrentList = []
magnetList = []
episodeList = []
phase = 0
count = 0
'''
def killingFinding():
	for m in splitting:
		if seriesName in m and selectedQuality in m:
			return m
'''
def urlRaiser(number):
	return f'https://nyaa.si/user/HorribleSubs?p={number+1}'

def parsingNyaasi(url):
	session = requests.Session()
	response = requests.get(url)
	#soup = BeautifulSoup(response.text, "html.parser")
	#finding = soup.findAll(tag)
	strainer = SoupStrainer(tag)
	soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
	splitting = str(soup).split('<a href=')	
	return splitting

def findEpisodeData(htmlCode):
	for episodeIndex in htmlCode:
		if selectedQuality in episodeIndex and seriesName in episodeIndex:
			episodeNumber = episodeIndex.split(' - ')[2][:4].replace(' [', '')
			magnetLink = str(htmlCode[htmlCode.index(episodeIndex)+2])[1:-40]
			torrentLink = str(htmlCode[htmlCode.index(episodeIndex)+1])[1:-42]
			print(episodeNumber)
			print(magnetLink)
			print(torrentLink)
			return episodeNumber
			

while True:

	episodeNumber = findEpisodeData(parsingNyaasi(urlRaiser(count)))

	count = count + 1

	if episodeNumber == '00':
		break

	time.sleep(0.1)