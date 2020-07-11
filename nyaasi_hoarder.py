import requests
from bs4 import BeautifulSoup, SoupStrainer
import argparse
import webbrowser
import re

# python nyaasi_hoarder.py Gundam Build Divers Re-RISE -fs HorribleSubs -q 1080p -save
# python nyaasi_hoarder.py Dorohedoro -ep 09 -q 1080p -dl magnet


class nyaasi_hoarder:
	def __init__(self, subTeam, seriesName, selectedQuality, selectedEpisode):
		self.selectedEpisode = selectedEpisode
		self.subTeam = subTeam

		self.seriesName = seriesName
		self.selectedQuality = selectedQuality

		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'

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

		# check/edit input
		if len(self.selectedEpisode) == 1:
			self.selectedEpisode = '0' + self.selectedEpisode

		#DEBUG
		#print(self.episodeListJustNumber)

		# it just makes the page number go up
	def urlRaiser(self, number):
		return self.masterUrl+"/user/"+self.subTeamUrl+"?p="+str(number+1)

	def isNumber(self, char): # I find myself using this a lot so I have to make a function for its own
		try:
			int(char)
			return True
		except:
			return False


		# getting the html. I just look up online for this method.
	def parsingNyaasi(self, url):
		session = requests.Session()
		response = requests.get(url)
		strainer = SoupStrainer(self.tag)
		soup = BeautifulSoup(response.text, "lxml", parse_only=strainer)
		return soup

		# some titles have adopted new formats like "S01E02" and is totally different from what they used to be. So this converts it to understandable info
	def convertEpisodeFormatFromFullToNumber(self, episodeFullTitle):

		episodeFullTitleCharList = []
		seasonKey = 'S'
		episodeKey = 'E'

		for index, char in enumerate(episodeFullTitle):
			episodeFullTitleCharList.append(char)

			try:
				# this reads from right to left. for example, "Re:Zero SE01E14" will find if there is any number there. Then it will start from right to left. 
				# If the next one is the number then good. If the next one is "E" then good. And so on.
				# Right now it is limited to 99 episodes and 99 seasons. I will try to find a way to make it through.

				if (index >= 5) and (self.isNumber(episodeFullTitleCharList[index]) == True) and (self.isNumber(episodeFullTitleCharList[index - 1]) == True) and (episodeFullTitleCharList[index - 2] == episodeKey) and (self.isNumber(episodeFullTitleCharList[index - 3]) == True) and (self.isNumber(episodeFullTitleCharList[index - 4]) == True) and (episodeFullTitleCharList[index - 5] == seasonKey):
					return (str(episodeFullTitleCharList[index - 4 ]) + str(episodeFullTitleCharList[index - 3])), (str(episodeFullTitleCharList[index - 1 ]) + str(episodeFullTitleCharList[index]))

			except Exception as e:
				print(e)
				break

			# this does most of the work to intepret the data including torrent, magnet, episode number, title, quality
	def findEpisodeData(self, htmlCode):
		self.episodeList = []
		self.episodeListJustNumber = []
		self.magnetList = []
		self.torrentList = []
		self.rawFilteredData = []

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

					# this method will decide what is the episode number cuz it's important
					# because right now there are two ways that people express the episode numbers, I have to use try and except
					# upcoming, I have to work around to read the season and not including it to the episodeList
					try:
						seasonNumber, episodeNumber = self.convertEpisodeFormatFromFullToNumber(episodeFullTitle)

						# just necessary measurements
						int(seasonNumber)
						int(episodeNumber)

					except:
						episodeNumber = episodeFullTitle.replace(f"[{self.subTeam}]", "").replace(self.seriesName, "")[3:8].replace("[", "").replace(" ","")

					if self.isNumber(episodeNumber) == True:

						self.episodeListJustNumber.append(episodeNumber)
						self.torrentList.append(self.masterUrl + torrentLink)
						self.magnetList.append(magnetLink)
						self.episodeList.append(episodeFullTitle)

						return episodeNumber

	def startFindingEpisode(self):
		pageCount = 0
		pageCountOnEp00 = 0
		startDedicatedTimeOut = True
		pageTimeOutMax = 10
		self.proceedToSaveData = True

		print("SCRIPT STARTED!\r\n")
		while True:
			try: 
				# main operation in this composition
				episodeNumber = self.findEpisodeData( self.parsingNyaasi( self.urlRaiser(pageCount) ) )
				#print(episodeNumber)

				if episodeNumber:
					print("", end="\r")
					print( self.episodeList[self.episodeListJustNumber.index(episodeNumber)] + ' FOUND!' )

				elif episodeNumber == None and pageCount > pageTimeOutMax and startDedicatedTimeOut == True:
					if pageCount - pageTimeOutMax == 1:
						print("LOOKING IN OLDER PAGES", end="", flush=True)

					print(".", end="", flush=True)

					if pageCount > (pageTimeOutMax + 10):
						print("", end="\r")
						print("\r\n")
						print("SEARCH TIMED OUT")

						if self.episodeList:
							print(f"CERTAIN EPISODE CANNOT BE FOUND (Episode {'0' + str(( int(self.episodeListJustNumber[-1]) - 1 )) })")
							self.proceedToSaveData = True

						else:
							print('THIS SERIES CANNOT BE FOUND')
							self.proceedToSaveData = False

						break

				
				pageCount += 1

				if self.episodeListJustNumber == []:
					continue
	
				else:
					#print(episodeNumber)

					latestEpisode = self.episodeListJustNumber[0]
					#print(episodeNumber)
					if self.selectedEpisode == 'all':

						if episodeNumber == '01' and pageCountOnEp00 == 0:
							print("\r\nFINDING EPISODE 00!", end ="", flush=True)
							startDedicatedTimeOut = False

						elif episodeNumber == '00':
							break

						elif self.episodeListJustNumber[-1] =='01' and episodeNumber == None:
							pageCountOnEp00 += 1
							print(".", end="", flush=True)

							if pageCountOnEp00 > 10:
								print("\r\n\r\nTHERE IS NO EPISODE 00!")
								break

					if self.selectedEpisode != 'all':
	
							if ( self.isNumber( latestEpisode ) == True ) and ( int( latestEpisode ) < int( self.selectedEpisode ) ):
								print("\r\nTHE EPISODE IS NOT AVAILABLE")
								print(f"THE LATEST EPISODE IS {latestEpisode}")
	
								self.proceedToSaveData = False
								break
	
							if episodeNumber == self.selectedEpisode:
								print("\r\n\r\nDONE!")
								break

			except (Exception) as e:
				print(str(e) + " LOOP ERROR")
				break

	def downloadTorrent(self, linkList, selectedEpisode):
		if linkList:

			if selectedEpisode == 'all':
				for link in linkList:
					webbrowser.open(link)
				
			elif selectedEpisode != 'all':
				webbrowser.open(linkList[-1])

	def saveTorrent(self, linkList, seriesList, linkType, selectedEpisode):
		f = open(f"{self.seriesName} in {self.selectedQuality} magnet and torrent links.txt", 'a') # a means (makes a new file and) append on it 

		if linkList:

			if linkType == 'magnet':
				f.write('Magnet links \r\n')
			elif linkType == 'torrent':
				f.write('Torrent links \r\n')

		
			if selectedEpisode != 'all': 
				f.write(seriesList[-1] +": "+ linkList[-1] + "\r\n") # some how I forgot how this works. The list will stop appending as soon as selected episode is in it. So the last value is good.

			elif selectedEpisode == 'all': # selectedEpisode 0 is download in list.
				for index, link in enumerate(linkList):
					f.write(seriesList[index] +": "+ link + "\r\n")

def main():
	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [episode] [fan sub] [quality] [-dl magnet|torrent] or [-save]')
	parser.add_argument(help='Put the actual series name here. If there is "-" sign in the name, use quotation mark ("") for the name.', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-ep', help='Number of the episode you want', action="store", dest='selectedEpisode', default='all', nargs='?')
	parser.add_argument('-fs', help='Name of the fansub team (Judas is default)', action="store", dest='subTeam', default='Judas', nargs='?')
	parser.add_argument('-q', help='1080p | 720p | 480p | 360p (1080p is default)', action="store", dest='selectedQuality', default='1080p', nargs='?')
	parser.add_argument('-dl', default='', help='Torrent all files through magnet link', action="store")
	parser.add_argument('-save', default='', help='Save links in a txt file', action="store_true")
	args = parser.parse_args()


	seperator = ' '

	# object
	nyaasi = nyaasi_hoarder(str(args.subTeam), seperator.join(args.seriesName), args.selectedQuality, args.selectedEpisode)

	# function that do the works
	nyaasi.startFindingEpisode()

	if nyaasi.proceedToSaveData:
		if args.dl == 'magnet':
			nyaasi.downloadTorrent(nyaasi.magnetList, args.selectedEpisode)

		elif args.dl == 'torrent':
			nyaasi.downloadTorrent(nyaasi.torrentList, args.selectedEpisode)

		if args.save:
			nyaasi.saveTorrent(nyaasi.magnetList, nyaasi.episodeList, 'magnet', args.selectedEpisode)
			nyaasi.saveTorrent(nyaasi.torrentList, nyaasi.episodeList, 'torrent', args.selectedEpisode)
	else:
		print("\r\nPLEASE TRY AGAIN")


if __name__ == '__main__':
	main()
