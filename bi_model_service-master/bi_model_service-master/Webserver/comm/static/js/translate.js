/*
 * translater
 * Copyright (c) 2017 antony
 * 502202879@qq.com
 */
stack={DW_predict_record_accuracy: "BI预测模型评估", DW_predictmodel_status: "BI预测运行状态", DW_user_clusting_platfrom: "BI用户消费行为聚类"
      ,WOB_hexinshuju:"CS_核心数据",DW_shangxianyouzhan:"CS_上线油站数据",DW_jituanyueshuju_1:'CS_集团月数据1'
	};
col_stack={ptype:"预测类型","count(1)":"总记录数",uid:"用户id",stid:"油站id",group_id:"集团id",merchant_id:"商户编号",update_time:"更新时间",activity_id:"活动id"
          ,stname:"油站名(简)",address:"地址"
		  ,user_coupon_id:'用户券id',errorrate:"误差率",derror:"天误差"
		  ,realprice_avg:"实付金额(均值)",predict_dt:'预测加油间隔',coupon_price:'券面额',wcount:'有效加油次数',dt_avg:'加油间隔均值',order_code:'订单号'
		  ,cdt_avg:'券使用频率'
		  ,'@stday':'开始日期','@enday':'结束日期'
	}
con_stack={"orderTime >= ":"YYYY-MM(-DD HH:mm:SS)","orderTime <= ":"YYYY-MM(-DD HH:mm:SS)","splittype in ":"'n+ ','S-'","orderId in ":"多个订单号,隔开"
		  ,"shopshortname in ":"'上海A','深圳B'","shopshortname like ":"填入包含的关键字即可"
		  ,"ordertime >= ":"YYYYMMDD","ordertime < ":"YYYYMMDD"
	}