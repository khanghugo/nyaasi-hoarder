import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser

# argument parsers to run as command line
# example of usage: python nyaasi-hoarder.py Fate Grand Order - Absolute Demonic Front Babylonia -q 1080 -dl magnet
parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [-dl] [-save]')
parser.add_argument(help='Put the actual series name here', action="store", dest='seriesName', nargs='*')
parser.add_argument('-q', help='1080p/720p/480p/360p', action="store", dest='selectedQuality', default='1080p', nargs='?')
parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store")
parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
args = parser.parse_args()

# since argparse returns in list, I have to make it to string
seperator = ' '

if args.seriesName: 
	seriesName = seperator.join(args.seriesName)

if args.selectedQuality:
	selectedQuality = args.selectedQuality

#use these comments if you want to run by executing the script only
#seriesName = 'Fate Grand Order - Absolute Demonic Front Babylonia'
#selectedQuality = '1080p'
#arg.dl = True
#arg.save = True

# a head up
print(seriesName +' in ' +selectedQuality)


# righy now, only HorribleSubs is supported. in the future, the sub team will be an input
url = 'https://nyaa.si/user/HorribleSubs'
tag = 'a'
masterUrl = 'https://nyaa.si'

#some defines value to use
torrentList = []
magnetList = []
episodeList = []
count = 0
repeatTime = 0
phase = 0

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

#this is where the output is piped to

def downloadThroughTorrent(linkList):
	for link in linkList:
		webbrowser.open(link)

def saveTorrentLink(linkList, seriesList, linkType):
	f = open(f"{seriesName} in {selectedQuality} magnet and torret links.txt", 'a') # a means (makes a new file and) append on it 

	if linkType == 'magnet':
		f.write('Magnet links \r\n')
	elif linkType == 'torrent':
		f.write('Torrent links \r\n')

	for link in linkList:
		f.write('Episode ' + seriesList[linkList.index(link)] +": "+ link + "\r\n")
		

#this is where the script happens
while repeatTime <= 20:

	#the input is count which starts with 0
	episodeNumber = findEpisodeData(parsingNyaasi(urlRaiser(count)))

	#count associates with the urlRaiser to check every pages. So as this number increases, more pages are checked
	count = count + 1

	#for many series, 01 maybe the first episode, but some aren't so I have to incorporate a little part to check 00 episode
	if episodeNumber == '01': # since the episode number is in string, if the episode happen to be 100.5, I may need to add some lines to make it work

		#this script is to find, not to find something is not there.
		print('Finding for episode 00 (mandatory for every series because it is not fed with the number of episodes but the latest one')
		print('You can cancel it now instead! Or find it out by yourself because it will just take time!)')
		phase = 1 # the fact that episode 01 is found, it will now start phase '1' where it will find episode 00

	if phase == 1:
		repeatTime = repeatTime + 1 # the loop starts with a condition. this means if repeatTime is too high, the loop will stop so the dl and save can take part in. I cannot use the last condition to check this because not every episode after the '01' condition will forever be '01' but NoneType object instead

	# pretty self-explanatory
	if episodeNumber == '00':
		print('Done')
		break
	# when finding episode 00, the script has limited pages to check on, and the repeatTime is the number of pages need checking after 01
	if repeatTime > 20:
		print('No episode 00 found!')
		print('Done')
		break

if args.dl == 'magnet':
	downloadThroughTorrent(magnetList)

elif args.dl == 'torrent':
	downloadThroughTorrent(torrentList)

if args.save:
	saveTorrentLink(magnetList, episodeList, 'magnet')
	saveTorrentLink(torrentList, episodeList, 'torrent')
