#!/usr/bin/env bash
python3 ../Shield/general_shield.py './flask_app.py' 'mode=sf_url&lourl=http://120.77.65.191:10080/&interval=199'
python3 ../Shield/general_shield.py 'python3 file_support.py' 'mode=sf_url&lourl=http://120.77.65.191:10033/&interval=199'
python3 ../Shield/general_shield.py 'python3 file_support.py DOWNLOAD /../' 'mode=sf_url&lourl=http://120.77.65.191:10034/&interval=199'