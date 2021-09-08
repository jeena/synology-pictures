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
	os.system(cmd)

if __name__ == "__main__":
	ha_path = os.getenv('HA_PATH')
	ha_path = "root@bundang.swierczyniec.info:/media/Synology"
	host_ip = os.getenv('DB_HOST')
	conn = synology.connect_db(host_ip, os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
	names = "richard|yingfen|kaylee"
	pictures = synology.fetch_paths_for_names(conn, names, 20)
	synology.close_db(conn)
	dirpath = synology.fetch_files("jeena@" + host_ip, "/var/services/homes/jeena/Photos", pictures)

	with os.scandir(dirpath) as dirs:
		for i, entry in enumerate(dirs):
			upload_photo(ha_path, resize_and_crop(i, os.path.join(dirpath, entry.name)))
	shutil.rmtree(dirpath)

