#!/usr/local/bin/python3
import click,subprocess,re,copy,json,sys,pprint,datetime,time,getopt
import random,threading
# from jinja2 import Template
import flask
from flask import Flask,request,session,render_template,url_for,redirect,send_from_directory
from flask_login import *
from flask_plotfunc import *
import sys
# sys.path.append('../DBbase')
# from db_func import *
# from hcomponents import *
# sys.path.append('../.settings')
# from config import *
sys.path.append('../predict')
from simple_func_backp import *

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?R2'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, ename, id, active=True,authenticated=True):
        self.name = ename
        self.id = id
        self.active = active
        self.authenticated=authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.active == False
    @property
    def is_authenticated(self):
        return self.authenticated


def add_transferm(ss):
    special_s_list = ['(', ')']
    for x in special_s_list:
        ss = ss.replace(x, '\\' + x)
    return ss


class WebInstance():
    sqlb_all = {}
    ppath_now = ""
    tas = ".."
    today = day_forpast(0)
    yesterday = day_forpast(-1)
    ppath = "../Webserver/"
    fpath="http://%s:%s/" %(config.WBASE['WEBserver'], config.WBASE['FILE_PORT'])
    download_path="http://%s:%s/" %(config.WBASE['WEBserver'], config.WBASE['DOWNLOAD_PORT'])
    dpath = "../.data/"
    # hql_log="/home/bi/gitpro/tmp/hql_log";log_num=0
    REF_url="http://%s:%s/shortcut/maindir/S2_sallocation_diff" %(config.WBASE['WEBserver'],config.WBASE['WEB_PORT'])
    task_cres="""create table data_center.dc_S2_taskinfo (id INT AUTO_INCREMENT,uid int(8),uname varchar(24),task_tag varchar(34),task_cond varchar(3344),status int(3) default -1,CreateTime datetime,updateTime datetime,path varchar(333),cod char(4),explain1 text,explain2 text,PRIMARY KEY (id) );"""
    task_ins="""insert into data_center.dc_S2_taskinfo(uid,uname,task_tag,task_cond,CreateTime) values(%s,'%s','%s','%s',now())"""
    task_upd="""update data_center.dc_S2_taskinfo set updateTime=now(),status=%s,path='%s',cod='%s',explain1='%s' where id = %s """
    get_taskid = "SELECT max(id) maxid from data_center.dc_S2_taskinfo"
    q_task="select status,unix_timestamp(now())-unix_timestamp(CreateTime) dur,path,cod,explain1 from data_center.dc_S2_taskinfo where id=%s"
    list_task="select *,unix_timestamp(updateTime)-unix_timestamp(CreateTime) dur from data_center.dc_S2_taskinfo where %s order by CreateTime desc"

    ln_cres="create table S2_logincount as select %s employeeid,'%s' ename,'%s' email,now() CreateTime,now() LastLoginTime,0 logincounts"
    ln_upd="update S2_logincount set LastLoginTime=now(),logincounts=logincounts+1%s where employeeid = %s "
    ln_ins="insert into S2_logincount select %s employeeid,'%s' ename,'%s' email,now() CreateTime,now() LastLoginTime,0 logincounts"
    last_ln="select *,(unix_timestamp(now())-unix_timestamp((LastLoginTime)))/3600 h,datediff(now(),LastLoginTime) d from S2_logincount where employeeid=%s"

    def tic(self):
        self.ttic=datetime.datetime.now()
        print("tic at:: %s" %self.ttic)
        return self.ttic

    def toc(self):
        self.ttoc=datetime.datetime.now()
        dt=self.ttoc-self.ttic
        sec=dt.seconds+dt.microseconds/1000000; mi=int(sec/60); takens=" TIME Taken:: %s min %.6f sec" %(mi,sec%60)
        print("toc at:: %s" %datetime.datetime.now()+" ( %s )" %takens)
        return sec,takens


class WebInstance_ms(WebInstance):
    def __init__(self, name=''):
        super(WebInstance_ms, self).__init__()
        self.task_cres = """create table db2.dbo.dc_S2_taskinfo (id INT identity(1,1),uid int,uname nvarchar(24),task_tag nvarchar(34),task_cond nvarchar(3344),status int default -1,CreateTime datetime,updateTime datetime,path nvarchar(333),cod char(4),explain1 nvarchar(2000),explain2 nvarchar(2000));"""
        self.task_ins = """insert into db2.dbo.dc_S2_taskinfo(uid,uname,task_tag,task_cond,CreateTime) values(%s,'%s','%s','%s',getdate())"""
        self.task_upd = """update db2.dbo.dc_S2_taskinfo set updateTime=getdate(),status=%s,path='%s',cod='%s',explain1='%s' where id = %s """
        self.q_task = "select status,datediff(second,CreateTime,getdate()) as dur,path,cod,explain1 from db2.dbo.dc_S2_taskinfo where id=%s"
        self.list_task = "select *,datediff(second,CreateTime,updateTime) as dur from db2.dbo.dc_S2_taskinfo where %s order by CreateTime desc"


def do_upgrade_crea(mye, ups, cres=''):
    mye.c_conn(config.MYSQL_BI_RW_ENV)
    try:
        return mye.sql_engine().execute(ups).rowcount
    except Exception as err:
        print(err)
        if err.args[0] and cres!='':
            mye.getdata(cres);return mye.sql_engine().execute(ups).rowcount
        else:
            print(err);return 0


def add_task(uid,uname,task_tag,task_cond):
    ins=wi.task_ins %(uid,uname,task_tag,task_cond)
    do_upgrade_crea(my,ins,wi.task_cres)
    tid = my.c_conn(config.MYSQL_BI_RW_ENV).getdata(wi.get_taskid)[0]['maxid']
    my.quit()
    return tid


def update_task(status,id,path,cod,res=''):
    upd=wi.task_upd %(status,path,cod,res,id)
    do_upgrade_crea(my, upd)


def regist_usr(ename,emid,email=''):
    # ups=wi.ln_upd %('' if email=='' else ",email='%s'" %email, emid)
    # ins=wi.ln_ins %(emid,ename,email)
    # cres=wi.ln_cres %(emid,ename,email)
    # if do_upgrade_crea(my,ups,cres) == 0 : do_upgrade_crea(my,ins,cres)
    return login_user(User(ename,emid))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'comm/images'),
                               'bark-01.png', mimetype='image/vnd.microsoft.icon')


@login_manager.user_loader
def load_user(user_id):
    usr=User('AnonymousUser',-1,False,True)
    return usr


@login_manager.unauthorized_handler
def unauthorized():
    print(request.environ)
    return redirect(url_for(login_manager.login_view,next=request.environ['PATH_INFO']))
    # return redirect('http://bidata.hanshuai.com/sso.php?referer=http://'+request.environ['HTTP_HOST']+request.environ['PATH_INFO'])


@app.route('/Readme', methods=['GET'])
def readme():
    return json.dumps({'info': 'Welcome! to BARK2.0'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(1,vars(session),vars(request))
        # r=requests.post('http://10.10.9.244/user/login',data = {'username':request.values.get('username'),'password':request.values.get('password')}).text
        # ee=re.findall('"employeeid":"(\d+)","email":"(\w+.\w+@\w+.com)"',r)
        # if len(ee)==0: return json.dumps({"sta":'wrong number',"info":"/" })
        # emid,ename=ee[0];

        regist_usr('anyone', 0)

        flask.flash('Logged in successfully.')
        next = request.values.get('next')

        if 0: return flask.abort(400)
        return json.dumps({"sta":"success","next":next if next else "/" })
        #return redirect(next or url_for('index'))
    return render_template('login.html', base_dict=config.WBASE)


@app.route("/plotdtbyuid/<path:uids>")
@login_required
def plotdt(uids='-2'):
    uids = uids.split(',')
    if len(uids) > 9:
        return 'too many uids you want,take it easy. ~.~ '
    plotdtbyuids(uids, wi.dpath + '/1.png')
    return redirect(wi.download_path + '.data/1.png')


@app.route("/plotoilprice", methods=['GET'])
@login_required
def plotoilprice():
    re_dic = request.values.to_dict()
    plot_oil_price_(re_dic, wi.dpath + 'oil_price.html')
    return redirect(wi.download_path + '.data/oil_price.html')


@app.route("/PlotOilStationNum", methods=['GET'])
@login_required
def plotoilstationnum():
    re_dic = request.values.to_dict()
    plot_oil_station_num_(re_dic, wi.dpath + 'oil_station_num.html')
    return redirect(wi.download_path + '.data/oil_station_num.html')


@app.route("/PlotOilStationNumGeo", methods=['GET'])
@login_required
def plotgeostationnum(nothing=''):
    re_dic = request.values.to_dict()
    plot_geo_station_num(re_dic, wi.dpath + 'geo_station_num.html')
    return redirect(wi.download_path + '.data/geo_station_num.html')


@app.route("/PlotOilStationGeo", methods=['GET'])
@login_required
def plotgeostation(nothing=''):
    re_dic = request.values.to_dict()
    plot_geo_station(re_dic, wi.dpath + 'geo_station.html')
    return redirect(wi.download_path + '.data/geo_station.html')


@app.route("/PlotStationLostAvg", methods=['GET'])
@login_required
def plotstationlostavg(nothing=''):
    re_dic = request.values.to_dict()
    if 'enddate' not in re_dic:
        re_dic['enddate'] = day_forpast()
    filename = 'station_lostavg_%(mer_id)s.html' % re_dic
    plot_station_lostavg(re_dic, wi.dpath + filename)
    return redirect(wi.download_path + '.data/' + filename)


@app.route("/PlotStation3NTends", methods=['GET'])
@login_required
def plotstation3ntends(nothing=''):
    re_dic = request.values.to_dict()
    if 'enddate' not in re_dic:
        re_dic['enddate'] = day_forpast()
    filename = 'Station3NTends_%(mer_id)s_%(N)s.html' % re_dic
    plot_station_3ntends(re_dic, wi.dpath + filename)
    return redirect(wi.download_path + '.data/' + filename)


@app.route("/PWatchDog_Bark1", methods=['GET'])
@login_required
def pwatchdog_bark1(nothing=''):
    dw = my_(config.MYSQL_BI_RW_ENV)

    sqls1 = 'SELECT UNIX_TIMESTAMP(now())- UNIX_TIMESTAMP(update_time) delay_seconds FROM bimodels.bm_predictmodel_status where mid = 2'
    p_dic1 = dw.to_dataframe(sqls1).to_dict(orient='records')[0]
    p_dic1.update({'ID': 1, 'descrip': '线上实施消费预测延迟(s)', 'value1':p_dic1['delay_seconds'], 'value2':'-',
                   'valueTime': day_forpast(0, ss='%Y-%m-%d %H:%M:%S'),})
    if p_dic1['value1'] < 1200:
        p_dic1.update({'level_result': '0:正常'})
    else:
        p_dic1.update({'level_result': '1:需要关注'})

    sqls2 = ''
    Pwatchdog_data = [p_dic1]
    return render_template("Pwatchdog_bark1.html", Pwatchdog_data=Pwatchdog_data,)


@app.route("/shortcut/<path:arg>")
@login_required
def shortcut(arg=""):
    wpath = "http://%s:%s/shortcut/" %(config.WBASE['WEBserver'], config.WBASE['WEB_PORT'])

    ppath_now = wi.ppath + arg
    wpath_now = wpath + arg

    status, res = subprocess.getstatusoutput("cat %s/sqlbs.pycon" % ppath_now)
    if status == 0:
        sqlb = eval('{%s}' %(res,))
        sqlbs = {k:SqlHandler(sqls) for k, sqls in sqlb.items()}
        wi.sqlb_all.update(sqlbs)
        kss = {k:hand.cont_list for k, hand in sqlbs.items()}
        grss = {k:hand.group_list for k, hand in sqlbs.items()}
        ss = render_template("tags.html", base_dict=config.WBASE, tags=kss, grs=grss)  # , ins=ins, titles_s=titles_s)
        return ss
    status, res = subprocess.getstatusoutput("ls -a " + ppath_now+"/")
    # print(ppath_now,status,res)
    if status==0:
        return render_template("cdpath.html",path=wpath_now,conts=res.split("\n"))
    status, res = subprocess.getstatusoutput("cat " + ppath_now)
    if status == 0:
        return res
    return "%s:%s" %(status,res)


def general_odata(db_object, ex, path_x):
    try:
        db_object.to_dataframe(ex).to_csv(path_x, sep='\t')
        status, res = (0,'')
    except Exception as err:
        status, res = (1, ';'.join(err.args).replace("'", '|'))
    return status, res


def hive_odata(ex, path_x):
    log_file = "%s_%s" % (wi.hql_log, wi.log_num)
    wi.log_num += 1
    rdir = "/data/home/hanxuechen/hqlbase/" + str(random.randint(0, 0x1000)) + ".hql2"
    status, res = my.hive_sql2(ex, tmpf=log_file, tos=" > " + path_x, rdir=rdir)
    if status == 0:
        cod = "utf8"
    return status, res


def task_thread(tid, con, cond):
    # config 后期可以解耦 ----------------------------------------------------------------------------
    ENV_cond = {'con[:2] == "DW"': 'general_odata(my.c_conn(config.MYSQL_BI_RW_ENV),ex,path_x)',
                'con[:3] == "WOB"': 'general_odata(my.c_conn(config.MYSQL_PRODUCT_R_ENV),ex,path_x)',
                'con[:2] == "H_"': 'hive_odata(ex,path_x)'
                }
    ENV_else = {'else': 'general_odata(my.c_conn(config.MYSQL_BI_RW_ENV),ex,path_x)'}
    # config 后期可以解耦 -----------------------------------------------------------------------------

    cond = json.loads(cond)  #
    try:
        ex = wi.sqlb_all[con].render_sqls(cond)
    except:
        return redirect('/shortcut/sqlbanks')
    print("ex!!!!!::::  ", ex, )
    print(current_user, tid, con, cond)
    path_x = '%s/%s' %(wi.dpath, tid)
    cod = "utf8"
    status, res = (0, '')
    for v, k in ENV_cond.items():
        if eval(v):
            status, res = eval(k)
            ENV_else.pop('else')
    if 'else' in ENV_else:
        status, res = eval(ENV_else['else'])
    print(status, res)

    # if con[:2] == "DW":
    #     # status, res = subprocess.getstatusoutput("""mysql -h100.99.107.242 -uweicheche_data -pW1Pcxp7di0YBIdu5 bimodels -e "%s" > %s """ %(ex,path_x))
    #     try:
    #         my.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(ex).to_csv(path_x,sep='\t')
    #     except Exception as err:
    #         status, res = (1, ';'.join(err.args).replace("'",'|'))
    # if con[:3] == 'WOB':
    #     try:
    #         my.c_conn(config.MYSQL_PRODUCT_R_ENV).to_dataframe(ex).to_csv(path_x,sep='\t')
    #     except Exception as err:
    #         status, res = (1, ';'.join(err.args).replace("'",'|'))
    # elif con[:2] == "H_":
    #     log_file = "%s_%s" %(wi.hql_log,wi.log_num)
    #     wi.log_num += 1
    #     rdir = "/data/home/hanxuechen/hqlbase/"+str(random.randint(0,0x1000))+".hql2"
    #     status, res = my.hive_sql2(ex,tmpf=log_file,tos=" > "+path_x,rdir=rdir)
    #     if status == 0:
    #         cod = "utf8"
    # else:
    #     # status, res = subprocess.getstatusoutput("""mysql -h100.115.75.20 -uweicheche_data -pW1Pcxp7di0YBIdu5 bimodels -e "%s" > %s """ %(ex,path_x))
    #     try:
    #         my.c_conn(config.MYSQL_BI_RW_ENV).to_dataframe(ex).to_csv(path_x, sep='\t', index=False)
    #     except Exception as err:
    #         status, res = (1, ';'.join(err.args).replace("'",'|'))
    # # print('update_task!!!****',status,tid,path_x,cod,res)
    update_task(status, tid, path_x, cod, res)
        # return redirect(url_for('v_table',dpath=path_x,code=cod))
        # return json.dumps({'next':url_for('v_table',dpath=path_x,code=cod),'menunum':'menu2'})


@app.route("/sqlbs2/<con>", methods=['GET', 'POST'])
def sqlbs2(con):
    cond = request.values.to_dict()['cond']
    dcond = json.loads(cond)
    for k in list(dcond.keys()):
        if dcond[k] == '': dcond.pop(k)
    # conds=re.sub('"','',json.dumps(dcond))
    tid = add_task(current_user.id,current_user.name,con,cond)
    try:
        task_thread(tid,con,cond)
        # t1 = threading.Thread(target=task_thread,args=(tid,con,cond))
        # t1.setDaemon(True)
        # t1.start()
    except Exception as err:
        print(err, vars(err))
    return json.dumps({'next': url_for('v_table', taskid=tid, dpath=wi.dpath+'/%s' % tid), 'menunum':'menu2'})


@app.route("/sqlrestart/<tid>", methods=['GET'])
@login_required
def sqlrestart(tid):
    my.c_conn(config.MYSQL_BI_RW_ENV)
    my.sql_engine('update data_center.dc_S2_taskinfo set CreateTime=now() where id = %s' % tid)
    taskinfo = my.getdata('select * from data_center.dc_S2_taskinfo where id = %s' % tid)
    con = taskinfo[0]['task_tag']
    cond = taskinfo[0]['task_cond']
    task_response = task_thread(tid,con,cond)
    my.quit()
    if task_response:
        return task_response
    return redirect(url_for('v_table', taskid=tid, dpath=wi.dpath + '/%s' % tid))


@app.route("/taskrestart/<tid>", methods=['GET'])
@login_required
def taskrestart(tid):
    return redirect('/sqlrestart/%s' %tid)


@app.route("/v_table", methods=['GET', 'POST'])
def v_table():
    cod = request.values.get('code')
    pat = request.values.get('dpath')

    proc = subprocess.Popen("/usr/bin/head -n 999 "+pat, shell=True, stdout=subprocess.PIPE)
    cod = "utf8" if cod is None else cod
    res, errs = proc.communicate(timeout=15)
    lines = [line.split("\t") for line in str(res,cod).split("\n")[:-1]] if errs is None else []
    ss = render_template("v_tab_uu.html", base_dict=config.WBASE, lines=lines, xlsn=pat, tas=wi.tas)
    return ss


@app.route("/task_mamt", methods=['GET', 'POST'])
@login_required
def task_mamt():
    para = request.values.to_dict()
    if para == {}:
        return render_template("task_Management.html",base_dict=config.WBASE,user=current_user.name)
    be = ['CreateTime>=' + para['be'] if 'be' in para else wi.yesterday]
    ed = ['date(CreateTime)<=' + para['ed']] if 'ed' in para else []
    tag = ["task_tag like '%%%s%%'" % para['tag']] if 'tag' in para else []
    name = ["uname like '%%%s%%' " % para['name']] if 'name' in para else []
    wherec = ' and '.join(be + ed + tag + name)
    task_data = my.c_conn(config.MYSQL_BI_RW_ENV).getdata(wi.list_task % wherec)
    return render_template("task_Management.html", base_dict=config.WBASE, task_data=task_data, user=current_user.name)


def to_aggfunc(ss):
    aggfunc = np.sum
    if ss == 'count':
        aggfunc = len
    elif ss == 'mean':
        aggfunc = np.mean()
    elif ss == 'unique_count':
        aggfunc = lambda x: len(x.unique())
    return aggfunc


@app.route("/bi_reshape/", methods=["POST"])
def bi_reshape():
    wi.tic()
    re_dic = request.values.to_dict()
    cod = 'utf8' if not re_dic['code'] else re_dic['code']
    rows = re_dic['nav1'].split(',') if re_dic['nav1'] else []
    cols = re_dic['nav2'].split(',') if re_dic['nav2'] else []
    targets = re_dic['nav3'].split(',') if re_dic['nav3'] else []
    tar_d = {}
    vals = []
    for target in targets:
        x, v = target.split(':')
        if x not in tar_d:
            tar_d[x] = []
        tar_d[x] += [to_aggfunc(v)]
        vals += [x]
    print(re_dic)
    data = pd.read_csv(re_dic['url'], sep='\t', encoding=cod)
    print(rows,cols,tar_d)
    if tar_d:
        dfr = pd.pivot_table(data, index=rows, columns=cols, aggfunc=tar_d)
    else:
        dfr = data.loc[:,rows+cols]
    dfr.to_excel(re_dic['url'] + '.xlsx')
    dfr.to_html(re_dic['url'] + '.html')
    tt, tas = wi.toc()
    respath = wi.download_path + re_dic['url']
    return json.dumps({"download": respath+".xlsx", "update": respath+".html", "tas": tas})


if __name__ == "__main__":
    my = ms_(config.MYSQL_BI_RW_ENV)
    wi = WebInstance_ms()
    kargs = dict(host='0.0.0.0', port=int(config.WBASE['WEB_PORT']), threaded=True, debug=False)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dp:",)
        opts_dict = {x[0]: x[1] for x in opts}
        if '-p' in opts_dict:
            kargs['port'] = int(opts_dict['-p'])
        kargs.update({'debug': '-d' in opts_dict})

    except getopt.GetoptError as err:
        print(err)
        # print help information and exit:

    app.run(**kargs)

    # app.run(port=int(config.WBASE['WEB_PORT']), host='0.0.0.0', debug=True, threaded=True)
