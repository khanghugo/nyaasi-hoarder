import re
import requests
from bs4 import BeautifulSoup
import os
import argparse
#from urllib.parse import unquote

def is_number(s):
	try:
		int(s)
	except:
		return False

	return True

def remove_spec_char(s):
	return re.sub('[^A-Za-z0-9.[]-]+', '_', s) # replace all special characters except for `.` with `_`

class sub_team_page: # one trick to speed up the searching is adding the name of the anime to the query # todo
	def __init__(self, sub_team):
		self.sub_team = sub_team

		self.sub_team_dict = {
		"EMBER": "Ember_Encodes",
		"HR": "HR-Minifreeza",
		"YakuboEncodes": "yakubo",
		"Raze": "Raze876",
		"Anime Time": "sff",
		"FFA": "FreeForAll",
		"AkihitoSubs": "AkihitoSenpai"
		}
	def to_page(self, number):
		website = 'https://nyaa.si'

		if self.sub_team in self.sub_team_dict:
			sub_team_alias = self.sub_team_dict[self.sub_team]
		else:
			sub_team_alias = self.sub_team

		return f'{website}/user/{sub_team_alias}?p={number}'


class parser:
	def __init__(self, url):
		self.url = url

	def parsing(self):
		r = requests.get(self.url)

		if r.status_code != 200:
			return False

		#return BeautifulSoup(r, 'html.parser')
		return [str(x) for x in BeautifulSoup(r.text, 'html.parser').find_all('td')]

	def print_code(self):
		r = requests.get(self.url)
		print(r.status_code)

class reading:
	def __init__(self, html, name, ep, quality, team):
		self.html = html # this should be a list
		self.name = name
		self.ep = ep
		self.quality = quality
		self.team = team

		self.title_list = []
		self.ep_number_list = []
		self.torrent_list = []
		self.magnet_list = []
		self.time_uploaded_list = []
	
	def print_page_html(self):
		print(self.html)

	def find_episode_number(self, title):
		# general, not team specific
		try:
			episode_number = re.findall(' - [0-9]{2} .', title)[-1].replace('-', '').replace('[','').strip()
			if int(episode_number): return episode_number
			else: raise Exception
		except:
			return re.findall(" S[0-9]{2}E[0-9]{2} ", title)[0].strip()[4:]
		# can add more specific cases if we create the same dict from sub_team_page class

	def extract_index(self):
		# todo, return 'Cannot connect when the code is not 200' : ok
		if not self.html:
			return False

		title_index = [self.html.index(x) for x in self.html if self.name in x if self.quality in x if 'magnet:?' not in x] # magnet:? is to make sure names with 1 word be filtered
	
		return title_index
		# for x in self.html:
		# 	if (self.name and self.quality in x):
		# 		print(x)
	
	def extract_debug(self):
		for i in self.html:
			if self.name in i and self.quality in i:
				print(i)


	def extract_info(self):
		website = 'https://nyaa.si'
		if not self.extract_index():
			return

		for i in self.extract_index():
			full_title = re.findall('"([^"]*)"', self.html[i])[-1]
			episode_number = self.find_episode_number(full_title)
			# sometimes, there could be a movie instead, this would filter it.
			if not is_number(episode_number): continue

			self.title_list.append(full_title)
			self.ep_number_list.append(episode_number)

			links = re.findall('"([^"]*)"', self.html[i + 1])
			self.torrent_list.append(f'{website}{links[1]}')
			self.magnet_list.append(links[3])

			# torrent_link = links[1]
			# magnet_link = links[3]

			self.time_uploaded_list.append(int(re.findall('"([^"]*)"', self.html[i + 3])[1]))

			#time_uploaded = int(re.findall('"([^"]*)"', self.html[index + 3])[1])
class writing:
	def __init__(self, name, q, name_list, t_list, m_list):
		self.name = name
		self.q = q
		self.name_list = name_list
		self.t_list = t_list
		self.m_list = m_list

	def save_file(self):
		# save links to a file
		with open(f'{self.name} [{self.q}].txt', 'a') as f:
			for n, t, m in zip(self.name_list, self.t_list, self.m_list):
				f.write(n)
				f.write('\n')
				f.write(t)
				f.write('\n')
				f.write(m)
				f.write('\r\n')
		# download torrent file for save
		for t, n in zip(self.t_list, self.name_list):
			r = requests.get(t)
			# cd = r.headers.get('content-disposition')
			# filename = remove_spec_char( unquote( re.findall('filename="([^"]*)', cd)[0] )) # unquote will decode all html characters, i can make my own library for that but later
			filename = f'{remove_spec_char(n)}.torrent'
			open(filename, 'wb+').write(r.content)

	def magnet_file(self):
		for i in self.m_list:
			os.startfile(i)

	def torrent_file(self):
		for t, n in zip(self.t_list, self.name_list):
			# exact same code above
			r = requests.get(t)
			filename = f'{remove_spec_char(n)}.torrent'
			open(filename, 'wb+').write(r.content)
			# extra step
			os.startfile(filename)

class nyaasi_hoarder: # composition
	def __init__(self, name, ep, q, team, save):
		self.name = name
		self.ep = ep 
		self.q = q 
		self.team = team
		self.save = save

		if len(self.ep) == 1:
			self.ep = f'0{self.ep}'

	def print_team_dict(self):
		print(sub_team_page('foobar').sub_team_dict)
	
	def print_info(self):
		print('Anime name is {self.name}')
		print('Selected episode is {self.ep}')
		print('Selected quality is {self.q}')
		print('Sub team is {self.team}')
	
	def print_page_html(self, p): # p accounts for an integer
		obj = self.page_info(p)
		obj.extract_info()
		print(obj.html)
	
	def page_info(self, p):
		return reading(parser(sub_team_page(self.team).to_page(p)).parsing(),self.name,self.ep,self.q,self.team)

	def read_info(self, p):
		obj = self.page_info(p)

		# if not obj:
		# 	print(f'Cannot connect to {sub_team_page(self.team).to_page(p)}')
		# 	return False
		# else:
		# 	obj.extract_info()
		# 	return obj.title_list, obj.ep_number_list, obj.torrent_list, obj.magnet_list, obj.time_uploaded_list

		obj.extract_info()
		return obj.title_list, obj.ep_number_list, obj.torrent_list, obj.magnet_list, obj.time_uploaded_list

	def start(self):
		start_page = 1 # page 0 and page 1 are the same

		episode_00_search_count = 0

		timeout_count = 0
		timeout_max = 10

		title = []
		torrent = []
		magnet = []

		while True:
			obj = self.read_info(start_page)
			start_page += 1

			if not obj[0]:
				timeout_count += 1
				print('.', end='', flush=True)
				if timeout_count == timeout_max:
					if title:
						print('\nCannot find the remaining episodes')
					if not title:
						print('\nCannot find the series')
					break
				continue

			else:
				timeout_count = 0
				# obj.title_list, obj.ep_number_list, obj.torrent_list, obj.magnet_list, obj.time_uploaded_list
				for i in obj[0]:
					print(f'FOUND {i}')

				latest_episode = obj[1][0]
				if not is_number(latest_episode):
					print('latest_episode ERROR')
					break
				
				# self.ep methods
				current_episode = obj[1][-1]
				if self.ep == 'all':
					# list comprehension or just simple assignment will not do the job. since pages are loaded multiple times with
					# differnt outputs every time, it's better to have a list defined and append from that.
					for i in obj[0]:
						title.append(i)
					for i in obj[2]:
						torrent.append(i)
					for i in obj[3]:
						magnet.append(i)

					if current_episode == '01' and episode_00_search_count == 0:
						print('Searching for episode 00!')
						episode_00_search_count += 1

					# these lines wont be called
					# if current_episode == '00':
					# 	print('\nEpisode 00 found!')
					# 	break

					# elif episode_00_search_count < episode_00_search_max:
					# 	print('.', end='\r', flush=True)
					# else:
					# 	print('Episode 00 not found!')
					# 	break
				
				if self.ep == 'latest':
					# saving as a list for consistency
					title = [ obj[0][0] ]
					#number = [ obj[1][0] ]
					torrent = [ obj[2][0] ]
					magnet = [ obj[3][0] ]
					#time_up = [ obj[4][0] ] # not decided yet
					break
				
				if is_number(self.ep):	
					if int(self.ep) > int(latest_episode):
						print(f'Episode {self.ep} is not available yet')
						print(f'Latest episode is {latest_episode}')
						break

					for index, i in enumerate(obj[1]):
						if self.ep == i:
							title = [ obj[0][index] ]
							torrent = [ obj[2][index] ]
							magnet = [ obj[3][index] ]
							break
			

		# return self.name, self.q, title, torrent, magnet
		# proceed to save from here
		#print(title)
		if not title:
			print('Try again!')
			quit()

		print('Proceed to saving')
		w = writing(self.name, self.q, title, torrent, magnet)

		if self.save == 'magnet':
			w.magnet_file()
		if self.save == 'torrent':
			w.torrent_file()
		if self.save == 'save':
			w.save_file()

		# this doesnt work??? it would call all functions there
		# save_dict = {
		# 	'torrent': w.torrent_file(),
		# 	'magnet': w.magnet_file(),
		# 	'save': w.save_file()
		# }
		# save_dict[self.save] or the loop below
		# for i in save_dict:
		# 	if self.save in save_dict: save_dict[i]


	
class debug:
	def main(self):
		name = 'Monster Musume no Oisha-san'
		ep = 'all'
		quality = '720p'
		team = 'HorribleSubs'

		obj = nyaasi_hoarder(name, ep, quality, team, 'save')
		obj.start()
		# obj.print_page_html(1)
		# rewrite.py "Monster Musume no Oisha-san" 

		# page = sub_team_page(team).to_page(2)

		# soupa = parser(page)
		# soup = soupa.parsing()


		# r = reading(soup, name, ep, quality, team)
		# r.extract_debug()



		#print(r.title_list)

		# page = sub_team_page(team).to_page(0)

		# soup = parser(page).parsing()
		# if not soup:
		# 	quit()

		# #print(soup)
		# r = reading(soup, name, ep, quality, team)
		# r.extract_info()

		# print(r.title_list)
		# # print(r.ep_number_list)
		# # print(r.time_uploaded_list)
		# # print(r.torrent_list)

		# file = writing(name, quality, r.title_list, r.torrent_list, r.magnet_list)
		# file.save_file()

def main():
	name = ""
	d_ep = "latest"
	d_quality = "1080p"
	d_team = "Judas"
	d_save = 'save'
	ep_opt = ['latest', 'all', ""]
	q_opt = ['1080p', '720p', '480p', '360p', ""]
	save_opt = ['save', 'torrent', 'magnet', ""]

	parser = argparse.ArgumentParser()
	parser.add_argument(action='store', dest='name', nargs='*')
	parser.add_argument('-ep', action='store', dest='ep', nargs='?', default=d_ep)
	parser.add_argument('-q', action='store', dest='q', nargs='?', default=d_quality)
	parser.add_argument('-fs', action='store', dest='fs', nargs='?', default=d_team)
	parser.add_argument('-save', action='store', dest='save', nargs='?', default=d_save)
	args = parser.parse_args()

	if args.name:
		name = ' '.join(args.name)
		q = args.q
		ep = args.ep 
		team = args.fs 
		save = args.save

	else:
		# name input
		while True:
			name = input("Series Name: ")
			if name:
				break

		#episode input
		while True:
			ep = input("Episode: ")
			if not ep: ep = d_ep
			try:
				int(ep)
				break
			except ValueError:
				if ep in ep_opt:
					break
			
		# quality input
		while True:
			q = input("Quality: ")
			if not q: q = d_quality
			if q in q_opt:
				break

		# sub input
		team = input("Sub team: ")

		# saving input
		while True:
			save = input("Download/save? (torrent,magnet,save): ")
			if not save: save = d_save
			if save in save_opt:
				break
	# print(name)
	# print(q)
	# print(ep)
	# print(team)
	# print(save)

	obj = nyaasi_hoarder(name, ep, q, team, save)
	#obj = nyaasi_hoarder("Monster Musume no Oisha-san", 'latest', '1080p', 'HorribleSubs', 'save')
	obj.start()

if __name__ == '__main__':
	main()





