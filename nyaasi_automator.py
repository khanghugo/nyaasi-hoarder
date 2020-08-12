import os
from datetime import datetime
import time
import nyaasi_hoarder as nh
from winsound import Beep
import argparse


def slice_by_colon(s):
    return s.split(': ')[-1].strip()


class TimeStuff:
    def __init__(self, input_second):
        self.input_second = input_second

    def to_day(self):
        sec = int(self.input_second)

        day = sec // (24 * 3600)
        sec %= (24 * 3600)

        hour = sec // 3600
        sec %= 3600

        minute = sec // 60
        sec %= 60

        time_format = [day, hour, minute, sec]

        # from 0 3:9:59 to 00 03:09:59 so it looks prettier
        for index, i in enumerate(time_format):
            if len(str(i)) == 1:
                time_format[index] = f'0{i}'

        return time_format

    def to_format(self):
        return datetime.fromtimestamp(self.input_second)

    def add_x_weeks(self, x):
        return self.input_second + (60 * 60 * 24 * 7 * x)

    def time_difference(self):
        return int(datetime.now().timestamp() - self.input_second)

    def time_difference_by_week(self, x):
        return self.add_x_weeks(x) - datetime.now().timestamp()


class FileDoer:
    def __init__(self, info_list):
        self.file = 'nh_auto.cfg'
        self.info_list = info_list

    def line_format(self):
        line_1 = "Name: "
        line_2 = "Latest Episode: "
        line_3 = "Selected Quality: "
        line_4 = "Sub Team: "
        line_5 = "Uploaded: "

        return [line_1, line_2, line_3, line_4, line_5]

    def check_file(self):
        try:
            with open(self.file, 'r'):
                pass
        except FileNotFoundError:
            return False

        return True

    def write_new_file(self):
        with open(self.file, 'a') as file:
            file.close()

    def to_lines(self):
        with open(self.file, 'r') as file:
            return file.readlines()

    def write_new_line(self):
        with open(self.file, 'w+') as file:
            for format_text, item, index in zip(self.line_format(), self.info_list, range(0, 5)):
                if index == 4:
                    uploaded_time_format = TimeStuff(item).to_format()
                    file.write(f'{format_text}{uploaded_time_format} : {item}\n')
                    continue

                file.write(f'{format_text}{item}\n')

            file.write('\n')

    def append_new_line(self):
        lines_from_file = self.to_lines()
        with open(self.file, 'w') as file:

            for format_text, item, index in zip(self.line_format(), self.info_list, range(0, 5)):
                if index == 4:
                    uploaded_time_format = TimeStuff(item).to_format()
                    lines_from_file.append(f'{format_text}{uploaded_time_format} : {item}\n')
                    continue

                lines_from_file.append(f'{format_text}{item}\n')

            lines_from_file.append('\n')
            file.writelines(lines_from_file)

    def update_line(self, index):
        lines_from_file = self.to_lines()
        with open(self.file, 'w') as file:

            for format_text, enum, item in zip(self.line_format(), range(0, 5), self.info_list):
                if enum == 4:  # weird var name but okay
                    uploaded_time_format = TimeStuff(item).to_format()
                    lines_from_file[index + enum] = f'{format_text}{uploaded_time_format} : {item}\n'
                    continue

                lines_from_file[index + enum] = f'{format_text}{item}\n'

            file.writelines(lines_from_file)

    def read_indices(self):
        return [index for index, line in enumerate(self.to_lines()) if self.line_format()[0] in line]

    def fetch_info_from_index(self, index):
        yield self.to_lines()[index].replace(self.line_format()[0], '').strip()

        for i in range(1, 5):
            yield slice_by_colon(self.to_lines()[index + i])

    def is_changed(self, index):
        for old, new, index in zip(self.fetch_info_from_index(index), self.info_list, range(0, 5)):
            if old != new and index == 0:
                return False
            if old != new and index != 0:
                return True

    def print_changes(self, index):  # difference between new self.info_list and what is in the file
        for old, new, line_format in zip(self.fetch_info_from_index(index), self.info_list, self.line_format()):
            if old != new:
                print(f'{line_format}{old} (old)')
                print(f'{line_format}{new} (new)')


def add_mode():
    d_ep = "latest"
    d_quality = "1080p"
    d_team = "Judas"
    d_save = 'save'
    ep_opt = ['latest', 'all', ""]
    q_opt = ['1080p', '720p', '480p', '360p', ""]
    save_opt = ['save', 'torrent', 'magnet', ""]

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

    # name = "Umayon"
    # ep = "all"
    # q = "480p"
    # team = "HorribleSubs"
    # save = "torrent"

    obj = nh.NyaasiHoarder(name, ep, q, team, save)
    obj.start()
    print('Proceeding to save!')
    obj.save_to_file()

    info_list = [obj.name, obj.latest_episode, obj.q, obj.team, obj.time[0]]
    file = FileDoer(info_list)

    indices = file.read_indices()

    break_loop = 0
    for index in indices:
        if break_loop:
            break
        if file.is_changed(index):
            print("It seems like there is differences between your input and config file!")
            file.print_changes(index)
            while True:
                overwrite_input = input("Do you wish to overwrite?(y/n): ")
                if overwrite_input not in ['y', 'n']:
                    continue
                if overwrite_input == 'y':
                    file.update_line(index)
                    break_loop = 1
                    break
                if overwrite_input == 'n':
                    break_loop = 1
                    break
    else:
        file.append_new_line()


def main():
    parser = argparse.ArgumentParser(prog='nyaasi_automator', usage='%(prog)s [-a]')
    parser.add_argument("-am", action="store_true",
                        help="This will run nyaasi_hoarder like normal but also add to your configuration file")
    args = parser.parse_args()

    if args.am:
        add_mode()

    if not args.am:
        file = FileDoer('foobar')  # dummy text because we're checking here

        if file.check_file():
            pass
        else:
            print('First runtime detected! Config file created! `add mode` activated!')
            file.write_new_line()
            add_mode()

        d_save = 'save'

        # I hate the fact that there are so many variables have to sitting outside of the While True scope
        name_index = [index for index in file.read_indices()]
        #  name_list = [list(file.fetch_info_from_index(index))[0] for index in file.read_indices()]
        name_list = [list(file.fetch_info_from_index(index))[0] for index in name_index]
        #  name_dict = {index: value for (index, value) in zip(file.read_indices(), name_list)}
        time_sleep = 10  # seconds

        sequence_count = 0
        sequence_max = 4

        name_found = []
        episode_found = []
        # print(name_dict)

        while True:  # because the check will run forever until you stop it
            wait_time_list = []  # the name_found is reset by sequence

            for index, name in zip(name_index, name_list):
                saved_info_list = [item for item in list(file.fetch_info_from_index(index))]
                saved_name = saved_info_list[0]
                saved_latest_episode = saved_info_list[1]
                saved_q = saved_info_list[2]
                saved_team = saved_info_list[3]

                obj = nh.NyaasiHoarder(saved_name, 'latest', saved_q, saved_team, d_save)
                obj.start_silent()

                uploaded_time = obj.time[0]

                time_obj = TimeStuff(uploaded_time)

                # overwrite the last file object
                # the only thing changes are the latest episode and the uploaded time so the others may remain the same
                info_list = [saved_name, obj.latest_episode, saved_q, saved_team, uploaded_time]
                file = FileDoer(info_list)

                wait_time = None
                episode_number_difference = int(obj.latest_episode) - int(list(file.fetch_info_from_index(index))[1])
                if episode_number_difference > 0:
                    obj.save_to_file()
                    file.update_line(index)
                    wait_time = int(60 * 60 * 24 * 7)

                elif episode_number_difference <= 0:
                    wait_time = time_obj.time_difference_by_week(
                        (episode_number_difference + 1) // (episode_number_difference + 1)
                    )
                    if wait_time < 0:
                        wait_time = 0

                # wait time of the anime will be appended
                wait_time_list.append(wait_time)

                # logic to pass the variables out of the scope
                if int(saved_latest_episode) < int(obj.latest_episode):
                    latest_episode = obj.latest_episode
                else:
                    latest_episode = None
                    saved_name = None

                if (len(episode_found) and len(name_found)) < len(name_list):
                    # this represents the new episode found
                    episode_found.append(latest_episode)
                    # this represents the name of the anime that has new episode found
                    name_found.append(saved_name)

            else:  # for/else loop
                # the scope of this `else` is different from `for` so I need a list of the other one passed to the
                # outer scope to make it work. this kindda sucks but it looks neat i guess?

                os.system('cls')
                for name, wait_time, new_ep, latest_ep in zip(name_list, wait_time_list, name_found, episode_found):
                    if name == new_ep:
                        print(f"New episode {latest_ep} for {name}")
                        Beep(440, 500)

                    if wait_time == 0:
                        print(f'{name} is overdue!')
                    day, hour, minute, second = TimeStuff(wait_time).to_day()
                    print(f'ETA for {name}: {day} {hour}:{minute}:{second} days')

            time.sleep(time_sleep)

            if sequence_count % sequence_max == 3:
                name_found.clear()
                episode_found.clear()
            sequence_count += 1


if __name__ == '__main__':
    main()
    # add_mode()
