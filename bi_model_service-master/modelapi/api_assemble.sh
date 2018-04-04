#!/usr/bin/env bash
python3 ../Shield/general_shield.py './flask_api.py LAN > /tmp/model_api.logerr 2>&1' 'mode=sf_url&lourl=http://10.44.121.20:8111/ReadMe&interval=6666'