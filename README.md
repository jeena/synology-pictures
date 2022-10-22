Synology Photos extraction
===========================

I have all my photos in a Synology Photos database and want to do fun stuff with it.

I'm getting the pictures from the Synology and upload them into Home Assistant. Make sure you have access to the database.

Installation
------------

```
sudo apt-get install ufraw-batch imagemagick
git submodule update --init --recursive
pipenv install
pipenv shell
cd heic2jpeg
pipenv install
cd ..
```

License
-------

GPL v3
