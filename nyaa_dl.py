#!/usr/bin/python

from math import floor, log
from time import sleep
from os import getcwd
from os.path import join, abspath
from argparse import ArgumentParser
import requests
from qbittorrent import Client

KW_1 = "<a href=\"/download/"

def fill0(n, d):
	r = str(n)

	for i in range(floor(log(n, 10)) + 1, d):
		r = "0" + r

	return r

def send_req(url):
	res = None

	success = False

	while True:
		try:
			res = requests.get(url)
			success = (res.status_code == 200)
		except:
			pass

		if success:
			break
		else:
			print("net err, retrying")
			sleep(5)

	return res

start = 1
end = None
digits = 2
tpath = "./torrents"
vpath = "./S1"

parser = ArgumentParser()

parser.add_argument("-s", "--start", type=int,
	                help="start episode index, defaults to 1")

parser.add_argument("-e", "--end", type=int,
	                help="end episode index, by default it's the same as start")

parser.add_argument("-d", "--digits", type=int,
	                help="number of digits in episode index, defaults to 2")

parser.add_argument("-p", "--tpath", type=str,
	                help="dir path, the program saves the .torrent here, defaults to \"./torrents\"")

parser.add_argument("-P", "--vpath", type=str,
	                help="dir path, qb should save the video files here, defaults to ./S1")

parser.add_argument("search_term", type=str,
	                help="the search term, must include a '*' symbol, the episode index is put in place of it")

args = parser.parse_args()

search_term = args.search_term

if "*" not in search_term:
	print("there is no '*' in the search term, exiting")
	exit(1)

if args.start != None:
	start = args.start

if args.end == None:
	end = start
else:
	end = args.end

if args.digits != None:
	digits = args.digits

if args.tpath != None:
	tpath = args.tpath

if args.vpath != None:
	vpath = args.vpath

vpath = abspath(vpath)

qb = Client("http://localhost:1317")

for i in range(start, end + 1):
	print("next target is E" + str(i))

	cst = search_term.replace("*", fill0(i, digits))
	suburl = cst.replace(" ", "+")

	print("fetching feed")

	sr = send_req("https://nyaa.si/?f=0&c=0_0&q={}&s=seeders&o=desc".format(suburl))
	st = sr.text

	id_si = id_ei = None

	try:
		ti = st.index(cst)

		id_si = st.index(KW_1, ti) + len(KW_1)
		id_ei = st.index(".torrent", id_si)
	except:
		print("no match, skipping")
		continue

	_id = st[id_si:id_ei]

	print("match, id is " + _id)
	print("dling .torrent file")

	tr = send_req("https://nyaa.si/download/{}.torrent".format(_id))

	tfp = join(tpath, _id + ".torrent")

	print("saving .torrent file")

	tfw = open(tfp, "wb")
	tfw.write(tr.content)
	tfw.close()

	print("sending .torrent file to qb")

	tfr = open(tfp, "rb")
	qb.download_from_file(tfr, savepath=vpath)
	tfr.close()

print("done")

