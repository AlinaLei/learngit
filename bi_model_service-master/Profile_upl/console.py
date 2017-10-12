from Createsqls import *
import numpy as np
import sys
sys.path.append('../DBbase')
from db_func import *
from hcomponents import *
# sys.path.append('../.settings')
# import config

PRO_Database = 'profile'

dfsql_choice = {'crm_latest_station': """
    select uid,stid mer_id,member_level_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      ,consumer_trends,accum_oil_liter,accum_oil_cnt,first_oil_time,last_oil_time,lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_station where stid not in (171073,177370,177619,176669,177525,10258,10261)"""
                , 'crm_latest_group': """
    select uid,group_id mer_id,member_level_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      ,consumer_trends,accum_oil_liter,accum_oil_cnt,first_oil_time,last_oil_time,lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_group where group_id not in (1,2,184,210,254)"""
                , 'crm_latest_platform': """
    select uid,0 mer_id,0 member_level_id
      ,last_30day_oil_liter liter30,last_30day_oil_cnt cnt30,last_60day_oil_liter liter60,last_60day_oil_cnt cnt60
      ,consumer_trends,accum_oil_liter,accum_oil_cnt,first_oil_time,last_oil_time,lost_days,callback_cnt 
      ,accum_oil_cnt-lost_days uvalue0,last_60day_oil_liter-lost_days uvalue1
    from dw.dw_crm_latest_platform """
                , 'inspay_orders_station': """
    select uid,stid mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    and stid not in (171073,177370,177619,176669,177525,10258,10261)
    and group_id not in (1,2,184,210,254)"""
                , 'inspay_orders_group': """
    select uid,group_id mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    and stid not in (171073,177370,177619,176669,177525,10258,10261)
    and group_id not in (1,2,184,210,254)"""
               , 'inspay_orders_platform': """
    select uid,0 mer_id,oil
      ,orig_price,orig_price/list_unit_price liters,(orig_price-real_price)/orig_price price_marate
      ,coupon_discount/orig_price coupon_marate
      ,credit_unit_discount/list_unit_price credit_marate
    from dw.dw_inspay_orders where batch_date = %(do_day)s 
    and stid not in (171073,177370,177619,176669,177525,10258,10261)
    and group_id not in (1,2,184,210,254)"""}

get_config_bytarid = """
select *
  ,scopelevel & 8 platform,scopelevel & 4 'group',scopelevel & 2 station,scopelevel & 1 user
from profile.pr_target_config where tar_id = %s"""
get_spreadconfig_bytarid = """select * from profile.pr_target_spread_config where tar_id = %s"""

TODAYS = day_forpast(d=0)
TOMORROW = day_forpast(d=1)

global_df_dict = {}
dw = my_(config.MYSQL_BI_RW_ENV)
sql_para = {}


def addan_pr_targetspread_config(tar_id,spread_num=5,stattype=0,name=""):
    content1 = {
        'pr_target_config': {'tar_id': [tar_id]
          , 'name': ["'%s'" % name]
          , 'create_time': 'now()'}
        , 'pr_target_spread_config': {'tar_id': tar_id
          , 'stattype': stattype
          , 'spr_id': [i+1 for i in range(spread_num)]
          , 'create_time': 'now()'}}
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
    addan_pr_targetspread_config(20, spread_num=5, stattype=0, name="用户平均价值")


def dist_spread(spread_config, df, clv):
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
    dfr = pd.pivot_table(df, index=['mer_id', cla], values=[clv], aggfunc=[len, np.mean, np.std], margins=True)
    return dfr.iloc[:-1,:]


def record_spread(df, clv):
    dfrquery = pd.pivot_table(df.query(clv+'>0'), index=['mer_id'], values=[clv], aggfunc=[len], margins=True)
    dfr = pd.pivot_table(df.fillna(0), index=['mer_id'], values=[clv], aggfunc=[len, np.mean], margins=True)
    dfr['std'] = dfrquery['len']
    return dfr.iloc[:-1, :]


def do_day_tar_config(tar_config,daylist,spreadtype=1):
    idiot_flag = dict(tar_config.loc[0, ['platform', 'group', 'station', 'user']] > 0)
    clv = tar_config.loc[0, 'columns']
    originsql = tar_config.loc[0, 'originsql']
    otable = tar_config.loc[0, 'otable']
    tarid = tar_config.loc[0, 'tar_id']
    spread_config = dw.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(get_spreadconfig_bytarid % tarid)
    for d in daylist:
        sql_para['do_day'] = day_forpast(d)
        print(d, sql_para)
        for v, k in idiot_flag.items():
            if k:
                sqlkey = originsql + v
                valname = 'df_' + sqlkey + sql_para['do_day']
                otable_name = otable.replace('_i_', v)
                if valname not in global_df_dict:
                    global_df_dict[valname] = dw.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(dfsql_choice[sqlkey] % sql_para)
                    print(valname,otable_name,len(global_df_dict[valname]))
                if len(global_df_dict[valname]) == 0:
                    continue
                if spreadtype == 1:
                    dfr = dist_spread(spread_config, global_df_dict[valname], clv)
                elif spreadtype == 0:
                    dfr = record_spread(global_df_dict[valname], clv)
                else:
                    continue
                dfr.columns = dfr.columns.droplevel(1)
                dfr['value_c'] = dfr['len']
                dfr['value_e'] = dfr['mean']
                dfr['value_ob'] = dfr['std']
                dfr['batch_date'] = sql_para['do_day']
                dfr['tar_id'] = tarid
                dfr['update_time'] = 'now()'
                dfr = dfr.drop(['len', 'mean', 'std'], 1).reset_index()
                dw.c_conn(config.MYSQL_BI_RW_ENV)
                pname = sql_para['do_day'][:-1]
                pvalue = 10* (int(pname) + 1)
                # dw.add_partition_gener(sql_para['do_day'], sql_para['do_day'], otable_name, 'list')
                dw.add_partition_gener(pname+'X', pvalue, otable_name)
                print(dw.df_upd_tosql(dfr, batch=1000, table=otable_name))


def doa_bytarid(tarid=10, dp=-1):
    print(__name__, tarid)
    tar_config = dw.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(get_config_bytarid % tarid)
    do_day_tar_config(tar_config, range(dp, 0), tar_config.loc[0, 'spreadtype'])


def cons_makeup():
    [doa_bytarid(i, -999) for i in [110, 120, 130, 140, 150]]


def cons_():
    print(__name__)
    [doa_bytarid(tarid=i) for i in [10, 20, 21, 22, 23, 24, 30, 110, 120, 130, 140, 150]]


if __name__ == "__main__":
    print('hello console %s' % sys.path[0], sys.argv)
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'cons':
            eval(sys.argv[2])
        else:
            cons_()