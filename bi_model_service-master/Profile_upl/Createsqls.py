create_sqls = {'pr_target_config':
'''
create table IF NOT EXISTS profile.pr_target_config (
tar_id int(6) DEFAULT NULL COMMENT '指标id' ,
scopelevel int(8) DEFAULT NULL COMMENT '适用范围，位存储，由高到低位分别表示 平台|集团|油站|用户。如一个仅集团和油站适用的指标则scopelevel=6，更高位预留，0表示失效',
property int(4) DEFAULT NULL COMMENT '0-动态属性，1-静态属性',
spreadtype int(4) DEFAULT NULL COMMENT '展开(子指标)类型，0：不包含子指标，1：子指标为离散的几种状态，2： ,负数：共用子指标的tar_id',
name text DEFAULT NULL COMMENT '名称内容',
account_for text DEFAULT NULL COMMENT '指标解释',
originsql text DEFAULT NULL COMMENT '',
columns text DEFAULT NULL COMMENT '',
otable text DEFAULT NULL COMMENT '',
create_time datetime DEFAULT NULL COMMENT '创建时间',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '预留text',
PRIMARY KEY `TID` (`tar_id`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指标配置表';
''',
'pr_target_spread_config':
'''
create table IF NOT EXISTS profile.pr_target_spread_config (
tar_id int(6) DEFAULT NULL COMMENT '指标id',
spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id' ,
stattype int(6) DEFAULT NULL COMMENT '统计类型：0-累计,1-单天，2-' ,
upper_bound double(20,6) DEFAULT NULL COMMENT '上界:一般不取等号',
lower_bound double(20,6) DEFAULT NULL COMMENT '下界',
name text DEFAULT NULL COMMENT '名称内容',
account_for text DEFAULT NULL COMMENT '子指标解释',
create_time datetime DEFAULT NULL COMMENT '创建时间',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '预留text',
PRIMARY KEY `T_sID` (`tar_id`,`spr_id`),
KEY `SPID` (`spr_id`),
KEY `TID` (`tar_id`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='展开(子指标)配置表';
''',
'pr_stations_user_dis_':
'''
create table IF NOT EXISTS profile.pr_stations_user_dis_ (
mer_id int(11) NOT NULL COMMENT '油站id',
tar_id int(6) DEFAULT NULL COMMENT '指标id',
spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '预留text',
batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
KEY `T_sID` (`tar_id`,`spr_id`),
KEY `MER_taID` (`mer_id`,`tar_id`),
KEY `MERID` (`mer_id`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像(动态)：油站-用户分布'
PARTITION BY range (batch_date)
(PARTITION p0 VALUES less than (20000101));
''',
'pr_groups_user_dis_':
'''
create table IF NOT EXISTS profile.pr_groups_user_dis_ (
mer_id int(11) NOT NULL COMMENT '集团id',
tar_id int(6) DEFAULT NULL COMMENT '指标id',
spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '预留text',
batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
KEY `T_sID` (`tar_id`,`spr_id`),
KEY `MER_taID` (`mer_id`,`tar_id`),
KEY `MERID` (`mer_id`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像(动态)：集团-用户分布'
PARTITION BY range (batch_date)
(PARTITION p0 VALUES less than (20000101));
''',
'pr_platforms_user_dis_':
'''
create table IF NOT EXISTS profile.pr_platforms_user_dis_ (
mer_id int(11) NOT NULL COMMENT '平台id',
tar_id int(6) DEFAULT NULL COMMENT '指标id',
spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
update_time datetime DEFAULT NULL COMMENT '更新时间',
obligate text DEFAULT NULL COMMENT '预留text',
batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
KEY `T_sID` (`tar_id`,`spr_id`),
KEY `MER_taID` (`mer_id`,`tar_id`),
KEY `MERID` (`mer_id`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像(动态)：平台-用户分布'
PARTITION BY range (batch_date)
(PARTITION p0 VALUES less than (20000101));
''',
'pr_stations_order_other_':
'''
    create table IF NOT EXISTS profile.pr_stations_order_other_ (
    mer_id int(11) NOT NULL COMMENT '油站id',
    tar_id int(6) DEFAULT NULL COMMENT '指标id',
    spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
    value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
    value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
    value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
    update_time datetime DEFAULT NULL COMMENT '更新时间',
    obligate text DEFAULT NULL COMMENT '预留text',
    batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
    PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
    KEY `T_sID` (`tar_id`,`spr_id`),
    KEY `MER_taID` (`mer_id`,`tar_id`),
    KEY `MERID` (`mer_id`),
    KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
    )ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像：油站-订单和其他方向'
    PARTITION BY range (batch_date)
    (PARTITION p0 VALUES less than (20000101));
''',
'pr_groups_order_other_':
'''
    create table IF NOT EXISTS profile.pr_groups_order_other_ (
    mer_id int(11) NOT NULL COMMENT '集团id',
    tar_id int(6) DEFAULT NULL COMMENT '指标id',
    spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
    value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
    value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
    value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
    update_time datetime DEFAULT NULL COMMENT '更新时间',
    obligate text DEFAULT NULL COMMENT '预留text',
    batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
    PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
    KEY `T_sID` (`tar_id`,`spr_id`),
    KEY `MER_taID` (`mer_id`,`tar_id`),
    KEY `MERID` (`mer_id`),
    KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
    )ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像：集团-订单和其他方向'
    PARTITION BY range (batch_date)
    (PARTITION p0 VALUES less than (20000101));
''',
'pr_platforms_order_other_':
'''
    create table IF NOT EXISTS profile.pr_platforms_order_other_ (
    mer_id int(11) NOT NULL COMMENT '平台id',
    tar_id int(6) DEFAULT NULL COMMENT '指标id',
    spr_id int(6) DEFAULT NULL COMMENT '展开(子指标)指标id',
    value_c double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是计数',
    value_e double(20,6) DEFAULT NULL COMMENT '对应指标取值2_一般是均值',
    value_ob double(20,6) DEFAULT NULL COMMENT '对应指标取值3_预留',
    update_time datetime DEFAULT NULL COMMENT '更新时间',
    obligate text DEFAULT NULL COMMENT '预留text',
    batch_date int(10) DEFAULT NULL COMMENT '跑批日期',
    PRIMARY KEY `MER_tapsID` (`mer_id`,`tar_id`,`spr_id`,`batch_date`),
    KEY `T_sID` (`tar_id`,`spr_id`),
    KEY `MER_taID` (`mer_id`,`tar_id`),
    KEY `MERID` (`mer_id`),
    KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
    )ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画像：平台-订单和其他方向'
    PARTITION BY range (batch_date)
    (PARTITION p0 VALUES less than (20000101));
''',
'pr_stations_tag':
"""
CREATE TABLE `profile`.`pr_stations_tag` (
  `mer_id` int(11) NOT NULL COMMENT '油站id',
  `tar_id` int(6) NOT NULL DEFAULT '0' COMMENT '指标id',
  `spr_id` int(6) NOT NULL DEFAULT '0' COMMENT '展开(子指标)指标id',
  `value_e` double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是均值',
  `value_ob` double(20,6) DEFAULT NULL COMMENT '对应指标取值2_预留',
  `create_time` datetime DEFAULT NULL COMMENT '更新时间',
  `begin_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`mer_id`,`tar_id`,`spr_id`),
  KEY `T_sID` (`tar_id`,`spr_id`),
  KEY `MER_taID` (`mer_id`,`tar_id`),
  KEY `MERID` (`mer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='标签: 油站';
""",
'pr_groups_tag':
"""
CREATE TABLE `profile`.`pr_groups_tag` (
   `mer_id` int(11) NOT NULL COMMENT '集团id',
   `tar_id` int(6) NOT NULL DEFAULT '0' COMMENT '指标id',
   `spr_id` int(6) NOT NULL DEFAULT '0' COMMENT '展开(子指标)指标id',
   `value_e` double(20,6) DEFAULT NULL COMMENT '对应指标取值1_一般是均值',
   `value_ob` double(20,6) DEFAULT NULL COMMENT '对应指标取值2_预留',
   `create_time` datetime DEFAULT NULL COMMENT '更新时间',
   `begin_time` datetime DEFAULT NULL COMMENT '开始时间',
   `end_time` datetime DEFAULT NULL COMMENT '结束时间',
   PRIMARY KEY (`mer_id`,`tar_id`,`spr_id`),
   KEY `T_sID` (`tar_id`,`spr_id`),
   KEY `MER_taID` (`mer_id`,`tar_id`),
   KEY `MERID` (`mer_id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='标签: 集团';
""",
'mid_cos_n_xxx_template':
"""
create table IF NOT EXISTS data_center.mid_cos_n_xxx_template (
cycle_days int(4) DEFAULT 0 COMMENT '周期天数(N值,取零无意义,最多统计该用户3N内的油品订单)',
stid int(11) NOT NULL COMMENT '油站id',
uid int(11) NOT NULL COMMENT '用户id',
lastday_ts int(6) DEFAULT 0 COMMENT '最近一天的加油次数',
last1_ts int(6) DEFAULT 0 COMMENT '最近倒数第一个N天周期的加油次数',
last2_ts int(6) DEFAULT 0 COMMENT '最近倒数第二个N天周期的加油次数',
last3_ts int(6) DEFAULT 0 COMMENT '最近倒数第三个N天周期的加油次数',
PRIMARY KEY `IDX_nsu` (`cycle_days`,`stid`,`uid`),
KEY `IDX_CYC` (`cycle_days`) USING BTREE,
KEY `IDX_STID` (`stid`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='动态3N(N=30/14/7)统计[油站-用户]中间表-cos constant oil statistics持续加油统计-模板';
""",
'mid_cos_dyn_xxx_template':
"""
create table IF NOT EXISTS data_center.mid_cos_dyn_xxx_template (
cycle_days int(4) DEFAULT 0 COMMENT '周期天数(N值,取零无意义,最多统计该用户3N内的油品订单)',
stid int(11) NOT NULL COMMENT '油站id',
uid int(11) NOT NULL COMMENT '用户id',
lastday_ts int(6) DEFAULT 0 COMMENT '最近一天的加油次数',
last1_ts int(6) DEFAULT 0 COMMENT '最近倒数第一个N天周期的加油次数',
last2_ts int(6) DEFAULT 0 COMMENT '最近倒数第二个N天周期的加油次数',
last3_ts int(6) DEFAULT 0 COMMENT '最近倒数第三个N天周期的加油次数',
PRIMARY KEY `IDX_su` (`stid`,`uid`),
KEY `IDX_CYC` (`cycle_days`) USING BTREE,
KEY `IDX_STID` (`stid`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='动态3N统计[油站-用户]中间表-cos constant oil statistics持续加油统计-dyn 动态n值-模板';
""",
'pr_crma_stations_couponstat':
"""
CREATE TABLE profile.pr_crma_stations_couponstat (
  `batch_date` date NOT NULL COMMENT '跑批日期',
  `uid` int(11) NOT NULL DEFAULT '0' COMMENT '用户id',
  `activity_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '同UCU表activity_type',
  `mer_id` int(11) NOT NULL COMMENT '油站id',
  `useful` int(11) DEFAULT NULL COMMENT '用户持有的有效券数量',
  `usedtoday` int(11) DEFAULT NULL COMMENT '用户今天内使用券数量',
  `used90` int(11) DEFAULT NULL COMMENT '用户90天内使用券数量',
  `expired90` int(11) DEFAULT NULL COMMENT '用户90天内过期券数量',
  `used60` int(11) DEFAULT NULL COMMENT '用户60天内使用券数量',
  `expired60` int(11) DEFAULT NULL COMMENT '用户60天内过期券数量',
  `used30` int(11) DEFAULT NULL COMMENT '用户30天内使用券数量',
  `expired30` int(11) DEFAULT NULL COMMENT '用户30天内过期券数量',
  PRIMARY KEY (`batch_date`,`uid`,`activity_type`,`mer_id`),
  KEY `IDX_uid` (`uid`),
  KEY `IDX_activity_type` (`activity_type`),
  KEY `IDX_mer_id` (`mer_id`),
  KEY `IDX_bacth` (`batch_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='油站的用户券统计表, crma--crm补充表'
PARTITION BY RANGE  COLUMNS(batch_date)
(PARTITION p_0 VALUES LESS THAN ('2018-01-01') ENGINE = InnoDB)
""",
'pr_crma_groups_couponstat':
"""
CREATE TABLE profile.pr_crma_groups_couponstat (
  `batch_date` date NOT NULL COMMENT '跑批日期',
  `uid` int(11) NOT NULL DEFAULT '0' COMMENT '用户id',
  `activity_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '同UCU表activity_type',
  `mer_id` int(11) NOT NULL COMMENT '集团id',
  `useful` int(11) DEFAULT NULL COMMENT '用户持有的有效券数量',
  `usedtoday` int(11) DEFAULT NULL COMMENT '用户今天内使用券数量',
  `used90` int(11) DEFAULT NULL COMMENT '用户90天内使用券数量',
  `expired90` int(11) DEFAULT NULL COMMENT '用户90天内过期券数量',
  `used60` int(11) DEFAULT NULL COMMENT '用户60天内使用券数量',
  `expired60` int(11) DEFAULT NULL COMMENT '用户60天内过期券数量',
  `used30` int(11) DEFAULT NULL COMMENT '用户30天内使用券数量',
  `expired30` int(11) DEFAULT NULL COMMENT '用户30天内过期券数量',
  PRIMARY KEY (`batch_date`,`uid`,`activity_type`,`mer_id`),
  KEY `IDX_uid` (`uid`),
  KEY `IDX_activity_type` (`activity_type`),
  KEY `IDX_mer_id` (`mer_id`),
  KEY `IDX_bacth` (`batch_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='集团的用户券统计表, crma--crm补充表'
PARTITION BY RANGE  COLUMNS(batch_date)
(PARTITION p_0 VALUES LESS THAN ('2018-01-01') ENGINE = InnoDB)"""}


content1 = {
  'pr_target_config': {
    'tar_id': [10, 21, 30, 110, 120]
    , 'scopelevel': [14, 14, 14, 14, 14]
    , 'property': [0, 0, 0, 0, 0]
    , 'spreadtype': [1, 1, 1, 1, 1]
    , 'name': ["'消费频次分布'", "'用户平均价值'", "'用户流失天数'", "'单价分布'", "'升数分布'"]
    , 'originsql': ["'crm_latest_'", "'crm_latest_'", "'crm_latest_'", "'inspay_orders_'", "'inspay_orders_'"]
    , 'otable': ["'profile.pr__i_s_user_dis_'", "'profile.pr__i_s_user_dis_'", "'profile.pr__i_s_user_dis_'", "'profile.pr__i_s_order_other_'", "'profile.pr__i_s_order_other_'"]
    , 'create_time': 'now()'}
  , 'pr_target_spread_config': {
    'tar_id': [10,10,10,10,10,   21, 21, 21, 21, 21,         30,30,30,30,30,30,30,  110,110,110,110, 120,120,120,120,120]
    , 'spr_id': [1, 2, 3, 4, 5,      1, 2, 3, 4, 5,           1, 2, 3, 4, 5, 6, 7,    1, 2, 3, 4,     1, 2, 3, 4, 5]
    , 'stattype':[0, 0, 0, 0, 0,     0, 0, 0, 0, 0,           0, 0, 0, 0, 0, 0, 0,   1, 1, 1, 1,      1, 1, 1, 1, 1]
    , 'lower_bound': [-1,1,3,9,20, -1,660,3200,36000,300000,  -1,2,7,15,32,66,129,  -1,55,160,320,    -1,6,16,36,65]
    , 'upper_bound': [1,3,9,20,-1, 660,3200,36000,300000,-1,  2,7,15,32,66,129,-1,  55,160,320,-1,    6,16,36,66,-1]
    , 'create_time': 'now()'}
}

