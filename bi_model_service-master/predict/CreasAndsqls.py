
bm_clusting_centersinfo_ = '''
create table IF NOT EXISTS bimodels.bm_clusting_centersinfo (
clustingid int(4) DEFAULT NULL COMMENT '类别id',
ctype int(4) DEFAULT 0 COMMENT '中心类型: 0-platform',
uid double(20,6) DEFAULT NULL COMMENT '中心值：用户id',
wcount double(20,6) DEFAULT NULL COMMENT '中心值：喂车次数',
realprice_avg double(20,6) DEFAULT NULL COMMENT '中心值：应付金额均值',
realprice_std0 double(20,6) DEFAULT NULL COMMENT '中心值：应付金额标准差',
liters_avg double(20,6) DEFAULT NULL COMMENT '中心值：加油升数均值',
liters_std0 double(20,6) DEFAULT NULL COMMENT '中心值：加油升数标准差',
mainstid double(20,6) DEFAULT NULL COMMENT '中心值：主油站id',
mainsta_rate double(20,6) DEFAULT NULL COMMENT '中心值：主油站频率',
cc_avg double(20,6) DEFAULT NULL COMMENT '中心值：积分使用/喂车次数',
cdt_avg double(20,6) DEFAULT NULL COMMENT '中心值：代金券使用次数/喂车次数',
cd_avg double(20,6) DEFAULT NULL COMMENT '中心值：代金券使用金额/喂车次数',
dt_avg double(20,6) DEFAULT NULL COMMENT '中心值：间隔天数均值',
dt_std0 double(20,6) DEFAULT NULL COMMENT '中心值：间隔天数标准差',
dt_max double(20,6) DEFAULT NULL COMMENT '中心值：最大间隔天数',
paytoc_avg double(20,6) DEFAULT NULL COMMENT '中心值：平均付款时刻',
paytoc_std0 double(20,6) DEFAULT NULL COMMENT '中心值：付款时刻方差',
weekday_avg double(20,6) DEFAULT NULL COMMENT '中心值：',
weekday_std0 double(20,6) DEFAULT NULL COMMENT '中心值：',
monthday_avg double(20,6) DEFAULT NULL COMMENT '中心值：',
monthday_std0 double(20,6) DEFAULT NULL COMMENT '中心值：',
dto_max double(20,6) DEFAULT NULL COMMENT '(整体聚类)除异常后的最大间隔天数',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '',
PRIMARY KEY `CID` (`clustingid`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行为clusting类型(及和类型中心)表';
'''
bm_user_clusting_platform_ = '''
create table IF NOT EXISTS bimodels.bm_user_clusting_platform (
uid int(11) DEFAULT NULL COMMENT '用户id',
wcount int(11) DEFAULT NULL COMMENT '喂车次数',
realprice_avg double(20,6) DEFAULT NULL COMMENT '应付金额均值',
realprice_std0 double(20,6) DEFAULT NULL COMMENT '应付金额标准差',
liters_avg double(20,6) DEFAULT NULL COMMENT '加油升数均值',
liters_std0 double(20,6) DEFAULT NULL COMMENT '加油升数标准差',
mainstid int(11) DEFAULT NULL COMMENT '主油站id',
mainsta_rate double(20,6) DEFAULT NULL COMMENT '主油站频率',
cc_avg double(20,6) DEFAULT NULL COMMENT '积分使用/喂车次数',
cdt_avg double(20,6) DEFAULT NULL COMMENT '代金券使用次数/喂车次数',
cd_avg double(20,6) DEFAULT NULL COMMENT '代金券使用金额/喂车次数',
dt_avg double(20,6) DEFAULT NULL COMMENT '间隔天数均值',
dt_std0 double(20,6) DEFAULT NULL COMMENT '间隔天数标准差',
dt_max double(20,6) DEFAULT NULL COMMENT '最大间隔天数',
paytoc_avg double(20,6) DEFAULT NULL COMMENT '平均付款时刻(在一天中的位置如12:36 = 12.60)',
paytoc_std0 double(20,6) DEFAULT NULL COMMENT '付款时刻方差',
weekday_avg double(20,6) DEFAULT NULL COMMENT '',
weekday_std0 double(20,6) DEFAULT NULL COMMENT '',
monthday_avg double(20,6) DEFAULT NULL COMMENT '',
monthday_std0 double(20,6) DEFAULT NULL COMMENT '',
dto_max double(20,6) DEFAULT NULL COMMENT '剔除异常后的最大间隔天数',
dt_clustinginfo text DEFAULT NULL COMMENT '个人间隔天聚类info',
user_clustingid int(4) DEFAULT NULL COMMENT '用户行为聚类类别id',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '',
PRIMARY KEY `IDX_UID` (`uid`),
KEY `CID` (`user_clustingid`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户加油行为画像及行为聚类结果';
'''
bm_predictmodel_status_ = '''
create table IF NOT EXISTS bimodels.bm_predictmodel_status (
mid int(11) DEFAULT NULL COMMENT 'modelid',
minfo text DEFAULT NULL COMMENT 'model描述',
numb0 double(20,6) DEFAULT NULL COMMENT '',
numb1 double(20,6) DEFAULT NULL COMMENT '',
numb2 double(20,6) DEFAULT NULL COMMENT '',
record0 int(14) DEFAULT NULL COMMENT '',
record1 int(14) DEFAULT NULL COMMENT '',
record2 int(14) DEFAULT NULL COMMENT '',
obligate text DEFAULT NULL COMMENT '扩展',
update_time datetime DEFAULT NULL COMMENT '更新时间',
PRIMARY KEY `IDX_MID` (`mid`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='消费预测模型状态';
'''
bm_user_predict_record_ = '''
create table IF NOT EXISTS bimodels.bm_user_predict_record (
uid int(11) DEFAULT NULL COMMENT 'uid',
predict_time datetime DEFAULT NULL COMMENT '预测时间，一般和订单的paytime一致',
ptype int(4) DEFAULT NULL COMMENT '预测类型: 0-E; 1-S; 2-LR; 3-RNN; 4-ANN',
rewei_time datetime DEFAULT NULL COMMENT '预测消费时间',
predict_dt double(20,6) DEFAULT NULL COMMENT '预测值',
paccuracy double(20,6) DEFAULT NULL COMMENT '预估准确度',
real_time datetime DEFAULT NULL COMMENT '真实的：下次消费时间',
real_dt double(20,6) DEFAULT NULL COMMENT '真实的: 间隔时间',
rerror double(20,6) DEFAULT NULL COMMENT '绝对误差(注意不是误差的绝对值)',
derror int(6) DEFAULT NULL COMMENT '常用指标:天误差',
errorrate1 double(20,6) DEFAULT NULL COMMENT '误差率1',
errorrate2 double(20,6) DEFAULT NULL COMMENT '误差率2',
modelpara text DEFAULT NULL COMMENT '模型参数',
modelchoice text DEFAULT NULL COMMENT '模型选择细节',
obligate text DEFAULT NULL COMMENT '扩展',
update_time datetime DEFAULT NULL COMMENT '更新时间',
PRIMARY KEY `IDX_UIDT` (`uid`,`predict_time`),
KEY `IDX_UID` (`uid`),
KEY `IDX_PRE_TIME` (`predict_time`) USING BTREE,
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='消费预测历史记录-用于评估';
'''
bm_user_predict__ = '''
create table IF NOT EXISTS bimodels.bm_user_predict_ (
uid int(11) DEFAULT NULL COMMENT 'uid',
predict_time datetime DEFAULT NULL COMMENT '预测时间，一般和订单的paytime一致',
ptype int(4) DEFAULT NULL COMMENT '预测类型: 0-E; 1-S; 2-LR; 3-RNN; 4-ANN',
rewei_time datetime DEFAULT NULL COMMENT '预测消费时间',
predict_dt double(20,6) DEFAULT NULL COMMENT '预测值',
paccuracy double(20,6) DEFAULT NULL COMMENT '预估准确度',
real_time datetime DEFAULT NULL COMMENT '真实的：下次消费时间',
real_dt double(20,6) DEFAULT NULL COMMENT '真实的: 间隔时间',
rerror double(20,6) DEFAULT NULL COMMENT '绝对误差(注意不是误差的绝对值)',
derror int(6) DEFAULT NULL COMMENT '常用指标:天误差',
errorrate1 double(20,6) DEFAULT NULL COMMENT '误差率1',
errorrate2 double(20,6) DEFAULT NULL COMMENT '误差率2',
modelpara text DEFAULT NULL COMMENT '模型参数',
modelchoice text DEFAULT NULL COMMENT '模型选择细节',
obligate text DEFAULT NULL COMMENT '扩展',
update_time datetime DEFAULT NULL COMMENT '更新时间',
PRIMARY KEY `IDX_UIDT` (`uid`,`predict_time`),
KEY `IDX_UID` (`uid`),
KEY `IDX_PRE_TIME` (`predict_time`) USING BTREE,
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='消费预测表-';
'''

user_order_sql_bi = '''select uid,stid, pay_time/24/3600 daytime,from_unixtime(pay_time) paytime , real_price realprice, orig_price op, orig_price/list_unit_price liters
, cast(from_unixtime(pay_time, '%%H')  as unsigned)+cast(from_unixtime(pay_time, '%%i')  as unsigned)/60 paytoc
, cost_credit cc, coupon_discount cd, pay_time,order_time create_time
, DAYOFWEEK(from_unixtime(pay_time)) weekday
, DAYOFMONTH(from_unixtime(pay_time)) monthday
, DAYOFYEAR(from_unixtime(pay_time)) yd
from dw.dw_inspay_orders
where stid not in (171073,177370,177619,176669,177525,10258,10261) and uid = %s
and batch_date <= FROM_UNIXTIME(%s,'%%Y-%%m-%%d') 
order by pay_time'''
user_order_sql_o = '''
select 
  user_id uid,merchant_id  stid,pay_time/24/3600 daytime,from_unixtime(pay_time) paytime ,goods_amount/100 op,pay_money/100  realprice,goods_number liters,market_price,actual_price,
  cast(from_unixtime(pay_time, '%%H')  as unsigned)+cast(from_unixtime(pay_time, '%%i')  as unsigned)/60 paytoc,
  OI.credit_fee cc,OI.coupon_fee cd, O.pay_time ,O.create_time,
  DAYOFWEEK(from_unixtime(pay_time)) weekday,
  DAYOFMONTH(from_unixtime(pay_time)) monthday,
  DAYOFYEAR(from_unixtime(pay_time)) yd
from ods.ods_wei_order_info O
left join ods.ods_wei_order_items OI 
ON O.id = OI.order_id
where merchant_id not in (171073,177370,177619,176669,177525,10258,10261) and user_id = %s
and is_suborder = 1 and goods_type = 10
and order_status in (1160,2010) 
and O.batch_date <= FROM_UNIXTIME(%s,'%%Y-%%m-%%d')
order by pay_time
'''
user_order_sql_on = '''
select 
  user_id uid,merchant_id  stid,pay_time/24/3600 daytime,from_unixtime(pay_time) paytime ,goods_amount/100 op,pay_money/100  realprice,goods_number liters,market_price,actual_price,
  cast(from_unixtime(pay_time, '%H')  as unsigned)+cast(from_unixtime(pay_time, '%i')  as unsigned)/60 paytoc,
  OI.credit_fee/100 cc,OI.coupon_fee/100 cd, O.pay_time ,O.create_time,
  DAYOFWEEK(from_unixtime(pay_time)) weekday,
  DAYOFMONTH(from_unixtime(pay_time)) monthday,
  DAYOFYEAR(from_unixtime(pay_time)) yd
from ods.ods_wei_order_info O
left join ods.ods_wei_order_items OI 
ON O.id = OI.order_id
where merchant_id not in (171073,177370,177619,176669,177525,10258,10261) 
and user_id > 0 and user_id in (_i_)
and O.batch_date >= '_i_' and O.batch_date <= '_i_'
and is_suborder = 1 and goods_type = 10
and order_status in (1160,2010) 
and pay_time >= _i_ and pay_time <= _i_ 
and merchant_id in (_i_)
order by pay_time
'''
df_pms12_sql = "select mid, numb0, numb1, record0, record1, obligate, update_time from bimodels.bm_predictmodel_status where mid in (1,2)"
makeup_sql = """select uid from( 
 select *,max(real_time) mreal_time from bimodels.bm_user_predict_record 
 where uid not in (select uid from bimodels.bm_user_predict_) 
 group by uid) P 
where mreal_time < (select FROM_UNIXTIME(record0-300) from bimodels.bm_predictmodel_status where mid = 2)"""

CON_rollbacksql = "update bimodels.bm_predictmodel_status set update_time=FROM_UNIXTIME(record0-%(TIME_interval_s)s),record0=record0-%(TIME_interval_s)s where mid = %(do_modelid)s"
CON_updatesql = "update bimodels.bm_predictmodel_status set record0=%(endtime)s,update_time=FROM_UNIXTIME(%(endtime)s) where mid = %(do_modelid)s"
Param = {'TIME_interval_s': 140, 'endtime': 1666666666, 'do_modelid': '2'}