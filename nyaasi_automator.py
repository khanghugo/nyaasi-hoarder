import nyaasi_hoarder as nh
import argparse
from datetime import datetime, timedelta
import re
import time
import os
import winsound

parser = argparse.ArgumentParser(prog='nyaasi_automator',usage='%(prog)s [-a]')
parser.add_argument("-am", action="store_true", help="This will run nyaasi_hoarder like normal but also add to your configuration file")
args = parser.parse_args()

# predefinied stuff
m = open('na_config.txt', 'a')
m.close()

os.system('cls')

seriesName = ""
selectedEpisode = ""
selectedQuality = ""
subTeam = ""
save = None
dl = 'torrent'

def slice_string(sth):
	return sth.split(": ")[-1].strip() # split at the colon, choose the second item cus the first one is the label, cut the first char which is a space

def fetch_info(l, index):
	yield l[index].strip()
	for i in range(1, 5):
		yield slice_string(l[index + i])

def detect_indices(l):
	for index, line in enumerate(l):
		if 'Latest episode' in line:
			yield index - 1

def seconds_to_format(sec):
	day = sec // (24*3600)
	sec %= (24*3600)

	hour = sec // 3600
	sec %= 3600

	minute = sec // 60
	sec %= 60

	a = [day, hour, minute, sec]
	for index, i in enumerate(a):
		if len(str(i)) == 1: a[index] = f'0{i}'

	return a

# run nyaasi_hoarder like normal when the optional argument is given
def op(seriesName, selectedEpisode, selectedQuality, subTeam, save, dl):
	d_subTeam = 'Judas'
	d_selectedQuality = '1080p'
	d_selectedEpisode = 'all'
	d_save = 1

	selectedEpisode_options = ['latest', 'all', ""]
	selectedQuality_options = ['1080p', '720p', '480p', '360p', ""]
	saving_options = ['save', 'torrent', 'magnet', ""]

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
	if not save and not dl: save = d_save

	#else: (lambda __print: (__print('try again'), (quit(), None)[1])[1])(__import__('__builtin__', level=0).__dict__['print'])


	# before the script start, it would make sure if the selected series is not recorded in the file
	info_list = [seriesName, selectedEpisode, selectedQuality, subTeam] # this order has to match with the config list
	is_series_new = None
	overwrite = None
	overwrite_items = []

	with open("na_config.txt", "r") as datfile:
		datfile_lines = datfile.readlines()

		if f'{seriesName}\n' in datfile_lines: # there is a new line in the list, this should fix it
			print("It seems like you already have the series saved")
			seriesName_index = datfile_lines.index(f'{seriesName}\n')
			for i in range(1, 4):
				overwrite_items.append(info_list[i])

				if slice_string(datfile_lines[seriesName_index + i]) != info_list[i] and i != 1: # to ignore the episode
					print(f"{datfile_lines[seriesName_index + i].strip()} (old)")
					print(f"{info_list[i]} (new)\n")

			# y/n input
			yn_options = ['y','n']
			while True:
				userinput = input('Do you want to overwrite changes? (y/n): ')
				if any(x in userinput for x in yn_options):
					if userinput == 'y': 
						overwrite = 1
						break
					if userinput == 'n':
						overwrite = 0
						break
		else:
			is_series_new = 1
	# object, it is just for this condition I guess? When I get to the automated part, this should change
	nyaasi = nh.nyaasi_hoarder(seriesName, selectedEpisode, selectedQuality, subTeam)

	nyaasi.startFindingEpisode_silent()
	save = 1
	if nyaasi.proceedToSaveData:
		if dl == 'magnet':
			nyaasi.downloadTorrent(nyaasi.magnetList, selectedEpisode)

		elif dl == 'torrent':
			nyaasi.downloadTorrent(nyaasi.torrentList, selectedEpisode)

		if save:
			nyaasi.saveTorrent(nyaasi.magnetList, nyaasi.episodeList, 'magnet', selectedEpisode)
			nyaasi.saveTorrent(nyaasi.torrentList, nyaasi.episodeList, 'torrent', selectedEpisode)

		# write those datas into a file
		# nyaasi.episodeListJustNumber[0] = the latest episode
		# todo: write a last-update line: ok

		# three states so I need to specify, using `not overwrite` will also count None
		if overwrite == 0:
			quit()

		uploaded_time_unix = nyaasi.time_uploaded[0]
		uploaded_time = datetime.fromtimestamp( uploaded_time_unix )
		
		with open("na_config.txt", "w+") as datfile:  # change mode
			if is_series_new:
				datfile_lines.append(f"{seriesName}\n")
				datfile_lines.append(f"Latest episode: {nyaasi.episodeListJustNumber[0]}\n")
				datfile_lines.append(f"Quality: {selectedQuality}\n")
				datfile_lines.append(f"Sub team: {subTeam}\n")
				datfile_lines.append(f"Last uploaded: {uploaded_time} : {uploaded_time_unix}\n")
				datfile_lines.append("\n")

			if overwrite:
				datfile_lines[seriesName_index + 1] = f"Latest episode: {nyaasi.episodeListJustNumber[0]}\n"
				datfile_lines[seriesName_index + 2] = f"Quality: {overwrite_items[1]}\n"
				datfile_lines[seriesName_index + 3] = f"Sub team: {overwrite_items[2]}\n"
				datfile_lines[seriesName_index + 4] = f"Last uploaded: {uploaded_time} : {uploaded_time_unix}\n"

			datfile.writelines(datfile_lines)

	else:
		print("\r\nPLEASE TRY AGAIN")

# everything starts here
if args.am:
	op(seriesName, selectedEpisode, selectedQuality, subTeam, save, dl)
	# with open("na_config.txt", "r") as datfile:
	# 	datfile_lines = datfile.readlines()

	# 	(a,b,c,d,e) = fetch_info(datfile_lines, 0)
	# 	print(a)
		
if not args.am:
	saved_series = []
	wait_time_list = []
	series_found = []
	sequence_fixed = 4
	sequence = 0
	frequency = 440
	time_sleep = 30 # seconds

	datfile = open("na_config.txt", "r")
	datfile_lines = datfile.readlines()
	if len(datfile_lines) == 0:
		print("No series found, Proceed to -am")
		datfile.close()
		op(seriesName, selectedEpisode, selectedQuality, subTeam, save, dl)
		print("Please run again!")
		quit()
	while True:
		wait_time_list.clear()
		saved_series.clear()
		for index in detect_indices(datfile_lines):
			(name, ep, q, sub, t) = fetch_info(datfile_lines, index)
			nyaasi = nh.nyaasi_hoarder(name, 'latest', q, sub)
			nyaasi.startFindingEpisode_silent()
								
			if nyaasi.time_uploaded:
				uploaded_time_unix = nyaasi.time_uploaded[0]
			else: uploaded_time_unix = 0

			uploaded_time = datetime.fromtimestamp( uploaded_time_unix )
			current_time = datetime.now()
			current_time_unix = current_time.timestamp()
			# `t`, `uploaded_time_unix`, `current_time_unix` could be 3 different values if we have a new episode
			latest = nyaasi.episodeListJustNumber[0]
			if int(ep) < int(latest):
				s = 0
				series_found.append(name)

				# print(f'Newer episode of {name} found! Episode {latest}') # moved out of this loop
				if dl == 'magnet':
					nyaasi.downloadTorrent(nyaasi.magnetList, latest)
				elif dl == 'torrent':
					nyaasi.downloadTorrent(nyaasi.torrentList, latest)
				if save:
					nyaasi.saveTorrent(nyaasi.magnetList, nyaasi.episodeList, 'magnet', latest)
					nyaasi.saveTorrent(nyaasi.torrentList, nyaasi.episodeList, 'torrent', latest)
					datfile.close()
				with open("na_config.txt", 'w') as datfile:
					datfile_lines[index + 1] = f"Latest episode: {nyaasi.episodeListJustNumber[0]}\n"
					datfile_lines[index + 2] = f"Quality: {q}\n"
					datfile_lines[index + 3] = f"Sub team: {sub}\n"
					datfile_lines[index + 4] = f"Last uploaded: {uploaded_time} : {uploaded_time_unix}\n"
					datfile.writelines(datfile_lines)
				wait_time_unix = (3600 * 24 * 7)
			else:
				wait_time_unix = (int(t) + (3600 * 24 * 7)) - current_time_unix # last uploaded plus a week time and subtract to the current time
				if wait_time_unix < 0: wait_time_unix = 0

			wait_time_list.append(wait_time_unix)
			saved_series.append(name)

		os.system('cls')
		for name, wait_time in zip(saved_series, wait_time_list):
			if name in series_found:
				winsound.Beep(frequency, 500)
				print(f'New episode {latest} for {name} found!')
			if wait_time == 0:
				print(f'{name} is overdue!')

			# wow = [day, hour, min, sec]
			wow = seconds_to_format(int(wait_time))
			print(f"ETA for {name}: {wow[0]} {wow[1]}:{wow[2]}:{wow[3]} day(s)")

		time.sleep(time_sleep)

		# restart something every certain times
		# here i clear series_found so if the series is found, it would beep 3 times
		if sequence % sequence_fixed == 3:
			series_found.clear()
		sequence += 1

# limitations:
# for both 2 files, the written link file will be named exactly as your input
# if you write "Re:ZERO" instead of the whole thing, the file will be named like that and the checking mechanism here
# will just see your series name like that.
# you should just write the whole thing for convenience purpose. I can use MAL and user's confirmation but hey...
# imjsut starting working on this new feature