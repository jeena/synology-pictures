#!/usr/bin/env python3

from datetime import datetime
import sys
import os
import synology
import edit
import shutil

import matrix_commander
from matrix_commander import main

def years_ago(path):
	img = edit.Image(path)
	takenyear = int(img.get_takentime()[:4])
	diff_year = datetime.today().year - takenyear
	ret = "Today, "
	ret += str(diff_year)
	ret += " year"
	if diff_year > 1:
		ret += "s"
	ret += " ago."
	return ret

def post_photo(path):
	argv = ["matrix-commander"]
	argv.extend(["--message", "" + years_ago(path) + ""])
	argv.extend(["--image", path])
	argv.extend(["--print-event-id"])
	return matrix_commander.main(argv)

if __name__ == "__main__":
	if len(sys.argv) != 2:
	        print("Usage: matrix.py richard|kaylee")
	        exit(1)
	        
	sy_host = os.getenv('SY_DB_HOST')
	sy_user = os.getenv('SY_USER')
	conn = synology.connect_db(sy_host, os.getenv('SY_DB_USER'), os.getenv('SY_DB_PASSWD'))
	names = sys.argv[1]
	month = datetime.today().month
	day = datetime.today().day
	pictures = synology.fetch_path_for_names_day_and_month(conn, names, month, day, 1)
	synology.close_db(conn)
	dirpath = synology.fetch_files(sy_user + "@" + sy_host, pictures)
	ret = 0
	with os.scandir(dirpath) as dirs:
		for i, entry in enumerate(dirs):
			ret = post_photo(os.path.join(dirpath, entry.name))
	shutil.rmtree(dirpath)
	exit(ret)

