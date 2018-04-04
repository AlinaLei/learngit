etl_sqls = {'pr_coupon_user_coupons':
"""
REPLACE INTO  `profile`.pr_coupon_user_coupons (`batch_date`,`uid`, `activity_type`, `useful`, `used60`, `expired60`, `used30`, `expired30`)
SELECT SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY) AS batch_date,cuc1.uid, cuc1.activity_type, 
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time >= UNIX_TIMESTAMP(now())) as useful,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
        SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 60 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used60,  
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
            DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 60 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired60,   
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
        SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 30 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used30,  
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
            DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 30 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired30 
FROM ods.ods_wei_coupon_user_coupons cuc1 
LEFT JOIN ods.ods_wei_coupon_use_record cur1 ON cuc1.user_coupon_id = cur1.user_coupon_id 
INNER JOIN ods.ods_wei_coupons C ON C.coupon_id = cuc1.coupon_id and C.merchant_id not in (171073,177370,177619,176669,177525,10258,10261) 
WHERE cuc1.is_delete = 0 and cuc1.activity_type >= 7 and cuc1.uid > 0
AND cuc1.coupon_status in (1,2)
AND cuc1.end_time >= UNIX_TIMESTAMP(SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 60 DAY)) 
GROUP BY cuc1.uid, cuc1.activity_type
""",
'pr_level_user_tag':
"""
REPLACE INTO  `profile`.pr_level_user_tag(`batch_date`, `uid`, `merchant_type`, `merchant_id`, `level_name`,`sort` , `upgrade_condition`, `score`, `hard`, `post`, `hard_degree`, `pass_day`, `month_cycle`)
SELECT SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY) AS batch_date,
        gold.uid, gold.merchant_type, gold.merchant_id, gold.level_name, gold.sort, gold.upgrade_condition,
  IFNULL(gold.score1,0) AS score,
        gold.upgrade_condition - IFNULL(gold.score1,0) AS hard,
        IFNULL(gold.score2,0) AS post,
  (gold.upgrade_condition - IFNULL(gold.score1,0.1)) / IFNULL(gold.score2,gold.upgrade_condition) AS hard_degree,
  day(DATE_ADD(curdate(),INTERVAL -1 day)) AS pass_day ,
  DATEDIFF(date_add(curdate()-day(curdate())+1,interval 1 month ),DATE_ADD(curdate(),interval -day(curdate())+1 day)) AS month_cycle 
FROM
(SELECT g1.uid, c1.merchant_type, c1.merchant_id, c1.level_name, c1.sort, c1.upgrade_condition, exp1.score1 ,exp2.score2
FROM
        dw.dw_crm_latest_group AS g1
LEFT JOIN ods.ods_wei_user_tag_all a1 ON g1.uid = a1.uid AND a1.merchant_id = g1.group_id
LEFT JOIN ods.ods_wei_level_config c1 ON c1.id = a1.tag AND c1.merchant_id = g1.group_id
LEFT JOIN
(SELECT l1.uid, l1.merchant_id, FROM_UNIXTIME(l1.create_time),SUM(l1.exp)as score1
FROM ods.ods_wei_user_exp_log l1
WHERE  l1.create_time >= UNIX_TIMESTAMP(date_sub(date_sub(date_format(now(),'%y-%m-%d'),interval extract( day from now())-1 day),interval 0 month))
GROUP BY l1.uid,l1.merchant_id )as exp1
ON g1.uid = exp1.uid AND g1.group_id = exp1.merchant_id
LEFT JOIN
(SELECT l1.uid, l1.merchant_id, FROM_UNIXTIME(l1.create_time),SUM(l1.exp)as score2
FROM ods.ods_wei_user_exp_log l1
WHERE  l1.create_time >= UNIX_TIMESTAMP(date_sub(date_sub(date_format(now(),'%y-%m-%d'),interval extract( day from now())-1 day),interval 1 month))
  AND l1.create_time < UNIX_TIMESTAMP(date_sub(date_sub(date_format(now(),'%y-%m-%d'),interval extract( day from now())-1 day),interval 0 month))
GROUP BY l1.uid,l1.merchant_id )as exp2
ON g1.uid = exp2.uid AND g1.group_id = exp2.merchant_id
WHERE a1.end_time > UNIX_TIMESTAMP( NOW() ) 
AND c1.sort > 1
AND c1.is_delete = 0
) AS gold
WHERE (gold.upgrade_condition > gold.score1 OR gold.score1 IS NULL)
""",
'pr_crma_stations_couponstat':
"""
set @today=DATE_FORMAT(NOW(), '%Y-%m-%d');
set @dayago1=SUBDATE(@today,INTERVAL 1 DAY);
set @dayago91=SUBDATE(@today,INTERVAL 91 DAY);
set @dayago61=SUBDATE(@today,INTERVAL 61 DAY);
set @dayago31=SUBDATE(@today,INTERVAL 31 DAY);
REPLACE INTO profile.pr_crma_stations_couponstat (`batch_date`,`uid`,`activity_type`,`mer_id`,`useful`,`usedtoday`,`used90`,`expired90`,`used60`,`expired60`,`used30`,`expired30`)
SELECT @dayago1 AS batch_date,cuc1.uid, cuc1.activity_type, merchant_id,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time >= UNIX_TIMESTAMP(@today)) as useful,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date = @dayago1) as usedtoday,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago91 AND @dayago1) as used90,  
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago91) AND UNIX_TIMESTAMP(@today)) as expired90,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago61 AND @dayago1) as used60,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago61) AND UNIX_TIMESTAMP(@today)) as expired60,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago31 AND @dayago1) as used30,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago31) AND UNIX_TIMESTAMP(@today)) as expired30 
FROM ods.ods_wei_coupon_user_coupons cuc1 
LEFT JOIN ods.ods_wei_coupon_use_record cur1 ON cuc1.user_coupon_id = cur1.user_coupon_id 
INNER JOIN ods.ods_wei_coupons C ON C.coupon_id = cuc1.coupon_id 
WHERE cuc1.is_delete = 0 and merchant_type = 1 and cuc1.uid > 0
AND cuc1.coupon_status in (1,2) 
AND cuc1.create_time >= UNIX_TIMESTAMP(@dayago91) 
GROUP BY cuc1.uid, cuc1.activity_type, merchant_id
""",
'pr_crma_groups_couponstat':
"""
set @today=DATE_FORMAT(NOW(), '%Y-%m-%d');
set @dayago1=SUBDATE(@today,INTERVAL 1 DAY);
set @dayago91=SUBDATE(@today,INTERVAL 91 DAY);
set @dayago61=SUBDATE(@today,INTERVAL 61 DAY);
set @dayago31=SUBDATE(@today,INTERVAL 31 DAY);
REPLACE INTO profile.pr_crma_groups_couponstat (`batch_date`,`uid`,`activity_type`,`mer_id`,`useful`,`usedtoday`,`used90`,`expired90`,`used60`,`expired60`,`used30`,`expired30`)
SELECT @dayago1 AS batch_date,cuc1.uid, cuc1.activity_type, merchant_id,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time >= UNIX_TIMESTAMP(@today)) as useful,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date = @dayago1) as usedtoday,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago91 AND @dayago1) as used90,  
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago91) AND UNIX_TIMESTAMP(@today)) as expired90,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago61 AND @dayago1) as used60,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago61) AND UNIX_TIMESTAMP(@today)) as expired60,
    SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN @dayago31 AND @dayago1) as used30,
    SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(@dayago31) AND UNIX_TIMESTAMP(@today)) as expired30  
FROM ods.ods_wei_coupon_user_coupons cuc1 
LEFT JOIN ods.ods_wei_coupon_use_record cur1 ON cuc1.user_coupon_id = cur1.user_coupon_id 
INNER JOIN ods.ods_wei_coupons C ON C.coupon_id = cuc1.coupon_id 
WHERE cuc1.is_delete = 0 and merchant_type = 2 and cuc1.uid > 0
AND cuc1.coupon_status in (1,2) 
AND cuc1.create_time >= UNIX_TIMESTAMP(@dayago91) 
GROUP BY cuc1.uid, cuc1.activity_type, merchant_id 
""",
# 'pr_crma_stations_couponstat':
#   """
#   REPLACE INTO profile.pr_crma_stations_couponstat (`batch_date`,`uid`,`activity_type`,`mer_id`,`useful`,`used90`,`expired90`,`used60`,`expired60`,`used30`,`expired30`)
#   SELECT SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY) AS batch_date,cuc1.uid, cuc1.activity_type, merchant_id,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time >= UNIX_TIMESTAMP(now())) as useful,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 90 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used90,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 90 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired90,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 60 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used60,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 60 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired60,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 30 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used30,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 30 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired30
#   FROM ods.ods_wei_coupon_user_coupons cuc1
#   LEFT JOIN ods.ods_wei_coupon_use_record cur1 ON cuc1.user_coupon_id = cur1.user_coupon_id
#   INNER JOIN ods.ods_wei_coupons C ON C.coupon_id = cuc1.coupon_id
#   WHERE cuc1.is_delete = 0 and merchant_type = 1 and cuc1.uid > 0
#   AND cuc1.coupon_status in (1,2)
#   AND cuc1.create_time >= UNIX_TIMESTAMP(SUBDATE(NOW(),INTERVAL 90 DAY))
#   GROUP BY cuc1.uid, cuc1.activity_type, merchant_id
#   """,
# 'pr_crma_groups_couponstat':
#   """
#   REPLACE INTO profile.pr_crma_groups_couponstat (`batch_date`,`uid`,`activity_type`,`mer_id`,`useful`,`used90`,`expired90`,`used60`,`expired60`,`used30`,`expired30`)
#   SELECT SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY) AS batch_date,cuc1.uid, cuc1.activity_type,merchant_id,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time >= UNIX_TIMESTAMP(now())) as useful,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 90 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used90,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 90 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired90,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 60 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used60,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 60 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired60,
#       SUM(cuc1.coupon_status = 2 AND cur1.batch_date BETWEEN SUBDATE(
#           SUBDATE(DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 1 DAY),INTERVAL 30 DAY) AND DATE_FORMAT(NOW(), '%Y-%m-%d')) as used30,
#       SUM(cuc1.coupon_status = 1 AND cuc1.end_time BETWEEN UNIX_TIMESTAMP(SUBDATE(
#               DATE_FORMAT(NOW(), '%Y-%m-%d'),INTERVAL 30 DAY)) AND UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d'))) as expired30
#   FROM ods.ods_wei_coupon_user_coupons cuc1
#   LEFT JOIN ods.ods_wei_coupon_use_record cur1 ON cuc1.user_coupon_id = cur1.user_coupon_id
#   INNER JOIN ods.ods_wei_coupons C ON C.coupon_id = cuc1.coupon_id
#   WHERE cuc1.is_delete = 0 and merchant_type = 2 and cuc1.uid > 0
#   AND cuc1.coupon_status in (1,2)
#   AND cuc1.create_time >= UNIX_TIMESTAMP(SUBDATE(NOW(),INTERVAL 90 DAY))
#   GROUP BY cuc1.uid, cuc1.activity_type, merchant_id
#   """
}
