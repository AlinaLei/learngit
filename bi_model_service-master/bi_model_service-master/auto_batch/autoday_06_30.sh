#!/bin/sh
source /etc/profile
psh=/home/xuecheng/gitpro/bi_model_service/auto_batch
ls $psh/data_shield.py | xargs -n 1 -i -P 8 sh -c " python3 {} 1> {}_log  2> {}_err "
