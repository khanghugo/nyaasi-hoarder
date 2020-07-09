import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser
import re

# python nyaasi_hoarder.py Gundam Build Divers Re-RISE -fs HorribleSubs -q 1080p -save
# python nyaasi_hoarder.py Dorohedoro -ep 09 -q 1080p -dl magnet


class nyaasi_hoarder:
	def __init__(self, subTeam, seriesName, selectedQuality):
		self.subTeam = subTeam

		self.seriesName = seriesName
		self.selectedQuality = selectedQuality

		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'

		self.episodeList = []
		self.episodeListJustNumber = []
		self.magnetList = []
		self.torrentList = []
		self.rawFilteredData = []


		# add more if U like it.
		self.subTeamDict = {
		"EMBER": "Ember_Encodes",
		"HR": "HR-Minifreeza",
		"YakuboEncodes": "yakubo"
		}

		if self.subTeam in self.subTeamDict:
			self.subTeamUrl = self.subTeamDict[ self.subTeam ]

		else:
			self.subTeamUrl = self.subTeam

		#DEBUG
		#print(self.episodeListJustNumber)

		# it just makes the page number go up
	def urlRaiser(self, number):
		return self.masterUrl+"/user/"+self.subTeamUrl+"?p="+str(number+1)

		# getting the html. I just look up online for this method.
	def parsingNyaasi(self, url):
		session = requests.Session()
		response = requests.get(url)
		strainer = SoupStrainer(self.tag)
		soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
		return soup

		# some titles have adopted new formats like "S01E02" and is totally different from what they used to be. So this converts it to understandable info
	def convertEpisodeFormatFromFullToNumber(self, episodeFullTitle):

		def isNumber(char):
			try:
				int(char)
				return True

			except:
				return False

		episodeFullTitleCharList = []
		seasonKey = 'S'
		episodeKey = 'E'

		for index, char in enumerate(episodeFullTitle):
			episodeFullTitleCharList.append(char)

			try:
				# this reads from right to left. for example, "Re:Zero SE01E14" will find if there is any number there. Then it will start from right to left. 
				# If the next one is the number then good. If the next one is "E" then good. And so on.
				# Right now it is limited to 99 episodes and 99 seasons. I will try to find a way to make it through.

				if (index >= 5) and (isNumber(episodeFullTitleCharList[index]) == True) and (isNumber(episodeFullTitleCharList[index - 1]) == True) and (episodeFullTitleCharList[index - 2] == episodeKey) and (isNumber(episodeFullTitleCharList[index - 3]) == True) and (isNumber(episodeFullTitleCharList[index - 4]) == True) and (episodeFullTitleCharList[index - 5] == seasonKey):
					return (str(episodeFullTitleCharList[index - 4 ]) + str(episodeFullTitleCharList[index - 3])), (str(episodeFullTitleCharList[index - 1 ]) + str(episodeFullTitleCharList[index]))

			except Exception as e:
				print(e)
				break

			# this does most of the work to intepret the data including torrent, magnet, episode number, title, quality
	def findEpisodeData(self, htmlCode):

			# from chunk of text to list
		for htmlLinesWithSelectedClass in htmlCode.find_all('a'):
			self.rawFilteredData.append(str(htmlLinesWithSelectedClass))

		for entriesIn_rawFilteredData_Index, entriesIn_rawFilteredData in enumerate(self.rawFilteredData):

			# casually filtering text
			if self.selectedQuality in entriesIn_rawFilteredData and self.seriesName in entriesIn_rawFilteredData and self.subTeam in entriesIn_rawFilteredData and "magnet:?" not in entriesIn_rawFilteredData:

				# at this point, I forgot how these things work. I think they are in the quotation mark ("") so this just takes all the text in it.
				# if the website changes, this would be the first thing that breaks
				episodeFullTitle = re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index]))[1]

				torrentLink = re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index + 1]))[0]
				magnetLink = re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index + 2]))[0]

				# throughout the html, there are many times when the title repeats, it just makes sure that doesn't happen.
				if episodeFullTitle not in self.episodeList:

					print(episodeFullTitle + ' FOUND!')
					self.torrentList.append(self.masterUrl + torrentLink)
					self.magnetList.append(magnetLink)
					self.episodeList.append(episodeFullTitle)

					# this method will decide what is the episode number cuz it's important
					# because right now there are two ways that people express the episode numbers, I have to use try and except
					# upcoming, I have to work around to read the season and not including it to the episodeList
					try:
						seasonNumber, episodeNumber = self.convertEpisodeFormatFromFullToNumber(episodeFullTitle)

						# just necessary measurements
						int(seasonNumber)
						int(episodeNumber)

						#debug
						#episodeNumber += ' AAAAAASAAA'

					except:
						episodeNumber = episodeFullTitle.replace(f"[{self.subTeam}]", "").replace(self.seriesName, "")[3:8].replace("[", "").replace(" ","")

					#print('THE EPISODE NUMBER IS ' + episodeNumber)

					self.episodeListJustNumber.append(episodeNumber)
					#print(self.episodeListJustNumber)

					# even though a lot of things are processed here. The main() loop down there will just evaluate the episode number to move on so I am going to return this back to it.
					return episodeNumber

				
				else:
					pass




	def downloadTorrent(self, linkList, selectedEpisode):
		if selectedEpisode == 'all':
			for link in linkList:
				webbrowser.open(link)
				
		elif selectedEpisode != 'all':
			webbrowser.open(linkList[-1])

	def saveTorrent(self, linkList, seriesList, linkType, selectedEpisode):
		f = open(f"{self.seriesName} in {self.selectedQuality} magnet and torrent links.txt", 'a') # a means (makes a new file and) append on it 

		if linkType == 'magnet':
			f.write('Magnet links \r\n')
		elif linkType == 'torrent':
			f.write('Torrent links \r\n')

		
		if selectedEpisode != 'all': 
			f.write(selectedEpisode +": "+ linkList[-1] + "\r\n")

		elif selectedEpisode == 'all': # selectedEpisode 0 is download in list.
			for index, link in enumerate(linkList):
				f.write(seriesList[index] +": "+ link + "\r\n")

		#print(linkList)

				#f.write(seriesList[linkList.index(link)] +": "+ link + "\r\n")

	#print(self.convertEpisodeFormatFromFullToNumber('Rezero S01E14'))


def main():
	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [episode] [fan sub] [quality] [-dl magnet|torrent] or [-save]')
	parser.add_argument(help='Put the actual series name here. If there is "-" sign in the name, use quotation mark ("") for the name.', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-ep', help='Episode number. Add 0 for episodes below 10. Ex: 09, 01, 00', action="store", dest='dlEpisode', default='all', nargs='?')
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

			if nyaasi.episodeListJustNumber == []:
				continue

			else:
				if args.dlEpisode == 'all':
					if nyaasi.episodeListJustNumber[-1] == '01':
						#print('yes')
						if phase == 0:
							print("\r\nFINDING EPISODE 00!", end ="", flush=True)
						phase += 1
						print(".", end="", flush=True)

						if phase > 10:
							print("\r\n\r\nTHERE IS NO EPISODE 00!")
							break

					elif nyaasi.episodeListJustNumber[-1] == '00':
						break

				if args.dlEpisode != 'all':
					if nyaasi.episodeListJustNumber[-1] == args.dlEpisode:
						print("\r\n\r\nDONE!")
						break

		except Exception as e:
			print(e)
			break

	selectedEpisode = args.dlEpisode

	if args.dl == 'magnet':
		nyaasi.downloadTorrent(nyaasi.magnetList, selectedEpisode)

	elif args.dl == 'torrent':
		nyaasi.downloadTorrent(nyaasi.torrentList, selectedEpisode)

	if args.save:
		nyaasi.saveTorrent(nyaasi.magnetList, nyaasi.episodeList, 'magnet', selectedEpisode)
		nyaasi.saveTorrent(nyaasi.torrentList, nyaasi.episodeList, 'torrent', selectedEpisode)

def debugAAA():
	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [episode] [fan sub] [quality] [-dl magnet|torrent] or [-save]')
	parser.add_argument(help='Put the actual series name here. If there is "-" sign in the name, use quotation mark ("") for the name.', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-ep', help='Episode number. Add 0 for episodes below 10. Ex: 09, 01, 00', action="store", dest='dlEpisode', default='all', nargs='?')
	parser.add_argument('-fs', help='Name of the fansub team (Judas is default)', action="store", dest='subTeam', default='Judas', nargs='?')
	parser.add_argument('-q', help='1080p | 720p | 480p | 360p (1080p is default)', action="store", dest='selectedQuality', default='1080p', nargs='?')
	parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store")
	parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
	args = parser.parse_args()


	seperator = ' '

	# object
	nyaasi = nyaasi_hoarder(str(args.subTeam), seperator.join(args.seriesName), args.selectedQuality)

	print(nyaasi.convertEpisodeFormatFromFullToNumber('ReZERO S01E14'))


if __name__ == '__main__':
	main()
	#debugAAA()
