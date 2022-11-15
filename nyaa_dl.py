#!/usr/bin/python

from math import floor, log
from time import sleep
from os.path import isfile, isdir, join, abspath, basename
import re
from glob import glob
from enum import Enum, auto
from argparse import ArgumentParser
import requests
from qbittorrent import Client

class Mode(Enum):
	SEARCH = auto()
	AUTO = auto()

KW_1 = "<a href=\"/download/"
KW_2 = "title=\""
KW_3 = "href=\"/view/"

tpath = "./torrents"
vpath = "./S1"

parser = ArgumentParser()

parser.add_argument("-s", "--start", type=int,
	                help="start ep index, defaults to next ep in vpath")

parser.add_argument("-e", "--end", type=int,
	                help="end ep index, defaults to start")

parser.add_argument("-d", "--digits", type=int,
	                help="digits in ep index, defaults to 2")

parser.add_argument("-p", "--tpath", type=str,
	                help=".torrent files go here, defaults to \"./torrents\"")

parser.add_argument("-P", "--vpath", type=str,
	                help="qb should save the vid files here, defaults to ./S1")

parser.add_argument("search_term", type=str,
	                help="if contains a '*' symbol, auto mode (ep i put there), else, search mode")

args = parser.parse_args()

search_term = args.search_term

if args.tpath != None:
	tpath = args.tpath

if args.vpath != None:
	vpath = args.vpath

vpath = abspath(vpath)

mode = None

if "*" in search_term:
	mode = Mode.AUTO
else:
	mode = Mode.SEARCH

try:
	qb = Client("http://localhost:1317")
except:
	print("pls start qb")
	exit(1)

def fill0(n, d):
	r = str(n)

	for i in range(floor(log(n, 10)) + 1, d):
		r = "0" + r

	return r

def check_dir(dp, name):
	if not isdir(dp):
		print("no such dir: {} ({})".format(dp, name))
		exit(1)

def send_req(url):
	res = None

	success = False

	while True:
		try:
			res = requests.get(url, timeout=10)
			success = (res.status_code == 200)
		except:
			pass

		if success:
			break
		else:
			print("net err, retrying")
			sleep(5)

	return res

def fetch_feed(cst):
	suburl = cst.replace(" ", "+")

	print("fetching feed")
	sr = send_req("https://nyaa.si/?f=0&c=0_0&q={}&s=seeders&o=desc".format(suburl))

	return sr.text

def dl_by_id(_id):
	tfp = join(tpath, _id + ".torrent")

	print("checking if .torrent file is already down... ", end="")

	if isfile(tfp):
		print("yes")
	else:
		print("no")

		print("dling .torrent file")
		tr = send_req("https://nyaa.si/download/{}.torrent".format(_id))

		print("saving .torrent file")

		tfw = open(tfp, "wb")
		tfw.write(tr.content)
		tfw.close()

	print("sending .torrent file to qb")

	tfr = open(tfp, "rb")
	qb.download_from_file(tfr, savepath=vpath)
	tfr.close()

check_dir(tpath, "tpath")
check_dir(vpath, "vpath")

if mode == Mode.AUTO:
	start = 1
	end = None
	digits = 2

	if args.digits != None:
		digits = args.digits

	if args.start == None:
		bnr = re.compile("^E[0-9]{{1,{}}}\..*$".format(digits))

		vfs = glob(join(vpath, "*"))
		ns = False

		for x in vfs:
			bn = basename(x)

			if not bnr.match(bn):
				continue

			try:
				start = max(int(bn[1:(bn.index("."))]), start)
				ns = True
			except:
				pass

		start += ns
	else:
		start = args.start

	if args.end == None:
		end = start
	else:
		end = args.end

	print("scraping eps from E{} to E{}".format(start, end))

	for i in range(start, end + 1):
		print("next target is E" + str(i))

		cst = search_term.replace("*", fill0(i, digits))

		st = fetch_feed(cst)

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
		dl_by_id(_id)
elif mode == Mode.SEARCH:
	st = fetch_feed(search_term)

	rs = []
	pi = 0

	while True:
		tt_si = tt_ei = None
		id_si = id_ei = None

		try:
			vi = st.index(KW_3, pi)
			vj = st.index("\"", vi + len(KW_3))

			if st[vj - 1] == "s":
				vi = st.index("<a", vi);

			tt_si = st.index(KW_2, vi) + len(KW_2)
			tt_ei = st.index("\"", tt_si)

			id_si = st.index(KW_1, vi) + len(KW_1)
			id_ei = pi = st.index(".torrent", id_si)
		except:
			break

		rs.append([
			st[tt_si:tt_ei],
			st[id_si:id_ei]
		])

	for i in range(len(rs) - 1, -1, -1):
		print("{}. {}".format(i + 1, rs[i][0]))

	ris = input("i'd like to watch: ").split(" ")

	for x in ris:
		x = int(x)
		_id = rs[x - 1][1]

		print("next target is \"{}\", id is {}".format(rs[x - 1][0], _id))
		dl_by_id(_id)

print("done")

