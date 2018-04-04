bm_nm_smartcoupon_apirecord_ = '''
create table IF NOT EXISTS bimodels.bm_nm_smartcoupon_apirecord (
record_code varchar(44) DEFAULT NULL COMMENT '记录编号',
`send_code` varchar(35) DEFAULT NULL COMMENT '任务唯一码',
para_merchant_id int(11) DEFAULT 0 COMMENT '请求参数:merchant_id',
para_merchant_type int(4) DEFAULT 0 COMMENT '请求参数:merchant_type',
para_prefer_gcode char(6) DEFAULT NULL COMMENT '请求参数：prefer_gcode',
para_limitx int(9) DEFAULT -1 COMMENT '请求参数:limitx',
obligate_args text DEFAULT NULL COMMENT '其他请求参数',
update_time datetime DEFAULT NULL COMMENT '更新时间',
PRIMARY KEY `REX_re` (`record_code`),
KEY `IDX_UPD_TIME` (`update_time`) USING BTREE
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='智能发券请求记录';
'''
bm_nm_smartcoupon_abtest_record_ = '''
CREATE TABLE `bm_nm_smartcoupon_abtest_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `apirecord_code` varchar(44) DEFAULT NULL COMMENT '记录编号',
  `send_code` varchar(35) DEFAULT NULL COMMENT '任务唯一码',
  `uid` int(11) DEFAULT '0' COMMENT '用户id',
  `time_limit` int(11) DEFAULT '0',
  `time_limit_type` int(4) DEFAULT '0',
  `cill` double(14,2) DEFAULT '0.00',
  `coupon_price` double(14,2) DEFAULT '0.00',
  `sendtoc` double(14,2) DEFAULT '0.00',
  `sendtimestamp` int(14) DEFAULT '0',
  `rank_score` double(10,5) DEFAULT '0.00000',
  `coupon_type` int(4) DEFAULT '0',
  `coupon_tag` varchar(11) DEFAULT NULL,
  `ab_type` int(4) DEFAULT NULL COMMENT 'AB测试的组别,一般0为实际作用组,其他(>0)的为对照组',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `obligate` text COMMENT '其他',
  PRIMARY KEY (`id`),
  KEY `IDX_reco` (`apirecord_code`),
  KEY `IDX_seco` (`send_code`),
  KEY `IDX_UPD_TIME` (`update_time`) USING BTREE,
  KEY `IDX_uid` (`uid`),
  KEY `IDX_ab_type` (`ab_type`)
) ENGINE=InnoDB AUTO_INCREMENT=1414 DEFAULT CHARSET=utf8 COMMENT='智能发券请求对应的券列表';

'''