#!/bin/sh
source /etc/profile
psh=/home/xuecheng/gitpro/bi_model_service/auto_batch
echo $psh
cd $psh
python3 Pro_console.py cons "cons_('10,20,21,22,23,24,30,40')" > Pro_console.py_log  2> Pro_console.py_err
python3 Pro_console.py cons "cons_('110,120,130,140,150')" >> Pro_console.py_log  2>> Pro_console.py_err
awk 'BEGIN{for(i=-1; i>=-1; i--) print i}'  | xargs -n 1 -i -P 8 sh -c "python3 Pro_console.py cons 'do_cos_ndyn({})'"
python3 Pro_console.py cons "cons_('250,251,252,253')" >> Pro_console.py_log  2>> Pro_console.py_err
python3 Pro_console.py cons "cons_('531,532,533,539')" >> Pro_console.py_log  2>> Pro_console.py_err
# ls $psh/P*console.py | xargs -n 1 -i -P 8 sh -c " python3 {} cons cons_('10,20,21,22,23,24,30,40') > {}_log  2> {}_err "
# ls $psh/P*console.py | xargs -n 1 -i -P 8 sh -c " python3 {} cons cons_('110,120,130,140,150') > {}_log  2> {}_err "
