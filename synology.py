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
SELECT folder.name, unit.filename, user_info.name AS user
FROM unit
    LEFT OUTER JOIN face ON face.ref_id_unit = unit.id
    LEFT OUTER JOIN folder ON folder.id = unit.id_folder
    LEFT OUTER JOIN user_info ON user_info.id = unit.id_user
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
	
def fetch_path_for_names_day_and_month(conn, names, month, day, limit=1):
	sql_query = """
SELECT folder.name, unit.filename, user_info.name AS user, EXTRACT(YEAR FROM to_timestamp(unit.takentime)::date) as year
FROM unit
    LEFT OUTER JOIN face ON face.ref_id_unit = unit.id
    LEFT OUTER JOIN folder ON folder.id = unit.id_folder
    LEFT OUTER JOIN user_info ON user_info.id = unit.id_user
WHERE
    face.id_person in (SELECT id FROM person WHERE lower(name) SIMILAR TO %s)
AND
    EXTRACT(MONTH FROM to_timestamp(unit.takentime)::date) = %s
AND
    EXTRACT(DAY FROM to_timestamp(unit.takentime)::date) = %s
ORDER BY random()
LIMIT %s;
"""
	cur = conn.cursor()
	cur.execute(sql_query, ('%(' + names + ')%', month, day, limit))
	pictures = cur.fetchall()
	cur.close()

	return pictures

def fetch_files(remotehost, pictures):
	dirpath = tempfile.mkdtemp()
	for picture in pictures:
		# /var/services/homes/kaylee/Photos/MobileBackup/iPhone/2018/09/IMG_20180908_094627.HEIC
		# /volume1/photo/jeena/William/Pictures/Photos/Moments/Mobile/SM-N986B/DCIM/Camera/20210924_122532.jpg
		path = picture[0]
		name = picture[1]
		user = picture[2]
		year = picture[3] + "-" if len(picture) > 3 else ""
		if user == '/volume1/photo':
			lib_path = "/photo"
		else:
			lib_path = "/homes/" + user + "/Photos"
		remotefile = '\ '.join('/'.join([lib_path, path, name]).split())
		localfile = '/'.join([dirpath, str(year) + name])
		escaped_remotefile = helper.escape_file_path(remotefile)
		cmd = 'scp -P 23 "' + remotehost + ':' + escaped_remotefile + '" "' + localfile + '"'
		if os.system(cmd) == 0:
			(p, e) = os.path.splitext(localfile)
			if e == ".HEIC":
				old_localfile = localfile
				localfile = old_localfile + ".jpg"
				cmd = 'heif-convert "' + old_localfile + '"  "' + localfile + '"'
				os.system(cmd)
				os.remove(old_localfile)
                        # Get .xmp file if available
			cmd = 'scp -P 23 "' + remotehost + ':' + escaped_remotefile + '.xmp" "' + localfile + '.xmp"'
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
	dirpath = fetch_files("jeena@" + host_ip, pictures)
	shutil.rmtree(dirpath)
