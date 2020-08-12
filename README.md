# nyaasi_hoarder

This script will torrent the selected anime. It can also save torrent links and files for later use.

It can run with command-line option `python nyaasi-hoarder.py "anime name" -ep 00 -fs "HorribleSubs" -q 1080p -save save`.

You must include the quotation marks when the name of either sub team or anime has `-` in.

`-ep` has `all` as default so you may not need to write `-ep` in the command-line to download all episode.

You can use `magnet` and `torrent` to instead of `save` by `-save` to download the files. But you need the BitTorrent softwares running first
since I am not using any special or certain methods to start a torrent file.

Different fan sub team has different anime names, either in English or Japanese. So know your stuffs~

# nyaasi_automator

It utilizes nyaasi_hoarder to download your animes of choice from a list you put in.

Simply `nyaasi_automator.py` and it will prompt you to enter the info of your animes then they will be saved to `nh_auto.cfg`.

The next use, the script will read it and loops forever to check whether the anime is updated or not. 

So now, you don't need to look up if new episode is available, this would just do all the work for you.

Add `-am` to enter `add mode` in order to add more animes into your list.



