#!/usr/bin/env bash
LISTEN_ip=120.77.65.191
python3 ../Shield/general_shield.py './flask_app.py' 'mode=sf_url&lourl=http://'$LISTEN_ip':10080/&interval=199'
python3 ../Shield/general_shield.py 'python3 file_support.py' 'mode=sf_url&lourl=http://'$LISTEN_ip':10033/&interval=199'
python3 ../Shield/general_shield.py 'python3 file_support.py 10034 /../' 'mode=sf_url&lourl=http://'$LISTEN_ip':10034/&interval=199'