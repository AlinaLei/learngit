#!/bin/sh
source /etc/profile
psh=/home/xuecheng/gitpro/bi_model_service/auto_batch
echo $psh
cd $psh
python3 Pro_console.py cons "cons_etl(table_name='pr_coupon_user_coupons')" > etl.log  2> etl.err
python3 Pro_console.py cons "cons_etl(table_name='pr_level_user_tag')" >> etl.log  2>> etl.err
python3 Pro_console.py cons "cons_etl(table_name='pr_crma_stations_couponstat')" >> etl.log  2>> etl.err
python3 Pro_console.py cons "cons_etl(table_name='pr_crma_groups_couponstat')" >> etl.log  2>> etl.err
# echo -e 'pr_level_user_tag\npr_level_user_tag2' | xargs -n 1 -i -P 8 sh -c 'python3 Pro_console.py cons "cons_etl(table_name='{}')" >> etl.log  2>> etl.err'