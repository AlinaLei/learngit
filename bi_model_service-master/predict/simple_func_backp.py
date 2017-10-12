
from CreasAndsqls import *
import sys
sys.path.append('../DBbase')
from db_func import *
sys.path.append('../.settings')
import config
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sn

# global parameters:
endtime = 1666666666


# funct:  用户订单df预处理 ##
def uo_df_p(df):
    df['dt'] = df['daytime'].diff()[1:].reset_index()['daytime']
    df = df.drop(df[df.dt < 0.05].index).fillna(0) # 0.005等于432秒 去掉间隔太近的样本
    return df


def user_order_detail(uid):
    dw = my_(config.MYSQL_BI_RW_ENV)
    df = dw.to_dataframe(user_order_sql_bi % (uid, endtime))
    if df.__len__() < 2:
        return None
    df = uo_df_p(df)
    dw.quit()
    return df

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