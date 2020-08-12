import re
import requests
from bs4 import BeautifulSoup
import os
import argparse
from query_encoder import query_encoder
import time


# from urllib.parse import unquote

def is_number(s):
    try:
        int(s)
    except ValueError:
        return False

    return True


def remove_spec_char(s):
    return re.sub('[^A-Za-z0-9.[]-]+', '_', s)  # replace all special characters except for `.` with `_`


class SubTeam:
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


class Parser:
    def __init__(self, url, name):
        self.url = url
        self.name = query_encoder(name).name_to_query()  # this will make a query `q=name`

    def print_url(self):
        print(f'{self.url}&q={self.name}')

    def print_code(self):
        r = requests.get(self.url)
        print(r.status_code)

    def parsing(self):
        # url irself will look like `https://nyaa.si/user/horriblesubs?p=3`
        r = requests.get(f'{self.url}&q={self.name}')

        if r.status_code != 200:
            return False

        # return BeautifulSoup(r, 'html.parser')
        return [str(x) for x in BeautifulSoup(r.text, 'html.parser').find_all('td')]


class Reader:
    def __init__(self, html, name, ep, quality, team):
        self.html = html  # this should be a list
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
            episode_number_p1 = re.findall(" - [0-9]{2} .| - [0-9]{3} .", title)
            if episode_number_p1:
                pass
            else:
                raise ValueError
            return episode_number_p1[-1].replace('-', '').replace('[', '').strip()

        except ValueError:
            episode_number_p1 = re.findall(" S[0-9]{2}E[0-9]{2} ", title)
            if episode_number_p1:
                pass
            else:
                return False
            return episode_number_p1[0].strip()[4:]

    # can add more specific cases if we create the same dict from sub_team_page class

    def extract_index(self):
        if not self.html:
            return False

        title_index = [self.html.index(x) for x in self.html if self.name in x if self.quality in x if
                       'magnet:?' not in x]  # magnet:? is to make sure names with 1 word be filtered
        return title_index

    def extract_info(self):
        website = 'https://nyaa.si'
        if not self.extract_index():
            return

        for i in self.extract_index():
            full_title = re.findall('"([^"]*)"', self.html[i])[-1]
            episode_number = self.find_episode_number(full_title)
            # sometimes, there could be a movie instead, this would filter it.
            if not is_number(episode_number):
                continue

            self.title_list.append(full_title)
            self.ep_number_list.append(episode_number)

            links = re.findall('"([^"]*)"', self.html[i + 1])
            self.torrent_list.append(f'{website}{links[1]}')
            self.magnet_list.append(links[3])

            self.time_uploaded_list.append(int(re.findall('"([^"]*)"', self.html[i + 3])[1]))


class Writer:
    def __init__(self, name, q, name_list, t_list, m_list):
        self.name = name
        self.q = q
        self.name_list = name_list
        self.t_list = t_list
        self.m_list = m_list
        self.number_of_file = len(self.name_list)

    def print_filename(self):
        filename = f'{remove_spec_char(self.name[0])}.torrent'
        print(filename)

    def save_file(self):
        count = 1

        # save links to a file
        print("Writing txt file!")
        with open(f'{self.name} [{self.q}].txt', 'a') as f:
            for n, t, m in zip(self.name_list, self.t_list, self.m_list):
                f.write(n)
                f.write('\n')
                f.write(t)
                f.write('\n')
                f.write(m)
                f.write('\r\n')

        # download torrent file for save
        print('Downloading torrent file!')
        for t, n in zip(self.t_list, self.name_list):
            print(f'{count} out of {self.number_of_file}', end='\r', flush=True)
            count += 1

            r = requests.get(t)
            filename = f'{remove_spec_char(n)}.torrent'
            open(filename, 'wb+').write(r.content)

    def magnet_file(self):
        for i in self.m_list:
            os.startfile(i)

    def torrent_file(self):
        count = 1
        l_torrent = []
        print('Opening torrent file!')

        for t, n in zip(self.t_list, self.name_list):
            print(f'{count} out of {self.number_of_file}', end='\r', flush=True)
            count += 1

            # exact same code above
            r = requests.get(t)
            filename = f'{remove_spec_char(n)}.torrent'
            l_torrent.append(filename)
            open(filename, 'wb+').write(r.content)
            # extra step
            os.startfile(filename)

        print('Cleaning up torrent files!')
        time.sleep(
            1)  # for the time being, this processes too fast that the last file (episode 0 or 1) ends up being
        # deleted before
        # being processed by torrenting softwares
        self.torrent_cleanup(l_torrent)

    def torrent_cleanup(self, l_torrent):
        for i in l_torrent:
            os.remove(i)


class NyaasiHoarder:  # composition
    def __init__(self, name, ep, q, team, save):
        self.name = name
        self.ep = ep
        self.q = q
        self.team = team
        self.save = save

        self.file_title = []
        self.torrent = []
        self.magnet = []
        self.time = []

        self.latest_episode = 0

        if len(self.ep) == 1:
            self.ep = f'0{self.ep}'

    def print_team_dict(self):
        print(SubTeam('foobar').sub_team_dict)

    def print_info(self):
        print('Anime name is {self.name}')
        print('Selected episode is {self.ep}')
        print('Selected quality is {self.q}')
        print('Sub team is {self.team}')

    def print_page_html(self, p):  # p accounts for an integer
        obj = self.page_info(p)
        obj.extract_info()
        print(obj.html)

    def page_info(self, p):
        return Reader(Parser(SubTeam(self.team).to_page(p), self.name).parsing(), self.name, self.ep, self.q,
                      self.team)

    def read_info(self, p):
        obj = self.page_info(p)

        obj.extract_info()
        return obj.title_list, obj.ep_number_list, obj.torrent_list, obj.magnet_list, obj.time_uploaded_list

    def start(self):
        print('', end='\n')
        start_page = 1  # page 0 and page 1 are the same

        episode_00_search_count = 0

        timeout_count = 0
        timeout_max = 10

        while True:
            obj = self.read_info(start_page)
            start_page += 1

            if not obj[1]:
                timeout_count += 1
                if int(self.latest_episode) < 50:  # nyaasi shows 75 entries for a page, i just use 50 just to be sure
                    break

                print('.', end='', flush=True)
                if timeout_count == timeout_max:
                    if episode_00_search_count:
                        print('\nCannot find episode 00')
                    if self.file_title:
                        print('\nCannot find the remaining episodes')
                    if not self.file_title:
                        print('\nCannot find the series')
                    break
                continue

            else:
                timeout_count = 0
                # obj.title_list, obj.ep_number_list, obj.torrent_list, obj.magnet_list, obj.time_uploaded_list
                for i in obj[0]:
                    print(f'FOUND {i}')

                if not self.latest_episode:
                    # this will save the latest episode and it'll work even pages change
                    self.latest_episode = obj[1][0]

                # self.ep methods
                current_episode = obj[1][-1]
                if self.ep == 'all':
                    # list comprehension or just simple assignment will not do the job. since pages are loaded
                    # multiple times with differnt outputs every time, it's better to have a list defined and append
                    # from that.
                    for i in obj[0]:
                        self.file_title.append(i)
                    for i in obj[2]:
                        self.torrent.append(i)
                    for i in obj[3]:
                        self.magnet.append(i)
                    for i in obj[4]:
                        self.time.append(i)

                    if current_episode == '01' and episode_00_search_count == 0:
                        print('Searching for episode 00!')
                        episode_00_search_count += 1

                if self.ep == 'latest':
                    self.file_title.append(obj[0][0])
                    self.torrent.append(obj[2][0])
                    self.magnet.append(obj[3][0])
                    self.time.append(obj[4][0])
                    break

                if is_number(self.ep):  # when the selected episode is a numerical episode
                    if int(self.ep) > int(self.latest_episode):
                        print(f'Episode {self.ep} is not available yet')
                        print(f'Latest episode is {self.latest_episode}')
                        break

                    for i in obj[1]:
                        if self.ep == i:
                            self.file_title.append(obj[0][0])
                            self.torrent.append(obj[2][0])
                            self.magnet.append(obj[3][0])
                            self.time.append(obj[4][0])
                            break

    def start_silent(self):
        start_page = 1
        episode_00_search_count = 0
        timeout_count = 0
        timeout_max = 10
        while True:
            obj = self.read_info(start_page)
            start_page += 1
            if not obj[1]:
                timeout_count += 1
                if int(self.latest_episode) < 50:
                    break
                if timeout_count == timeout_max:
                    break
                continue
            else:
                timeout_count = 0
                if not self.latest_episode:
                    self.latest_episode = obj[1][0]
                current_episode = obj[1][-1]
                if self.ep == 'all':
                    for i in obj[0]:
                        self.file_title.append(i)
                    for i in obj[2]:
                        self.torrent.append(i)
                    for i in obj[3]:
                        self.magnet.append(i)
                    for i in obj[4]:
                        self.time.append(i)
                    if current_episode == '01' and episode_00_search_count == 0:
                        episode_00_search_count += 1
                if self.ep == 'latest':
                    self.file_title.append(obj[0][0])
                    self.torrent.append(obj[2][0])
                    self.magnet.append(obj[3][0])
                    self.time.append(obj[4][0])
                    break
                if is_number(self.ep):  # when the selected episode is a numerical episode
                    if int(self.ep) > int(self.latest_episode):
                        break
                    for i in obj[1]:
                        if self.ep == i:
                            self.file_title.append(obj[0][0])
                            self.torrent.append(obj[2][0])
                            self.magnet.append(obj[3][0])
                            self.time.append(obj[4][0])
                            break

    def save_to_file(self):
        if not self.file_title:
            print("Cannot save! Try again")
            quit()

        w = Writer(self.name, self.q, self.file_title, self.torrent, self.magnet)

        if self.save == 'magnet':
            w.magnet_file()
        if self.save == 'torrent':
            w.torrent_file()
        if self.save == 'save':
            w.save_file()


def main():
    d_ep = "latest"
    d_quality = "1080p"
    d_team = "Judas"
    d_save = 'save'
    ep_opt = ['latest', 'all', ""]
    q_opt = ['1080p', '720p', '480p', '360p', ""]
    save_opt = ['save', 'torrent', 'magnet', ""]

    parser = argparse.ArgumentParser()
    parser.add_argument(action='store', dest='name', nargs='*')
    parser.add_argument('-ep', action='store', dest='ep', nargs='?', default=d_ep,
                        help='Number of the episode or `all` or `latest`')
    parser.add_argument('-q', action='store', dest='q', nargs='?', default=d_quality)
    parser.add_argument('-fs', action='store', dest='fs', nargs='?', default=d_team)
    parser.add_argument('-save', action='store', dest='save', nargs='?', default=d_save,
                        help='torrent or magnet or save')
    args = parser.parse_args()

    if args.name:
        name = ' '.join(args.name)

        if args.q in q_opt:
            q = args.q
        else:
            q = d_quality

        if args.ep in ep_opt or is_number(args.ep):
            ep = args.ep
        else:
            ep = d_ep

        team = args.fs

        if args.save in save_opt:
            save = args.save
        else:
            save = d_save

    else:
        # name input
        while True:
            name = input("Series Name: ")
            if name:
                break

        # episode input
        while True:
            ep = input("Episode: ")
            if not ep:
                ep = d_ep
            try:
                int(ep)
                break
            except ValueError:
                if ep in ep_opt:
                    break

        # quality input
        while True:
            q = input("Quality: ")
            if not q:
                q = d_quality
            if q in q_opt:
                break

        # sub input
        team = input("Sub team: ")
        if not team:
            team = d_team

        # saving input
        while True:
            save = input("Download/save? (torrent,magnet,save): ")
            if not save:
                save = d_save
            if save in save_opt:
                break

    # len(ep) is resolved in nyaasi_hoarder, no need to be fixed here (when `1` is fed instead of `01`).
    obj = NyaasiHoarder(name, ep, q, team, save)
    obj.start()
    print('Proceeding to save!')
    obj.save_to_file()


def debug():
    obj = Parser(SubTeam('HorribleSubs').to_page(1), 'Black Clover')
    soup = obj.parsing()
    obj2 = Reader(soup, 'Black Clover', 'all', '1080p', 'save')
    # ind = obj2.extract_index()
    # print(len(ind))
    obj2.extract_info()


if __name__ == '__main__':
    main()
# debug()
