#!/bin/bash

PATH=/home/jeena/.local/bin/:$PATH
cd /home/jeena/Projects/synology-pictures/
pipenv run python3 ha.py
