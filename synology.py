#!/usr/bin/env python3

import psycopg2
import tempfile
import shutil
import os

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
SELECT folder.name, unit.filename
FROM unit
    LEFT OUTER JOIN face ON face.ref_id_unit = unit.id
    LEFT OUTER JOIN folder ON folder.id = unit.id_folder
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
		remotefile = '\ '.join('/'.join([lib_path, picture[0], picture[1]]).split())
		localfile = '/'.join([dirpath, picture[1]])
		escaped_remotefile = remotefile.replace(" ", "\ ").replace("(", "\(").replace(")", "\)").replace("&", "\&")
		cmd = 'scp "' + remotehost + ':' + escaped_remotefile + '" "' + localfile + '"'
		os.system(cmd)
	return dirpath


if __name__ == "__main__":
	host_ip = os.getenv('DB_HOST')
	conn = connect_db(host_ip, os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
	names = "richard|yingfen"
	pictures = fetch_paths_for_names(conn, names, 5)
	close_db(conn)
	dirpath = fetch_files("jeena@" + host_ip, "/var/services/homes/jeena/Photos", pictures)
	shutil.rmtree(dirpath)
