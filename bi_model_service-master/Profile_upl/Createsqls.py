create_sqls = {'pr_target_config': '''
create table IF NOT EXISTS profile.pr_target_config (
tar_id int(6) DEFAULT NULL COMMENT '指标id' ,
scopelevel int(8) DEFAULT NULL COMMENT '适用范围，位存储，由高到低位分别表示 平台|集团|油站|用户。如一个仅集团和油站适用的指标则scopelevel=6，更高位预留，0表示失效',
property int(4) DEFAULT NULL COMMENT '0-动态属性，1-静态属性',
spreadtype int(4) DEFAULT NULL COMMENT '展开(子指标)类型，0：不包含子指标，1：子指标为离散的几种状态，2：',
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
'''
, 'pr_target_spread_config': '''
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
'''
, 'pr_stations_user_dis_': '''
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
'''
, 'pr_groups_user_dis_': '''
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
'''
, 'pr_platforms_user_dis_': '''
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
'''
, 'pr_stations_order_other_': '''
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
               '''
, 'pr_groups_order_other_': '''
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
'''
, 'pr_platforms_order_other_': '''
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
'''}


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
    'tar_id': [10,10,10,10,10,   21, 21, 21, 21, 21,     30,30,30,30,30,  110,110,110,110, 120,120,120,120,120]
    , 'spr_id': [1, 2, 3, 4, 5,      1, 2, 3, 4, 5,      1, 2, 3, 4, 5,     1, 2, 3, 4,      1, 2, 3, 4, 5]
    , 'stattype':[0, 0, 0, 0, 0,     0, 0, 0, 0, 0,      0, 0, 0, 0, 0,     1, 1, 1, 1,      1, 1, 1, 1, 1]
    , 'lower_bound': [-1,1,3,9,20, -1,660,3200,36000,300000, -1,2,7,15,32, -1,55,160,320, -1,6,16,36,65]
    , 'upper_bound': [1,3,9,20,-1, 660,3200,36000,300000,-1, 2,7,15,32,-1, 55,160,320,-1, 6,16,36,66,-1]
    , 'create_time': 'now()'}
}

