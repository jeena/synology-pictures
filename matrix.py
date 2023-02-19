#!/usr/bin/env python3

from datetime import datetime
import sys
import os
import synology
import edit
import shutil
import argparse
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

def post_photo(path, roomid):
	argv = ["matrix-commander"]
	argv.extend(["--message", "" + years_ago(path) + ""])
	argv.extend(["--image", path])
	argv.extend(["--print-event-id"])
	argv.extend(["--room", roomid])
	return matrix_commander.main(argv)
	
def get_args():
	parser = argparse.ArgumentParser(description='Post dates picture(s) to a Matrix room')
	parser.add_argument('-n', '--names', required=True)
	parser.add_argument('-e', '--exclude', default=None, required=False)
	parser.add_argument('-r', '--roomid', required=True)
	parser.add_argument('-m', '--month', default=datetime.today().month, type=int)
	parser.add_argument('-d', '--day', default=datetime.today().day, type=int)
	parser.add_argument('-s', '--size', default=1, type=int)
	return parser.parse_args()

if __name__ == "__main__":
	args = get_args()
	sy_host = os.getenv('SY_DB_HOST')
	sy_user = os.getenv('SY_USER')
	
	# Get img paths from database
	conn = synology.connect_db(sy_host, os.getenv('SY_DB_USER'), os.getenv('SY_DB_PASSWD'))
	pictures = synology.fetch_path_for_names_exclude_day_and_month(conn,
		args.names, args.exclude, args.month, args.day, args.size)
	synology.close_db(conn)
	
	# Fetch files from synology to tmp
	dirpath = synology.fetch_files(sy_user + "@" + sy_host, pictures)
	
	# Traverse dirs and post picures in matrix room
	ret = 0
	with os.scandir(dirpath) as dirs:
		for i, entry in enumerate(dirs):
			ret = post_photo(os.path.join(dirpath, entry.name), args.roomid)
			
	# Cleanup
	shutil.rmtree(dirpath)
	exit(ret)

