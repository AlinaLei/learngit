##
import sys
sys.path.append('F:/python_pro/bi_model_service/predict')
sys.path.append('F:/python_pro/bi_model_service/DBbase')
sys.path.append('F:/python_pro/bi_model_service/.settings')

from console import *
import matplotlib.pyplot as plt
import seaborn as sn

uidssql = '''
select uid,wcount,now() paytime_1, 0 lastpaytime, now() p_paytimeA, now() p_paytimeB, now() p_paytimeC, 0 realdiff
    , 0 pA, 0 pB,0 pC
    , 0 errA, 0 errB, 0 errC, 0 dayerrA, 0 dayerrB, 0 dayerrC, 0 errrateA, 0 errrateB, 0 errrateC , 0 mse
from bimodels.bm_user_clusting_platform where uid > 0 and wcount < 9 and wcount > 3
order by update_time desc
limit 20000
'''
LIST_Seffectandy_columns = ['feed', 'liters', 'realprice', 'cd', 'cc', 'paytoc', 'yd', 'monthday', 'weekday', 'dt']
LIST_Closeadd_columns = ['feed', 'liters', 'realprice', 'cd', 'cc', 'ordertimes']

dw = my_('bi_wr_RP')
dfr = dw.to_dataframe(uidssql)
dfr = dfr.set_index('uid')
print('all:%s' % len(dfr))

# ex1
startdtime = datetime.datetime.strptime('20100101', "%Y%m%d")
i=0
timer1 = Timer_(1)
timer2 = Timer_(2)
timer3 = Timer_(3)
S1 = [0,0,0,0,0]
S2 = [0,0,0,0,0]
S3 = [0,0,0,0,0]

dayseconds = 3600 * 24
datediff = lambda dx,dy: (dy - startdtime).days - (dx - startdtime).days
errrate_x = lambda y,yp: (yp-y)/(y+0.01) if yp >= y else (y-yp)/(yp+0.01)  # 修正的误差率
errrate = lambda y,yp: (yp-y)/(y+0.01) if yp >= y else (y-yp)/(y+0.01)


def e1_kmeans_dprocess(X, n_clusters=3):
    kmeans = KMeans(n_clusters=3)
    r_kmeans = kmeans.fit(X)
    Xm = X.mean()
    ind = r_kmeans.labels_ == kmeans.n_clusters
    for mi in range(kmeans.n_clusters):
        indt = r_kmeans.labels_ == mi
        if r_kmeans.cluster_centers_[mi] > 2 * Xm and r_kmeans.labels_[indt].__len__() / r_kmeans.labels_.__len__() < 0.144:
            # print(uid,r_kmeans.cluster_centers_[mi],Xm,r_kmeans.labels_[indt].__len__(),r_kmeans.labels_.__len__())
            ind = (ind) | (indt)
        if r_kmeans.cluster_centers_[mi] > max_dt:
            ind = (ind) | (indt)
    return ind


def e1_uo_df_p(df):
    df = df.fillna(0)
    df['dt'] = df['daytime'].diff()[1:].reset_index()['daytime']
    #df['ordertimes'] = 1
    ind_tooclose = df[df.dt < 0.05].index  # 0.005等于432秒 去掉间隔太近的样本
    #for i in ind_tooclose:
    #    df.loc[i+1, LIST_Closeadd_columns] += df.loc[i, LIST_Closeadd_columns]
    df = df.drop(ind_tooclose).fillna(df.dt.mean())
    return df


def upddfr(uid,dfr,ss='A'):
    dfr.loc[uid, 'p_paytime'+ss] = dfr.loc[uid, 'paytime_1'] + datetime.timedelta(days=float(dfr.loc[uid, 'p'+ss]))
    dfr.loc[uid, 'err'+ss] = (dfr.loc[uid, 'p_paytime'+ss] - dfr.loc[uid, 'lastpaytime']).total_seconds() / dayseconds
    delpC = datediff(dfr.loc[uid, 'paytime_1'], dfr.loc[uid, 'p_paytime'+ss])
    dfr.loc[uid, 'dayerr'+ss] = abs(delpC - dfr.loc[uid, 'realdiff'])
    dfr.loc[uid, 'errrate'+ss] = errrate(dfr.loc[uid, 'realdiff'], delpC)


def tf_predict(uid,df,dfr):
    center_path = ''
    net_mun = 2
    datao_storage = eval('[%s]' % ','.join(["[0, 0, '']"] * net_mun))
    np_dfe = np.matrix(df[LIST_Seffectandy_columns])
    np_dfe_6 = nth_ladder_create(np_dfe, 6)

    modelchoice = {'errors': np.array([0.0] * net_mun), 'improve': 0.0, 'times': 0}
    stind = int(df.__len__() * 0.88)
    test_times = df.__len__() - stind
    tasklist = []
    # task1 = threading.Thread(target=net_creat_restore_fit_save_
    #                          , args=(np_dfe_6, center_path
    #                                  , {'alter': 'ROL', 'hiden_layers': [], 'active_functions': ['tf.nn.sigmoid']
    #                                      , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
    #                                  , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
    #                                         lprint=False)
    #                                  , datao_storage[0], True,))
    # task1.setDaemon(True)
    # task1.start()
    task2 = threading.Thread(target=net_creat_restore_fit_save_
                             , args=(np_dfe_6, center_path
                                     , {'alter': 'RNN', 'hiden_layers': [7],
                                        'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                                         , 'RELU_exp': '0.01*L1_loss'}
                                     , dict(test_size = test_times, steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                            lprint=False)
                                     , datao_storage[0], True,))
    tasklist += [task2]
    task3 = threading.Thread(target=net_creat_restore_fit_save_
                             , args=(np_dfe, center_path
                                     , {'alter': 'ANN', 'hiden_layers': [7],
                                        'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                                         , 'RELU_exp': '0.01*L1_loss'}
                                     , dict(test_size = test_times, steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                            lprint=False)
                                     , datao_storage[1], True,))
    tasklist += [task3]
    [p.setDaemon(True) for p in tasklist]
    [p.start() for p in tasklist]
    [p.join() for p in tasklist]
    real_arr = np.array(df['dt'].iloc[-(test_times + 1):-1])

    testerror = [errorsum(datao_storage[i][0].T, real_arr) for i in range(net_mun)]
    modelchoice['errors'] += np.array(testerror)
    modelchoice['times'] += test_times
    prearray = np.array([d[1] for d in datao_storage])
    conlist = [d[2] for d in datao_storage]
    prelist = prearray.round(3).tolist()
    print(df['uid'].iloc[0], prelist, df['dt'].iloc[-1], modelchoice['errors'].round(3).tolist(), modelchoice['times'], test_times)
    ptype = int(modelchoice['errors'].argsort()[0])

    dfr.loc[uid, 'pC'] = prelist[ptype]

    upddfr(uid, dfr, 'C')

    S = abs(dfr.loc[uid, 'dayerrC'])
    if S < 3: S3[S] += 1
    S3[3] += 1 if dfr.loc[uid, 'errrateC'] < 0.99 else 0
    S3[4] += abs(dfr.loc[uid, 'errC'])
    # del mybp


dfrind = dfr.index.tolist()
random.shuffle(dfrind)
for uid in dfrind:
#for uid in [737522]:
    # wecar250 = my_('250')
    # if (i % 10) > 0:
    #    i += 1
    #    continue

    dw = my_('bi_wr_RP')
    df = dw.to_dataframe(user_order_sql_bi % (uid, 1666666666))

    df = uo_df_feed(df)
    df = uo_df_p(df)
    
    if len(df) < 3:
        dfr.drop(uid)
        continue 

    if len(df) < 20:

        dfr.loc[uid, 'lastpaytime'] = df.paytime.iloc[-1]
        df = df.iloc[:-1, :]
        dfr.loc[uid, 'paytime_1'] = df.paytime.iloc[-1]
        dfr.loc[uid, 'realdiff'] = datediff(dfr.loc[uid, 'paytime_1'], dfr.loc[uid, 'lastpaytime'])

        dt = np.array(df['dt'])
        pre, P, p = stat_pre(dt[:-1])
        dfr.loc[uid, 'pA'] = pre
        upddfr(uid, dfr, 'A')
        S = abs(dfr.loc[uid, 'dayerrA'])
        if S < 3: S1[S] += 1
        S1[3] += 1 if dfr.loc[uid, 'errrateA'] < 0.99 else 0
        S1[4] += abs(dfr.loc[uid, 'errA'])

        dfr.loc[uid, 'pB'] = dt[:-1].mean()
        upddfr(uid, dfr, 'B')
        S = abs(dfr.loc[uid, 'dayerrB'])
        if S < 3: S2[S] += 1
        S2[3] += 1 if dfr.loc[uid, 'errrateB'] < 0.99 else 0
        S2[4] += abs(dfr.loc[uid, 'errB'])
        # dfr.drop(uid)
    else:
        ind = e1_kmeans_dprocess(np.matrix(df.dt).T, n_clusters=3)
        df = df[~ind]
        #df['dt'].clip(0,df['dt'][~ind].max())


        dfr.loc[uid, 'lastpaytime'] = df.paytime.iloc[-1]
        df = df.iloc[:-1,:]
        dfr.loc[uid, 'paytime_1'] = df.paytime.iloc[-1]
        dfr.loc[uid, 'realdiff'] = datediff(dfr.loc[uid, 'paytime_1'], dfr.loc[uid, 'lastpaytime'])

        # 方法1：分布统计
        timer1.tic()
        dt = np.array(df['dt'])
        pre,P,p = stat_pre(dt[:-1])
        dfr.loc[uid, 'pA'] = pre
        upddfr(uid,dfr,'A')
        timer1.toc()
        S = abs(dfr.loc[uid, 'dayerrA'])
        if S < 3: S1[S] += 1
        S1[3] += 1 if dfr.loc[uid, 'errrateA'] < 0.99 else 0
        S1[4] += abs(dfr.loc[uid, 'errA'])

        # 方法2：回归
        # timer2.tic()
        # da = np.matrix(df[['H', 'wd', 'feed', 'rp', 'cd', 'dt']])
        # my = myLR(da).normaliz().nth_ladder(n=6).devide(test_size=1).myfit()
        # dfr.loc[uid, 'pB'] = my.ypo_test[0, 0]
        # upddfr(uid,dfr, 'B')
        # timer2.toc()
        # S = abs(dfr.loc[uid, 'dayerrB'])
        # if S < 3: S2[S] += 1
        # S2[3] += 1 if dfr.loc[uid, 'errrateB'] < 0.99 else 0
        # S2[4] += abs(dfr.loc[uid, 'errB'])

        # BP
        timer3.tic()
        # t1 = threading.Thread(target=tf_predict,args=(uid,df,dfr,))
        # t1.setDaemon(True)
        # t1.start()
        # threading_hold_print(5, 1, sleept=2, flush_ss='')
        tf_predict(uid,df,dfr,)

        # da = nth_ladder_create(np.matrix(df[['feed', 'rp', 'cd', 'H', 'yd', 'md', 'wd', 'dt']]),n=6)
        # mybp.datainit(da).normalizy().normalizx().sessinit()
        # if i > 1: mybp.layersW = layersW
        # mybp.networkfit(10001, batch_train_lp = 1.5 , op_oerr = 0.0002 ,op_otimes = 2)
        # dfr.loc[uid, 'pC'] = mybp.netpredict()[-1]
        # dfr.loc[uid, 'mse'] = mybp.mse
        ## my.bpnetworkinit(hidenlayer_nodes=[7])
        ## if i > 1 : my.syn = mysyn
        ## my.bpnetworkfit(times = 5000, learnrate = (my.y_train.shape[0])**-1/12, batch_train_lp = 2, fitstop_oerr = -0.0000034 ,fitstop_otimes = 2).bppredict()
        ## dfr.loc[uid, 'pC'] = my.ypo_test[0, 0]
        # dfr.loc[uid, 'p_paytimeC'] = dfr.loc[uid, 'paytime_1'] + datetime.timedelta(days=float(dfr.loc[uid, 'pC']))
        # dfr.loc[uid, 'errC'] = (dfr.loc[uid, 'p_paytimeC'] - dfr.loc[uid, 'lastpaytime']).total_seconds() / dayseconds
        # delpC = datediff(dfr.loc[uid, 'paytime_1'], dfr.loc[uid, 'p_paytimeC'])
        # dfr.loc[uid, 'dayerrC'] = delpC - delr
        # dfr.loc[uid, 'errrateC'] = errrate(delr, delpC)
        timer3.toc()

        # layersW = mybp.layersW
        # mysyn = my.syn

    if (i%20) == 0:
        print('**'*3, i, uid, S1, S2, S3,'mse:%s' %dfr.mse.sum(), threading.activeCount())
    i += 1
threading_hold_print(2, 1, sleept=2)
timer3.toc()
print(i, S1, S2, S3,'mse:%s' %dfr.mse.sum(), threading.activeCount())
#dfr.to_excel(u'F:\python_pro\\xlsx\ex7.4.xlsx')
dfr.loc[dfr.pA!=0,:].to_excel(u'F:\python_pro\\xlsx\ex7.4.xlsx')

x_ = np.array(df.dt)
x__ = x_.mean()

fig = plt.figure(figsize=(14, 11))#figsize=(10,6)
pl = fig.add_subplot(111) #表示在2*2的网格的格式里，占第一个位置
sn.distplot(x_, color="#988CBE", bins=16, rug=True, ax=pl)
pl.plot([0,0],[0,2],color='#000000')
pl.plot([x__,x__], [0, 2], color='#009900',label='mean')
pl.annotate('mean of delta_d(%2.3f)' %x__, xy=(x__, 0), xytext=(x__, -0.02), bbox=dict(boxstyle='sawtooth',fc="w")
            , arrowprops=dict(arrowstyle="-|>"#"-|>"代表箭头头上是实心的
                              , connectionstyle="arc,rad=0.4",fc='r'))

pl.set_title(u'plot distributing: delta_d of uid=%s' %uid)
pl.set_xlabel('delta_d')
pl.set_ylabel('Rate(p)')
pl.grid(True)

pl.axis([-1, x_.max()+1]+list(pl.properties()['ybound']))
fig.savefig('C:\\Users\Administrator\Desktop\Figure_1.png')


## 测试单调性
import sys
sys.path.append('F:/python_pro/bi_model_service/predict')
sys.path.append('F:/python_pro/bi_model_service/DBbase')
sys.path.append('F:/python_pro/bi_model_service/.settings')

from console import *
import matplotlib.pyplot as plt

x_train = np.linspace(0,1,400)[:, np.newaxis]
#x_train1 = np.linspace(0,1,400)[:, np.newaxis]
x_train1 = np.random.rand(400)[:, np.newaxis]
x_train2 = np.random.rand(400)[:, np.newaxis]
y_train = np.sin(x_train*5) * 0.4 + 0.42*rand_ab(-0.5,0.5)
alldata = np.hstack((x_train,x_train1,x_train2,y_train))
myNN = tensor_con(3, [14, 3], ['tf.nn.tanh','tf.nn.tanh', 'tf.nn.sigmoid'], learnrate=0.01, Regu='0.01*L1_loss', name='XXX').sessinit()
myNN.datainit(alldata, test_size=1).normalizy('rel_n11').normalizx()
plt.plot(myNN.x_data,myNN.y_data,'o')

for i in range(10000):
    myNN.networkfit_withCross(5, batch_train_lp=0
                              , op_oerr=0.0002, op_otimes=3
                              , eprint=True, lprint=True)
    plt.plot(myNN.x_data[:,0],myNN.sess.run(myNN.alllayers[-1],{myNN.xinput: myNN.x_data}))
    plt.pause(0.1)

# plot symfunc
def func_plot(f,xrange=(0,100,1000),ty=1):
    X=np.linspace(*xrange)
    try:
        plt.plot(X, f(X))
    except Exception as err:
        print(err)
        plt.plot(X, np.array(list(map(f,X))))

def f1(X):
    my.x_test[0,0] = X
    yp,ypo = my.bppredict()
    return yp[0]

func_plot(f1,(0,1,100))
func_plot(lambda x:((abs(x)+1)*((np.e)**(-x/np.e/2)+1))**-1,xrange=(-10,10,1000))



#####  tensorflow test
# 1.训练的数据
# Make up some real data
x_data = np.linspace(0,1,200)[:, np.newaxis]
noise = np.random.normal(0, 0.04, x_data.shape)
y_data = np.sin(x_data*10)*0.4 +0.42+noise

plt.plot(x_data,y_data)

import tensorflow as tf
def add_layer(inputs, in_size, out_size, activation_function=None):
    # add one more layer and return the output of this layer
    # 区别：大框架，定义层 layer，里面有 小部件
    with tf.name_scope('layer'):
        # 区别：小部件
        with tf.name_scope('weights'):
            Weights = tf.Variable(tf.random_normal([in_size, out_size]), name='W')
        with tf.name_scope('biases'):
            biases = tf.Variable(tf.zeros([1, out_size]) + 0.1, name='b')
        with tf.name_scope('Wx_plus_b'):
            Wx_plus_b = tf.add(tf.matmul(inputs, Weights), biases)
        if activation_function is None:
            outputs = Wx_plus_b
        else:
            outputs = activation_function(Wx_plus_b, )
        return outputs


# define placeholder for inputs to network
# 区别：大框架，里面有 inputs x，y
with tf.name_scope('inputs'):
    xs = tf.placeholder(tf.float32, [None, 1], name='x_input')
    ys = tf.placeholder(tf.float32, [None, 1], name='y_input')

# add hidden layer
l1 = add_layer(xs, 1, 12, activation_function=tf.nn.sigmoid)
l2 = add_layer(l1, 12, 6, activation_function=tf.nn.sigmoid)
# add output layer
prediction = add_layer(l2, 6, 1, activation_function=None)

# the error between prediciton and real data
# 区别：定义框架 loss
with tf.name_scope('loss'):
    loss = tf.reduce_mean(tf.reduce_sum(tf.square(ys - prediction),reduction_indices=[1]))

# 区别：定义框架 train
with tf.name_scope('train'):
    train_step = tf.train.GradientDescentOptimizer(0.2).minimize(loss)

sess = tf.Session()

# 区别：sess.graph 把所有框架加载到一个文件中放到文件夹"logs/"里
# 接着打开terminal，进入你存放的文件夹地址上一层，运行命令 tensorboard --logdir='logs/'
# 会返回一个地址，然后用浏览器打开这个地址，在 graph 标签栏下打开
sess.run(tf.global_variables_initializer())
# important step
for i in range(10000000):
    # training train_step 和 loss 都是由 placeholder 定义的运算，所以这里要用 feed 传入参数
    sess.run(train_step, feed_dict={xs: x_data, ys: y_data})
    if i % 500 == 0:
        # to see the step improvement
        plt.plot(x_data, sess.run(prediction, feed_dict={xs: x_data}))
        plt.pause(0.1)
        mse = sess.run(loss, feed_dict={xs: x_data, ys: y_data})
        print(mse)
        if mse < 0.002: break
writer = tf.summary.FileWriter(u".logs\\networks", mybp.sess.graph)
##### tensorflow test


wecar250 = my_('250')
df=wecar250.to_dataframe('''
select inspay_orig_price op,mod(inspay_orig_price,5) mop,ordertime,DAYOFWEEK(ordertime) weekday,UNIX_TIMESTAMP(ordertime) ut,cast(DATE_FORMAT(ordertime , '%H' ) as unsigned) H
from wei_inspay_orders where uid=596 and ( order_status = 3 or order_status = 4 ) order by ordertime''')

df['feed'] = 0.1  # feed 加满标识
df.loc[df.mop != 0 | (df.op < 50), 'feed'] = 1  # 加满
df.loc[df.op > df.op.mean(), 'feed'] = 0.6  # 加半满
df['dt'] = df['ut'].diff()[1:].reset_index()['ut'] / 3600 / 24
df['dt'] = df['dt'].fillna(0)


da = np.matrix(df[['H','weekday','feed','op','dt']])
my=myLR(da[1:,:]).normaliz().nth_ladder(n=4).devide(test_size=1).myfit()
plt.plot(my.y_train)
plt.plot(my.yp_train)
plt.show()
print(my.rmse(),my.r2())
print(my.coef_,my.intercept_)

plt.figure(2)
df.loc[df['dt'] > 60,'dt'] = 60
da1 = np.matrix(df[['H','weekday','feed','op','dt']])
my1=myLR(da1[1:,:]).normaliz().nth_ladder(n=7).devide(test_size=1).myfit()
plt.plot(my1.y_train)
plt.plot(my1.yp_train)
plt.show()
print(my1.rmse(),my1.r2())
print(my1.coef_,my1.intercept_)


dt=np.array(df['dt'])
stat_pre(dt)


plt.hist(dt[:-1],75)
sn.distplot(dt[:-1],bins=100, kde=True)



x=syp.Symbol('x')
f=0.250216804909089*2.71828182845905**(-0.166811203272726*x**1.5)*x**0.5
exec('f=lambda x:'+str(f*len(dt)))
func_plot(f,(0,50,200))


# @
def hello(fn):
    def wrapper():
        print("hello, %s" % fn.__name__)
        fn()
        print("goodby, %s" % fn.__name__)
    return wrapper

@hello
def foo():
    print("i am foo")

foo()

from functools import wraps

def memo(fn):
    cache = {}
    miss = object()

    @wraps(fn)
    def wrapper(*args):
        result = cache.get(args, miss)
        if result is miss:
            result = fn(*args)
            cache[args] = result
        return result

    return wrapper


@memo
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


data = [435, 4, 5, 3, 5, 3, 4, 342, 423, 23, 3, 5, 23421, 42, 1, 1, 2, 34, 3, 24,564,65456,1,312,546,54,654,564,564,65,4,564,6,564,1,2312,461,6,484,6,4,1,8,46,1,564]
atimer = Timer_(0)
for i in range(10000):
    random.shuffle(data)
    data_copy = data.copy()
    num,base_list = speed_find_sev(data, 3)
    # print('****')
    num,base_list = speed_find_sev(data_copy, 10)
    atimer.toc(1)
times = np.array(atimer.tictoc)
print(times,times.mean(),times.sum())


atimer = Timer_(0)
for i in range(10000):
    random.shuffle(data)
    data_copy = data.copy()
    num,base_list = speed_find_sev(data, 3)
    # print('****')
    num,base_list = speed_find_sev(data, 10, base_list)
    atimer.toc(1)
times = np.array(atimer.tictoc)
print(times,times.mean(),times.sum())