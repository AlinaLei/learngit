import sys
sys.path.append('../DBbase')
import random
from db_func import *
import pyecharts


def plot_oil_price_(re_dic, to_path):
    dw = my_(config.MYSQL_BI_RW_ENV)
    sql1 = "select * from bi_papapa.city_oil_price where origin='%(origin)s' and province='%(region)s' group by offer_date,oil_number order by offer_date desc limit 400; " % re_dic
    data2 = dw.to_dataframe(sql1)
    data2 = data2[::-1]
    # data2['offer_date'] = pd.DatetimeIndex(data2['offer_date']).strftime('%Y-%m-%d')
    # offer_date=pd.DatetimeIndex(data2['offer_date']).strftime('%Y-%m-%d')
    # func = lambda x, y: x if y in x else x + [y]
    price_min = data2['price'].min()
    offer_date = data2.loc[data2['offer_date'].duplicated() == False, ['offer_date', 'price']]
    oil_number_0 = data2[data2['oil_number'] == '0'][['offer_date', 'price']]  # data2.query('oil_number=0')[['offer_date', 'price']]
    oil_number_89 = data2[data2['oil_number'] == '89'][['offer_date', 'price']]
    oil_number_92 = data2[data2['oil_number'] == '92'][['offer_date', 'price']]
    oil_number_95 = data2[data2['oil_number'] == '95'][['offer_date', 'price']]
    oil_number_98 = data2[data2['oil_number'] == '98'][['offer_date', 'price']]

    dfr = offer_date.merge(oil_number_0, how='left', on='offer_date', suffixes=['','_0'])\
                    .merge(oil_number_89, how='left', on='offer_date', suffixes=['','_89'])\
                    .merge(oil_number_92, how='left', on='offer_date', suffixes=['','_92'])\
                    .merge(oil_number_95, how='left', on='offer_date', suffixes=['','_95'])\
                    .merge(oil_number_98, how='left', on='offer_date', suffixes=['', '_98'])

    line = pyecharts.Line(re_dic['region'], "油价趋势："+re_dic['origin'], width=1400, height=700)
    tem_dic = dict(label_text_size=12, is_label_show=True,
             is_fill=True, area_opacity=0.12, line_width=2, is_smooth=True, mark_point=["average"],
             yaxis_min=price_min)
    line.add("0号柴油", dfr['offer_date'], dfr['price_0'], **tem_dic)
    line.add("89号汽油", dfr['offer_date'], dfr['price_89'], **tem_dic)
    line.add("92号汽油", dfr['offer_date'], dfr['price_92'], **tem_dic)
    line.add("95号汽油", dfr['offer_date'], dfr['price_95'], **tem_dic)
    line.add("98号汽油", dfr['offer_date'], dfr['price_98'], **tem_dic)
    line.render(to_path)


def change_city(x, y):
    for i in y:
        if i in x:
            return i


def plot_oil_station_num_(re_dic, to_path):
    standard_province = ['安徽', '贵州', '澳门', '北京', '重庆', '福建', '福建', '甘肃', '广东', '广西', '广州', '海南', '河北', '黑龙江', '河南', '湖北', '湖南', '江苏',
           '江西', '吉林', '辽宁', '内蒙古', '宁夏', '青海', '山东', '上海', '陕西', '山西', '四川', '台湾', '天津', '香港', '新疆', '西藏', '云南', '浙江']
    dw = my_(config.MYSQL_BI_RW_ENV)
    muchcols_table = 'data_center.dc_stations_muchcols_enc'
    if re_dic['scale'] == 'china':
        sqls = "select province scale,count(*) numbers from %s where name like '%%%s%%' group by province order by numbers desc" % (muchcols_table, re_dic['name'])
        count_station_ = dw.to_dataframe(sqls)
        count_station_['scale'] = count_station_['scale'].apply(lambda x: change_city(x, standard_province))
    else:
        re_dic['scale'] = re_dic['scale'].split('省')[0]
        re_dic['scale'] = re_dic['scale'].split('市')[0]
        sqls = "select city scale,count(*) numbers from %s where province like '%%%s%%' and name like '%%%s%%' group by city order by numbers desc" % (muchcols_table, re_dic['scale'], re_dic['name'])
        count_station_ = dw.to_dataframe(sqls)

    num_Max = count_station_['numbers'].max()
    name_str = "油站名包含'%s':" %re_dic['name'] if re_dic['name'] else ''
    page = pyecharts.Page()
    style = pyecharts.Style(width=1300, height=860, background_color='#606a79', title_color="#eee", title_pos="center")
    map1 = pyecharts.Map(name_str+"油站分布地图", **style.init_style)
    map1.add("", count_station_['scale'], count_station_['numbers'], maptype=re_dic['scale'], visual_range=[0, num_Max], is_label_show=True,
               is_visualmap=True, visual_text_color='#eee')
    page.add(map1)
    chart2 = pyecharts.Bar(name_str+"油站分布柱状图", **style.init_style)
    chart2.add("", count_station_['scale'][:25], count_station_['numbers'][:25], maptype=re_dic['scale'], visual_range=[0, num_Max], is_label_show=True,
               is_visualmap=True, visual_text_color='#eee')
    page.add(chart2)
    page.render(to_path)


def plot_geo_station_num(re_dic, to_path):
    dw = my_(config.MYSQL_BI_RW_ENV)
    muchcols_table = 'data_center.dc_stations_muchcols_enc'
    sqls = "select city scale,avg(latitude) avg_lat,avg(longitude) avg_lng,count(*) numbers from %s where name like '%%%s%%' group by city order by numbers desc" % (
    muchcols_table, re_dic['name'])
    count_station_ = dw.to_dataframe(sqls)
    # count_station_['scale'] = count_station_['scale'].apply(lambda x: change_city(x, pro))
    coords = {}
    for i in range(len(count_station_)):
        coords[count_station_.loc[i, 'scale']] = [count_station_.loc[i, 'avg_lng'], count_station_.loc[i, 'avg_lat']]

    num_Max = count_station_['numbers'].max()
    name_str = "油站名包含'%s':" % re_dic['name'] if re_dic['name'] else ''
    page = pyecharts.Page()
    style = pyecharts.Style(width=1300, height=860, background_color='#404a66', title_color="#eee", title_pos="center")
    geo = pyecharts.Geo(name_str + "油站分布地图", **style.init_style)
    geo.add("", count_station_['scale'], count_station_['numbers'], visual_text_color="#eee", is_legend_show=False,
            symbol_size=12, is_visualmap=True, visual_range=[0, num_Max],
            tooltip_formatter='{b}',
            label_emphasis_textsize=15,
            label_emphasis_pos='right', geo_cities_coords=coords)
    page.add(geo)
    chart2 = pyecharts.Bar(name_str + "油站分布柱状图", **style.init_style)
    chart2.add("", count_station_['scale'][:25], count_station_['numbers'][:25], visual_range=[0, num_Max],
               is_label_show=True,
               is_visualmap=True, visual_text_color='#eee')
    page.add(chart2)
    page.render(to_path)


def plot_geo_station(re_dic, to_path):
    dw = my_(config.MYSQL_BI_RW_ENV)
    muchcols_table = 'data_center.dc_stations_muchcols_enc'
    sqls = "select name scale,latitude lat,longitude lng from %s where name like '%%%s%%'" % (muchcols_table, re_dic['name'])
    count_station_ = dw.to_dataframe(sqls)
    count_station_['numbers']=1
    coords={}
    for i in range(len(count_station_)):
        coords[count_station_.loc[i,'scale']]=[count_station_.loc[i,'lng'],count_station_.loc[i,'lat']]
    # num_Max = count_station_['numbers'].max()
    name_str = "油站名包含'%s':" %re_dic['name'] if re_dic['name'] else ''
    page = pyecharts.Page()
    style = pyecharts.Style(width=1300, height=860, background_color='#404a49', title_color="#eee", title_pos="center")
    geo = pyecharts.Geo(name_str+"油站分布地图",**style.init_style)
    geo.add("",count_station_['scale'], count_station_['numbers'], visual_text_color="#eee", is_legend_show=False,
              symbol_size=11, is_visualmap=True,
              tooltip_formatter='{b}',
              label_emphasis_textsize=15,
              label_emphasis_pos='right',geo_cities_coords=coords)
    page.add(geo)
    page.render(to_path)


def add_whereadd_redic(re_dic, defalt_begin=-66):
    day_ago = day_forpast(defalt_begin)
    re_dic['whereadd'] = ' and batch_date >= %s' % day_ago
    if 'begindate' in re_dic:
        re_dic['whereadd'] = re_dic['whereadd'].replace(day_ago, re_dic['begindate'])
    if 'enddate' in re_dic:
        re_dic['whereadd'] += ' and batch_date <= %s' % re_dic['enddate']
    return re_dic


def get_station_detail_(re_dic):
    dw = my_(config.MYSQL_BI_RW_ENV)
    df_station = dw.to_dataframe("SELECT stname,city FROM ods.ods_wei_stations where stid = %(mer_id)s" % re_dic)
    smart_sql = """
    select task_name,startdate,if(enddate<=startdate,DATE_FORMAT(now(),'%%Y%%m%%d'),enddate) enddate
    from 
      (SELECT task_name,min(DATE_FORMAT(FROM_UNIXTIME(start_time),'%%Y%%m%%d')) startdate,max(DATE_FORMAT(FROM_UNIXTIME(if(end_time<update_time,end_time,update_time)),'%%Y%%m%%d')) enddate 
      FROM ods.ods_wei_smart_coupon_task 
      where merchant_id = %(mer_id)s and start_time and status > 1 
      and start_time between UNIX_TIMESTAMP(%(begindate)s) and UNIX_TIMESTAMP(%(enddate)s)
      group by task_name) X """ % re_dic
    df_smarttime = dw.to_dataframe(smart_sql)
    return df_station.to_dict(orient='records')[0], df_smarttime.to_dict(orient='records')


def lineadd_sted(line, dic_smarttime, x_label, max_value):
    for d in dic_smarttime:
        rand = 0.01*random.random()
        Y = [max_value+rand if int(d['enddate'])>=x>=int(d['startdate']) else None for x in x_label]
        line.add(d['task_name'], x_label, Y, is_fill=True, area_opacity=0.2, is_smooth=True, xaxis_interval=0,
                 # mark_point=["max", {"coord": [int(d['startdate']), max_value], "name": "活动开始时间"},
                            # {"coord": [int(d['enddate']), max_value], "name": "活动结束时间"}]
                 )


def plot_station_lostavg(re_dic, to_path):
    re_dic = add_whereadd_redic(re_dic)
    dic_station, dic_smarttime = get_station_detail_(re_dic)
    re_dic['stname'] = '%s-%s' % (dic_station['city'], dic_station['stname'])

    dw = my_(config.MYSQL_BI_RW_ENV)
    sql_mer = """SELECT 
      sum(if(spr_id<3,value_c,0)) users_7,sum(if(spr_id<4,value_c,0)) users_15,sum(value_c*value_e) lostday_a,sum(value_c) users_a,batch_date 
    FROM profile.pr_stations_user_dis_ where mer_id = %(mer_id)s and tar_id = 30 %(whereadd)s group by batch_date""" % re_dic
    sql_all = """SELECT 
      sum(if(spr_id<3,value_c,0)) users_7,sum(if(spr_id<4,value_c,0)) users_15,sum(value_c*value_e) lostday_a,sum(value_c) users_a,batch_date  
    FROM profile.pr_platforms_user_dis_ where mer_id = 0 and tar_id = 30 %(whereadd)s group by batch_date""" % re_dic
    data_mer = dw.to_dataframe(sql_mer)
    data_all = dw.to_dataframe(sql_all)
    page = pyecharts.Page(page_title='流失分析',)
    X = data_all['batch_date']
    tem_dic = dict(label_text_size=12, is_label_show=False,
                   is_fill=True, area_opacity=0.08, line_width=2, is_smooth=True, mark_line=["average"]
                   , xaxis_interval=1, xaxis_rotate=45)
    line1 = pyecharts.Line("平均流失天数趋势：", "%(stname)s(%(mer_id)s)" % re_dic, width=1500, height=600)
    lostavg_mer = (data_mer['lostday_a'] / data_mer['users_a']).round(2)
    lostavg_all = (data_all['lostday_a'] / data_all['users_a']).round(2)
    line1.add("油站", X, lostavg_mer, **tem_dic)
    line1.add("全平台", X, lostavg_all, **tem_dic)
    page.add(line1)

    rrate_mer = (data_mer['users_15'] / data_mer['users_a']).round(4)
    rrate_all = (data_all['users_15'] / data_all['users_a']).round(4)
    line2 = pyecharts.Line("流失15日内的用户占比：", "%(stname)s(%(mer_id)s)" % re_dic, width=1500, height=600)
    conb_ = np.append(rrate_mer, rrate_all)
    tem_dic.update({'yaxis_min': conb_.min() * 0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    line2.add("油站", X, rrate_mer, **tem_dic)
    line2.add("全平台", X, rrate_all, **tem_dic)
    page.add(line2)

    rrate_mer = (data_mer['users_7'] / data_mer['users_a']).round(4)
    rrate_all = (data_all['users_7'] / data_all['users_a']).round(4)
    line2 = pyecharts.Line("流失7日内的用户占比：", "%(stname)s(%(mer_id)s)" % re_dic, width=1500, height=600)
    conb_ = np.append(rrate_mer, rrate_all)
    tem_dic.update({'yaxis_min': conb_.min() * 0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    line2.add("油站", X, rrate_mer, **tem_dic)
    line2.add("全平台", X, rrate_all, **tem_dic)
    page.add(line2)

    page.render(to_path)


def plot_station_3ntends(re_dic, to_path):
    
    re_dic = add_whereadd_redic(re_dic)
    dic_station, dic_smarttime = get_station_detail_(re_dic)
    re_dic['stname'] = '%s-%s' % (dic_station['city'], dic_station['stname'])

    mapp = {'30':'250', '14':'251', '7':'252', 'dyn':'253'}
    re_dic['tar_id'] = mapp[re_dic['N']]
    dw = my_(config.MYSQL_BI_RW_ENV)
    sql_mer = "SELECT * FROM profile.pr_stations_user_dis2_ where mer_id = %(mer_id)s and tar_id = %(tar_id)s %(whereadd)s" % re_dic
    sql_all = "SELECT * FROM profile.pr_platforms_user_dis2_ where mer_id = 0 and tar_id = %(tar_id)s %(whereadd)s" % re_dic
    data_mer = dw.to_dataframe(sql_mer)
    data_all = dw.to_dataframe(sql_all)
    page = pyecharts.Page(page_title='3N分析',)
    tem_dic = dict(label_text_size=12, is_label_show=False,
                   is_fill=True, area_opacity=0.12, line_width=2, is_smooth=True, mark_line=["average"]
                   ,xaxis_interval=1, xaxis_rotate=45)

    line1 = pyecharts.Line("当日加油的隔(N-2N)天回流占比:", "%(stname)s(%(mer_id)s)-(N=%(N)s)" % re_dic, width=1500, height=600)
    X = data_all.query('spr_id==11')['batch_date'].tolist()
    N1today_mer_rate = np.array(data_mer.query('spr_id==9')['value_c']) / np.array(data_mer.query('spr_id==8')['value_c'])
    N1today_all_rate = np.array(data_all.query('spr_id==9')['value_c']) / np.array(data_all.query('spr_id==8')['value_c'])
    Y_mer = N1today_mer_rate.round(4)
    Y_all = N1today_all_rate.round(4)
    conb_ = np.append(Y_mer,Y_all)
    tem_dic.update({'yaxis_min':conb_.min()*0.6})
    lineadd_sted(line1, dic_smarttime, X, conb_.max() * 1.2)
    line1.add("油站", X, Y_mer, **tem_dic)
    line1.add("全平台", X, Y_all, **tem_dic)

    page.add(line1)

    line2 = pyecharts.Line("当日加油的隔(2N-3N)天回流占比:", "%(stname)s(%(mer_id)s)-(N=%(N)s)" % re_dic, width=1500, height=600)
    X = data_all.query('spr_id==11')['batch_date']
    N2today_mer_rate = np.array(data_mer.query('spr_id==10')['value_c']) / np.array(data_mer.query('spr_id==8')['value_c'])
    N2today_all_rate = np.array(data_all.query('spr_id==10')['value_c']) / np.array(data_all.query('spr_id==8')['value_c'])
    Y_mer = N2today_mer_rate.round(4)
    Y_all = N2today_all_rate.round(4)
    conb_ = np.append(Y_mer, Y_all)
    tem_dic.update({'yaxis_min': conb_.min()*0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    line2.add("油站:", X, Y_mer, **tem_dic)
    line2.add("全平台", X, Y_all, **tem_dic)
    page.add(line2)

    line2 = pyecharts.Line("最近周期加油用户中睡眠回流占比:", "%(stname)s(%(mer_id)s)-(N=%(N)s)" % re_dic, width=1500, height=600)
    N3_mer_rate = np.array(data_mer.query('spr_id==4')['value_c']) / np.array(data_mer.query('spr_id==2')['value_c'])
    N3_all_rate = np.array(data_all.query('spr_id==4')['value_c']) / np.array(data_all.query('spr_id==2')['value_c'])
    Y_mer = N3_mer_rate.round(4)
    Y_all = N3_all_rate.round(4)
    conb_ = np.append(Y_mer, Y_all)
    tem_dic.update({'yaxis_min': conb_.min() * 0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    tem_dic.update({'yaxis_min': conb_.min()*0.6})
    line2.add("油站", X, Y_mer, **tem_dic)
    line2.add("全平台", X, Y_all, **tem_dic)
    page.add(line2)

    line2 = pyecharts.Line("睡眠回流占比:", "%(stname)s(%(mer_id)s)-(N=%(N)s)" % re_dic, width=1500, height=600)
    N3_mer_rate = np.array(data_mer.query('spr_id==4')['value_c']) / np.array(data_mer.query('spr_id==3')['value_c'])
    N3_all_rate = np.array(data_all.query('spr_id==4')['value_c']) / np.array(data_all.query('spr_id==3')['value_c'])
    Y_mer = N3_mer_rate.round(4)
    Y_all = N3_all_rate.round(4)
    conb_ = np.append(Y_mer, Y_all)
    tem_dic.update({'yaxis_min': conb_.min() * 0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    tem_dic.update({'yaxis_min': conb_.min() - 0.04})
    line2.add("油站", X, Y_mer, **tem_dic)
    line2.add("全平台", X, Y_all, **tem_dic)
    page.add(line2)

    line2 = pyecharts.Line("有睡眠趋势的用户占比:", "%(stname)s(%(mer_id)s)-(N=%(N)s)" % re_dic, width=1500, height=600)
    N3_mer_rate = np.array(data_mer.query('spr_id==5')['value_c']) / np.array(data_mer.query('spr_id==1')['value_c'])
    N3_all_rate = np.array(data_all.query('spr_id==5')['value_c']) / np.array(data_all.query('spr_id==1')['value_c'])
    Y_mer = N3_mer_rate.round(4)
    Y_all = N3_all_rate.round(4)
    conb_ = np.append(Y_mer, Y_all)
    tem_dic.update({'yaxis_min': conb_.min() * 0.6})
    lineadd_sted(line2, dic_smarttime, X, conb_.max() * 1.2)
    tem_dic.update({'yaxis_min': conb_.min() - 0.04})
    line2.add("油站", X, Y_mer, **tem_dic)
    line2.add("全平台", X, Y_all, **tem_dic)
    page.add(line2)

    page.render(to_path)






# def get_data(country='', province=''):
#     pro = ['安徽', '贵州', '澳门', '北京', '重庆', '福建', '福建', '甘肃', '广东', '广西', '广州', '海南', '河北', '黑龙江', '河南', '湖北', '湖南', '江苏',
#            '江西', '吉林', '辽宁', '内蒙古', '宁夏', '青海', '山东', '上海', '陕西', '山西', '四川', '台湾', '天津', '香港', '新疆', '西藏', '云南', '浙江']
#     if country == 'china':
#         dict_data1 = {'maptype': country,
#                       'value': [],
#                       'city_data': []}
#         count_station_province = dw_in.to_dataframe(
#             'select province,count(*) as numbers from %s group by province order by numbers desc' % (muchcols_table))
#         count_station_province['province'] = count_station_province['province'].apply(lambda x: change_city(x, pro))
#         print(count_station_province)
#         for i, row in count_station_province.iterrows():
#             dict_data1['city_data'].append(row['province'])
#             dict_data1['value'].append(row['numbers'])
#         return dict_data1
#     else:
#         count_station_city = dw_in.to_dataframe(
#             "select city,count(*) as numbers from %s where province='%s' group by city order by numbers desc" % (
#             muchcols_table, province))
#         province = province.split('省')[0]
#         province = province.split('市')[0]
#         dict_data1 = {'maptype': province,
#                       'value': [],
#                       'city_data': []}
#         for i, row in count_station_city.iterrows():
#             dict_data1['city_data'].append(row['city'])
#             dict_data1['value'].append(row['numbers'])
#         return dict_data1
#
#
# def create_charts(dict_data):
#     page = Page()
#     style = Style(width=1200, height=800)
#
#     attr = dict_data['city_data']
#     value = dict_data['value']
#     chart1 = Map(dict_data['maptype'] + "油站分布地图", **style.init_style)
#     chart1.add("", attr, value, maptype=dict_data['maptype'], visual_range=[0, max(value)], is_label_show=True,
#                is_visualmap=True, visual_text_color='#000')
#     page.add(chart1)
#
#     chart2 = Bar(dict_data['maptype'] + "油站分布柱状图", **style.init_style)
#     chart2.add("", attr, value, maptype=dict_data['maptype'], visual_range=[0, max(value)], is_label_show=True,
#                is_visualmap=True, visual_text_color='#000')
#     page.add(chart2)
#     page.render()


"""
def predict(uid):
    wecar250 = my_(config.MYSQL_PRODUCT_R_ENV)
    df = wecar250.to_dataframe(
        'select ordertime,UNIX_TIMESTAMP(ordertime) ut from wei_inspay_orders where uid = %s and ( order_status = 3 or order_status = 4 ) order by ordertime' % uid)
    if len(df) < 2: return 0, len(df)
    x_ = np.array(df.ut.diff().fillna(0)) / 3600 / 24
    if len(x_) < 9: return x.mean(), len(df)
    return stat_pre(x_)


def test():
    dw = my_(config.MYSQL_BI_RW_ENV)
    uid = dw.getdata('select uid from consume_time where  consume_times > 100 AND minprice > 40 AND average_price > 40 limit 12,1')[0]['uid']
    wecar250 = my_(config.MYSQL_PRODUCT_R_ENV)
    df = wecar250.to_dataframe('select ordertime,UNIX_TIMESTAMP(ordertime) ut from wei_inspay_orders where uid = %s and ( order_status = 3 or order_status = 4 ) order by ordertime' % uid)
    x_ = np.array(df.ut.diff().fillna(0)) / 3600 / 24
    namd_, p = cdffit(x_, rl_CDF)
    num = 50  # 几种模拟分布的方式对比   生成的样本数 num
    # rand_pdf 是ARM的一种实现  rand_cdf 是 ITM   详见 http://blog.csdn.net/pizi0475/article/details/48689237
    fg = rand_pdf(rl_pdf.subs(namd, namd_), num)
    xym = fg.__next__()
    predict, P, randarray = fg.__next__()
    cdf = rl_cdf.subs(namd, namd_)
    randarray1 = np.array(rand_cdf(cdf, num, dx=0.1))
    randarray2 = np.array(stats.expon.rvs(scale=namd_, size=num))
    print(uid, namd_, p, xym)
    print(randarray, predict, P)
    print(randarray1, randarray1.mean(), cdf.subs(x, randarray1.mean()))
    print(randarray2, randarray2.mean())
"""