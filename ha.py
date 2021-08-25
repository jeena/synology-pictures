#!/usr/bin/env python3

import synology
import os
import shutil
import edit

def prepare_photo(i, path):
	# sudo apt-get install ufraw-batch
	# convert 13895032967_642e23af42_o.jpg -adaptive-resize 1920x1080\> -size 1920x1080 xc:black +swap  -gravity center -composite 01.jpg
	# filename, file_extension = os.path.splitext(path)
	n_path = new_path(i, path)
	cmd = 'convert "' + path + '" -adaptive-resize 1920x1080\> -size 1920x1080 xc:black +swap  -gravity center -composite ' + n_path
	print(cmd)
	os.system(cmd)
	# os.rename(path, new_path)
	return n_path

def new_path(i, path):
        return os.path.join(os.path.dirname(path), str(i) + '.jpg')

def resize_and_crop(i, path):
        n_path = new_path(i, path)
        img = edit.Image(path)
        img.crop()
        img.safe(n_path)
        return n_path

def upload_photo(remotepath, path):
	cmd = 'scp ' + path + ' ' + remotepath
	os.system(cmd)

if __name__ == "__main__":
	ha_path = os.getenv('HA_PATH')
	ha_path = "root@bundang.swierczyniec.info:/media/Synology"
	host_ip = os.getenv('DB_HOST')
	conn = synology.connect_db(host_ip, os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
	names = "richard|yingfen"
	pictures = synology.fetch_paths_for_names(conn, names, 20)
	synology.close_db(conn)
	dirpath = synology.fetch_files("jeena@" + host_ip, "/var/services/homes/jeena/Photos", pictures)

	with os.scandir(dirpath) as dirs:
		for i, entry in enumerate(dirs):
			upload_photo(ha_path, resize_and_crop(i, os.path.join(dirpath, entry.name)))
	shutil.rmtree(dirpath)

