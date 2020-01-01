import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser

class nyaasi_hoarder:
	def __init__(self, subTeam, seriesName, selectedQuality):
		self.subTeam = subTeam
		self.seriesName = seriesName
		self.selectedQuality = selectedQuality
		self.url = 'https://nyaa.si/user/HorribleSubs'
		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'
		self.episodeList = []
		self.magnetList = []
		self.torrentList = []

	def urlRaiser(self, number):
		return f'https://nyaa.si/user/HorribleSubs?p={number+1}'

	def parsingNyaasi(self, url):
		session = requests.Session()
		response = requests.get(url)
		strainer = SoupStrainer(self.tag)
		soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
		splitting = str(soup).split('<a href=')	
		return splitting

	def findEpisodeData(self, htmlCode):
		for episodeIndex in htmlCode:
			if self.selectedQuality in episodeIndex and self.seriesName in episodeIndex:

				#yea this is only HR focused so their syntax is focused, more generalized script may come soon
				episodeNumber = episodeIndex.split(' - ')[2][:4].replace(' [', '')

				#index() is really useful to find the link
				magnetLink = str(htmlCode[htmlCode.index(episodeIndex)+2])[1:-40]
				torrentLink = str(htmlCode[htmlCode.index(episodeIndex)+1])[1:-42]
				print('Episode ' + episodeNumber + ' added!')

				#this makes into a list for multi-purpose uses
				self.torrentList.append(self.masterUrl + torrentLink)
				self.magnetList.append(magnetLink)
				self.episodeList.append(episodeNumber)

				#return this value so the loop can check logics
				return episodeNumber
	def downloadThroughTorrent(self, linkList):
		for link in linkList:
			webbrowser.open(link)

	def saveTorrentLink(self, linkList, seriesList, linkType):
		f = open(f"{self.seriesName} in {self.selectedQuality} magnet and torret links.txt", 'a') # a means (makes a new file and) append on it 

		if linkType == 'magnet':
			f.write('Magnet links \r\n')
		elif linkType == 'torrent':
			f.write('Torrent links \r\n')

		for link in linkList:
			f.write('Episode ' + seriesList[linkList.index(link)] +": "+ link + "\r\n")


def main():
	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [-dl] [-save]')
	parser.add_argument(help='Put the actual series name here', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-q', help='1080p/720p/480p/360p', action="store", dest='selectedQuality', default='1080p', nargs='?')
	parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store")
	parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
	args = parser.parse_args()


	# a little actions to convert parameter as a list to a string for use
	seperator = ' '
	#if args.seriesName: 
	#	seriesName = seperator.join(args.seriesName)
	#if args.selectedQuality:
	#	selectedQuality = args.selectedQuality

	# object
	nyaasi = nyaasi_hoarder('HorribleSubs', seperator.join(args.seriesName), args.selectedQuality)
	#print(seperator.join(args.seriesName))
	#print(args.selectedQuality)
	#print(nyaasi.findEpisodeData(nyaasi.parsingNyaasi(nyaasi.urlRaiser(0))))

	#this is where the script happens
	count = 0
	repeatTime = 0
	phase = 0
	
	while repeatTime <= 20:
	
		#the input is count which starts with 0
		episodeNumber = nyaasi.findEpisodeData(nyaasi.parsingNyaasi(nyaasi.urlRaiser(count)))

		#count associates with the urlRaiser to check every pages. So as this number increases, more pages are checked
		count += 1
		#for many series, 01 maybe the first episode, but some aren't so I have to incorporate a little part to check 00 episode
		if episodeNumber == '01': # since the episode number is in string, if the episode happen to be 100.5, I may need to add some lines to make it work
	
			#this script is to find, not to find something is not there.
			print('Finding for episode 00 (mandatory for every series because it is not fed with the number of episodes but the latest one')
			print('You can cancel it now instead! Or find it out by yourself because it will just take time!)')
			phase = 1 # the fact that episode 01 is found, it will now start phase '1' where it will find episode 00
	
		if phase == 1:
			repeatTime += 1 # the loop starts with a condition. this means if repeatTime is too high, the loop will stop so the dl and save can take part in. I cannot use the last condition to check this because not every episode after the '01' condition will forever be '01' but NoneType object instead
	
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
		nyaasi.downloadThroughTorrent(nyaasi.magnetList)
	
	elif args.dl == 'torrent':
		nyaasi.downloadThroughTorrent(nyaasi.torrentList)
	
	if args.save:
		nyaasi.saveTorrentLink(nyaasi.magnetList, nyaasi.episodeList, 'magnet')
		nyaasi.saveTorrentLink(nyaasi.torrentList, nyaasi.episodeList, 'torrent')
	

if __name__ == '__main__':
	main()