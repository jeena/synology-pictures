#!/usr/bin/env python3

import synology
import os
import shutil
import edit

def new_path(i, path):
        return os.path.join(os.path.dirname(path), str(i) + '.jpg')

def resize_and_crop(i, path):
        n_path = new_path(i, path)
        img = edit.Image(path)
        img.crop()
        img.add_metadata()
        img.safe(n_path)
        return n_path
        

def upload_photo(remotepath, path):
	cmd = 'scp ' + path + ' ' + remotepath
	print(cmd)
	os.system(cmd)

if __name__ == "__main__":
	ha_path = os.getenv('HA_PATH')
	sy_host = os.getenv('SY_DB_HOST')
	sy_user = os.getenv('SY_USER')
	conn = synology.connect_db(sy_host, os.getenv('SY_DB_USER'), os.getenv('SY_DB_PASSWD'))
	names = os.getenv('SY_SEARCH')
	pictures = synology.fetch_paths_for_names(conn, names, 20)
	synology.close_db(conn)
	dirpath = synology.fetch_files(sy_user + "@" + sy_host, pictures)

	with os.scandir(dirpath) as dirs:
		for i, entry in enumerate(dirs):
			upload_photo(ha_path, resize_and_crop(i, os.path.join(dirpath, entry.name)))
	shutil.rmtree(dirpath)

