import sys
import random
import multiprocessing
sys.path.append('../')
sys.path.append('../DBbase')
from db_func import *


## 通过其他油站模拟测试数据：
# test_mer_list = ['']
SQL_crm_latest = """
set @yesterday:=(select max(batch_date) from profile.pr_coupon_user_coupons);
select CRM.uid,gender,member_level_id
  ,last_30day_oil_liter liter30,last_60day_oil_liter liter60,last_90day_oil_cnt cnt90,max_30day_oil_cnt mcnt30
  ,consumer_trends,accum_oil_liter,accum_oil_cnt,first_oil_time,last_oil_time,lost_days,callback_cnt
  ,wcount,realprice_avg,liters_avg,liters_std0,mainstid,mainsta_rate,cdt_avg,cd_avg,dt_avg,dt_std0,paytoc_avg
  ,predict_time,ptype,predict_dt,(UNIX_TIMESTAMP(now())-UNIX_TIMESTAMP(rewei_time))/24/3600 already_lated
  ,UCO.useful have_coupon,UCO.used60,UCO.expired60
from dw.dw_crm_latest_%(mer_describ)s CRM
inner join bimodels.bm_user_clusting_platform UC
on UC.uid = CRM.uid
inner join bimodels.bm_user_predict_ UP
ON UP.uid = CRM.uid
left join 
  (select uid,sum(useful) useful,sum(used60) used60,sum(expired60) expired60 
   from profile.pr_coupon_user_coupons 
   where activity_type in (%(activity_type)s) and batch_date=@yesterday
   group by uid) UCO 
ON UCO.uid = CRM.uid
where %(mer_col)s = %(merid)s 
and CRM.last_90day_oil_cnt > 2
and CRM.prefer_oil_id in (10,11,12,13,23,24,25,36,37,38,39,49,50,51,52,59,60,61,62,63,65,68,69,70,74,78,83,85,86,87,88,90,91,92,93,98,101,102)
limit 100000"""

SQL_level_user_tag = """
set @yesterday_c:=(select max(batch_date) from profile.pr_coupon_user_coupons);
set @yesterday_l:=(select max(batch_date) from profile.pr_level_user_tag);
select LEV.uid,sort,upgrade_condition,score,hard,post,hard_degree,pass_day,month_cycle
  ,UCO.useful have_coupon,UCO.used60,UCO.expired60
  ,last_30day_oil_liter liter30,last_60day_oil_liter liter60,last_90day_oil_cnt cnt90,max_30day_oil_cnt mcnt30
  ,wcount,realprice_avg,liters_avg,liters_std0,mainstid,mainsta_rate,cdt_avg,cd_avg,dt_avg,dt_std0,paytoc_avg
from profile.pr_level_user_tag LEV
left join 
  (select uid,sum(useful) useful,sum(used60) used60,sum(expired60) expired60 
   from profile.pr_coupon_user_coupons 
   where activity_type in (%(activity_type)s) and batch_date=@yesterday_c
   group by uid) UCO 
ON UCO.uid = LEV.uid
left join dw.dw_crm_latest_%(mer_describ)s CRM
on LEV.uid = CRM.uid and CRM.%(mer_col)s = LEV.merchant_id
inner join bimodels.bm_user_clusting_platform UC
on UC.uid = LEV.uid
where LEV.batch_date=@yesterday_l and LEV.merchant_id = %(merid)s and LEV.merchant_type = %(merchant_type)s
and CRM.last_90day_oil_cnt > 2
and CRM.prefer_oil_id in (10,11,12,13,23,24,25,36,37,38,39,49,50,51,52,59,60,61,62,63,65,68,69,70,74,78,83,85,86,87,88,90,91,92,93,98,101,102)
limit 100000"""

SQL_crm_latest_birth = """
set @yesterday_c:=(select max(batch_date) from profile.pr_coupon_user_coupons);
select CRM.uid,CRM.gender,member_level_id
  ,last_30day_oil_liter liter30,last_60day_oil_liter liter60,last_90day_oil_cnt cnt90,max_30day_oil_cnt mcnt30
  ,wcount,realprice_avg,liters_avg,liters_std0,mainstid,mainsta_rate,cdt_avg,cd_avg,dt_avg,dt_std0,paytoc_avg
  ,FROM_UNIXTIME(birthday,'%%Y-%%m-%%d') birthday
  ,FROM_UNIXTIME(birthday,'%%Y') birth_year 
  ,FROM_UNIXTIME(birthday,'%%m') birth_month
  ,FROM_UNIXTIME(birthday,'%%d') birth_day
from dw.dw_crm_latest_%(mer_describ)s CRM
left join bimodels.bm_user_clusting_platform UC
on UC.uid = CRM.uid
# left join ods.ods_wei_users US
# on US.uid = CRM.uid
where %(mer_col)s = %(merid)s and FROM_UNIXTIME(birthday,'%%m%%d') >= DATE_FORMAT('%(begin)s','%%m%%d') and FROM_UNIXTIME(birthday,'%%m%%d') <= DATE_FORMAT('%(end)s','%%m%%d')
and CRM.uid not in (select uid from profile.pr_coupon_user_coupons where batch_date=@yesterday_c and activity_type=%(activity_type)s and (useful+used60+expired60)<1)
and CRM.prefer_oil_id in (10,11,12,13,23,24,25,36,37,38,39,49,50,51,52,59,60,61,62,63,65,68,69,70,74,78,83,85,86,87,88,90,91,92,93,98,101,102)
limit 100000"""

# set @yesterday:=(select max(batch_date) from profile.pr_%(mer_describ)ss_user_dis_);
SQL_merchant_profile_user = """
select 
  tar_id,spr_id,avg(value_c) value_c,avg(value_e) value_e,avg(value_ob) value_ob
from profile.pr_%(mer_describ)ss_user_dis_ where batch_date >= %(3ds_sago)s and mer_id = %(merid)s 
group by tar_id,spr_id """

SQL_merchant_profile_order = """
select 
  tar_id,spr_id,avg(value_c) value_c,avg(value_e) value_e,avg(value_ob) value_ob
from profile.pr_%(mer_describ)ss_order_other_ where batch_date >= %(3ds_sago)s and mer_id = %(merid)s
group by tar_id,spr_id """

# 通过油站(stid)查找 同集团的油站有多少个(siblings)
SQL_stid_siblings = """
SELECT gs1.group_id,gs1.stid,gs2.* FROM ods.ods_wei_group_stations gs1
left join 
  (select group_id group_id2,stid stid2 from ods.ods_wei_group_stations where isvalid = 1) gs2 
on gs2.group_id2=gs1.group_id
where gs1.stid = %s and gs1.isvalid = 1
"""
# 汽油的油号
SQL_onlyoil = """SELECT * FROM ods.`ods_wei_ol_oil` where isvalid = 1 and oil_name like "%汽油%" ;"""

MTKR = {'0': {'merchant_type': 0, 'mer_describ': 'platform', 'mer_col': 'mer_id', 'merid': 0},
        '1': {'merchant_type': 1, 'mer_describ': 'station', 'mer_col': 'stid', 'merid': 0},
        '2': {'merchant_type': 2, 'mer_describ': 'group', 'mer_col': 'group_id', 'merid': 0}
        }
SEND_HOUR = [8, 9, 11.6, 12.1, 15, 17.5, 18, 19, 21, 22]
BIRTH_coupon_price = [5, 6.66, 8.88, 10, 15, 16.66, 18.88, 20]
ALL_DFR_LIST = ['uid', 'time_limit', 'time_limit_type', 'cill', 'coupon_price', 'sendtoc', 'sendtimestamp', 'rank_score', 'coupon_type', 'coupon_tag']
ALL_DFRbirth_LIST = ['uid', 'gender', 'time_limit', 'time_limit_type', 'cill', 'coupon_price', 'sendday',  'sendtoc', 'sendtimestamp', 'age', 'coupon_type', 'coupon_tag']
GI_ = {'N1': 20, 'N2': 14, 'N3': 10, 'R1': 0.8, 'R2': 0.4, 'R3': 0.4, 'R4': 0.01, 'R5': 0.1, 'R6': 0.1, 'R7': 0.1, 'R8': 0.5, 'R9': -0.4, 'R10': 0, 'N4': 2, 'R11': 0.6,
       'R99': 0.3, 'R100': 0.5}


def onlyoil():
    dw = my_(config.MYSQL_BI_RW_ENV)
    df = dw.to_dataframe(SQL_onlyoil)
    return ','.join(list(df['oil_id'].map(str)))


def str_takeout_bit(s, gap, num):
    dmakeup = gap*num - s.__len__()
    if dmakeup > 0:
        s = '0'*dmakeup + s
    s = s[-6:]
    return [s[i*gap:i*gap+gap] for i in range(num)]


def get_latebound(dt, sifte_e, tp='callb'):    # 获取召回券/客单价券须发的迟到区间
    if tp == 'callb':
        bound_a = dt * (-sifte_e + GI_['R1'])
        bound_b = (dt + GI_['N1']) * (sifte_e + 1) ** 4
    else:
        bound_a = dt * (-0.5*sifte_e + GI_['R9'])
        bound_b = dt * (GI_['R10'] + 0.5*sifte_e) + GI_['N4']
    return bound_a, bound_b


def paytoc2sendtoc(dfl):
    dfl = dfl.apply(int)
    for i in SEND_HOUR[:-1]:
        ind = dfl - i
        dfl.loc[(ind > -1) & (ind < 2)] = i
    return dfl


def sifte_callback(df, degree):

    sifte_e = (degree - 10) / 90  # 方向度/权重[0,1]:  由力度[10,100]归一化到01区间 目前的力度值在10-100内取整5,不会超过此取值范围。
    dfr = df.query('predict_dt>0&uid>0').copy()
    # print(len(df),len(dfr))
    for x in ['have_coupon', 'used60', 'expired60']:
        dfr[x].fillna(0, inplace=True)
    dfr.fillna(dfr.mean(), inplace=True)
    dfr.fillna(0, inplace=True)
    dfr['predict_dt'] += (4 - dfr['predict_dt']).clip(0, 4) * 0.66   # 召回的低间隔控制:dt本来就很低的会稍微再等等
    # dfr['already_lated'] = (datetime.datetime.now() - dfr['rewei_time']).apply(lambda xx: xx.total_seconds() / 24 / 3600).round(2)
    bound_a, bound_b = get_latebound(dfr['predict_dt'], sifte_e)
    # bound_a = dfr['predict_dt'] * (-sifte_e + GI_['R1'])
    # bound_b = (dfr['predict_dt'] + GI_['N1']) * (sifte_e + 1)**4
    dfr = dfr[(dfr['already_lated'] > bound_a) & (dfr['already_lated'] < bound_b)]
    dfr['time_limit'] = (0.7*dfr['dt_avg'] + 0.7*dfr['predict_dt'] + 0.5).clip(2, GI_['N2']+GI_['N3']*sifte_e).round()
    dfr.insert(0, 'time_limit_type', 1)
    dfr.insert(0, 'halfheart', 0)
    dfr.loc[dfr['mainsta_rate'] < 0.4, 'halfheart'] = 1
    dfr['sensit'] = (GI_['R2'] * np.log(1 + dfr['cd_avg']) + GI_['R3'] * dfr['cdt_avg']).clip(0, 1).round(2)
    dfr['cill'] = (dfr['realprice_avg'] * (1+0.1*np.log10(1+dfr['sensit']))).round()
    dfr['coupon_price_percent'] = (GI_['R4']*(2+3*sifte_e-2*dfr['sensit']) + GI_['R5']*np.log10(1.4+0.7*dfr['expired60']+dfr['halfheart'])).clip(0.009, 0.16).round(6)
    dfr['coupon_price'] = (dfr['coupon_price_percent']*dfr['cill']).round(1).clip(1, 29)
    dfr.query('cill>17&cill<9999', inplace=True)  # 这一波筛选必不可少
    dfr['sendtoc'] = paytoc2sendtoc(dfr['paytoc_avg'])
    dfr['sendtimestamp'] = dfr['sendtoc'].apply(lambda xx: time_replace({'hour': int(xx), 'minute': int((xx-int(xx))*60), 'second': 0}))
    tmpx = dfr['already_lated'] - dfr['predict_dt']
    dfr['rank_score'] = (((abs(tmpx) + 1)*(np.e**(-tmpx/np.e)+1))**-1 + GI_['R6']*np.log10(dfr['wcount']+dfr['cnt90']+3*dfr['mcnt30']) + GI_['R8']*dfr['sensit'] - (GI_['R7']+1-sifte_e)*dfr['have_coupon']).round(3)
    dfr.query('rank_score>0', inplace=True)  # 2.
    dfr.insert(0, 'coupon_tag', '召回(%s)' % degree)
    dfr.insert(0, 'coupon_type', 3)
    dfr = dfr.sort_values(by='rank_score', ascending=False).loc[:, ALL_DFR_LIST]
    return dfr.iloc[: int((GI_['R99']+GI_['R100']*sifte_e)*len(dfr)) + 1]


def sifte_stickhold(df, degree):

    sifte_e = (degree - 10) / 90
    df.query('pass_day>0&month_cycle>0&score>=0&upgrade_condition>0', inplace=True)
    df['during_perc'] = (df['pass_day']/df['month_cycle']) * (0.8+0.5*sifte_e)
    df['com_perc'] = df['score'] / df['upgrade_condition']
    dfr = df.query('com_perc<during_perc').copy()
    for x in ['have_coupon', 'used60', 'expired60']:
        dfr[x].fillna(0, inplace=True)
    dfr.fillna(dfr.mean(), inplace=True)
    dfr.fillna(0, inplace=True)
    # dfr['time_limit'] = (2*dfr['dt_avg']).clip(2, GI_['N2']+GI_['N3']*sifte_e).round()
    dfr['time_limit'] = 15 if day_forpast(0, ss='%d') < '16' else 8   # 将上面改成按时间返回15天或8天
    dfr.insert(0, 'time_limit_type', 1)
    dfr.insert(0, 'halfheart', 0)
    dfr.loc[dfr['mainsta_rate'] < 0.4, 'halfheart'] = 1
    dfr['sensit'] = (GI_['R2'] * np.log(1 + dfr['cd_avg']) + GI_['R3'] * dfr['cdt_avg']).clip(0, 1).round(2)
    dfr['cill'] = (dfr['realprice_avg'] * (1 + 0.1 * np.log10(1 + dfr['sensit']))).round()
    dfr['coupon_price_percent'] = (GI_['R4']*(2+3*sifte_e-2*dfr['sensit']) + GI_['R5']*np.log10(1.4+0.6*dfr['expired60']+dfr['halfheart'])).clip(0.009, 0.16).round(6)
    dfr['coupon_price'] = (dfr['coupon_price_percent']*dfr['cill']).round(1).clip(1, 29)
    dfr.query('cill>17&cill<9999', inplace=True)  # 这一波筛选必不可少
    dfr['sendtoc'] = paytoc2sendtoc(dfr['paytoc_avg'])
    dfr['sendtimestamp'] = dfr['sendtoc'].apply(lambda xx: time_replace({'hour': int(xx), 'minute': int((xx - int(xx)) * 60), 'second': 0}))
    dfr['rank_score'] = 0.1*(1+dfr['dt_avg'])**-1 + GI_['R6']*np.log10(dfr['wcount']+dfr['cnt90']+3*dfr['mcnt30']) + 0.5*dfr['hard_degree'] + 0.2*(dfr['during_perc'] - dfr['com_perc']) + 0.2*dfr['sort'] - (GI_['R7']+1-sifte_e)*dfr['have_coupon']
    dfr.query('rank_score>0', inplace=True)  # 2.
    dfr.insert(0, 'coupon_tag', '保级(%s)' % degree)
    dfr.insert(0, 'coupon_type', 2)
    dfr = dfr.sort_values(by='rank_score', ascending=False).loc[:, ALL_DFR_LIST]
    return dfr.iloc[: int((GI_['R99']+GI_['R100']*sifte_e)*len(dfr)) + 1]


def sifte_singleprice(df, degree):

    sifte_e = (degree - 10) / 90
    dfr = df.query('predict_dt>0&uid>0').copy()
    for x in ['have_coupon', 'used60', 'expired60']:
        dfr[x].fillna(0, inplace=True)
    dfr.fillna(dfr.mean(), inplace=True)
    dfr.fillna(0, inplace=True)
    # dfr['already_lated'] = (datetime.datetime.now() - dfr['rewei_time']).apply(lambda xx: xx.total_seconds() / 24 / 3600).round(2)
    bound_a, bound_b = get_latebound(dfr['predict_dt'], sifte_e, 'singlep')
    dfr = dfr[(dfr['already_lated'] > bound_a) & (dfr['already_lated'] < bound_b)]
    # dfr['time_limit'] = (.9*dfr['dt_avg'] + .9*dfr['predict_dt'] + 0.5).clip(3, 1.2*GI_['N2'] + GI_['N3'] * sifte_e).round()
    dfr.insert(0, 'time_limit', (.9*dfr['dt_avg'] + .9*dfr['predict_dt'] + 0.5).clip(3, 1.2*GI_['N2'] + GI_['N3']*sifte_e).round())
    dfr.insert(0, 'time_limit_type', 1)
    dfr['sensit'] = (GI_['R2'] * np.log(1 + dfr['cd_avg']) + GI_['R3'] * dfr['cdt_avg']).clip(0, 1).round(2)
    dfr['std_lu'] = np.log10(dfr['liters_std0'] + 1) / np.log10(dfr['liters_std0'].max())    # 升数标准差取log10并归一化
    dfr['cill'] = (dfr['realprice_avg'] * (1 + 0.1 * np.log10(1 + dfr['sensit']) + GI_['R11']*dfr['std_lu'])).round()
    dfr['coupon_price_percent'] = (GI_['R4']*(2+3*sifte_e-2*dfr['sensit']) + GI_['R5']*np.log10(1.4+0.7*dfr['expired60']+.4)).clip(0.009, 0.16).round(6)
    dfr['coupon_price'] = (dfr['coupon_price_percent']*dfr['cill']).round(1).clip(1, 29)
    dfr.query('cill>19&cill<9999', inplace=True)  # 这一波筛选必不可少
    dfr['sendtoc'] = paytoc2sendtoc(dfr['paytoc_avg'])
    dfr['sendtimestamp'] = dfr['sendtoc'].apply(lambda xx: time_replace({'hour': int(xx), 'minute': int((xx - int(xx)) * 60), 'second': 0}))
    dfr['rank_score'] = ((abs(dfr['already_lated'])+1)**-1 + GI_['R6']*np.log10(dfr['wcount'] + dfr['cnt90'] + 3*dfr['mcnt30']) + GI_['R8']*dfr['sensit'] - (GI_['R7']+1-sifte_e)*dfr['have_coupon']).round(3)
    dfr.query('rank_score>0', inplace=True)  # 2.
    dfr.insert(0, 'coupon_tag', '客单价(%s)' % degree)
    dfr.insert(0, 'coupon_type', 1)
    dfr = dfr.sort_values(by='rank_score', ascending=False).loc[:, ALL_DFR_LIST]
    return dfr.iloc[: int((GI_['R99']-0.15+GI_['R100']*sifte_e)*len(dfr)) + 1]


def siblings_num_is_1(merchant_id, merchant_type):
    # 单站只有一个集团的，请求转化为对应集团的请求
    dw = my_(config.MYSQL_BI_RW_ENV)
    if merchant_type == '1':
        siblings = dw.to_dataframe(SQL_stid_siblings % merchant_id)
        if len(siblings) == 1:
            merchant_id = '%s' % siblings.group_id[0]
            merchant_type = '2'
    return merchant_id, merchant_type


def add_smartcoupon_re(merchant_id, merchant_type, prefer_gcode, limitx, args, dfr):
    dw = my_(config.MYSQL_BI_RW_ENV)
    task_code = ("'%s'" % args.pop('send_code')) if 'send_code' in args else ''
    data = {'para_merchant_id': merchant_id,
            'para_merchant_type': merchant_type,
            'para_prefer_gcode': "'%s'" % prefer_gcode,
            'para_limitx': limitx,
            'obligate_args': "'" + '&'.join(['%s=%s' % (v, k) for v, k in args.items()]) + "'",
            'update_time': 'now()',
            'record_code': "'%s-%s-%s-%s'" % (merchant_type, merchant_id, prefer_gcode, day_forpast(ss='%Y%m%d%H%M'))
            'send_code': task_code}
    dw.di_upd_tosql(data, 'bimodels.bm_nm_smartcoupon_apirecord')

    dfr.insert(0, 'apirecord_code', data['record_code'])
    dfr.insert(0, 'update_time', 'now()')
    dfr['coupon_tag'] = dfr['coupon_tag'].map(lambda x: "'%s'" % x)
    dw.df_upd_tosql(dfr, 1000, 'bimodels.bm_nm_smartcoupon_abtest_record')


def geti_merchant_coupon(merchant_id, merchant_type, prefer_gcode=1, force_gcode=False, limitx=-1, **args):
    # prefer_gcode 6位16进制, 从高到低每两位分别代表3个目标的程度(客单价、粘性、召回)
    if type(prefer_gcode) is int:
        prefer_gcode = hex(prefer_gcode)[2:]
    merchant_id, merchant_type = siblings_num_is_1(merchant_id, merchant_type)
    degrees = str_takeout_bit(prefer_gcode, 2, 3)
    limitx = int(limitx)
    limitx = 200000 if limitx < 1 else limitx
    littletimer = Timer_(1)

    para = MTKR[merchant_type].copy()  # copy可以消除高并发时会产生的隐患，如果没有并发测试的话，还是copy了比较靠谱
    para.update({'merid': merchant_id, 'yesterday': day_forpast(d=-1)})

    dfr = {'single_price': pd.DataFrame([]),
           'stick_hold': pd.DataFrame([]),
           'call_back': pd.DataFrame([])}
    df_crm = pd.DataFrame([])
    df_level = pd.DataFrame([])

    dw = my_(config.MYSQL_BI_RW_ENV)
    # single_price 提升客单价
    singlep_degree = int(degrees[0], 16)
    if singlep_degree > 9:
        para.update({'activity_type': '7,8,12,14'})
        df_crm = df_crm if len(df_crm) else dw.to_dataframe(SQL_crm_latest % para)
        littletimer.toc(True)
        dfr['single_price'] = sifte_singleprice(df_crm, singlep_degree).iloc[:limitx]

    # stick_hold 保持粘性
    stickh_degree = int(degrees[1], 16)
    if stickh_degree > 9:
        para.update({'activity_type': '13'})
        df_level = df_level if len(df_level) else dw.to_dataframe(SQL_level_user_tag % para)
        littletimer.toc(True)
        dfr['stick_hold'] = sifte_stickhold(df_level, stickh_degree).iloc[:limitx]

    # call_back 召回
    callb_degree = int(degrees[2], 16)
    if callb_degree > 9:
        para.update({'activity_type': '7,8,12,14'})
        df_crm = df_crm if len(df_crm) else dw.to_dataframe(SQL_crm_latest % para)
        littletimer.toc(True)
        dfr['call_back'] = sifte_callback(df_crm, callb_degree).iloc[:limitx]

    # # if merchant_type == 1 and merchant_id in ['171073']:  # 钓鱼岛油站   --测试期间全是测试id--
    # for cla in ['single_price','stick_hold','call_back']:
    #     if len(dfr[cla]):
    #         dfr[cla]['uid'] = dfr[cla]['uid'].apply(lambda x: random.choice([727823, 1140411, 518732, 1112334, 2289583]))

    littletimer.toc()
    dfr_len = {v: len(k) for v, k in dfr.items()}
    dfr_all = pd.DataFrame([])
    for v, k in dfr_len.items():
        if k:
            dfr_all = dfr_all.append(dfr[v], ignore_index=True)
    # -------------------ABtest功能筛选器：筛选对照组不发券，并记录AB标记；----------------------------------------------  筛选器在~deve_mode时有效
    if len(dfr_all) and int(args['deve_mode']) < 1:  # 后面希望借用deve_mode调节A组比例的话（这样理解，表示A组的比例，1自然就是不用筛选器咯） if int(args['deve_mode']) < 1:
        dfr_all['ab_type'] = dfr_all['uid'].map(lambda x: 0 if random.random() < 0.8 else 1)
        multiprocessing.Process(target=add_smartcoupon_re,
                                args=(merchant_id, merchant_type, prefer_gcode, limitx, args, dfr_all)).start()
        dfr_all.query('ab_type<1', inplace=True)
        dfr_all.drop(['ab_type'], 1, inplace=True)
    # -------------------ABtest功能筛选器：筛选对照组不发券，并记录AB标记；----------------------------------------------
    if len(dfr_all):
        return_dict = {'status': 0, 'info': '请求成功',
                       'datalength': len(dfr_all),
                       'couponnum': dfr_len,
                       'timetaken': littletimer.tictoc,
                       'columns': dfr_all.columns.tolist(),
                       'data': np.array(dfr_all).tolist() if int(args['deve_mode']) else dfr_all.to_json(orient='records')}
    else:    # 钓鱼岛油站 ['171073']   --该分支表示：测试期间请求钓鱼岛无数据返回时借用其他油站数据--
        if merchant_type == '1' and merchant_id in []:
            rent_merid = '119296'
            return_dict = geti_merchant_coupon(rent_merid, '1', prefer_gcode, force_gcode, limitx=10, **args)   # 但通过迭代实现 有风险
            return_dict.update({'测试借用': '%s => %s' % (merchant_id, rent_merid)})
        else:
            return_dict = {'status': 0, 'info': '请求成功', 'datalength': 0,
                           'timetaken': littletimer.tictoc}
    return return_dict


def birth2stamp(x):
    re_dict = {'month': int(x['birth_month']), 'day': int(x['birth_day']), 'hour': int(x['sendtoc']), 'minute': int((x['sendtoc']-int(x['sendtoc']))*60), 'second': 0}
    return time_replace(re_dict)


def geti_merchant_coupon_birth(merchant_id, merchant_type, birth_begin=None, birth_end=None, **args):

    if type(birth_begin) is not str or len(birth_begin) < 8:
        birth_begin = day_forpast(d=0, ss="%Y-%m-%d")
    if type(birth_end) is not str or birth_end < birth_begin:
        birth_end = birth_begin

    dw = my_(config.MYSQL_BI_RW_ENV)
    para = MTKR[merchant_type].copy()
    para.update({'merid': merchant_id, 'begin': birth_begin, 'end': birth_end})
    para.update({'activity_type': '15'})
    df = dw.to_dataframe(SQL_crm_latest_birth % para)
    if len(df):
        df['realprice_avg'] = df.realprice_avg.fillna(120)   # 生日券是没妈的孩子,资料太少导致很多null需要处理
        df.paytoc_avg.fillna(9, inplace=True)
        df = df.fillna(df.mean())
        df = df.fillna(0)    # 因为人数太少 上一步依然不能保证去掉null

        df['coupon_price'] = (df['realprice_avg'] * 0.04 + df.liter30/(df.mcnt30+0.01) * 0.26).clip(2, 25).round(2)
        for i in BIRTH_coupon_price:
            ind = df['coupon_price'] - i
            df.loc[(ind > -1) & (ind < 2), 'coupon_price'] = i
        df['cill'] = (df['coupon_price'] + 0.01).round(2)
        df['sendday'] = df['birthday'].apply(lambda x: re.sub('\d{4}', day_forpast(ss="%Y"), x))
        df['sendtoc'] = paytoc2sendtoc(df['paytoc_avg'])
        df['sendtimestamp'] = df.apply(birth2stamp, axis=1)
        df['age'] = df['birth_year'].apply(lambda x: int(day_forpast(ss="%Y")) - int(x))
        df['time_limit'] = 14
        df['time_limit_type'] = 1
        df['coupon_type'] = 4
        df['coupon_tag'] = '生日礼券'
        dfr = df.loc[:, ALL_DFRbirth_LIST].fillna(10)

        return_dict = {'status': 0, 'info': '请求成功',
                       'datalength': len(dfr),
                       'columns': dfr.columns.tolist(),
                       'data': np.array(dfr).tolist() if int(args['deve_mode']) else dfr.to_json(orient='records')}
    else:
        if merchant_type == '1' and merchant_id in []:  # 钓鱼岛油站  ['171073']   --测试期间请求钓鱼岛无数据返回时借用其他油站数据--
            rent_merid = 176558
            return_dict = geti_merchant_coupon_birth(rent_merid, '1', birth_begin, birth_end, **args)   # 但通过迭代实现 有风险
            return_dict.update({'测试借用': '%s => %s' % (merchant_id, rent_merid)})
        else:
            return_dict = {'status': 0, 'info': '请求成功', 'datalength': 0}
    return return_dict

# simple_redis_var
simpleredis_glo = {'days': [day_forpast(d=-1)], }
simpleredis_dfu_all = {day_forpast(d=-1): {}}
simpleredis_dfo_all = {day_forpast(d=-1): {}}
simpleredis_dfu = {day_forpast(d=-1): {}}
simpleredis_dfo = {day_forpast(d=-1): {}}
listsimpleredis_df = [simpleredis_dfu_all, simpleredis_dfo_all, simpleredis_dfu, simpleredis_dfo]


# 内存分发和数据库IO
def redis_basicio(redis_var, mer_typeid, sqls):  # 简单redis功能IO 提升budget和recommende接口速度
    yesterday = day_forpast(d=-1)
    if simpleredis_glo['days'][-1] < yesterday:
        simpleredis_glo['days'] += [yesterday]
        if len(simpleredis_glo['days']) > 7:
            leftout_day = simpleredis_glo['days'].pop(0)
            [sr.pop(leftout_day) if leftout_day in sr else 0 for sr in listsimpleredis_df]

    if yesterday not in redis_var:
        redis_var[yesterday] = {}
    if mer_typeid in redis_var[yesterday]:
        dfr = redis_var[yesterday][mer_typeid]
    else:
        dw = my_(config.MYSQL_BI_RW_ENV)
        dfr = dw.to_dataframe(sqls)
        redis_var[yesterday][mer_typeid] = dfr
        dw.quit()
    return dfr


# 监控内存分发状态
def show_sredis_status(show_num, val_name='listsimpleredis_df'):
    res = ''
    if show_num == '1':
        res = simpleredis_glo
    elif show_num == '2':
        filepathname = '%s/%s_%s.pyv' % (PRO_PATH + '/.logs/api_sredis_value', val_name, day_forpast(0))
        v_holder(eval(val_name)).store(filepathname)
        res = '成功存储到(%s),请让安东尼用ipython查看' % filepathname

    return_dict = {'status': 0,
                   'info': '请求成功',
                   'datalength': len(res),
                   'data': res}
    return return_dict


# 获取油站画像
def merchant_profile(merchant_id, merchant_type):
    para = MTKR[merchant_type].copy()
    para.update({'merid': merchant_id, '3ds_sago': day_forpast(d=-3)})
    para0 = MTKR['0'].copy()
    para0.update({'3ds_sago': day_forpast(d=-3)})
    mer_typeid = '%s:%s' % (merchant_type, merchant_id)

    dfu_all = redis_basicio(simpleredis_dfu_all, mer_typeid, SQL_merchant_profile_user % para0)
    dfu = redis_basicio(simpleredis_dfu, mer_typeid, SQL_merchant_profile_user % para)
    dfo_all = redis_basicio(simpleredis_dfo_all, mer_typeid, SQL_merchant_profile_order % para0)
    dfo = redis_basicio(simpleredis_dfo, mer_typeid, SQL_merchant_profile_order % para)
    # 关联平台platform取,为后面保持格式一致（主要是会有些tar_id下的spr_id可能部分油站不一定有）
    dfu_m = pd.merge(dfu_all, dfu, how='left', on=['tar_id', 'spr_id'], suffixes=['_all', '']).fillna(0)
    dfo_m = pd.merge(dfo_all, dfo, how='left', on=['tar_id', 'spr_id'], suffixes=['_all', '']).fillna(0)
    return dfu_m, dfo_m


# 流失区间估计和人数占比估计
def range_rate(lost_ab):
    bound_list = [2, 7, 15, 32, 66, 129]
    # bound_arr = np.array(bound_list)
    # delta = bound_arr - lost_ab
    # ind = len(delta[delta < 0])
    ind = x_inlist_index(lost_ab, [2, 7, 15, 32, 66, 129]) + 1
    if ind == 6:
        return ind, 1 - ((629-lost_ab)/(629-129))**2
    elif ind == 0:
        return ind, 1
    else:
        return ind, (lost_ab - bound_list[ind-1])/(bound_list[ind] - bound_list[ind-1])


def get_people_by_interval(bound_a, bound_b, lost_dist):  # 通过区间估计触达人数

    ind_a, r_a = range_rate(bound_a)
    ind_b, r_b = range_rate(bound_b)
    ss = 0
    if ind_b - ind_a > 1:
        ss = lost_dist.iloc[ind_a + 1:ind_b].sum() + lost_dist.iloc[ind_a] * (1 - r_a) + lost_dist.iloc[ind_b] * r_b
    elif ind_b - ind_a > 0:
        ss = lost_dist.iloc[ind_a] * (1 - r_a) + lost_dist.iloc[ind_b] * r_b
    elif ind_b == ind_a:
        ss = lost_dist.iloc[ind_b] * (r_b - r_a)
    return ss


# 获取预算
def geti_merchant_budget(merchant_id, merchant_type, prefer_gcode, during_days='30', **args):
    # prefer_gcode 6位16进制, 从高到低每两位分别代表3个目标的程度(客单价、粘性、召回)
    if type(during_days) is str and during_days >= '0':
        during_days = int(during_days)
    elif type(during_days) is not int:
        during_days = 0
    merchant_id, merchant_type = siblings_num_is_1(merchant_id, merchant_type)
    res = {}
    dfu_m, dfo_m = merchant_profile(merchant_id, merchant_type)
    if len(dfu_m) == 0 or len(dfo_m) == 0:
        return {'extra_budget_info': 'maybe sth. wrong with merchant_profile'}
    if type(prefer_gcode) is int:
        prefer_gcode = hex(prefer_gcode)[2:]
    degrees = str_takeout_bit(prefer_gcode, 2, 3)
    ss, sifte_e, buffer = 0, 0, 1
    # call_back 召回
    callb_degree = int(degrees[2], 16)
    if callb_degree > 9:
        sifte_e = (callb_degree - 10) / 90
        lost_dist = dfu_m.query('tar_id == 30').loc[:, 'value_c']
        avg_dt = 12                                     # 平均间隔  后面修改
        bound_a, bound_b = get_latebound(avg_dt, sifte_e)
        ss = get_people_by_interval(bound_a+avg_dt, bound_b+avg_dt, lost_dist)

    # stick_hold 保持粘性
    stickh_degree = int(degrees[1], 16)
    if stickh_degree > 9:
        sifte_e = (stickh_degree - 10) / 90
        lev_dist = dfu_m.query('tar_id == 40').loc[:, 'value_c']
        ss = lev_dist.sum()*(0.85+0.35*sifte_e)*0.5   # 当前全平台水平的估计波动范围(后可能需要改)

    # single_price 提升客单价
    singlep_degree = int(degrees[0], 16)
    if singlep_degree > 9:
        buffer = 1.1
        sifte_e = (singlep_degree - 10) / 90
        lost_dist = dfu_m.query('tar_id == 30').loc[:, 'value_c']
        # print(lost_dist)
        avg_dt = 12  # 平均间隔  后面修改
        bound_a, bound_b = get_latebound(avg_dt, sifte_e, 'singlep')
        ss = get_people_by_interval(bound_a+avg_dt, bound_b+avg_dt, lost_dist)
        # res = {'customer_a': round(ss*0.75-10), 'customer_b': round(ss*1.25+20), 'pmoney_a': ss*0.06*160, 'pmoney_b': ss*0.15*180}
    # 计算按天数衰弱的ss
    ss_eday = int(0.66*ss*(1-2**-(during_days/6+.3))*(0.66+0.14*np.log(during_days+1)+0.01*during_days) + 2)
    if ss_eday > 0:
        customer_a = round(ss_eday*0.8-7) if ss_eday > 10 else round(ss_eday*0.4)
        customer_b = round(ss_eday*(1.25-0.2*sifte_e)+10)
        pmonet_buf = buffer*(6+4*sifte_e)
        pmoney_a = customer_a*pmonet_buf*0.98-10
        pmoney_b = customer_b*pmonet_buf*1.04+20
        res.update({'customer_a': customer_a, 'customer_b': customer_b, 'pmoney_a': pmoney_a, 'pmoney_b': pmoney_b})
    else:
        res.update({'customer_a': 0, 'customer_b': 0, 'pmoney_a': 0, 'pmoney_b': 0,
                    'extra_budget_info': 'maybe sth. wrong with this merchant'})
    return_dict = {'status': 0, 'info': '请求成功',
                   'datalength': len(res),
                   'data': res}
    return return_dict


# 力度值划归到10到100 每5一个档 后面产品细化改这里就好
def changeto_weight(num):
    if type(num) == list:
        num = np.array(num)
    num5 = (num // 5 * 5).clip(10, 100)
    return num5.tolist()


def geti_merchant_recommende(merchant_id, merchant_type, prefer_gcode=0, need_budget=False, **args):
    # prefer_gcode 用到各自的预留位01
    merchant_id, merchant_type = siblings_num_is_1(merchant_id, merchant_type)
    res = {}
    # print(day_forpast(ss='Timestamp'))
    dfu_m, dfo_m = merchant_profile(merchant_id, merchant_type)

    if len(dfu_m) == 0 or len(dfo_m) == 0:
        return {'extra_budget_info': 'maybe sth. wrong with merchant_profile'}
    if type(prefer_gcode) is int:
        prefer_gcode = hex(prefer_gcode)[2:]
    degrees = str_takeout_bit(prefer_gcode, 2, 3)
    ori = 40

    callb_degree = int(degrees[2], 16)
    if callb_degree == 1:
        lost_dist = dfu_m.query('tar_id == 30').loc[:, ['value_c_all', 'value_c']]
        if lost_dist.value_c.sum():
            incline = np.array(lost_dist.value_c/lost_dist.value_c.sum()) / np.array(lost_dist.value_c_all/lost_dist.value_c_all.sum()) + 0.01
            mn = 4  # measure number

            recommende = changeto_weight(ori * (incline[-mn:].mean()/incline[:mn].mean()))
        else:
            recommende = ori
            res.update({'extra_recommend_info': 'maybe this merchant can not do this'})
        res.update({'recommende': recommende, 'prefer_gcode_toget': '0000%s' % hex(int(recommende))[2:]})

    # stick_hold 保持粘性
    stickh_degree = int(degrees[1], 16)
    if stickh_degree == 1:
        lost_dist = dfu_m.query('tar_id == 30').loc[:, ['value_c_all', 'value_c']]
        lev_dist = dfu_m.query('tar_id == 40').loc[:, ['value_c_all', 'value_c']]
        if lost_dist.value_c.sum() and lev_dist.value_c.sum():  # 补充需要等级分布有值
            incline = np.array(lost_dist.value_c/lost_dist.value_c.sum()) / np.array(lost_dist.value_c_all/lost_dist.value_c_all.sum()) + 0.01
            add_inlice = np.array(lev_dist.value_c/lev_dist.value_c.sum()) / np.array(lev_dist.value_c_all/lev_dist.value_c_all.sum()) + 0.01
            mn = 4  # measure number

            recommende = changeto_weight(ori * (incline[-mn:].mean() / incline[:mn].mean()) * add_inlice[0])
        else:
            recommende = ori
            res.update({'extra_recommend_info': 'maybe this merchant can not do stick_hold'})
        res.update({'recommende': recommende, 'prefer_gcode_toget': '00%s00' % hex(int(recommende))[2:]})

    # single_price 提升客单价
    singlep_degree = int(degrees[0], 16)
    if singlep_degree == 1:
        lost_dist = dfu_m.query('tar_id == 30').loc[:, ['value_c_all', 'value_c']]
        sprice_dist = dfo_m.query('tar_id == 110').loc[:, ['value_c_all', 'value_c']]
        if lost_dist.value_c.sum() and sprice_dist.value_c.sum():
            incline_lost = np.array(lost_dist.value_c/lost_dist.value_c.sum()) / np.array(lost_dist.value_c_all/lost_dist.value_c_all.sum()) + 0.01
            incline_sprice = np.array(sprice_dist.value_c/sprice_dist.value_c.sum()) / np.array(sprice_dist.value_c_all/sprice_dist.value_c_all.sum()) + 0.01
            mn = 3  # measure number

            recommende = changeto_weight(ori * (incline_lost[-mn:].mean()/incline_lost[:mn].mean())**.5 * (incline_sprice[:mn].mean()/incline_sprice[-mn:].mean()))
        else:
            recommende = ori
            res.update({'extra_recommend_info': 'maybe this merchant can not do singlep_degree'})
        res.update({'recommende': recommende, 'prefer_gcode_toget': '%s0000' % hex(int(recommende))[2:]})
    # 如果需要预计 一般配置页面初始化的时候会需要推荐力度和该推荐力度下的预计
    if need_budget and 'prefer_gcode_toget' in res:
        budget = geti_merchant_budget(merchant_id, merchant_type, res['prefer_gcode_toget'], '30')
        res.update(budget['data'])

    return_dict = {'status': 0,
                   'info': '请求成功',
                   'datalength': len(res),
                   'data': res}
    return return_dict
