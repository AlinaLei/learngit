/*
 * translater
 * Copyright (c) 2017 antony
 * 502202879@qq.com
 */
stack={DW_predict_record_accuracy: "BI预测模型评估", DW_predictmodel_status: "BI预测运行状态", DW_user_clusting_platfrom: "BI用户消费行为聚类"
      ,H_S2_smalltest_product: "微支付(测试)",H_S2_realsmall_product: "新微支付",H_S2_yuanlai_product: "缘来网服务期产品",H_S2_lanjing:"蓝鲸(包含测试)"
	  ,S2_spec_order: "分摊订单(高端&珍爱通)",S2_regular_order: "分摊订单(微支付&缘来网)",S2_realsmall_order: "新微支付订单(real服务期)",S2_regular_orderproduct:"蓝鲸订单"
	  ,OfflineOrder: "线下订单表",OfflineVipSuspendHistory: "线下高端会员暂停历史表",OfflineContractSuspendAndRecover: "线下合同暂停恢复表"
	  ,VipSuspendAndRecover:"珍爱通会员暂停恢复表",VipSuspendHistory:"珍爱通会员暂停历史表",XX:""
	};
col_stack={ptype:"预测类型","count(1)":"总记录数",uid:"用户id",stid:"油站id",group_id:"集团id",predict_dt:"预测间隔",update_time:"更新时间",activity_id:"活动id"
		  ,orderdate:"订单时间:日",ordermonth:"订单时间:月",splitdate:"分摊时间:日",splitmonth:"分摊时间:月",splitmoney:"分摊金额",typedesc:"产品类型(简述)",desc_:"产品类型(简述)"
		  ,monthdays:"月分摊天数"
	}
con_stack={"orderTime >= ":"YYYY-MM(-DD HH:mm:SS)","orderTime <= ":"YYYY-MM(-DD HH:mm:SS)","splittype in ":"'n+ ','S-'","orderId in ":"多个订单号,隔开"
		  ,"shopshortname in ":"'上海A','深圳B'","shopshortname like ":"填入包含的关键字即可"
		  ,"ordertime >= ":"YYYYMMDD","ordertime < ":"YYYYMMDD"
	}