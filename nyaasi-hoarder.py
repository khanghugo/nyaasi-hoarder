import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser
import re

class nyaasi_hoarder:
	def __init__(self, subTeam, seriesName, selectedQuality):
		self.subTeam = "Judas"
		self.seriesName = seriesName
		self.selectedQuality = selectedQuality
		#self.url = 'https://nyaa.si/user/HorribleSubs'
		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'
		self.episodeList = []
		self.magnetList = []
		self.torrentList = []
		self.rawData = []
		self.episodeListBug = ['']

	def urlRaiser(self, number):
		return f'https://nyaa.si/user/Judas?p={number+1}'

	def parsingNyaasi(self, url):
		session = requests.Session()
		response = requests.get(url)
		strainer = SoupStrainer(self.tag)
		soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
		return soup
		#splitting = str(soup).split('<a href=')	
		#return splitting

	def findEpisodeData(self, htmlCode):
		for htmlAttribute in htmlCode.find_all('a'):
			self.rawData.append(htmlAttribute)
		for episodeIndexRaw in self.rawData:
			episodeIndex = str(episodeIndexRaw)
			if self.selectedQuality in episodeIndex and self.seriesName in episodeIndex and self.subTeam in episodeIndex and "magnet" not in episodeIndex:
				episodeIndexNumber = self.rawData.index(episodeIndexRaw)
				episodeNumberRaw = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber]))[1]
				torrentLink = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber+1]))[0]
				magnetLink = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber+2]))[0]
				print(episodeNumberRaw + ' ADDED!')

				#this makes into a list for multi-purpose uses
				self.torrentList.append(self.masterUrl + torrentLink)
				self.magnetList.append(magnetLink)
				self.episodeList.append(episodeNumberRaw)

				episodeNumber = episodeNumberRaw.replace("[Judas]", "").replace(self.seriesName, "")[3:8].replace("[", "").replace(" ","")

				#print(episodeNumber)

				self.episodeListBug.append(episodeNumber)

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
			f.write(seriesList[linkList.index(link)] +": "+ link + "\r\n")


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
	nyaasi = nyaasi_hoarder('Judas', seperator.join(args.seriesName), args.selectedQuality)
	#print(seperator.join(args.seriesName))
	#print(args.selectedQuality)
	#print(nyaasi.findEpisodeData(nyaasi.parsingNyaasi(nyaasi.urlRaiser(0))))

	#this is where the script happens
	count = 0
	repeatTime = 0
	phase = 0
	
	# debug
	#phase1 = (nyaasi.parsingNyaasi(nyaasi.urlRaiser(count)))
	#phase2 = nyaasi.findEpisodeData(phase1)
	while repeatTime <= 20:
		try: 
			phase1 = (nyaasi.parsingNyaasi(nyaasi.urlRaiser(count)))
			phase2 = nyaasi.findEpisodeData(phase1)

			count += 1
		except KeyboardInterrupt:
			phase = 1
			break

	finalMagnetList = list(set(nyaasi.magnetList))
	finalTorrentList = list(set(nyaasi.torrentList))
	finalEpisodeList = list(set(nyaasi.episodeList))

	if args.dl == 'magnet':
		nyaasi.downloadThroughTorrent(finalMagnetList)
	
	elif args.dl == 'torrent':
		nyaasi.downloadThroughTorrent(finalTorrentList)
	
	if args.save:
		nyaasi.saveTorrentLink(finalMagnetList, finalEpisodeList, 'magnet')
		nyaasi.saveTorrentLink(finalTorrentList, finalEpisodeList, 'torrent')


if __name__ == '__main__':
	main()
