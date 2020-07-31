import requests
from bs4 import BeautifulSoup
import argparse
import webbrowser
import re

# python nyaasi_hoarder.py Gundam Build Divers Re-RISE -fs HorribleSubs -q 1080p -save
# python nyaasi_hoarder.py Dorohedoro -ep 09 -q 1080p -dl magnet

class nyaasi_hoarder:
	def __init__(self, seriesName, selectedEpisode, selectedQuality, subTeam):
		self.selectedEpisode = selectedEpisode
		self.subTeam = subTeam

		self.seriesName = seriesName
		self.selectedQuality = selectedQuality

		self.episodeList = []
		self.episodeListJustNumber = []
		self.magnetList = []
		self.torrentList = []
		self.rawFilteredData = []
		self.timeUploaded = []

		self.masterUrl = 'https://nyaa.si'
		self.tag = 'a'

		# add more if U like it.
		self.subTeamDict = {
		"EMBER": "Ember_Encodes",
		"HR": "HR-Minifreeza",
		"YakuboEncodes": "yakubo",
		"Raze": "Raze876",
		"Anime Time": "sff",
		"FFA": "FreeForAll",
		}

		if self.subTeam in self.subTeamDict:
			self.subTeamUrl = self.subTeamDict[ self.subTeam ]

		else:
			self.subTeamUrl = self.subTeam

		# check/edit input
		if self.selectedEpisode == 'latest':
			pass

		elif len(self.selectedEpisode) == 1:
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

	def remove_spec_chars(self, s):
		unaccepted_keys = ['?', '/', '\\', '<', '>', '|', '*', ':', '"', "_"]
		# windows naming is weird
		for i in unaccepted_keys:
			s = s.replace(i, ' ')

		return s

	def parsingNyaasi(self, url):
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "lxml")
		return soup

		# some titles have adopted new formats like "S01E02" and is totally different from what they used to be. So this converts it to understandable info
	def convertEpisodeFormatFromFullToNumber(self, episodeFullTitle):
		s1 = re.findall(" S[0-9]{2}E[0-9]{2} ", episodeFullTitle)
		#print(episodeFullTitle)
		try:
			seasonNumber = s1[0].strip()[1:-3]
			episodeNumber = s1[0].strip()[4:]
			return seasonNumber, episodeNumber
		except:
			raise Exception

	# this does most of the work to intepret the data including torrent, magnet, episode number, title, quality
	def findEpisodeData(self, htmlCode):
			# from chunk of text to list
		for htmlLinesWithSelectedClass in htmlCode.find_all('td'):
			self.rawFilteredData.append(str(htmlLinesWithSelectedClass))

		for entriesIn_rawFilteredData_Index, entriesIn_rawFilteredData in enumerate(self.rawFilteredData):
			# casually filtering text
			if self.selectedQuality in entriesIn_rawFilteredData and ( self.seriesName in entriesIn_rawFilteredData or self.remove_spec_chars(self.seriesName) in entriesIn_rawFilteredData ) and self.subTeam in entriesIn_rawFilteredData:
				# at this point, I forgot how these things work. I think they are in the quotation mark ("") so this just takes all the text in it.
				# if the website changes, this would be the first thing that breaks
				#print(self.rawFilteredData[entriesIn_rawFilteredData_Index])
				episodeFullTitle = re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index]))[-1]

				links = re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index + 1]))
				torrentLink = links[1]
				magnetLink = links[3]

				timeUploaded = int(re.findall('"([^"]*)"', str(self.rawFilteredData[entriesIn_rawFilteredData_Index + 3]))[1])

				#throughout the html, there are many times when the title repeats, it just makes sure that doesn't happen.
				if episodeFullTitle not in self.episodeList:
					# this method will decide what is the episode number cuz it's important
					# because right now there are two ways that people express the episode numbers, I have to use try and except
					# upcoming, I have to work around to read the season and not including it to the episodeList
					# now i realize each team has different naming scheme, right now, this code supprot one certain group, code is not scalable yet
					if self.subTeam != 'Raze':
						try:
							seasonNumber, episodeNumber = self.convertEpisodeFormatFromFullToNumber(episodeFullTitle)
							# just necessary measurements
							int(seasonNumber)
							int(episodeNumber)
	
						except:
							episodeNumber = episodeFullTitle.replace(f"[{self.subTeam}]", "").replace(self.seriesName, "")[3:8].replace("	[", "").replace(" ","")

					if self.subTeam == 'Raze':
						s = episodeFullTitle[:-10].replace(f" x264 {self.selectedQuality}","")
						episodeNumber = s[len(s)-5:].replace('-', '').strip()

					if self.isNumber(episodeNumber) == True:

						self.episodeListJustNumber.append(episodeNumber)
						self.torrentList.append(self.masterUrl + torrentLink)
						self.magnetList.append(magnetLink)
						self.episodeList.append(episodeFullTitle)
						self.timeUploaded.append(timeUploaded)

						return episodeNumber
						
	def startFindingEpisode(self):
		pageCount = 0
		pageCountOnEp00 = 0
		startDedicatedTimeOut = True
		pageTimeOutMax = 5
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
					latestEpisode = self.episodeListJustNumber[0]

					if self.selectedEpisode == 'all':

						if episodeNumber == '01' and pageCountOnEp00 == 0:
							print("\r\nFINDING EPISODE 00!", end ="", flush=True)
							startDedicatedTimeOut = False
							pageCountOnEp00 += 1

						elif episodeNumber == '00':
							break

						elif pageCountOnEp00 > 0:
							print(".", end="", flush=True)

							if pageCountOnEp00 > pageTimeOutMax:
								print("\r\n\r\nTHERE IS NO EPISODE 00!")
								break

							pageCountOnEp00 += 1

					if self.selectedEpisode != 'all':
	
							if self.selectedEpisode != 'latest' and ( self.isNumber( latestEpisode ) == True ) and ( int( latestEpisode ) < int( self.selectedEpisode ) ):
								print("\r\nTHE EPISODE IS NOT AVAILABLE")
								print(f"THE LATEST EPISODE IS {latestEpisode}")
								self.proceedToSaveData = False
								break
	
							if episodeNumber == self.selectedEpisode:
								break

							if self.selectedEpisode == "latest" and episodeNumber == latestEpisode:
								break

			except (Exception) as e:
				print(str(e) + " LOOP ERROR")
				break

		print('\r\nSCRIPT DONE!')

	def downloadTorrent(self, linkList, selectedEpisode):
		if linkList:

			if selectedEpisode == 'all':
				for link in linkList:
					webbrowser.open(link)
				
			elif selectedEpisode != 'all':
				webbrowser.open(linkList[-1])

	def saveTorrent(self, linkList, seriesList, linkType, selectedEpisode):
		seriesName = self.remove_spec_chars(self.seriesName)

		with open(f"{seriesName} in {self.selectedQuality} magnet and torrent links.txt", 'a') as f: # a means (makes a new file and) append on it 
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
	# default settings
	d_subTeam = 'Judas'
	d_selectedQuality = '1080p'
	d_selectedEpisode = 'all'
	selectedEpisode_options = ['latest', 'all', ""]
	selectedQuality_options = ['1080p', '720p', '480p', '360p', ""]
	saving_options = ['save', 'torrent', 'magnet', ""]

	parser = argparse.ArgumentParser(prog='nyaasi-hoarder',usage='%(prog)s [name] [episode] [quality] [fan sub] [-dl magnet|torrent] or [-save]')
	parser.add_argument(help='Put the actual series name here. If there is "-" sign in the name, use quotation mark ("") for the name.', action="store", dest='seriesName', nargs='*')
	parser.add_argument('-ep', help='Number of the episode you want. You can use `latest` to download the latest episode. Default is `all`', action="store", dest='selectedEpisode', default=d_selectedEpisode, nargs='?')
	parser.add_argument('-q', help='1080p | 720p | 480p | 360p . Default is `1080p`', action="store", dest='selectedQuality', default=d_selectedQuality, nargs='?')
	parser.add_argument('-fs', help='Name of the fansub team. Default is `Judas`', action="store", dest='subTeam', default=d_subTeam, nargs='?')
	parser.add_argument('-dl', default='', help='torrent | magnet', action="store")
	parser.add_argument('-save', default='', help='Save links into a txt file', action="store_true")
	args = parser.parse_args()

	# seriesName is input to a list instead of a string so it needs to be joined
	seperator = ' '
	if args.seriesName: args.seriesName = seperator.join(args.seriesName)

	# switch name so it's easier to read
	subTeam = args.subTeam
	selectedQuality = args.selectedQuality
	seriesName = args.seriesName
	selectedEpisode = args.selectedEpisode
	dl = args.dl
	save = args.save 

	if not seriesName:
		# name input
		seriesName = input("Series Name: ")

		#episode input
		while True:
			selectedEpisode = input("Episode: ")
			try:
				int(selectedEpisode)
				break
			except ValueError:
				if selectedEpisode in selectedEpisode_options:
					break
		
		# quality input
		while True:
			selectedQuality = input("Quality: ")
			try:
				if selectedQuality in selectedQuality_options:
					break
			except:
				break

		# sub input
		subTeam = input("Sub team: ")
		
		# saving input
		while True:
			saving = input("Download/save? (torrent,magnet,save): ")
			try: 
				if saving in saving_options:
					if 'save' in saving: save = 1
					elif 'torrent' in saving or 'magnet' in saving: dl = saving
					break
			except:
				break

	if not selectedEpisode:	selectedEpisode = d_selectedEpisode
	if not selectedQuality:	selectedQuality = d_selectedQuality
	if not subTeam:	subTeam = d_subTeam
	if not save and not dl: save = 1

	nyaasi = nyaasi_hoarder(seriesName, selectedEpisode, selectedQuality, subTeam)

	# function that do the works
	nyaasi.startFindingEpisode()

	if nyaasi.proceedToSaveData:
		if dl == 'magnet':
			nyaasi.downloadTorrent(nyaasi.magnetList, args.selectedEpisode)

		elif dl == 'torrent':
			nyaasi.downloadTorrent(nyaasi.torrentList, args.selectedEpisode)

		if save:
			nyaasi.saveTorrent(nyaasi.magnetList, nyaasi.episodeList, 'magnet', selectedEpisode)
			nyaasi.saveTorrent(nyaasi.torrentList, nyaasi.episodeList, 'torrent', selectedEpisode)
	else:
		print("\r\nPLEASE TRY AGAIN")
	
def debug():
	seriesName = 'Re:Zero'
	subTeam = 'Raze'
	selectedQuality = '1080p'
	selectedEpisode = 'all'

	nyaasi = nyaasi_hoarder(seriesName, selectedEpisode, selectedQuality, subTeam)
	nyaasi.findEpisodeData(nyaasi.parsingNyaasi('https://nyaa.si/user/Raze876'))

if __name__ == '__main__':
	main()
	#debug()
