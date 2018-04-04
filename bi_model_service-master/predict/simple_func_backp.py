
from CreasAndsqls import *
import sys
sys.path.append('../DBbase')
from db_func import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sn

# global parameters:


# funct:  用户订单df预处理 ##
def uo_df_p(df):
    df['dt'] = df['daytime'].diff()[1:].reset_index()['daytime']
    df = df.drop(df[df.dt < 0.05].index).fillna(0) # 0.005等于432秒 去掉间隔太近的样本
    return df


def user_order_detail(uid):
    dw = my_(config.MYSQL_BI_RW_ENV)
    sqlh = SqlHandler(user_order_sql_on)
    cond_uid = {'user_id in ': uid}
    df = dw.to_dataframe(sqlh.render_sqls(cond_uid))
    # df = dw.to_dataframe(user_order_sql_bi % (uid, endtime))
    if df.__len__() < 2:
        return None
    df = uo_df_p(df)
    dw.quit()
    return df


def plotdtbyuids(uids, to_path):
    Le = np.ceil(np.sqrt(len(uids)))
    fig = plt.figure(figsize=(14, 11))  # figsize=(10,6)

    for i, uid in enumerate(uids):
        df = user_order_detail(uid)
        x_ = np.array(df.dt)
        x__ = x_.mean()
        pl = fig.add_subplot(int('%d%d%s' % (Le, Le, i + 1)))
        sn.distplot(x_, color="#988CBE", bins=16, rug=True, ax=pl)
        pl.plot([0, 0], [0, 2], color='#000000')
        pl.plot([x__, x__], [0, 2], color='#009890', label='mean')
        ybound = pl.properties()['ybound']
        pl.annotate('mean of delta_d:%2.3f \n wcount: %d' % (x__, x_.__len__()), xy=(x__, 0)
                    , xytext=(x__, 0.6 * ybound[1])
                    , bbox=dict(boxstyle='sawtooth', fc="w")
                    , arrowprops=dict(arrowstyle="-|>"
                                      , connectionstyle="arc,rad=0.5", fc='r'))  # "-|>"代表箭头头上是实心的
        pl.set_title(u'plot distributing: delta_d of uid=%s' % uid)
        pl.set_xlabel('delta_d')
        pl.set_ylabel('Rate(p)')
        pl.grid(True)
        pl.axis([-1, x_.max() + 1] + list(ybound))
    fig.savefig(to_path)
