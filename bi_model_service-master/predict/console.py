# console of dataIO&dataprocess and Model choose
# -*- coding: utf-8 -*-
import threading
import multiprocessing
from CreasAndsqls import *
from M_stat import *
from M_ML import *
from M_tensorML import *
import sys
sys.path.append('../DBbase')
from db_func import *
from hcomponents import *
# sys.path.append('../.settings')
# import config

# global parameters:
TIME_interval_s = 140
endtime = 1666666666
N_Deffect_past_days = 6
LIST_Seffectandy_columns = ['feed', 'liters', 'realprice', 'cd', 'cc', 'paytoc', 'yd', 'monthday', 'weekday', 'dt']
ANN_Inodes = len(LIST_Seffectandy_columns) - 1
RNN_Inodes = ANN_Inodes + N_Deffect_past_days


# funct: ##
def kmeans_dprocess(X,n_clusters=4):
    if X.__len__() <  n_clusters:
        return 'simple size small than n_clusters(%s)' %n_clusters
    kmeans = KMeans(n_clusters=n_clusters)
    r_kmeans = kmeans.fit(X)
    Xm = X.mean()
    ind = r_kmeans.labels_ == kmeans.n_clusters
    for mi in range(kmeans.n_clusters):
        indt = r_kmeans.labels_ == mi
        if r_kmeans.cluster_centers_[mi] > 1.9 * Xm and r_kmeans.labels_[indt].__len__() / r_kmeans.labels_.__len__() < 0.16:
            # print(uid,r_kmeans.cluster_centers_[mi],Xm,r_kmeans.labels_[indt].__len__(),r_kmeans.labels_.__len__())
            ind = (ind) | (indt)
        if r_kmeans.cluster_centers_[mi] > max_dt:
            ind = (ind) | (indt)
    return ind,kmeans


# funct:  用户订单df预处理 ##
def uo_df_p(df):
    df = df.fillna(0)
    df['dt'] = df['daytime'].diff()[1:].reset_index()['daytime']
    df = df.drop(df[df.dt < 0.05].index).fillna(0.05) # 0.005等于432秒 去掉间隔太近的样本
    return df


# funct:  用户订单df算加满率 ##
def uo_df_feed(df):
    df.loc[:, 'feed'] = 0  # feed 加满标识
    df.loc[df.op % 20 != 0 | (df.op < 50), 'feed'] = 1  # 加满
    df.loc[df.op > df.op.mean(), 'feed'] = 0.6  # 加半满
    return df

# lambda: 日期差和误差率
startdtime = datetime.datetime.strptime('20100101', "%Y%m%d")
datediff = lambda dy,dx: (dy - startdtime).days - (dx - startdtime).days
errrate = lambda yp,y: (yp-y)/(yp+0.01) if yp >= y else (y-yp)/(yp+0.01)


#修正的误差率
def errrate_x(yp,y):
    return (yp-y)/(y+0.01) if yp >= y else (y-yp)/(yp+0.01)


# 模型筛选 误差汇总
def errorsum(x, r):
    return np.clip(abs(x - r), 0, 5).sum()


# funct: df 存数据库前的字符串加标点 #
def df_add_singlequotemark(df):
    for co in df.columns:
        if df[co].dtype.char == 'M' or df[co].dtype.char == 'O':
            if len(df[co]) and type(df[co][0]) is str and df[co][0][0] + df[co][0][-1] == "''":  # 避免重复加
                continue
            df[co] = df[co].apply(lambda x: ("'%s'" %x) if x else None)
    return df


# important func::
# net_creat_restore_fit_save_(alldata,center_path,{'alter':'RNNs','RELU_exp':'0.0001*L1_loss'}
# ,dict(steps=50001,batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True))


def net_creat_restore_fit_save_(alldata, center_path, create_opt, fit_opt, datao=[], iter_fit=False):
        tp = create_opt['alter'][:3]
        save_res = create_opt['alter'][-1]
        hd = create_opt['hiden_layers']
        test_size = create_opt['test_size']
        if tp == 'RNN':
            NN_Inodes = RNN_Inodes
        elif tp == 'ANN':
            NN_Inodes = ANN_Inodes
        else:
            NN_Inodes = alldata.shape[1] - 1
        NNname = '%s%s_%s_1' %(tp,NN_Inodes, ''.join([str(j) for j in hd]))
        myNN = tensor_con(NN_Inodes, hd, create_opt['active_functions'], learnrate=0.1, Regu=create_opt['RELU_exp'], name=NNname).sessinit()
        if save_res == 'r' and center_path:
            try:
                myNN.net_save_restore(center_path + '/%s/structure%s.CKPT' %(tp,NNname), 'restore')
            except Exception as err:
                print('restore_net Exception: :',err,center_path)
        myNN.datainit(alldata, test_size=test_size).normalizy('rel_n11').normalizx()
        if iter_fit:
            while(myNN.test_ind):
                myNN.networkfit_withCross(fit_opt['steps'], batch_train_lp=fit_opt['batch_train_lp']
                                            , op_oerr=fit_opt['op_oerr'], op_otimes=fit_opt['op_otimes']
                                            , eprint=fit_opt['eprint'], lprint=fit_opt['lprint'])
                myNN.netpredict(False)
                myNN.train_ind += [myNN.test_ind.pop(0)]
        else:
            myNN.networkfit_withCross(fit_opt['steps'], batch_train_lp=fit_opt['batch_train_lp']
                                       , op_oerr=fit_opt['op_oerr'], op_otimes=fit_opt['op_otimes']
                                       ,eprint=fit_opt['eprint'], lprint=fit_opt['lprint'])
            myNN.netpredict(False)

        mynn_yp =myNN.Inverse_normaliz().yp_data[-test_size:,0]

        if save_res == 's':
            myNN.net_save_restore('%s/%s/structure%s.CKPT' %(center_path,tp,NNname))
            v_holder(myNN.get_tfvalue()).store('%s/%s/pickle_layersW' %(center_path,tp))
            v_holder(myNN.get_tfvalue('layersb')).store('%s/%s/pickle_layersb' % (center_path, tp))

        if len(datao) ==2:
            datao[0] = mynn_yp
            datao[1] = tp


# funct:  用户订单df做预测 #
def userdf_predict(df,dw,center_path):

    df_up = dw.to_dataframe('select * from bimodels.bm_user_predict_ where uid = %s limit 1' % df['uid'].iloc[0])  # user_predict df

    if df_up.__len__() > 0 :
        if df['paytime'].iloc[-1] - df_up.loc[0, 'predict_time'] > datetime.timedelta(days=0.05):
            # print('发现已预测的验证::::', df_up.loc[0, 'uid'], df.iloc[-1, :], df_up)
            df_up.loc[0, 'real_time'] = df['paytime'].iloc[-1]
            if df['paytime'].iloc[-2] != df_up.loc[0, 'predict_time']:
                df_up.loc[0, 'obligate'] = df['paytime'].iloc[-2] - df_up.loc[0, 'predict_time']
            # df_up.loc[0, 'real_dt'] = df['dt'].iloc[-2]
            df_up.loc[0, 'real_dt'] = (df_up.loc[0, 'real_time'] - df_up.loc[0, 'predict_time']).total_seconds()/24/3600
            df_up.loc[0, 'rerror'] = df_up.loc[0, 'predict_dt'] - df_up.loc[0, 'real_dt']
            delta_p = datediff(df_up.loc[0, 'rewei_time'],df_up.loc[0, 'predict_time'])
            delta_r = datediff(df_up.loc[0, 'real_time'],df_up.loc[0, 'predict_time'])
            df_up.loc[0, 'derror'] = delta_p - delta_r
            df_up.loc[0, 'errorrate1'] = errrate(delta_p, delta_r)
            df_up.loc[0, 'errorrate2'] = errrate_x(delta_p, delta_r)
            try:
                df_up['real_dt'] = df_up['real_dt'].astype(float)
                df_up['rerror'] = df_up['rerror'].astype(float)
                df_up['errorrate1'] = df_up['errorrate1'].astype(float)
                df_up['errorrate2'] = df_up['errorrate2'].astype(float)
                df_up['derror'] = df_up['derror'].astype(int)
            except Exception as err:
                print(err,df_up)
                print(df)

            yield df_up
            # df_up.loc[0, 'predict_time']  df['paytime'].iloc[-1] 会不同嘛 ··
            df_up = df_up.drop(['real_time', 'real_dt', 'rerror','errorrate1','errorrate2','derror','obligate'], 1)
        else:
            yield -1  # will be continued
    else:
        yield 0
        df_up = dw.to_dataframe('select * from bimodels.bm_user_predict_ where uid = -999999 ')  # 如果没有的话  初始化一个df_up
    df_up.loc[0, 'predict_time'] = df['paytime'].iloc[-1]
    df_up.loc[0, 'uid'] = df['uid'].iloc[0]
    df_up.loc[0, 'paccuracy'] = 0.1
    if df.__len__() < 16:
        pre, probability, p = stat_pre(np.array(df['dt'].iloc[:-1]))
        df_up.loc[0, 'ptype'] = 1 if probability < 1 else 0
        df_up.loc[0, 'predict_dt'] = pre
        df_up.loc[0, 'modelpara'] = json.dumps({'cont': p, 'p_or_times': probability, 'strategy': '4'})
    else:
        '''#RNN_layersW = v_holder().pickup(center_path+'/RNN/pickle_layersW')
        myRNN = tensor_con(RNN_Inodes, [7], ['tf.nn.tanh', 'tf.nn.sigmoid'], learnrate=0.1, Regu='0.01*L1_loss'
                           , name='%s%s_%s_1' %('RNN',RNN_Inodes,7)).sessinit()  # layersw=RNN_layersW

        #ANN_layersW = v_holder().pickup(center_path + '/ANN/pickle_layersW')
        myANN = tensor_con(ANN_Inodes, [7], ['tf.nn.tanh', 'tf.nn.sigmoid'], learnrate=0.1, Regu='0.01*L1_loss'
                           , name='%s%s_%s_1' %('ANN',ANN_Inodes,7)).sessinit()  # layersw=ANN_layersW

        # if center_path:
        #    myRNN.net_save_restore(center_path + '/RNN/structureRNN15_7_1.CKPT', 'restore')
        #    myANN.net_save_restore(center_path + '/ANN/structureANN9_7_1.CKPT', 'restore')
        myLR = tensor_con(RNN_Inodes, [], ['tf.nn.sigmoid'], learnrate=0.1, Regu='0.01*L1_loss').sessinit()
        will be remove by 1.0'''

        net_mun = 5
        modelchoice = {'errors': np.array([-0.01, 0.0] + [0.0] * net_mun), 'improve': 0.0, 'times': 0}
        stind = int(df.__len__() * 0.88)
        if df_up.loc[0, 'modelchoice']:
            try:
                modelchoice1 = eval(df_up.loc[0, 'modelchoice'])
                if len(modelchoice1['errors']) == 2 + net_mun:
                    modelchoice1['errors'] = np.array(modelchoice1['errors'])
                    stind = df.__len__() - 1
                    modelchoice = modelchoice1
            except Exception as err:
                print('errflag(modelchoice):%s,uid:%s' %(err,df_up.loc[0, 'uid']))

        datao_storage = eval('[%s]' % ','.join(["[0, '']"] * net_mun))
        test_times = df.__len__() - stind
        np_dfe = np.matrix(df[LIST_Seffectandy_columns])
        np_dfe_6 = nth_ladder_create(np_dfe, N_Deffect_past_days)
        np_dfe_3 = nth_ladder_create(np_dfe, 3)
        np_dfe_2 = nth_ladder_create(np_dfe, 2)

        task1 = threading.Thread(target=net_creat_restore_fit_save_
                                 , args=(np_dfe_6, center_path
                                         , {'alter': 'ROL', 'hiden_layers': [], 'active_functions': ['tf.nn.sigmoid']
                                             , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
                                         , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                                lprint=False)
                                         , datao_storage[0],True,))
        task1.setDaemon(True)
        task1.start()
        task2 = threading.Thread(target=net_creat_restore_fit_save_
                                 , args=(np_dfe_6, center_path
                                         , {'alter': 'RNN', 'hiden_layers': [7],
                                            'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                                             , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
                                         , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                                lprint=False)
                                         , datao_storage[1],True,))
        task2.setDaemon(True)
        task2.start()
        task3 = threading.Thread(target=net_creat_restore_fit_save_
                                 , args=(np_dfe, center_path
                                         , {'alter': 'ANN', 'hiden_layers': [7],
                                            'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                                             , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
                                         , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                                lprint=False)
                                         , datao_storage[2],True,))
        task3.setDaemon(True)
        task3.start()
        task4 = threading.Thread(target=net_creat_restore_fit_save_
                                 , args=(np_dfe_3, center_path
                                         , {'alter': '3RN', 'hiden_layers': [7],
                                            'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                                             , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
                                         , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                                lprint=False)
                                         , datao_storage[3], True,))
        task4.setDaemon(True)
        task4.start()
        task5 = threading.Thread(target=net_creat_restore_fit_save_
                                 , args=(np_dfe_2, center_path
                                         , {'alter': '2RND', 'hiden_layers': [9,3],
                                            'active_functions': ['tf.nn.tanh', 'tf.nn.tanh', 'tf.nn.sigmoid']
                                             , 'RELU_exp': '0.01*L1_loss', 'test_size': test_times}
                                         , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False,
                                                lprint=False)
                                         , datao_storage[4], True,))
        task5.setDaemon(True)
        task5.start()

        dtmean = df['dt'].iloc[:-1].mean()
        pre, probability, p = stat_pre(np.array(df['dt'].iloc[:-1]))
        real_arr = np.array(df['dt'].iloc[-test_times:])

        nuv = [task1.join(), task2.join(), task3.join(), task4.join(), task5.join()]
        testerror = [errorsum(dtmean,real_arr)] + [errorsum(pre,real_arr)] + [errorsum(datao_storage[i][0].T, real_arr) for i in range(net_mun)]
        modelchoice['errors'] += np.array(testerror)
        modelchoice['times'] += test_times
        prearray = np.array([dtmean, pre] + [d[0][-1] for d in datao_storage])
        conlist = ['E', p] + [d[1] for d in datao_storage]
        prelist = prearray.round(3).tolist()
        print(prelist, df['dt'].iloc[-1], modelchoice['errors'].round(3).tolist(), modelchoice['times'], test_times)

        """prelist=[]
        conlist=[]
        for ei in range(stind, df.__len__()+1):
            dfe = df.iloc[:ei, :]

            pre, probability, p = stat_pre(np.array(dfe['dt'].iloc[:-1]))
            np_dfe = np.matrix(dfe[LIST_Seffectandy_columns])
            np_dfe_6 = nth_ladder_create(np_dfe, N_Deffect_past_days)

            datao_storage = [[0,''],[0,''],[0,'']]
            task1 = threading.Thread(target=net_creat_restore_fit_save_
              , args=(np_dfe_6, center_path
                , {'alter': 'ROL', 'hiden_layers': [], 'active_functions': ['tf.nn.sigmoid']
                  , 'RELU_exp': '0.01*L1_loss', 'test_size': 1}
                , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False, lprint=False)
                , datao_storage[0],))
            task1.setDaemon(True)
            task1.start()
            task2 = threading.Thread(target=net_creat_restore_fit_save_
              , args=(np_dfe_6, center_path
                , {'alter': 'RNNr', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                  , 'RELU_exp': '0.01*L1_loss', 'test_size': 1}
                , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False, lprint=False)
                , datao_storage[1],))
            task2.setDaemon(True)
            task2.start()
            task3 = threading.Thread(target=net_creat_restore_fit_save_
              , args=(np_dfe, center_path
              , {'alter': 'ANNr', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
                , 'RELU_exp': '0.01*L1_loss', 'test_size': 1}
              , dict(steps=52, batch_train_lp=1, op_oerr=0.0002, op_otimes=3, eprint=False, lprint=False)
              , datao_storage[2],))
            task3.setDaemon(True)
            task3.start()
            nuv = [task1.join(), task2.join(), task3.join()]
            prearray = np.array([dfe['dt'].iloc[:-1].mean(), pre, datao_storage[0][0][0], datao_storage[1][0][0], datao_storage[2][0][0]])
            conlist = ['E', p, datao_storage[0][1], datao_storage[1][1], datao_storage[2][1]]

            '''myLR.datainit(np_dfe_6, test_size=1).normalizy('rel_n11').normalizx()
            myLR.networkfit(5201, batch_train_lp=0, op_oerr=0.0002, op_otimes=1)
            mylr_yp = myLR.netpredict().tolist()

            myRNN.datainit(np_dfe_6, test_size=1).normalizy('rel_n11').normalizx()
            myRNN.networkfit(5201, batch_train_lp=0.6, op_oerr=0.0002, op_otimes=2, eprint=False, lprint=True)
            myrnn_yp = myRNN.netpredict().tolist()

            myANN.datainit(np_dfe, test_size=1).normalizy('rel_n11').normalizx()
            myANN.networkfit(5201, batch_train_lp=0.6, op_oerr=0.0002, op_otimes=2, eprint=False, lprint=True)
            myann_yp = myANN.netpredict().tolist()

            prearray = np.array([dfe['dt'].iloc[:-1].mean(), pre, mylr_yp[-1][0], myrnn_yp[-1][0], myann_yp[-1][0]])
            conlist = ['E', p, 'LR', 'RNN', 'ANN']
            will be remove by 1.0'''

            if ei < df.__len__():
                abs_error_tmp = abs(prearray - dfe['dt'].iloc[-1])
                abs_error_tmp[abs_error_tmp > 5] = 5
                modelchoice['errors'] += abs_error_tmp
                modelchoice['times'] += 1
            prelist = prearray.round(3).tolist()
            print(prelist, dfe['dt'].iloc[-1], modelchoice['errors'].round(3).tolist(), modelchoice['times'], ei)
            will be remove by 1.0"""

        df_up.loc[0, 'ptype'] = int(modelchoice['errors'].argsort()[0])
        df_up.loc[0, 'paccuracy'] = 0.1 + 0.03 * int(df_up.loc[0, 'ptype']/2)
        df_up.loc[0, 'predict_dt'] = prelist[df_up.loc[0, 'ptype']]
        df_up.loc[0, 'modelpara'] = json.dumps({'cont': conlist[df_up.loc[0, 'ptype']], 'p_or_times': df.__len__(), 'strategy': '4'})
        modelchoice['improve'] = round(1 - modelchoice['errors'][df_up.loc[0, 'ptype']] / modelchoice['errors'].mean(),3)
        modelchoice['errors'] = modelchoice['errors'].round(3).tolist()
        df_up.loc[0, 'modelchoice'] = json.dumps(modelchoice)

    df_up.loc[0, 'rewei_time'] = df_up.loc[0, 'predict_time'] + datetime.timedelta(days=float(df_up.loc[0, 'predict_dt']))
    df_up = df_add_singlequotemark(df_up)
    df_up['update_time'] = 'now()'
    yield df_up


# funct： 由N维df获取因素权重 #
def df_w_1(dfw):
    W_1 = dfw.max()
    W_1[:] = 1
    W_1['uid', 'mainstid'] = 10000000  # uid mainstid缩小1千万倍
    W_1['realprice_avg', 'realprice_std0'] = 1000
    return W_1


# funct: df_upd_dfr 由df 更新 user_profile dfr #
def df_userprofile_dfr(df,dfr,i):

    # user_profile ##############----------------------------------------------------------------------------------------------
    dfm = df.mean().fillna(0)
    dfs = df.sum().fillna(0)
    dfstd0 = df.std(ddof=0)  # ddof 自由度1表示 Normalized by N-1 by default
    dfr.loc[i, 'wcount'] = df.__len__()
    dfr.loc[i, 'cc_avg'] = dfs['cc'] / dfr.loc[i, 'wcount']
    dfr.loc[i, 'cdt_avg'] = df[df['cd'] > 0].__len__() / dfr.loc[i, 'wcount']
    dfr.loc[i, 'cd_avg'] = dfs['cd'] / dfr.loc[i, 'wcount']
    dfr.loc[i, 'dt_max'] = df.max()['dt']

    dfgc = df.groupby('stid').count()
    dfgcm = dfgc['uid'].max()
    dfr.loc[i, 'mainsta_rate'] = dfgcm / dfr.loc[i, 'wcount']
    dfr.loc[i, 'mainstid'] = dfgc[dfgc['uid'] == dfgcm].index[0]

    for ss in ['realprice', 'liters', 'paytoc', 'weekday', 'monthday', 'dt']:
        dfr.loc[i, ss + '_avg'] = dfm[ss]
        dfr.loc[i, ss + '_std0'] = dfstd0[ss]

    # 个人间隔天聚类(标记异常)
    dfp, df_1 = df.iloc[-1, :], df.iloc[:-1, :]
    if df_1.__len__() > 6:
        ind, kmeans = kmeans_dprocess(np.matrix(df_1.dt).T, n_clusters=4)
        dfr.loc[i, 'dto_max'] = df_1[ind == False].dt.max()
        dfr.loc[i, 'dt_clustinginfo'] = "'%s'" % json.dumps(
            {'cluster_centers_': kmeans.cluster_centers_.tolist(), 'drop_num': df_1[ind].__len__()})
        ind = np.hstack([ind, np.array([False])])
        df = df[ind == False]

    return df,dfr


def updateuser_profile_predict(uids, endtime):
    # funct： 更新uid的行为侧写和预测
    dw = my_(config.MYSQL_BI_RW_ENV)
    dfr = pd.DataFrame(data={'uid': uids, 'wcount': 0, 'mainstid': 0,'update_time': 'now()', 'user_clustingid': -1}, index=uids)

    df_cci = dw.to_dataframe('select * from bimodels.bm_clusting_centersinfo')  # df for bm_clusting_centersinfo
    df_pms = dw.to_dataframe(df_pms12_sql)  # bm_predictmodel_status 的 df 准备根据新算的更新
    r_kmeans = v_holder().pickup(df_pms.loc[0, 'obligate'])
    W_1 = df_w_1(df_cci.iloc[:, 2:22])

    for i in uids:
        dw_in = my_(config.MYSQL_BI_RW_ENV if datetime.datetime.now().hour else config.MYSQLs_BI_RW_ENV)
        df = dw_in.to_dataframe(user_order_sql_bi %(i,endtime))
        if df.__len__() < 2:
            dfr=dfr.drop(i)  # 1次加油的新用户不进入 bm_user_clusting_platfrom也不要他
            continue
        df = uo_df_p(df)
        df = uo_df_feed(df)

        df, dfr = df_userprofile_dfr(df,dfr,i)

        # bm_predictmodel_status 累计更新内容以及 bm_user_clusting_platfrom 每个uid的clusting中心和相关信息更新
        if dfr.loc[i, 'wcount'] > 6:
            X = np.array(dfr.loc[i:i, W_1.axes[0]] / W_1)
            n_center = int(r_kmeans.predict(X))
            n_dis = float(r_kmeans.transform(X)[0][n_center])
            df_last_ucp = dw_in.to_dataframe('select * from bimodels.bm_user_clusting_platfrom where uid = %s' % i)  # df for last bm_user_clusting_platfrom
            if df_last_ucp.__len__() < 1 or df_last_ucp.loc[0,'user_clustingid'] is None:
                num_add = 1
                dis_add = n_dis
            else:
                num_add = 0
                X = np.array(df_last_ucp.iloc[0:1, :20] / W_1)
                dis_add = n_dis - r_kmeans.transform(X)[0][int(r_kmeans.predict(X))]

            allerror = df_pms.loc[0, 'numb0'] * df_pms.loc[0, 'record1'] + dis_add
            df_pms.loc[0, 'record1'] += num_add
            df_pms.loc[0, 'numb0'] = allerror / df_pms.loc[0, 'record1']

            if dis_add > df_pms.loc[0, 'numb0'] or dis_add < - df_pms.loc[0, 'numb0']:
                print("dis_add:",dis_add,'; num_add:',num_add,'; numb0:',df_pms.loc[0, 'numb0'])

            dfr.loc[i, 'user_clustingid'] = n_center
            if df_last_ucp.__len__() and  n_center != df_last_ucp.loc[0,'user_clustingid']:
                if df_last_ucp.loc[0,'obligate']:
                    obi = json.loads(df_last_ucp.loc[0,'obligate'])
                    obi['ucid_changeroute'] += [n_center]
                    dfr.loc[i, 'obligate'] = "'%s'" % json.dumps(obi)
                else:
                    dfr.loc[i, 'obligate'] = "'%s'" % json.dumps({'ucid_changeroute': [n_center]})
                print('last_center:', df_last_ucp.loc[0,'user_clustingid'], dfr.loc[i, 'obligate'])

        # user_predict ###################--------------------------------
        if df.__len__() < 2:
            continue
        center_path = ''
        if dfr.loc[i, 'user_clustingid'] >= 0:
            try:
                center_path = df_cci.loc[dfr.loc[i, 'user_clustingid'],'obligate']
            except Exception as err:
                print('center_path get error :',err)
            # center_dtavg = df_cci.loc[dfr.loc[i, 'user_clustingid'],'dt_avg']
        gener = userdf_predict(df,dw_in,center_path)
        dw_in.c_conn(config.MYSQL_BI_RW_ENV)
        df_up_o = gener.__next__()  # df_up_o df_up_output or maybe an int (0,-1)  自从加了.copy()才解决了一个遗留已久的问题
        if type(df_up_o) is not int:
            df_up_o = df_add_singlequotemark(df_up_o.copy())
            df_up_o['update_time'] = 'now()'
            print('new record:',dw_in.df_upd_tosql(df_up_o, table='bimodels.bm_user_predict_record')
                  , '; delete:',dw_in.sql_engine('delete from bimodels.bm_user_predict_ where uid = %s' %i).rowcount)
        elif df_up_o == -1:
            print('0.05 have been perdicted :uid(%s) skip' %i)
            continue
        df_up_o = gener.__next__()
        print('uid:', df_up_o.loc[0, 'uid'],i, dw_in.df_upd_tosql(df_up_o,table='bimodels.bm_user_predict_'))
        # user_predict ###################
        dw_in.quit()

    dw.c_conn(config.MYSQL_BI_RW_ENV)
    df_pms['update_time'] = 'now()'
    df_pms = df_pms.loc[0:0, :]
    print('predictmodel_status:', dw.df_upd_tosql(df_pms.drop('obligate', 1),table='bimodels.bm_predictmodel_status')
          ,'插入user_clusting_platfrom:', dfr.__len__(),dw.df_upd_tosql(dfr, batch=1000, table='bimodels.bm_user_clusting_platfrom'))
    dw.quit()


def updateuser_profile(uids, endtime):
    # funct： 仅仅更新uid的行为侧写  init_env时使用
    dw = my_(config.MYSQL_BI_RW_ENV)
    dfr = pd.DataFrame(data={'uid': uids, 'wcount': 0, 'mainstid': 0, 'update_time': 'now()', 'user_clustingid': -1}, index=uids)
    for i in uids:

        df = dw.to_dataframe(user_order_sql_bi %(i,endtime))
        if df.__len__() < 2:
            dfr=dfr.drop(i)
            continue
        df = uo_df_p(df)
        df = uo_df_feed(df)

        # t1 = threading.Thread(target=df_userprofile_dfr, args=(df1, dfr, i, ))
        # t1.setDaemon(True)
        # t1.start()

        df, dfr = df_userprofile_dfr(df,dfr,i)

    print('开始插入dfr:', dfr.__len__())
    dw = my_(config.MYSQL_BI_RW_ENV)
    print(dw.df_upd_tosql(dfr, batch=1000, table='bimodels.bm_user_clusting_platfrom'))
    dw.quit()


def center_network_learning(endtime=1666666666):

    dw = my_(config.MYSQL_BI_RW_ENV)
    sqls_uidofclustingid = 'select uid from bimodels.bm_user_clusting_platfrom where user_clustingid = %s '

    df_pms = dw.to_dataframe(df_pms12_sql)
    r_kmeans = v_holder().pickup(df_pms.loc[0, 'obligate'])

    # =>更新bm_clusting_centersinfo
    df_ccif = dw.to_dataframe('select * from bimodels.bm_clusting_centersinfo')  # bm_clusting_centersinfo 的 df
    W_1 = df_w_1(df_ccif.iloc[:, 2:22])
    df_ccif = pd.DataFrame(r_kmeans.cluster_centers_, columns=df_ccif.iloc[:, 2:22].columns) * W_1
    df_ccif['clustingid'] = df_ccif.index
    df_ccif['update_time'] = 'now()'
    # =>更新bm_clusting_centersinfo的obligate

    for c in df_ccif['clustingid']:
        if int(c) != 1:
            continue
        tup15 = ()
        tup9 = ()
        for i in dw.to_dataframe(sqls_uidofclustingid % c)['uid']:
            df = dw.to_dataframe(user_order_sql_bi % (i, endtime))
            df = uo_df_p(df)
            df = uo_df_feed(df)
            dfp, df = df.iloc[-1, :], df.iloc[:-1, :]
            if df.__len__() > 6:
                ind, kmeans = kmeans_dprocess(np.matrix(df.dt).T, n_clusters=4)
                df = df[ind == False]
                if df.__len__() > 6:
                    da15 = nth_ladder_create(np.matrix(df[LIST_Seffectandy_columns]), N_Deffect_past_days)
                    da9 = np.matrix(df[LIST_Seffectandy_columns])
                    tup15 += (da15,)
                    tup9 += (da9,)
        allda15 = np.vstack(tup15)
        allda9 = np.vstack(tup9)
        df_ccif.loc[c, 'obligate'] = "'../.logs/values/bm_clusting_centersinfo_c%s'" % c
        center_path = eval(df_ccif.loc[c, 'obligate'])
        print('开始训练中心网络：c', c,center_path, allda15.shape, allda9.shape)

        '''# myRNN = tensor_con(RNN_Inodes, [7], ['tf.nn.tanh', 'tf.nn.sigmoid'], learnrate=0.1, Regu='0.0001*L1_loss')
        # myRNN.datainit(allda15, test_size=0.2).normalizy().normalizx().sessinit()
        # myRNN.networkfit_withCross(50001, batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True)
        # v_holder(myRNN.get_tfvalue()).store(center_path + '/RNN/pickle_layersW')
        # myRNN.net_save_restore(center_path + '/RNN/structure_15_7_1')
        # del myRNN
        # centernet_fit_save(allda15, center_path, tp='RNN')
        # task1 = multiprocessing.Process(target=centernet_fit_save, args=(allda15, center_path, 'RNN',))
        will be remove by 1.0'''

        task1 = multiprocessing.Process(target=net_creat_restore_fit_save_
          , args=(allda15, center_path
          , {'alter': 'RNNs', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
            , 'RELU_exp': '0.0001*L1_loss', 'test_size': 0.2}
          , dict(steps=520, batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True)))

        '''# myANN = tensor_con(ANN_Inodes, [7], ['tf.nn.tanh', 'tf.nn.sigmoid'], learnrate=0.1, Regu='0.0001*L1_loss').sessinit()
        # myANN.datainit(allda9, test_size=0.2).normalizy().normalizx()
        # myANN.networkfit_withCross(50001, batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True)
        # v_holder(myANN.get_tfvalue()).store(center_path + '/ANN/pickle_layersW')
        # myANN.net_save_restore(center_path + '/ANN/structure_9_7_1')
        # del myANN
        # centernet_fit_save(allda9, center_path, tp='ANN')
        # task2 = multiprocessing.Process(target=centernet_fit_save, args=(allda9, center_path, 'ANN',))
        will be remove by 1.0'''

        task2 = multiprocessing.Process(target=net_creat_restore_fit_save_
          , args=(allda9, center_path
          , {'alter': 'ANNs', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid']
            , 'RELU_exp': '0.0001*L1_loss', 'test_size': 0.2}
          , dict(steps=520, batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True)))
        nuv = [task1.start(),task2.start()]
        nuv = [task1.join(),task2.join()]

    print(dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df_ccif, table='bimodels.bm_clusting_centersinfo'))


def userclusting(endtime=1666666666,force=False):
    dw = my_(config.MYSQL_BI_RW_ENV)
    df_pms = dw.to_dataframe(df_pms12_sql + ' where mid = 1 ')  # bm_predictmodel_status 的 df
    if df_pms.__len__() and df_pms.loc[0, 'numb1'] > df_pms.loc[0, 'numb0'] and not force:
        print('no need to update userclusting ~ ')
        return
    df = dw.to_dataframe('select * from bimodels.bm_user_clusting_platfrom where uid > 0 and wcount > 6 ')

    W_1 = df_w_1(df.iloc[:, :20])
    X = np.array(df.iloc[:, :20] / W_1)

    s_nclusters = df_pms.loc[0, 'record0'] if df_pms.__len__() else 8  # 起始中心数
    Min_inertia = df_pms.loc[0, 'numb1'] if df_pms.__len__() else 998  # 平均误差阈值
    delta_inertia = -1
    last_inertia = df_pms.loc[0, 'numb0'] if df_pms.__len__() else 998
    for n in range(s_nclusters, s_nclusters + 10):
        kmeans = KMeans(n_clusters=n, max_iter=999)
        kmeans.fit(X)
        Mim = kmeans.inertia_ / X.shape[0]
        print(n, Mim, Min_inertia, delta_inertia)
        if Mim > Min_inertia:
            last_inertia = Mim
            continue
        elif last_inertia - Mim + 1 > delta_inertia:
            r_kmeans = kmeans
            delta_inertia = last_inertia - Mim
            last_inertia = Mim
            continue
        else:
            break

    # bm_predictmodel_status 的 df    =>更新 bm_predictmodel_status
    if df_pms.empty:
        df_pms = pd.DataFrame(
            {'mid': 1, 'minfo': "'行为聚类status. platfrom行为聚类模型状态: numb0-目前的平均误差; numb1-平均误差阈值; record0-聚类中心数; record1-样本总数'",
             'numb0': Mim, 'numb1': last_inertia + 1, 'record0': r_kmeans.n_clusters, 'record1': df.__len__(),
             'update_time': 'now()'}, index=[0])
    df_pms['record0'] = r_kmeans.n_clusters
    df_pms['record1'] = df.__len__()
    df_pms['numb0'] = Mim
    df_pms['numb1'] = last_inertia + 1
    df_pms.loc[0, 'obligate'] = "'../.logs/values/bm_clusting_centersinfo_kmeans'"
    v_holder(r_kmeans).store(eval(df_pms.loc[0, 'obligate']))
    df_pms['update_time'] = 'now()'
    print('df_pms:',dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df_pms, table='bimodels.bm_predictmodel_status'))

    # =>更新bm_user_clusting_platfrom 的 user_clustingid
    df.user_clustingid = r_kmeans.labels_
    df.update_time = 'now()'
    df.obligate = df.user_clustingid.map(lambda x:"'%s'" %json.dumps({'ucid_changeroute': [x]}))
    print(dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df[['uid', 'user_clustingid', 'update_time','obligate']], batch=1000
                                                         , table='bimodels.bm_user_clusting_platfrom'))
    center_network_learning(endtime)

# ************************************console***************************************


def threading_hold_print(stack_to, wait_to, sleept=5, flush_ss=' '*140+'stall waiting for: %s threads .... \r'):
    # console_afunc: console auxiliary
    #  stack_to 开始堵塞的进程数; wait_to 等到wait_to的进程数解除锁定 ; sleept
    if threading.activeCount() >= stack_to:
        while (threading.activeCount() > wait_to + 1):
            time.sleep(sleept)
            if len(flush_ss) >0:
                sys.stdout.write(flush_ss % (threading.activeCount()-1))
                sys.stdout.flush()


def devide_list(li,st=1,ed=1):
    # console_afunc: console auxiliary
    out = []
    while (li):
        indi = round(rand_ab(st, ed))
        out += [li[:indi]]
        li = li[indi:]
    return out


def get_endtime():
    dw = my_(config.MYSQL_BI_RW_ENV if datetime.datetime.now().hour else config.MYSQLs_BI_RW_ENV)
    df_pms2 = dw.to_dataframe("select record0 from bimodels.bm_predictmodel_status where mid = 2")
    endtime = day_forpast(-10, 0, 'stamp') if df_pms2.empty else df_pms2['record0'].iloc[0]
    dw.quit()
    return endtime


def get_todolist(dp):
    # console_afunc: console auxiliary
    upstate = ''
    dw = my_(config.MYSQL_BI_RW_ENV if datetime.datetime.now().hour else config.MYSQLs_BI_RW_ENV)
    sqlf = 'select uid from dw.dw_inspay_orders %s '
    if dp < 0:
        bestamp = day_forpast(dp, 0, 'stamp')
        bew = 'where pay_time >= %s' % bestamp
        endtime = 1666666666
    else:
        begintime = get_endtime()
        endtime = begintime + TIME_interval_s
        bew = 'where pay_time >= %s and pay_time <= %s' % (begintime, endtime)
        upstate = "update bimodels.bm_predictmodel_status set record0=%s,update_time=FROM_UNIXTIME(%s) where mid = 2" %(endtime,endtime)

    df = dw.to_dataframe(sqlf % bew)
    print(sqlf % bew)
    dw.c_conn(config.MYSQL_BI_RW_ENV).sql_engine(upstate)
    dw.quit()
    return list(set(df.uid)), endtime


def cons_userprofileing(dp=0,multiprocess=True):
    timer1 = Timer_(1)
    todolist,endtime = get_todolist(dp)
    remain = len(todolist)
    print('~~~~~go on cons_userprofileing()~~~~::: ', remain)
    processlist = []
    for a_list in devide_list(todolist,6,14):
        remain -= len(a_list)

        processlist.append(multiprocessing.Process(target=updateuser_profile_predict, args=(a_list,endtime,)))

        # t1 = threading.Thread(target=updateuser_profile_predict, args=(a_list, endtime,))
        # t1.setDaemon(True)
        # t1.start()
        # updateuser_profile_predict(uids=ali, endtime=endtime)
        # threading_hold_print(14, 10, sleept=5, flush_ss='')
        print('indi:: ', len(a_list), ';  remain:: ', remain, multiprocessing.current_process().name)
    # threading_hold_print(0, 0, sleept=2)
    if multiprocess:
        [p.start() for p in processlist]
        [p.join() for p in processlist]
    else :
        for p in processlist:
            p.start()
            p.join()
    # print('len(tf.global_variables())::: ',len(tf.global_variables()))
    timer1.toc()
    print('timertoc:::',timer1.alltoc[-1],(timer1.alltoc[-1]/TIME_interval_s)**-1,timer1.alltoc[-1]/(len(todolist)+1))
    return dp


def cons_makeup(tp=1):
    dw = my_(config.MYSQL_BI_RW_ENV if datetime.datetime.now().hour else config.MYSQLs_BI_RW_ENV)
    if tp == 1:
        dfuid = dw.to_dataframe(makeup_sql)
        uidlist = [r['uid'] for x, r in dfuid.iterrows()]
        endtime = get_endtime()
        print(uidlist)
        updateuser_profile_predict(uidlist,endtime)


def init_env(dp=-99):
    dw = my_(config.MYSQL_BI_RW_ENV)
    print(dw.sql_engine(bm_clusting_centersinfo_))
    print(dw.sql_engine(bm_user_clusting_platfrom_))
    print(dw.sql_engine(bm_predictmodel_status_))
    print(dw.sql_engine(bm_user_predict_record_))
    print(dw.sql_engine(bm_user_predict__))
    li,endtime = get_todolist(dp)

    while (li):
        indi = int(rand_ab(1000, 5000))
        print('indi::::: ', indi, ';  remain::::::::: ', len(li))

        t1 = threading.Thread(target=updateuser_profile, args=(li[:indi], endtime, ))
        t1.setDaemon(True)
        t1.start()
        threading_hold_print(14, 6, sleept=5, flush_ss='fthreads num: %s .. \r')
        # updateuser_profile(uids=, endtime=)
        li = li[indi:]
    threading_hold_print(1, 0 ,sleept=20)


    userclusting(endtime)

if __name__ == "__main__":
    print('hello console %s' %sys.path[0],sys.argv)
    if len(sys.argv) == 2:
        eval(sys.argv[1])
    else:
        # userclusting()
        print("rollback:", my_(config.MYSQL_BI_RW_ENV).sql_engine(CON_rollbacksql).rowcount)
        try:
            for ii in range(1009):
                print('ii::',ii)
                cons_userprofileing(0)
        except Exception as err:
            print('errflag0:',err)
            print("rollback:", my_(config.MYSQL_BI_RW_ENV).sql_engine(CON_rollbacksql).rowcount)
        cons_makeup()