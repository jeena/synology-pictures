#!/usr/bin/env python3

import psycopg2
import tempfile
import shutil
import os
import helper
from darktable import Darktable

def connect_db(db_host, db_user, db_passwd):
	return psycopg2.connect(
            host=db_host,
            database="synofoto",
            user=db_user,
            password=db_passwd)

def close_db(conn):
	conn.close()

def fetch_paths_for_names(conn, names, limit=20):
	sql_query = """
SELECT folder.name, unit.filename, user_info.name AS uname
FROM unit
    LEFT OUTER JOIN face ON face.ref_id_unit = unit.id
    LEFT OUTER JOIN folder ON folder.id = unit.id_folder
    LEFT OUTER JOIN user_info on user_info.id = folder.id_user
WHERE
    face.id_person in (SELECT id FROM person WHERE lower(name) SIMILAR TO %s)
ORDER BY random()
LIMIT %s;
"""
	cur = conn.cursor()
	cur.execute(sql_query, ('%(' + names + ')%', limit))
	pictures = cur.fetchall()
	cur.close()

	return pictures

def fetch_files(remotehost, lib_path, pictures):
	dirpath = tempfile.mkdtemp()
	for picture in pictures:
		pic_path = lib_path
		if picture[2].startswith('/'):
			pic_path = picture[2]
		else:
			pic_path = '/'.join([lib_path, picture[2], 'Photos'])
		remotefile = '\ '.join('/'.join([pic_path, picture[0], picture[1]]).split())
		localfile = '/'.join([dirpath, picture[1]])
		escaped_remotefile = helper.escape_file_path(remotefile)
		cmd = 'scp "' + remotehost + ':' + escaped_remotefile + '" "' + localfile + '"'
		if os.system(cmd) == 0:
			(p, e) = os.path.splitext(localfile)
			if e == ".HEIC":
				old_localfile = localfile
				localfile = old_localfile + ".jpg"
				cmd = 'heif-convert "' + old_localfile + '"  "' + localfile + '"'
				os.system(cmd)
				os.remove(old_localfile)
			# Get .xmp file if available
			cmd = 'scp "' + remotehost + ':' + escaped_remotefile + '.xmp" "' + localfile + '.xmp"'
			if os.system(cmd) == 0:
				# Use darktable
				d = Darktable(localfile)
				d.export()
				os.remove(localfile)
				os.remove(localfile + ".xmp")
	return dirpath


if __name__ == "__main__":
	host_ip = os.getenv('DB_HOST')
	conn = connect_db(host_ip, os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
	names = "richard|yingfen"
	pictures = fetch_paths_for_names(conn, names, 5)
	close_db(conn)
	dirpath = fetch_files("jeena@" + host_ip, "/var/services/homes/", pictures)
	shutil.rmtree(dirpath)
