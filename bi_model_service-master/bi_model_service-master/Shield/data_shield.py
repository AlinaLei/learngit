import os,sys,time,re
sys.path.append('../DBbase')
from db_func import *
from mail_func import *


def watchdog_a():
    SQL_watchdog_one = """
    SELECT batch_date,count(1) counts,count(DISTINCT %(dis_col)s) dis__%(dis_col)ss
    FROM profile.%(table_name)s
    where batch_date = %(yesterday)s
    GROUP BY batch_date
    """
    
    table_col = {'pr_groups_order_other_': 'mer_id',
                 'pr_platforms_order_other_': 'mer_id',
                 'pr_stations_order_other_': 'mer_id',
                 'pr_groups_user_dis_': 'mer_id',
                 'pr_platforms_user_dis_': 'mer_id',
                 'pr_stations_user_dis_': 'mer_id',
                 'pr_stations_user_dis2_': 'mer_id',
                 'pr_coupon_user_coupons': 'uid',
                 'pr_level_user_tag': 'uid',
                 'pr_crma_stations_couponstat': 'uid',
                 'pr_crma_groups_couponstat': 'uid',
                }
    para = {'yesterday': day_forpast(d=-1)}
    dw = my_(config.MYSQL_BI_RW_ENV)
    # dfr = {}
    ress = ''
    for x, v in table_col.items():
        para.update({'table_name': x, 'dis_col': v})
        df = dw.to_dataframe(SQL_watchdog_one %para)
        if df.__len__():
            continue
        dfs = df.drop('batch_date', 1).to_json(orient='records')
        # dfr[x] = df
        ress += 'profile.%-36s: %s \n' % (x, dfs)
        
    if ress:
        print(ress)
        subject = 'profile更新信息提示_' + para['yesterday']
        send_email_exqq(['xuechen.han@weicheche.cn', 'wenyi.liu@weicheche.cn'], subject, content=ress, filepaths=None)
    else:
        print('没问题')
        send_wechat_warning('每日数据检查OK！-——data_shield(watchdog_a)')


def watchdog_b():
    para = {'yesterday': day_forpast(d=-1)}
    table_names = ['mid_cos_dyn_%(yesterday)s' %para, 'mid_cos_dyn_%(yesterday)s' %para]
    dw = my_(config.MYSQL_BI_RW_ENV)
    ress = ''
    for x in table_names:
        df = dw.to_dataframe('select count(1) counts from data_center.%s' % x)
        if df.__len__():
            continue
        dfs = df.to_json(orient='records')
        ress += 'data_center.%-36s: %s \n' % (x, dfs)

    if ress:
        print(ress)
        subject = 'data_center中间表更新信息提示_' + para['yesterday']
        send_email_exqq(['xuechen.han@weicheche.cn'], subject, content=ress, filepaths=None)
    else:
        print('没问题')
        send_wechat_warning('每日数据检查OK！-——data_shield(watchdog_b)')


if __name__ == "__main__":
    watchdog_a()
    watchdog_b()