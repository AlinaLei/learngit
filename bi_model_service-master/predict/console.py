#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# console of dataIO&dataprocess and Model choose
import threading, copy
import multiprocessing
from CreasAndsqls import *
from M_stat import *
from M_ML import *
from M_tensorML import *
import sys
sys.path.append('../DBbase')
from db_func import *

# global parameters:
Param = {'TIME_interval_s': 140, 'endtime': 1666666666, 'do_modelid': '2', 'delay_second': 600}
# dict can be modefied by func: get_todolist
# delay_second 始终会延迟于现实的时间，若要保证实时取0，现限于新订单的同步，延迟10分钟以保证不漏单
mgr = multiprocessing.Manager()
GLOBAL_userdfs = mgr.dict()
N_Deffect_past_days = 6
LIST_Seffectandy_columns = ['feed', 'liters', 'realprice', 'cd', 'cc', 'paytoc', 'yd', 'monthday', 'weekday', 'dt']
LIST_Closeadd_columns = ['liters', 'realprice', 'cd', 'cc', 'ordertimes']  # LIST_Closex_varx_varx_var_columns  间隔近的 需要合并成一次加油的
LIST_Closemax_columns = ['feed']
# ANN_Inodes = len(LIST_Seffectandy_columns) - 1
# RNN_Inodes = ANN_Inodes + N_Deffect_past_days
GLOBAL_NNS = {}
Timer0 = Timer_(0)


# funct: ##
def kmeans_dprocess(x_var, n_clusters=4):
    if x_var.__len__() < n_clusters:
        return 'simple size small than n_clusters(%s)' % n_clusters
    kmeans = KMeans(n_clusters=n_clusters)
    r_kmeans = kmeans.fit(x_var)
    x_mean = x_var.mean()
    ind = r_kmeans.labels_ == kmeans.n_clusters
    for mi in range(kmeans.n_clusters):
        indt = r_kmeans.labels_ == mi
        if r_kmeans.cluster_centers_[mi] > 2 * x_mean and r_kmeans.labels_[indt].__len__() / r_kmeans.labels_.__len__() < 0.144:
            # print(uid,r_kmeans.cluster_centers_[mi],x_mean,r_kmeans.labels_[indt].__len__(),r_kmeans.labels_.__len__())
            ind = ind | indt
        if r_kmeans.cluster_centers_[mi] > max_dt:
            ind = ind | indt
    return ind, kmeans


# funct:  用户订单df预处理 ##
def uo_df_p(df):
    # df['durt'] = df['pay_time'] - df['creat_time']
    df = df.fillna(0)
    df['dt'] = df['daytime'].diff()[1:].reset_index()['daytime']
    df['ordertimes'] = 1
    ind_tooclose = df[df.dt < 0.05].index  # 0.005等于432秒 去掉间隔太近的样本
    for i in ind_tooclose:
        df.loc[i+1, LIST_Closeadd_columns] += df.loc[i, LIST_Closeadd_columns]
        df.loc[i+1, LIST_Closemax_columns] = df.loc[i:i+1, LIST_Closemax_columns].max()
    df.drop(ind_tooclose, inplace=True)
    df = df.fillna(df.dt.mean())   # 最后一个需要预测的位置先填上均值
    return df


# funct:  用户订单df算加满率 ##
def uo_df_feed(df):
    df['feed']= 0  # feed 加满标识
    df.loc[df.op % 20 != 0 | (df.op < 50), 'feed'] = 1  # 加满
    df.loc[df.op > df.op.mean(), 'feed'] = 0.6  # 加半满
    return df


# lambda: 日期差和误差率
startdtime = datetime.datetime.strptime('20100101', "%Y%m%d")
datediff = lambda dy,dx: (dy - startdtime).days - (dx - startdtime).days
errrate = lambda yp,y: (yp-y)/(yp+0.01) if yp >= y else (y-yp)/(yp+0.01)


# 修正的误差率
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
    save_res = create_opt['save_res'] if 'save_res' in create_opt else ''
    if type(create_opt) == tensor_con:
        myNN = copy.deepcopy(create_opt)
        myNN.sessinit()
        NNname = myNN.name
    else:
        NNname = create_opt['alter']
        NN_Inodes = alldata.shape[1] - 1
        myNN = tensor_con(NN_Inodes, create_opt['hiden_layers'], create_opt['active_functions'],
                          learnrate=0.1, Regu=create_opt['RELU_exp'], name=NNname).sessinit()
        GLOBAL_NNS[myNN.name] = myNN

    if save_res == 'r' and center_path:
        net_path = '%s/%s/structure%s.CKPT' %(center_path, NNname, NNname)
        if path_exist(net_path):
            try:
                myNN.net_save_restore(net_path, 'restore')
            except Exception as err:
                print('restore_net Exception :', err, net_path, path_exist(net_path))
                # iter_mkdir(net_path)
    test_pre_size = fit_opt['test_size'] + 1 if fit_opt['test_size'] >= 1 else int(fit_opt['test_size'] * len(alldata)) + 1
    myNN.datainit(alldata, test_size=test_pre_size).normalizy('rel_n11').normalizx()
    if iter_fit:
        while(myNN.test_ind):
            myNN.networkfit_withCross(fit_opt['steps'], batch_train_lp=fit_opt['batch_train_lp'], op_oerr=fit_opt['op_oerr'],
                                      op_otimes=fit_opt['op_otimes'], eprint=fit_opt['eprint'], lprint=fit_opt['lprint'])
            myNN.netpredict(False)
            myNN.train_ind += [myNN.test_ind.pop(0)]
    else:
        myNN.networkfit_withCross(fit_opt['steps'], batch_train_lp=fit_opt['batch_train_lp'], op_oerr=fit_opt['op_oerr'],
                                  op_otimes=fit_opt['op_otimes'], eprint=fit_opt['eprint'], lprint=fit_opt['lprint'])
        myNN.netpredict(False)

    mynn_yp = myNN.Inverse_normaliz().yp_data[-test_pre_size:, 0]

    if save_res == 's':
        v_holder(myNN.get_tfvalue('layersW')).store('%s/%s/pickle_layersW' % (center_path, NNname))
        v_holder(myNN.get_tfvalue('layersb')).store('%s/%s/pickle_layersb' % (center_path, NNname))
        myNN.net_save_restore('%s/%s/structure%s.CKPT' %(center_path, NNname, NNname))

    if len(datao) >= 2:
        datao[0] = mynn_yp[:-1]
        datao[1] = mynn_yp[-1,-1]
        datao[2] = NNname
    return 0

NNS_copt_dicts = [{'save_res': 'r', 'alter': 'LR_15', 'hiden_layers': [], 'active_functions': ['tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'},
                  {'save_res': 'r', 'alter': 'RNN_15', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'},
                  {'save_res': 'r', 'alter': 'ANN_9', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'},
                  {'save_res': 'r', 'alter': '3RN_12', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'},
                  {'save_res': 'r', 'alter': '2RND_11', 'hiden_layers': [9, 3], 'active_functions': ['tf.nn.tanh', 'tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}]
net_mun = len(NNS_copt_dicts)


# funct:  用户订单df做预测 #
def userdf_predict(df, df_up, df_up_99, center_path):

    if df_up.__len__() > 0:
        if df['paytime'].iloc[-1] - df_up.loc[0, 'predict_time'] > datetime.timedelta(days=0.05):
            # print('发现已预测的验证::::', df_up.loc[0, 'uid'], df.iloc[-1, :], df_up)
            df_up.loc[0, 'real_time'] = df['paytime'].iloc[-1]
            if df['paytime'].iloc[-2] != df_up.loc[0, 'predict_time']:
                df_up.loc[0, 'obligate'] = df['paytime'].iloc[-2] - df_up.loc[0, 'predict_time']
            # df_up.loc[0, 'real_dt'] = df['dt'].iloc[-2]
            df_up.loc[0, 'real_dt'] = (df_up.loc[0, 'real_time'] - df_up.loc[0, 'predict_time']).total_seconds()/24/3600
            df_up.loc[0, 'rerror'] = df_up.loc[0, 'predict_dt'] - df_up.loc[0, 'real_dt']
            delta_p = datediff(df_up.loc[0, 'rewei_time'], df_up.loc[0, 'predict_time'])
            delta_r = datediff(df_up.loc[0, 'real_time'], df_up.loc[0, 'predict_time'])
            df_up.loc[0, 'derror'] = delta_p - delta_r
            df_up.loc[0, 'errorrate1'] = errrate(delta_p, delta_r)
            df_up.loc[0, 'errorrate2'] = errrate_x(delta_p, delta_r)
            try:
                df_up['real_dt'] = df_up['real_dt'].astype(float)
                df_up['rerror'] = df_up['rerror'].astype(float)
                df_up['errorrate1'] = df_up['errorrate1'].astype(float)
                df_up['errorrate2'] = df_up['errorrate2'].astype(float)
                df_up['derror'] = df_up['derror'].astype(int)
            except Exception as err_:
                print(err_, df_up)
                print(df)

            yield df_up
            # df_up.loc[0, 'predict_time']  df['paytime'].iloc[-1] 会不同嘛 ··
            df_up.drop(['real_time', 'real_dt', 'rerror', 'errorrate1', 'errorrate2', 'derror', 'obligate'], 1, inplace=True)
        else:
            yield -1  # will be continued
    else:
        yield 0
        df_up = df_up_99

    df_up.loc[0, 'predict_time'] = df['paytime'].iloc[-1]
    df_up.loc[0, 'uid'] = df['uid'].iloc[0]
    df_up.loc[0, 'paccuracy'] = 0.1
    if df.__len__() < 16:
        pre, probability, p = stat_pre(np.array(df['dt'].iloc[:-1]))
        df_up.loc[0, 'ptype'] = 1 if probability < 1 else 0
        df_up.loc[0, 'predict_dt'] = pre
        df_up.loc[0, 'modelpara'] = json.dumps({'cont': p, 'p_or_times': probability, 'strategy': '5'})
    else:
        modelchoice = {'errors': np.array([0.19, 0.2] + [0.0] * net_mun), 'improve': 0.0, 'times': 0}
        stind = int(df.__len__() * 0.88)
        if df_up.loc[0, 'modelchoice']:
            modelchoice1 = eval(df_up.loc[0, 'modelchoice'])
            if type(modelchoice1) is str:
                modelchoice1 = json.loads(modelchoice1)
            if len(modelchoice1['errors']) == 2 + net_mun:
                modelchoice1['errors'] = np.array(modelchoice1['errors'])
                stind = df.__len__() - 1
                modelchoice = modelchoice1

        datao_storage = eval('[%s]' % ','.join(["[0, 0, '']"] * net_mun))
        test_times = df.__len__() - stind
        np_dfe = np.matrix(df[LIST_Seffectandy_columns])
        np_dfe_6 = nth_ladder_create(np_dfe, N_Deffect_past_days)
        np_dfe_3 = nth_ladder_create(np_dfe, 3)
        np_dfe_2 = nth_ladder_create(np_dfe, 2)
        tasklist = []
        # GLOBAL_NNS[NN1dict['alter']] if NN1dict['alter'] in GLOBAL_NNS else NN1dict,
        nns_fopt_dict = dict(test_size=test_times, steps=66, batch_train_lp=1, op_oerr=0.0002, op_otimes=3,
                             eprint=False, lprint=False)
        task1 = threading.Thread(target=net_creat_restore_fit_save_,
                                 args=(np_dfe_6, center_path, NNS_copt_dicts[0], nns_fopt_dict,
                                       datao_storage[0], True,))
        tasklist += [task1]
        task2 = threading.Thread(target=net_creat_restore_fit_save_,
                                 args=(np_dfe_6, center_path, NNS_copt_dicts[1], nns_fopt_dict,
                                       datao_storage[1], True,))
        tasklist += [task2]
        task3 = threading.Thread(target=net_creat_restore_fit_save_,
                                 args=(np_dfe, center_path, NNS_copt_dicts[2], nns_fopt_dict,
                                       datao_storage[2], True,))
        tasklist += [task3]
        task4 = threading.Thread(target=net_creat_restore_fit_save_,
                                 args=(np_dfe_3, center_path, NNS_copt_dicts[3], nns_fopt_dict,
                                       datao_storage[3], True,))
        tasklist += [task4]
        task5 = threading.Thread(target=net_creat_restore_fit_save_,
                                 args=(np_dfe_2, center_path, NNS_copt_dicts[4], nns_fopt_dict,
                                       datao_storage[4], True,))
        tasklist += [task5]
        [p.setDaemon(True) for p in tasklist]
        [p.start() for p in tasklist]
        dtmean = df['dt'].iloc[:-1].mean()
        pre, probability, p = stat_pre(np.array(df['dt'].iloc[:-1]))
        [p.join() for p in tasklist]

        real_arr = np.array(df['dt'].iloc[-(test_times+1):-1])
        testerror = [errorsum(dtmean, real_arr)] + [errorsum(pre, real_arr)] + [errorsum(datao_storage[i][0].T, real_arr) for i in range(net_mun)]
        modelchoice['errors'] += np.array(testerror)
        modelchoice['times'] += test_times
        prearray = np.array([dtmean, pre] + [d[1] for d in datao_storage])
        conlist = ['E', p] + [d[2] for d in datao_storage]
        prelist = prearray.round(3).tolist()
        print(prelist, df['dt'].iloc[-1], modelchoice['errors'].round(3).tolist(), modelchoice['times'], test_times, end='>>')

        df_up.loc[0, 'ptype'] = int(modelchoice['errors'].argsort()[0])
        df_up.loc[0, 'paccuracy'] = 0.1 + 0.03 * int(df_up.loc[0, 'ptype']/2)
        df_up.loc[0, 'predict_dt'] = prelist[df_up.loc[0, 'ptype']]
        df_up.loc[0, 'modelpara'] = json.dumps({'cont': conlist[df_up.loc[0, 'ptype']], 'p_or_times': df.__len__(), 'strategy': '5'})
        modelchoice['improve'] = round(1 - modelchoice['errors'][df_up.loc[0, 'ptype']] / modelchoice['errors'].mean(), 2)
        modelchoice['errors'] = modelchoice['errors'].round(2).tolist()
        df_up.loc[0, 'modelchoice'] = json.dumps(modelchoice)

    df_up.loc[0, 'rewei_time'] = df_up.loc[0, 'predict_time'] + datetime.timedelta(days=float(df_up.loc[0, 'predict_dt']))
    df_up = df_add_singlequotemark(df_up)
    df_up['update_time'] = 'now()'
    yield df_up


# funct： 由N维df获取因素权重 #
def df_w_1(dfw):
    w_1 = dfw.max()
    w_1[:] = 1
    w_1['uid', 'mainstid'] = 10000000  # uid mainstid缩小1千万倍
    w_1['realprice_std0', 'liters_std0'] = 1000
    w_1['realprice_avg', 'liters_avg', 'paytoc_avg', 'paytoc_std0', 'monthday_avg', 'monthday_std0'] = 10
    return w_1


# funct: df_upd_dfr 由df 更新 user_profile dfr #
def df_userprofile_dfr(df, dfr):
    # user_profile ##############----------------------------------------------------------------------------------------------
    i = df['uid'].iloc[0]
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
        ind, kmeans = kmeans_dprocess(np.matrix(df_1.dt).T, n_clusters=3)
        dfr.loc[i, 'dto_max'] = df_1[~ind].dt.max()
        dfr.loc[i, 'dt_clustinginfo'] = "'%s'" % json.dumps(
            {'cluster_centers_': kmeans.cluster_centers_.tolist(), 'drop_num': df_1[ind].__len__()})
        ind = np.hstack([ind, np.array([False])])
        # df = df[~ind]
        df['dt'].clip(0, df['dt'][~ind].max())
    return df, dfr


def updateuser_profile_predict(dfs_d, uids):
    #  *endtimes):
    # funct： 更新uid的行为侧写和预测
    # endtime = endtimes[0] if endtimes else Param['endtime']
    dw = my_(config.MYSQL_BI_RW_ENV)
    dfr = pd.DataFrame(data={'uid': uids, 'wcount': 0, 'mainstid': 0, 'update_time': 'now()', 'user_clustingid': -1}, index=uids)
    df_pms = dw.to_dataframe(df_pms12_sql)  # bm_predictmodel_status 的 df 准备根据新算的更新
    if 'r_kmeans' in Param:
        r_kmeans = Param['r_kmeans']
    else:
        r_kmeans = v_holder().pickup(df_pms.loc[0, 'obligate'])
        Param.update({'r_kmeans': r_kmeans})

    df_cci = dw.to_dataframe('select * from bimodels.bm_clusting_centersinfo')  # df for bm_clusting_centersinfo
    w_1 = df_w_1(df_cci.iloc[:, 2:22])
    dw_in = my_(config.MYSQL_BI_RW_ENV)
    df_up_99 = dw_in.to_dataframe('select * from bimodels.bm_user_predict_ where uid = -999999 ')   # 如果没有的话  初始化一个df_up_99
    for i in uids:
        df = dfs_d[i]    # .copy()
        # df = dw_in.to_dataframe(user_order_sql_o % (i, endtime))
        if df.__len__() < 2:
            dfr.drop(i, inplace=True)  # 1次加油的新用户不进入 bm_user_clusting_platform也不记录
            continue

        df_up = dw.to_dataframe('select * from bimodels.bm_user_predict_ where uid = %s limit 1' % df['uid'].iloc[0])  # user_predict df
        df = uo_df_feed(df)
        df = uo_df_p(df)

        df, dfr = df_userprofile_dfr(df, dfr)

        # bm_predictmodel_status 累计更新内容以及 bm_user_clusting_platform 每个uid的clusting中心和相关信息更新
        if dfr.loc[i, 'wcount'] > 6:
            x_var = np.array(dfr.loc[i:i, w_1.axes[0]] / w_1)
            n_center = int(r_kmeans.predict(x_var))
            n_dis = float(r_kmeans.transform(x_var)[0][n_center])
            df_last_ucp = dw_in.to_dataframe('select * from bimodels.bm_user_clusting_platform where uid = %s' % i)  # df for last bm_user_clusting_platform
            if df_last_ucp.__len__() < 1 or df_last_ucp.loc[0, 'user_clustingid'] is None:
                num_add = 1
                dis_add = n_dis
            else:
                num_add = 0
                x_var = np.array(df_last_ucp.iloc[0:1, :20] / w_1)
                dis_add = n_dis - r_kmeans.transform(x_var)[0][int(r_kmeans.predict(x_var))]

            allerror = df_pms.loc[0, 'numb0'] * df_pms.loc[0, 'record1'] + dis_add
            df_pms.loc[0, 'record1'] += num_add
            df_pms.loc[0, 'numb0'] = allerror / df_pms.loc[0, 'record1']

            if dis_add > df_pms.loc[0, 'numb0'] or dis_add < -df_pms.loc[0, 'numb0']:  # 暂时写的有问题  目前不会进入这里
                print("dis_add:",dis_add,'; num_add:',num_add,'; numb0:',df_pms.loc[0, 'numb0'])

            dfr.loc[i, 'user_clustingid'] = n_center
            if df_last_ucp.__len__() and n_center != df_last_ucp.loc[0,'user_clustingid']:
                if df_last_ucp.loc[0, 'obligate']:
                    obi = json.loads(df_last_ucp.loc[0,'obligate'])
                    obi['ucid_changeroute'] += [n_center]
                    dfr.loc[i, 'obligate'] = "'%s'" % json.dumps(obi)
                else:
                    dfr.loc[i, 'obligate'] = "'%s'" % json.dumps({'ucid_changeroute': [n_center]})
                # print('last_center:', df_last_ucp.loc[0,'user_clustingid'], dfr.loc[i, 'obligate'], )

        # user_predict -------------------------------------------###################------------------------------------------------------
        if df.__len__() < 3:
            continue
        center_path = ''
        if dfr.loc[i, 'user_clustingid'] >= 0:
            try:
                center_path = df_cci.loc[dfr.loc[i, 'user_clustingid'], 'obligate']
            except Exception as err:
                print('center_path get error :', err)
            # center_dtavg = df_cci.loc[dfr.loc[i, 'user_clustingid'],'dt_avg']
        gener = userdf_predict(df, df_up, df_up_99, center_path)
        # dw_in.c_conn(config.MYSQL_BI_RW_ENV)
        df_up_o = gener.__next__()  # df_up_o df_up_output or maybe an int (0,-1)  自从加了.copy()才解决了一个遗留已久的问题
        if type(df_up_o) is int and df_up_o == -1:
            print('0.05 have been perdicted :uid(%s) skip' % i)
            continue
        elif type(df_up_o) is not int:
            df_up_o = df_add_singlequotemark(df_up_o.copy())
            df_up_o['update_time'] = 'now()'
            print('new record:', dw_in.df_upd_tosql(df_up_o, table='bimodels.bm_user_predict_record')
                  , '; del:', [dw_in.sql_engine('delete from bimodels.bm_user_predict_ where uid = %s' % i)], end='>>>')
        df_up_o = gener.__next__()
        print('uid:', i, 'len:',df.__len__(), dw_in.df_upd_tosql(df_up_o,table='bimodels.bm_user_predict_'))
        # user_predict --------------------------------------------###################------------------------------------------------------

    dw.c_conn(config.MYSQL_BI_RW_ENV)
    df_pms['update_time'] = 'now()'
    df_pms = df_pms.loc[0:0, :]
    print('predictmodel_status:', dw.df_upd_tosql(df_pms.drop('obligate', 1), table='bimodels.bm_predictmodel_status'),
          '插入user_clusting_platform:', dfr.__len__(), dw.df_upd_tosql(dfr, batch=1000, table='bimodels.bm_user_clusting_platform'))


def updateuser_profile(uids, *endtimes):
    # funct： 仅仅更新uid的行为侧写  init_env时使用
    dw = my_(config.MYSQL_BI_RW_ENV)
    dfr = pd.DataFrame(data={'uid': uids, 'wcount': 0, 'mainstid': 0, 'update_time': 'now()', 'user_clustingid': -1}, index=uids)
    endtime = endtimes[0] if endtimes else Param['endtime']
    for i in uids:

        df = dw.to_dataframe(user_order_sql_o %(i,endtime))
        if df.__len__() < 2:
            dfr.drop(i, inplace=True)
            continue
        df = uo_df_feed(df)
        df = uo_df_p(df)
        df, dfr = df_userprofile_dfr(df,dfr)

    print('开始插入dfr:', dfr.__len__())
    dw = my_(config.MYSQL_BI_RW_ENV)
    print(dw.df_upd_tosql(dfr, batch=1000, table='bimodels.bm_user_clusting_platform'))
    dw.quit()


def center_network_learning():
    print('开始基于聚类的初始化网络')
    dw = my_(config.MYSQL_BI_RW_ENV)
    sqls_uidofclustingid = 'select uid from bimodels.bm_user_clusting_platform where user_clustingid = %s and wcount>2'

    df_pms = dw.to_dataframe(df_pms12_sql)
    r_kmeans = v_holder().pickup(df_pms.loc[0, 'obligate'])

    # =>更新bm_clusting_centersinfo
    df_ccif = dw.to_dataframe('select * from bimodels.bm_clusting_centersinfo')  # bm_clusting_centersinfo 的 df
    w_1 = df_w_1(df_ccif.iloc[:, 2:22])
    df_ccif = pd.DataFrame(r_kmeans.cluster_centers_, columns=df_ccif.iloc[:, 2:22].columns) * w_1
    df_ccif['clustingid'] = df_ccif.index
    df_ccif['update_time'] = 'now()'
    # =>更新bm_clusting_centersinfo的obligate

    NN1dict = {'save_res': 's', 'alter': 'ROL_15', 'hiden_layers': [], 'active_functions': ['tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}
    NN2dict = {'save_res': 's', 'alter': 'RNN_15', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}
    NN3dict = {'save_res': 's', 'alter': 'ANN_9', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}
    NN4dict = {'save_res': 's', 'alter': '3RN_12', 'hiden_layers': [7], 'active_functions': ['tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}
    NN5dict = {'save_res': 's', 'alter': '2RND_11', 'hiden_layers': [9, 3], 'active_functions': ['tf.nn.tanh', 'tf.nn.tanh', 'tf.nn.sigmoid'], 'RELU_exp': '0.01*L1_loss'}
    nns_fopt_dict = dict(test_size=0.2, steps=520, batch_train_lp=0, op_oerr=0.0002, op_otimes=2, eprint=True, lprint=True)

    for c in df_ccif['clustingid']:
        tup15 = ()
        tup12 = ()
        tup11 = ()
        tup9 = ()
        print('(clustingid=%s)收集数据' % c)
        for uid in dw.to_dataframe(sqls_uidofclustingid % c)['uid']:
            print(uid,end='|')
            df = dw.to_dataframe(user_order_sql_o % (uid, Param['endtime']))
            df = uo_df_feed(df)
            df = uo_df_p(df)
            if df.__len__() > 10:
                print('')
                da15 = nth_ladder_create(np.matrix(df[LIST_Seffectandy_columns]), N_Deffect_past_days)
                da12 = nth_ladder_create(np.matrix(df[LIST_Seffectandy_columns]), 3)
                da11 = nth_ladder_create(np.matrix(df[LIST_Seffectandy_columns]), 2)
                da9 = np.matrix(df[LIST_Seffectandy_columns])
                tup15 += (da15,)
                tup12 += (da12,)
                tup11 += (da11,)
                tup9 += (da9,)
        allda15 = np.vstack(tup15)
        allda12 = np.vstack(tup12)
        allda11 = np.vstack(tup11)
        allda9 = np.vstack(tup9)
        df_ccif.loc[c, 'obligate'] = "'../.logs/values/bm_clusting_centersinfo_c%s'" % c
        center_path = eval(df_ccif.loc[c, 'obligate'])
        print('开始训练中心网络：c', c, center_path, allda15.shape, allda9.shape)
        tasks = []
        tasks.append(multiprocessing.Process(target=net_creat_restore_fit_save_,
                                             args=(allda15, center_path, NN1dict, nns_fopt_dict)))
        tasks.append(multiprocessing.Process(target=net_creat_restore_fit_save_,
                                             args=(allda15, center_path, NN2dict, nns_fopt_dict)))
        tasks.append(multiprocessing.Process(target=net_creat_restore_fit_save_,
                                             args=(allda9, center_path, NN3dict, nns_fopt_dict)))
        tasks.append(multiprocessing.Process(target=net_creat_restore_fit_save_,
                                             args=(allda12, center_path, NN4dict, nns_fopt_dict)))
        tasks.append(multiprocessing.Process(target=net_creat_restore_fit_save_,
                                             args=(allda11, center_path, NN5dict, nns_fopt_dict)))
        for T in tasks:
            T.start()
            T.join()
    print(dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df_ccif, table='bimodels.bm_clusting_centersinfo'))


def userclusting(force=False):
    dw = my_(config.MYSQL_BI_RW_ENV)
    df_pms = dw.to_dataframe(df_pms12_sql + ' and mid = 1 ')  # bm_predictmodel_status 的 df
    if df_pms.__len__() and df_pms.loc[0, 'numb1'] > df_pms.loc[0, 'numb0'] and not force:
        print('no need to update userclusting ~ ')
        return
    df = dw.to_dataframe('select * from bimodels.bm_user_clusting_platform where uid > 0 and wcount > 6 ')

    w_1 = df_w_1(df.iloc[:, :20])
    x_var = np.array(df.iloc[:, :20] / w_1)
    print(x_var.__len__())

    s_nclusters = df_pms.loc[0, 'record0'] if df_pms.__len__() else 8  # 起始中心数
    Min_inertia = df_pms.loc[0, 'numb1'] if df_pms.__len__() else 998  # 平均误差阈值
    delta_inertia = -1
    last_inertia = df_pms.loc[0, 'numb0'] if df_pms.__len__() else 998
    Mim = 0
    r_kmeans = KMeans(n_clusters=s_nclusters - 1, max_iter=999)
    r_kmeans.fit(x_var)
    for n in range(s_nclusters, s_nclusters + 10):
        kmeans = KMeans(n_clusters=n, max_iter=999)
        kmeans.fit(x_var)
        Mim = kmeans.inertia_ / x_var.shape[0]
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
            {'mid': 1, 'minfo': "'行为聚类status. platform行为聚类模型状态: numb0-目前的平均误差; numb1-平均误差阈值; record0-聚类中心数; record1-样本总数'",
             'numb0': Mim, 'numb1': last_inertia + 1, 'record0': r_kmeans.n_clusters, 'record1': df.__len__(),
             'update_time': 'now()'}, index=[0])
    df_pms['record0'] = r_kmeans.n_clusters
    df_pms['record1'] = df.__len__()
    df_pms['numb0'] = Mim
    df_pms['numb1'] = last_inertia + 1
    df_pms.loc[0, 'obligate'] = "'../.logs/values/bm_clusting_centersinfo_kmeans'"
    v_holder(r_kmeans).store(eval(df_pms.loc[0, 'obligate']))
    df_pms['update_time'] = 'now()'
    print('df_pms:', dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df_pms, table='bimodels.bm_predictmodel_status'))

    # =>更新bm_user_clusting_platform 的 user_clustingid
    df.user_clustingid = r_kmeans.labels_
    df.update_time = 'now()'
    df.obligate = df.user_clustingid.map(lambda x: "'%s'" %json.dumps({'ucid_changeroute': [x]}))
    print(dw.c_conn(config.MYSQL_BI_RW_ENV).df_upd_tosql(df[['uid', 'user_clustingid', 'update_time', 'obligate']],
                                                         batch=1000, table='bimodels.bm_user_clusting_platform'))
    center_network_learning()

# ************************************************************************************console***************************************************************************************


def threading_hold_print(stack_to, wait_to, sleept=5, flush_ss=' '*140+'stall waiting for: %s threads .... \r'):
    # console_afunc: console auxiliary
    #  stack_to 开始堵塞的进程数; wait_to 等到wait_to的进程数解除锁定 ; sleept
    if threading.activeCount() >= stack_to:
        while threading.activeCount() > wait_to + 1:
            time.sleep(sleept)
            if len(flush_ss) > 0:
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


def get_endtime(rsimutime=False):
    if rsimutime:
        endtime = rsimutime
    else:
        dw = my_(config.MYSQL_BI_RW_ENV)
        df_pms2 = dw.to_dataframe("select record0 from bimodels.bm_predictmodel_status where mid = %s" % Param['do_modelid'])
        endtime = day_forpast(-10, 0, 'stamp') if df_pms2.empty else df_pms2['record0'].iloc[0]
        dw.quit()
    return endtime


def runtime_todolist(rsimutime):
    dw = my_(config.MYSQL_BI_RW_ENV)
    sqlh = SqlHandler(user_order_sql_on)
    begintime = get_endtime(rsimutime)
    if 'run_timestamp' in GLOBAL_userdfs and GLOBAL_userdfs['run_timestamp'] < begintime:
        print('GLOBAL_userdfs 需要补全%ss' %begintime - GLOBAL_userdfs['run_timestamp'], )
        begintime = int(GLOBAL_userdfs['run_timestamp'])
    Param['endtime'] = begintime + Param['TIME_interval_s']
    Param['begindate'] = time.strftime("%Y-%m-%d", time.localtime(begintime+0.5))
    Param['enddate'] = time.strftime("%Y-%m-%d", time.localtime(Param['endtime']))
    cond = {'pay_time >= ': begintime+0.5, 'pay_time <= ': Param['endtime']
            , 'O.batch_date >= ':Param['begindate'], 'O.batch_date <= ':Param['enddate']
            , 'merchant_id in ': Param['merchant_id in '] if 'merchant_id in ' in Param else ''
           }
    Timer0.runtime_delay(day_forpast(ss='stamp') - Param['endtime'] - Param['delay_second']).toc(True)
    df = dw.to_dataframe(sqlh.render_sqls(cond))
    for i,row in df.iterrows():
        uid = int(row['uid'])
        if uid in GLOBAL_userdfs:
            if GLOBAL_userdfs[uid].query('pay_time>=%s' % row.pay_time).__len__() == 0:
                L_ = GLOBAL_userdfs[uid].__len__()
                GLOBAL_userdfs[uid] = GLOBAL_userdfs[uid].append(row, ignore_index=True)
                print('GLOBAL_userdfs working::', uid, L_, GLOBAL_userdfs[uid].__len__())
            else:
                print(uid,'have this order',GLOBAL_userdfs[uid].query('pay_time>=%s' % row.pay_time).__len__(),GLOBAL_userdfs[uid].__len__())
        else:
            cond_uid = {'O.batch_date <= ': Param['enddate'], 'user_id in ': uid}
            GLOBAL_userdfs[uid] = dw.to_dataframe(sqlh.render_sqls(cond_uid))
    GLOBAL_userdfs.update({'run_timestamp': Param['endtime']})
    print(len(GLOBAL_userdfs),len(df))
    if not rsimutime:
        dw.c_conn(config.MYSQL_BI_RW_ENV).sql_engine(CON_updatesql % Param)
    return list(set(df.uid))


def cons_userprofileing(dp=0, rsimutime=False, multiprocess=True):
    # rsimutime模拟时间(只能在dp=0时用) 有值则不影响status mid=2  default False :正常模式
    todolist = runtime_todolist(rsimutime)
    Timer0.toc(True)
    remain = len(todolist)
    print('~~~~~~~~~go on cons_userprofileing()~~~~~~~~~~ 这一波的样本数:::', remain)
    processlist = []
    # processlist = multiprocessing.Pool(26)
    for a_list in devide_list(todolist, 6, 14):
        remain -= len(a_list)

        processlist.append(multiprocessing.Process(target=updateuser_profile_predict, args=(GLOBAL_userdfs,a_list,)))
        # processlist.apply_async(updateuser_profile_predict, args=(a_list, Param['endtime'],))

        # t1 = threading.Thread(target=updateuser_profile_predict, args=(a_list, Param['endtime'],))
        # t1.setDaemon(True)
        # t1.start()
        # updateuser_profile_predict(uids=ali, endtime=Param['endtime'])
        # threading_hold_print(14, 10, sleept=5, flush_ss='')
        print('indi:: ', len(a_list), ';  remain:: ', remain, multiprocessing.current_process().name)
        time.sleep(0.03)
    # threading_hold_print(0, 0, sleept=2)
    # processlist.close()
    # processlist.join()
    if multiprocess:
        # for p in processlist:
        #     p.daemon = True
        [p.start() for p in processlist]
        [p.join(Param['TIME_interval_s']) for p in processlist]
        [p.terminate() for p in processlist]
    else:
        for p in processlist:
            p.start()
            p.join(Param['TIME_interval_s'])
            p.terminate()
    Timer0.toc(True)
    print('timer:', Timer0.tictoc, (Timer0.tictoc[-1]/Param['TIME_interval_s'])**-1, Timer0.tictoc[-1]/(len(todolist)+1))
    Timer0.__init__(0)


def cons_makeup(tp=1):
    dw = my_(config.MYSQL_BI_RW_ENV)
    sqlh = SqlHandler(user_order_sql_on)
    if tp == 1:
        dfuid = dw.to_dataframe(makeup_sql)
        uidlist = [r['uid'] for x, r in dfuid.iterrows()]
        for uid in uidlist:
            cond_uid = {'O.batch_date <= ': Param['enddate'], 'user_id in ': uid}
            GLOBAL_userdfs[uid] = dw.to_dataframe(sqlh.render_sqls(cond_uid))
        endtime = get_endtime()
        print(uidlist)
        updateuser_profile_predict(GLOBAL_userdfs,uidlist)


def get_todolist(dp,rsimutime):
    # console_afunc: console auxiliary
    # do with the Param
    upstate = ''

    dw = my_(config.MYSQL_BI_RW_ENV)
    sqlf = 'select user_id uid from ods.ods_wei_order_info '
    if dp < 0:
        begintime = day_forpast(dp, 0, 'stamp')
        bew = 'where pay_time >= %s' % begintime
        Param['endtime'] = 1666666666
    else:
        begintime = get_endtime(rsimutime)
        Param['endtime'] = begintime + Param['TIME_interval_s']
        Timer0.runtime_delay(day_forpast(ss='stamp') - Param['endtime'] - Param['delay_second']).toc(True)
        bew = "pay_time >= %s and pay_time <= %s" % (begintime, Param['endtime'])
        upstate = CON_updatesql % Param

    begindate = time.strftime("%Y-%m-%d", time.localtime(begintime))
    enddate = time.strftime("%Y-%m-%d", time.localtime(Param['endtime']))
    bewhere = """where batch_date >= '%s' and batch_date <= '%s' and user_id > 0 
                 and merchant_id not in (171073,177370,177619,176669,177525,10258,10261) and is_suborder = 1 
                 and order_status in (1160,2010)  and %s""" % (begindate, enddate, bew) \
                 + (Param['merchants_ss'] if 'merchants_ss' in Param else '')   # for grey 只做灰度测试那些油站
    print(sqlf + bewhere)
    df = dw.to_dataframe(sqlf + bewhere)
    if not rsimutime:
        dw.c_conn(config.MYSQL_BI_RW_ENV).sql_engine(upstate)
    dw.quit()
    return list(set(df.uid))


def init_env(dp=-99):
    dw = my_(config.MYSQL_BI_RW_ENV)
    print(dw.sql_engine(bm_clusting_centersinfo_))
    print(dw.sql_engine(bm_user_clusting_platform_))
    print(dw.sql_engine(bm_predictmodel_status_))
    print(dw.sql_engine(bm_user_predict_record_))
    print(dw.sql_engine(bm_user_predict__))
    li, endtime = get_todolist(dp, False)

    while (li):
        indi = int(rand_ab(1000, 5000))
        print('indi::::: ', indi, ';  remain::::::::: ', len(li))

        t1 = threading.Thread(target=updateuser_profile, args=(li[:indi], endtime, ))
        t1.setDaemon(True)
        t1.start()
        threading_hold_print(14, 6, sleept=5, flush_ss='fthreads num: %s .. \r')
        # updateuser_profile(uids=, endtime=)
        li = li[indi:]
    threading_hold_print(1, 0, sleept=20)


    userclusting(endtime)

if __name__ == "__main__":

    print('hello console %s' % sys.path[0],sys.argv)
    if len(sys.argv) == 2:
        eval(sys.argv[1])
    else:
        if 'GREY_TEST' in os.environ and os.environ['GREY_TEST'] == '-2':
            Param.update({'TIME_interval_s': 600, 'do_modelid': '-2',
                          'merchants_ss': " and merchant_id in (159690,119296,177397,117491,177372,117491,176558,176820,8178,10473,163201,163240,163202,177549)",
                          'merchant_id in ': "159690,119296,177397,117491,177372,117491,176558,176820,8178,10473,163201,163240,163202,177549"
                        })  # for grey 只做灰度测试那些油站
        print("rollback:", my_(config.MYSQL_BI_RW_ENV).sql_engine(CON_rollbacksql % Param))
        try:
            for ii in range(666667):
                print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), ' ii::', ii)
                cons_userprofileing(0)  # , multiprocess=False)
        except Exception as err:
            print('errflag:(consoleERR)', err, err.args[0])
            print("rollback:", my_(config.MYSQL_BI_RW_ENV).sql_engine(CON_rollbacksql % Param))
        cons_makeup()