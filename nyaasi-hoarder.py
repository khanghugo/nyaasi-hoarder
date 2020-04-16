import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser
import re

# python nyaasi-hoarder.py "Re Zero kara Hajimeru Isekai Seikatsu - Director's Cut" -fs HorribleSubs -q 1080p -save
# python nyaasi-hoarder.py Dorohedoro -ep 09 -q 1080p -dl magnet


class nyaasi_hoarder:
	def __init__(self, subTeam, seriesName, selectedQuality):
		self.subTeam = subTeam
		self.seriesName = seriesName
		self.selectedQuality = selectedQuality
		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'
		self.episodeList = []
		self.magnetList = []
		self.torrentList = []
		self.rawData = []
		self.episodeListBug = []

	def urlRaiser(self, number):
		return self.masterUrl+"/user/"+self.subTeam+"?p="+str(number+1)

	def parsingNyaasi(self, url):
		session = requests.Session()
		response = requests.get(url)
		strainer = SoupStrainer(self.tag)
		soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
		return soup


	def findEpisodeData(self, htmlCode):

		for htmlAttribute in htmlCode.find_all('a'):
			self.rawData.append(str(htmlAttribute))

		for episodeIndex in self.rawData:

			if self.selectedQuality in episodeIndex and self.seriesName in episodeIndex and self.subTeam in episodeIndex and "magnet:?" not in episodeIndex:

				episodeIndexNumber = self.rawData.index(episodeIndex)
				
				episodeNumberRaw = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber]))[1]
				torrentLink = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber+1]))[0]
				magnetLink = re.findall('"([^"]*)"', str(self.rawData[episodeIndexNumber+2]))[0]

				if episodeNumberRaw not in self.episodeList:

					print(episodeNumberRaw + ' FOUND!')
					self.torrentList.append(self.masterUrl + torrentLink)
					self.magnetList.append(magnetLink)
					self.episodeList.append(episodeNumberRaw)

					episodeNumber = episodeNumberRaw.replace(f"[{self.subTeam}]", "").replace(self.seriesName, "")[3:8].replace("[", "").replace(" ","")

					self.episodeListBug.append(episodeNumber)
				
				else:
					pass



	def downloadThroughTorrent(self, linkList, mode):
		if mode == 0:
			for link in linkList:
				webbrowser.open(link)
				
		if mode == 1:
			webbrowser.open(linkList)

	def saveTorrentLink(self, linkList, seriesList, linkType, mode):
		f = open(f"{self.seriesName} in {self.selectedQuality} magnet and torret links.txt", 'a') # a means (makes a new file and) append on it 

		if linkType == 'magnet':
			f.write('Magnet links \r\n')
		elif linkType == 'torrent':
			f.write('Torrent links \r\n')

		
		if mode == 1: # mode 1 is downloading one single epsiode. I try to use the type() method instead but somehow I am too spaghetti for that.
			f.write(seriesList +": "+ linkList + "\r\n")

		if mode == 0: # mode 0 is download in list.
			for link in linkList:
				f.write(seriesList[linkList.index(link)] +": "+ link + "\r\n")

def main():
	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [-dl] [-save]')
	parser.add_argument(help='Put the actual series name here', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-ep', help='Episode Number', action="store", dest='dlEpisode', default='all', nargs='?')
	parser.add_argument('-fs', help='Name of the fansub team (Judas is default)', action="store", dest='subTeam', default='Judas', nargs='?')
	parser.add_argument('-q', help='1080p | 720p | 480p | 360p (1080p is default)', action="store", dest='selectedQuality', default='1080p', nargs='?')
	parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store")
	parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
	args = parser.parse_args()


	seperator = ' '

	# object
	nyaasi = nyaasi_hoarder(str(args.subTeam), seperator.join(args.seriesName), args.selectedQuality)


	#this is where the script happens
	count = 0
	phase = 0

	while True: # <=
		try: 

			episodeNumber = nyaasi.findEpisodeData(nyaasi.parsingNyaasi(nyaasi.urlRaiser(count)))

			count += 1

			if nyaasi.episodeListBug == []:
				continue

			else:
				if args.dlEpisode == 'all':
					if nyaasi.episodeListBug[-1] == '01':
						if phase == 0:
							print("\r\nFINDING EPISODE 00!", end ="", flush=True)
						phase += 1
						print(".", end="", flush=True)

						if phase > 10:
							print("\r\n\r\nTHERE IS NO EPISODE 00!")
							break

					elif nyaasi.episodeListBug[-1] == '00':
						break

				if args.dlEpisode != 'all':
					if nyaasi.episodeListBug[-1] == args.dlEpisode:
						print("\r\n\r\nDONE!")
						break



		except KeyboardInterrupt:
			break

	if args.dlEpisode == 'all':
		if args.dl == 'magnet':
			nyaasi.downloadThroughTorrent(nyaasi.magnetList, 0)
	
		elif args.dl == 'torrent':
			nyaasi.downloadThroughTorrent(nyaasi.torrentList, 0)
	
		if args.save:
			nyaasi.saveTorrentLink(nyaasi.magnetList, nyaasi.episodeList, 'magnet', 0)
			nyaasi.saveTorrentLink(nyaasi.torrentList, nyaasi.episodeList, 'torrent', 0)

	if args.dlEpisode != 'all':
		if args.dl == 'magnet':
			nyaasi.downloadThroughTorrent(nyaasi.magnetList[-1], 1)
	
		elif args.dl == 'torrent':
			nyaasi.downloadThroughTorrent(nyaasi.torrentList[-1], 1)
	
		if args.save:
			nyaasi.saveTorrentLink(nyaasi.magnetList[-1], nyaasi.episodeList[-1], 'magnet', 1)
			nyaasi.saveTorrentLink(nyaasi.torrentList[-1], nyaasi.episodeList[-1], 'torrent', 1)


if __name__ == '__main__':
	main()
