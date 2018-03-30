#!/usr/bin/env bash
#!/bin/sh
source /etc/profile
psh=/home/xuecheng/gitpro/bi_model_service/auto_batch
echo $psh
cd $psh
python3 Pro_console.py cons "drop_cos_ndyn()" >> Pro_console.py_log  2>> Pro_console.py_err