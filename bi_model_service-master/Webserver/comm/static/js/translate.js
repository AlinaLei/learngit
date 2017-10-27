/*
 * translater
 * Copyright (c) 2017 antony
 * 502202879@qq.com
 */
stack={DW_predict_record_accuracy: "BI预测模型评估", DW_predictmodel_status: "BI预测运行状态", DW_user_clusting_platfrom: "BI用户消费行为聚类"
      ,H_S2_smalltest_product: "微支付(测试)",H_S2_realsmall_product: "新微支付"
	  ,hxb_user_information:"和小宝用户明细",ln_users_information:"岭南用户明细"
	  ,ln_users_orders:"岭南用户订单明细",ln_storemaster_orders:"岭南店主订单明细",ln_valid_users:"岭南有效用户明细",ln_city_seller:"岭南地市商家归属"
	  ,ln_product_PV:"岭南商品PV",xqj_user_information:"寻秦集用户明细"
	};
col_stack={ptype:"预测类型","count(1)":"总记录数",uid:"用户id",stid:"油站id",group_id:"集团id",predict_dt:"预测间隔",update_time:"更新时间",activity_id:"活动id"
		  ,orderdate:"订单时间:日",ordermonth:"订单时间:月",splitdate:"分摊时间:日",splitmonth:"分摊时间:月",splitmoney:"分摊金额",typedesc:"产品类型(简述)",desc_:"产品类型(简述)"
		  ,monthdays:"月分摊天数",cmcc.mobilearea:"地市",sm.addtime:"注册时间"
	}
con_stack={"orderTime >= ":"YYYY-MM(-DD HH:mm:SS)","orderTime <= ":"YYYY-MM(-DD HH:mm:SS)","splittype in ":"'n+ ','S-'","orderId in ":"多个订单号,隔开"
		  ,"shopshortname in ":"'上海A','深圳B'","shopshortname like ":"填入包含的关键字即可"
		  ,"ordertime >= ":"YYYYMMDD","ordertime < ":"YYYYMMDD"
	}