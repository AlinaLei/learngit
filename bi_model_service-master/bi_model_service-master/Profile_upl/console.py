from Createsqls import *
from Etlsqls import * 
import numpy as np
import sys
sys.path.append('../DBbase')
from db_func import *
from hcomponents import *
# sys.path.append('../.settings')
# import config

PRO_Database = 'profile'

dfsql_choice = {'crm_latest_station': """
    select uid,stid mer_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      , accum_oil_liter,accum_oil_cnt, lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_station """
                # where stid not in (171073,177370,177619,176669,177525,10258,10261)"""
                , 'crm_latest_group': """
    select uid,group_id mer_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      , accum_oil_liter,accum_oil_cnt, lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_group """
                # where group_id not in (1,2,184,210,254)"""
                , 'crm_latest_platform': """
    select uid,0 mer_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      , accum_oil_liter,accum_oil_cnt, lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_platform """
                , 'inspay_orders_station': """
    select uid,stid mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    """
                , 'inspay_orders_group': """
    select uid,group_id mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    """
               , 'inspay_orders_platform': """
    select uid,0 mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    """
                , 'user_tag_group': """
    select uid,merchant_id mer_id,level_name,sort from profile.pr_level_user_tag 
    where batch_date = %(do_day)s """
                , 'user_tag_platform': """
    select uid,0 mer_id,level_name,sort from profile.pr_level_user_tag 
    where batch_date = %(do_day)s """}

for N3 in [7,14,30]:
    dfsql_choice['user_3n_%s_station' % N3] = """
    SELECT 
      stid mer_id,count(1) _XXX,sum(last1_ts>0) _XX1 #latest_o
      ,sum(last3_ts>0 and last2_ts=0) _10X #sleep_
      ,sum(last3_ts>0 and last2_ts=0 and last1_ts>0 ) _101 #sleep_o
      ,sum(last2_ts>0 and last1_ts=0) _X10 # tend_sleep
      ,sum(last2_ts>0 and last1_ts=0) _X11
      ,sum(last1_ts>0 and last1_ts>0 and last1_ts>0) _111
      ,sum(last3_ts>0 and last2_ts=0 and last1_ts=lastday_ts and lastday_ts>0) _10_today2N # 当天消费并且上一次间隔2N天以上
      ,sum(last2_ts>0 and last1_ts=lastday_ts and lastday_ts>0) _X1_today1N # 当天消费并且上一次间隔N天以上
      ,sum(lastday_ts>0) _XX1_today# 所有当天消费 
      ,sum(last3_ts>0) _1XX # 
    FROM data_center.mid_cos_n_%%(do_day)s
    where cycle_days = %s
    GROUP BY stid""" % N3
    dfsql_choice['user_3n_%s_platform' % N3] = dfsql_choice['user_3n_%s_station' % N3].replace('stid', "'0'")
dfsql_choice['user_3n_d_station'] = """
SELECT 
  stid mer_id,count(1) _XXX,sum(last1_ts>0) _XX1 #latest_o
  ,sum(last3_ts>0 and last2_ts=0) _10X #sleep_
  ,sum(last3_ts>0 and last2_ts=0 and last1_ts>0 ) _101 #sleep_o
  ,sum(last2_ts>0 and last1_ts=0) _X10 # tend_sleep
  ,sum(last2_ts>0 and last1_ts=0) _X11
  ,sum(last1_ts>0 and last1_ts>0 and last1_ts>0) _111
  ,sum(last3_ts>0 and last2_ts=0 and last1_ts=lastday_ts and lastday_ts>0) _10_today2N # 当天消费并且上一次间隔2N天以上
  ,sum(last2_ts>0 and last1_ts=lastday_ts and lastday_ts>0) _X1_today1N # 当天消费并且上一次间隔N天以上
  ,sum(lastday_ts>0) _XX1_today# 所有当天消费 
  ,sum(last3_ts>0) _1XX # 
FROM data_center.mid_cos_dyn_%(do_day)s
GROUP BY stid"""
dfsql_choice['user_3n_d_platform'] = dfsql_choice['user_3n_d_station'].replace('stid', "'0'")

for mer_ in ['station', 'group']:
    dfsql_choice['crma_'+ mer_] = '''
    SELECT mer_id,sum(useful) useful,sum(usedtoday) usedtoday
    FROM profile.pr_crma_stations_couponstat 
    where batch_date = %(do_day)s
    and useful+usedtoday 
    and activity_type in (%(activity_type in )s) 
    group by mer_id '''.replace('station', mer_)


dosql_drop_table_ifexists = "drop table if EXISTS %(table_name)s;"
dosql_copy_table_struct = "create table %(table_name)s like %(old_table_name)s;"
do_sql_cos_n = """
set @n_cycle = %(n_cycle)s;
set @today = DATE_ADD(%(do_day)s,INTERVAL 1 day);
set @begin_day = DATE_SUB(@today,INTERVAL 3*@n_cycle day);
insert into %(table_name)s
select 
    @n_cycle cycle_days,stid,uid,sum(batch_date=%(do_day)s) lastday_ts,sum(ABC=0) last1_ts,sum(ABC=1) last2_ts,sum(ABC=2) last3_ts
from 
    (select
        O.uid,stid,pay_time,floor((UNIX_TIMESTAMP(@today)-pay_time)/(@n_cycle*86400)) ABC,batch_date
    from dw.dw_inspay_orders O
    left join bimodels.bm_user_predict_ BP
    on BP.uid = O.uid
    where O.uid > 0 
    and O.batch_date >= @begin_day and O.batch_date < @today
    and pay_time > UNIX_TIMESTAMP(@begin_day) ) X
where ABC>=0 and ABC<=2
group by stid,uid
"""
do_sql_cos_dyn = """
set @today = DATE_ADD(%(do_day)s,INTERVAL 1 day);
set @begin_day = DATE_SUB(@today,INTERVAL 90 day);
insert into %(table_name)s
select 
    cycle_days,stid,uid,sum(batch_date=%(do_day)s) lastday_ts,sum(ABC=0) last1_ts,sum(ABC=1) last2_ts,sum(ABC=2) last3_ts
from 
    (select 
        O.uid,stid,pay_time,floor((UNIX_TIMESTAMP(@today)-pay_time)/((floor(predict_dt)+1)*86400)) ABC,floor(predict_dt)+1 cycle_days,batch_date
    from dw.dw_inspay_orders O
    inner join bimodels.bm_user_predict_ BP
    on BP.uid = O.uid
    where O.uid > 0 
    and O.batch_date >= @begin_day and O.batch_date < @today
    and pay_time > UNIX_TIMESTAMP(@begin_day) ) X
where ABC>=0 and ABC<=2
group by stid,uid"""

get_config_bytarid = """
select *,scopelevel & 8 platform,scopelevel & 4 'group',scopelevel & 2 station,scopelevel & 1 user
from profile.pr_target_config where tar_id = %s"""
get_spreadconfig_bytarid = """select * from profile.pr_target_spread_config where tar_id = %s"""
get_spreadconfig_byspreadtype = """select * from profile.pr_target_spread_config where tar_id = %s """

TODAYS = day_forpast(d=0)
TOMORROW = day_forpast(d=1)

global_df_dict = {}
dw = my_(config.MYSQL_BI_RW_ENV)
sql_para = {}


def addan_pr_targetspread_config(tar_id,spread_num=5,stattype=0,name=""):
    content1 = {
        'pr_target_config': {'tar_id': [tar_id]
        , 'create_time': 'now()'}
        , 'pr_target_spread_config': {'tar_id': tar_id
        , 'stattype': stattype
        , 'spr_id': [i+1 for i in range(spread_num)]
        , 'create_time': 'now()'}}
    if name: content1['pr_target_config']['name'] = name
    dw = my_(config.MYSQL_BI_RW_ENV)
    for k in content1:
        dw.df_upd_tosql(pd.DataFrame(data=content1[k]), table='%s.%s' % (PRO_Database, k))


def init_env():
    dw = my_(config.MYSQL_BI_RW_ENV)
    for k, v in create_sqls.items():
        print(dw.sql_engine(v).rowcount)
        if k in content1:
            df = pd.DataFrame(data=content1[k])
            print(df)
            dw.df_upd_tosql(df, batch=1000, table='%s.%s' % (PRO_Database,k))


def col_spread(df, clv):  # 对应spread_type = 2 , 无需需关联spread_config表, 直接由字段clv值的种类决定决定
    cla = 'spr_id'
    df[cla] = df[clv]
    dfr = pd.pivot_table(df, index=['mer_id', cla], values=[clv], aggfunc=[len, np.mean, np.std])
    return dfr


def colname_spred(spread_config, df):
    dfr_list = []
    for i, row in spread_config.iterrows():
        dfr_tmp = df.loc[:, ['mer_id', row['obligate']]]
        dfr_tmp.rename(columns={row['obligate']: 'value_c'}, inplace=True)
        dfr_tmp['spr_id'] = row['spr_id']
        dfr_list.append(dfr_tmp)
    dfr = pd.concat(dfr_list)
    return dfr


def dist_spread(spread_config, df, clv):  # 对应spread_type = 1 , 需关联spread_config表, 由字段clv所在区间决定
    cla = 'spr_id'
    df[cla] = -1
    # df['tar_id'] = str(spread_config.tar_id[0])
    for i, row in spread_config.iterrows():
        if row['upper_bound'] == -1:
            pind = df[clv] > row['lower_bound']
        elif row['lower_bound'] == -1:
            pind = df[clv] <= row['upper_bound']
        else:
            pind = (df[clv] <= row['upper_bound']) & (df[clv] > row['lower_bound'])
        df.loc[pind, cla] = row['spr_id']
    dfr = pd.pivot_table(df, index=['mer_id', cla], values=[clv], aggfunc=[len, np.mean, np.std])
    return dfr


def bigernumber_(x,th=0):   # 大于th的值的个数
    return len(x[x>0])


def record_spread(df, clv):  # 对应spread_type = 0 ,单指标 , 由单独计算的字段clv决定
    # dfrquery = pd.pivot_table(df.query(clv+'>0'), index=['mer_id'], values=[clv], aggfunc=[len])
    dfr = pd.pivot_table(df.fillna(0), index=['mer_id'], values=[clv], aggfunc=[len, np.mean, bigernumber_])
    dfr.rename(columns={'bigernumber_': 'value_ob'}, inplace=True)
    # dfr['std'] = dfrquery['len']
    return dfr


def do_day_tar_config(tar_config, daylist):
    spreadtype = tar_config.loc[0, 'spreadtype']
    dw = my_(config.MYSQL_BI_RW_ENV)
    idiot_flag =[c for c,v in tar_config.loc[0, ['platform', 'group', 'station', 'user']].iteritems() if v]
    clv = tar_config.loc[0, 'columns']  # 目标column
    originsql = tar_config.loc[0, 'originsql']
    otable = tar_config.loc[0, 'otable']   # 结果存放的目标表
    tarid = tar_config.loc[0, 'tar_id']
    obligate = tar_config.loc[0, 'obligate']  # obligate 可能存在某些其它条件
    if obligate:
        sql_para.update(json.loads(obligate.replace("'", '"')))
    if spreadtype >= 0:
        spread_config = dw.to_dataframe(get_spreadconfig_bytarid % tarid)
    else:
        spread_config = dw.to_dataframe(get_spreadconfig_byspreadtype % spreadtype)
    for d in daylist:
        sql_para['do_day'] = day_forpast(d)
        print(d, sql_para, idiot_flag)
        for v in idiot_flag:
            dw_in = my_(config.MYSQL_BI_RW_ENV)
            sqlkey = originsql + v
            valname = 'df_' + sqlkey + str(sql_para)
            otable_name = otable.replace('_i_', v)
            if valname not in global_df_dict:
                global_df_dict[valname] = dw_in.to_dataframe(dfsql_choice[sqlkey] % sql_para)
                if global_df_dict[valname] is None or len(global_df_dict[valname]) == 0:
                    continue
                print(valname, len(global_df_dict[valname]), end='>>')
            if spreadtype == 1:
                dfr = dist_spread(spread_config, global_df_dict[valname], clv)
            elif spreadtype == 0:
                dfr = record_spread(global_df_dict[valname], clv)
            elif spreadtype == 2:
                dfr = col_spread(global_df_dict[valname], clv)
            elif spreadtype in [-2, -3]:
                dfr = colname_spred(spread_config, global_df_dict[valname])
                dfr.reset_index(drop=True, inplace=True)
            else:
                continue
            if 'droplevel' in dir(dfr.columns):
                dfr.columns = dfr.columns.droplevel(1)
            if 'droplevel' in dir(dfr.index):
                dfr.reset_index(inplace=True)
            dfr.rename(columns={'len': 'value_c', 'mean': 'value_e', 'std': 'value_ob'}, inplace=True)
            dfr['batch_date'] = sql_para['do_day']
            dfr['tar_id'] = tarid
            dfr['update_time'] = 'now()'
            pname = sql_para['do_day'][:-1]
            pvalue = 10*(int(pname) + 1)
            # dw.add_partition_gener(sql_para['do_day'], sql_para['do_day'], otable_name, 'list')
            dw_in.add_partition_gener(pname+'X', pvalue, otable_name)
            print(dw_in.df_upd_tosql(dfr, batch=1000, table=otable_name))


def doa_bytarid(tarid='10', dp=-1):
    print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'tarid:', tarid)
    tar_config = dw.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(get_config_bytarid % tarid)
    do_day_tar_config(tar_config, dp if type(dp) is range else range(dp, 0))


def do_cos_ndyn(dp=-1, rep=True):
    dw = my_(config.MYSQL_BI_RW_ENV)
    sql_para['old_table_name'] = 'data_center.mid_cos_dyn_xxx_template'
    sql_para['do_day'] = day_forpast(dp)
    sql_para['table_name'] = 'data_center.mid_cos_dyn_' + sql_para['do_day']
    if rep:
        dw.sql_engine(dosql_drop_table_ifexists %sql_para)
    dw.sql_engine(dosql_copy_table_struct % sql_para)
    print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'dyn',)
    sql_list = (do_sql_cos_dyn % sql_para).split(';')
    dw.getdata(sql_list)

    sql_para['old_table_name'] = 'data_center.mid_cos_n_xxx_template'
    sql_para['table_name'] = 'data_center.mid_cos_n_' + sql_para['do_day']
    if rep:
        dw.c_conn(config.MYSQL_BI_RW_ENV).sql_engine(dosql_drop_table_ifexists % sql_para)
    dw.c_conn(config.MYSQL_BI_RW_ENV).sql_engine(dosql_copy_table_struct % sql_para)
    for N3 in [7, 14, 30]:
        sql_para['n_cycle'] = N3
        print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'N=%s' % N3,)
        sql_list = (do_sql_cos_n % sql_para).split(';')
        dw.getdata(sql_list)


def drop_cos_ndyn():
    dw = my_(config.MYSQL_BI_RW_ENV)
    df = dw.to_dataframe('use data_center;show tables')
    drop_tablename_list = df.Tables_in_data_center[df.Tables_in_data_center.str.contains(r'mid_cos_d{0,1}y{0,1}n_\d+')].tolist()
    for x in drop_tablename_list:
        print(x, dw.sql_engine('drop table data_center.%s' % x))


#  ========================================================================================================
def cons_makeup(tar_list='110,120,130,140,150'):  # 1.之后的指标需要补充历史数据的
    [doa_bytarid(i, -999) for i in tar_list.split(',')]


def cons_etl(table_name='pr_coupon_user_coupons'):
    pname = day_forpast(-1, ss='%Y_%m_%d')
    pvalue = day_forpast(0, ss="'%Y-%m-%d'")
    dw = my_(config.MYSQL_BI_RW_ENV)
    db_table = '%s.%s' % (PRO_Database,table_name)
    dw.add_partition_gener(pname, pvalue, table=db_table)
    dw.getdata(etl_sqls[table_name])
    dw.getdata('delete from %s where batch_date < %s' %(db_table, day_forpast(-120)))
    df = dw.get_partiotion(db_table)
    df0 = df.query('table_rows<1')
    if len(df0) > 1:
        dw.drop_partition(df0.loc[1, 'partition_name'], db_table)


# 控制台默认执行的任务
def cons_(tar_list='10,20,21,22,23,24,30,40,110,120,130,140,150', dp=-1):
    print(__name__)
    [doa_bytarid(i, dp) for i in tar_list.split(',')]


if __name__ == "__main__":
    print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'hello console %s' % sys.path[0], sys.argv)
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'cons':
            eval(sys.argv[2])
        else:
            cons_()
    print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'done')