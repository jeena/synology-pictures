#!/usr/bin/env python3

import synology
import shutil
import os
import pickle
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_httplib2  # This gotta be installed for build() to work
from googleapiclient.http import MediaFileUpload
import requests
import subprocess
import shlex

def get_creds():
	SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly',
		'https://www.googleapis.com/auth/photoslibrary.sharing',
		'https://www.googleapis.com/auth/photoslibrary',
		'https://www.googleapis.com/auth/photoslibrary.readonly']
	creds = None
	if(os.path.exists("token.pickle")):
		with open("token.pickle", "rb") as tokenFile:
			creds = pickle.load(tokenFile)
	if not creds or not creds.valid:
		if (creds and creds.expired and creds.refresh_token):
			creds.refresh(Request())
		else:
			# ssh -L 8081:localhost:8081 burgpreppach.swierczyniec.info
			flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
			creds = flow.run_local_server(port = 8081)
		with open("token.pickle", "wb") as tokenFile:
			pickle.dump(creds, tokenFile)
	return creds

def login_gphoto(creds):
	return build('photoslibrary', 'v1', credentials = creds, static_discovery=False)

def get_album(service, name):
	results = service.albums().list(pageSize=10, fields='nextPageToken,albums(id,title)').execute()
	if 'albums' in results:
		for r in results['albums']:
			if r['title'] == name:
				return r
	return None

def create_album(service, name):
	request_body = {'album': {'title': name }}
	results = service.albums().create(body=request_body).execute()
	return results

def empty_album(service, album):
	request_body = {'albumId': album['id'], 'pageSize': 100}
	results = service.mediaItems().search(body=request_body).execute()
	mediaItems = results.get('mediaItems')
	if mediaItems == None:
		return
	mediaIds = []
	for item in mediaItems:
		mediaIds.append(item['id'])

	request_body = { 'mediaItemIds': mediaIds }
	response = service.albums().batchRemoveMediaItems(albumId=album['id'], body=request_body).execute()

def upload_gphoto(service, creds, album, picture_path):
	upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
	headers = {
		'Authorization': 'Bearer ' + creds.token,
		'Content-type': 'application/octet-stream',
		'X-Goog-Upload-Protocol': 'raw'
	}
	img = open(os.path.join(picture_path), 'rb').read()
	response = requests.post(upload_url, data=img, headers=headers)
	request_body = {
		'albumId': album['id'],
		'newMediaItems': [
			{
				'simpleMediaItem': {
					'uploadToken': response.content.decode('utf-8')
				}
			}
		]
	}
	upload_response = service.mediaItems().batchCreate(body=request_body).execute()

if __name__ == "__main__":

	get_pictures = True
	if get_pictures:
		host_ip = os.getenv('DB_HOST')
		conn = synology.connect_db(host_ip, os.getenv('DB_USER'), os.getenv('DB_PASSWD'))
		names = "richard|yingfen"
		pictures = synology.fetch_paths_for_names(conn, names, 20)
		synology.close_db(conn)
		dirpath = synology.fetch_files("jeena@" + host_ip, "/var/services/homes/jeena/Drive", pictures)

	creds = get_creds()
	gclient = login_gphoto(creds)
	album = get_album(gclient, "Synology")
	if album == None:
		album = create_album(gclient, "Synology")

	empty_album(gclient, album)

	with os.scandir(dirpath) as dirs:
		for entry in dirs:
			upload_gphoto(gclient, creds, album, os.path.join(dirpath, entry.name))

	shutil.rmtree(dirpath)
