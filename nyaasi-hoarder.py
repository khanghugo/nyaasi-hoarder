import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser

# argument parsers to run as command line
# example of usage: python nyaasi-hoarder.py Fate Grand Order - Absolute Demonic Front Babylonia -q 1080 -dl
parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [-dl] [-save]')
parser.add_argument(help='Put the actual series name here', action="store", dest='seriesName', nargs='*')
parser.add_argument('-q', help='1080p/720p/480p/360p', action="store", dest='selectedQuality', default='1080p', nargs='?')
parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store_true")
parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
args = parser.parse_args()

# since argparse returns in list, I have to make it to string
seperator = ' '
seriesName = seperator.join(args.seriesName).replace("'", '')
print(seriesName)

selectedQuality = args.selectedQuality
print(selectedQuality)

# righy now, only HorribleSubs is supported. 
url = 'https://nyaa.si/user/HorribleSubs'
tag = 'a'
masterUrl = 'https://nyaa.si'

#some defines value to use
torrentList = []
magnetList = []
episodeList = []
count = 0
repeatTime = 10

#this makes the url query regarding of page raising up by one
def urlRaiser(number):
	return f'https://nyaa.si/user/HorribleSubs?p={number+1}'

#parsing with the fastest technology I can find
def parsingNyaasi(url):
	session = requests.Session()
	response = requests.get(url)
	strainer = SoupStrainer(tag)
	soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
	splitting = str(soup).split('<a href=')	
	return splitting

# this function returns episode number and torrent link
def findEpisodeData(htmlCode):
	for episodeIndex in htmlCode:
		if selectedQuality in episodeIndex and seriesName in episodeIndex:

			#yea this is only HR focused so their syntax is focused, more generalized script may come soon
			episodeNumber = episodeIndex.split(' - ')[2][:4].replace(' [', '')

			#index() is really useful to find the link
			magnetLink = str(htmlCode[htmlCode.index(episodeIndex)+2])[1:-40]
			torrentLink = str(htmlCode[htmlCode.index(episodeIndex)+1])[1:-42]
			print('Episode ' + episodeNumber + ' added!')

			#this makes into a list for multi-purpose uses
			torrentList.append(masterUrl + torrentLink)
			magnetList.append(magnetLink)
			episodeList.append(episodeNumber)

			#return this value so the loop can check logics
			return episodeNumber
			
#this is where the script happens
while repeatTime <= 10:

	#the input is count which starts with 0
	episodeNumber = findEpisodeData(parsingNyaasi(urlRaiser(count)))

	count = count + 1

	if episodeNumber == '01' or episodeList[-1] == '01':

		#this script is to find, not to find something is not there.
		print('Finding for episode 00 (mandatory for every series because it is not fed with the number of episodes but the latest one')
		print('You can cancel it now instead! Or find it out by yourself because it will just take time!)')

		repeatTime = repeatTime + 1

		if episodeList[-1] != '00' and repeatTime > 10:
			print('There is not episode 00')
			print('Done!')
			break

		continue
		#this is just the end point to the script
	if episodeNumber == '00':
		print('Done')
		break

#this is where the output is piped to
if args.dl:
	for link in magnetList:
		webbrowser.open(link)

if args.save:
	f = open(f"{seriesName} in {selectedQuality} magnet and torret links.txt", 'w+')
	for link in torrentList:
		f.write('Episode ' + episodeList[torrentList.index(link)] +": "+ link + "\r\n")
	for link2 in magnetList:
		f.write('Episode ' + episodeList[magnetList.index(link2)] +": "+ link2 + "\r\n")