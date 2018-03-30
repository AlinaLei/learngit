#!/usr/bin/env bash
ps auxf | grep file_support.py | cut -b 10-15 | xargs kill -9
python3 file_support.py > ../.logs/Webserver_3333log &
python3 file_support.py 'run("DOWNLOAD","/../")' > ../.logs/Webserver_3334log &
python3 flask_app.py