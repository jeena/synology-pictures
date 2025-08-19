⚠️ This repository has moved to https://git.jeena.net/jeena/synology-pictures

Synology Photos extraction
===========================

I have all my photos in a Synology Photos database and want to do fun stuff with it.

I'm getting the pictures from the Synology and upload them into Home Assistant. Make sure you have access to the database.

Installation
------------

```
sudo apt-get install ufraw-batch imagemagick libheif-examples libolm-dev
pipenv install
pipenv shell
```

Open postgresql port on Synology
================================

Taken from https://www.youtube.com/watch?v=MqJuKu38BsA

x.x.x.x should be your IP where the script runs

```
echo "host all all x.x.x.x/24 trust" >> /etc/postgresql/pg_hba.conf
sed -i /listen_addresses = '127.0.0.1'/listen_addresses = '*'/ /etc/postgresql/postgresql.conf
```

License
-------

GPL v3
