import click,subprocess,re,copy,json,sys,pprint,decimal,datetime,time
import random,threading
from jinja2 import Template
import flask
from flask import Flask,request,session,render_template,url_for,redirect
from flask_login import *
import sys
sys.path.append('../DBbase')
from db_func import *
from hcomponents import *
sys.path.append('../.settings')
from config import *
sys.path.append('../predict')
from simple_func_backp import *
import pandas as pd
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?R1'
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


class WebInstance():
    sqlb = {}; sqlall = {};ppath_now = ""; tas = ".."
    group_re = re.compile("group by (\S+?)[;\s]")
    today = day_forpast(0)
    yesterday = day_forpast(-1)
    ppath = "../Webserver/"
    fpath="http://%s:%s/" %(WBASE['WEBserver'],WBASE['FILE_PORT']);download_path="http://%s:%s/" %(WBASE['WEBserver'],WBASE['DOWNLOAD_PORT'])
    dpath="../.data"
    hql_log="/home/bi/gitpro/tmp/hql_log";log_num=0
    REF_url="http://%s:%s/shortcut/maindir/S2_sallocation_diff" %(WBASE['WEBserver'],WBASE['WEB_PORT'])
    #task_cres="""create table data_center.dc_S2_taskinfo (id INT AUTO_INCREMENT,uid int(8),uname varchar(24),task_tag varchar(34),task_cond varchar(3344),status int(3) default -1,CreateTime datetime,updateTime datetime,path varchar(333),cod char(4),explain1 text,explain2 text,PRIMARY KEY (id) );"""
    task_cres = """create table db2.dbo.dc_S2_taskinfo (id INT identity(1,1),uid int,uname nvarchar(24),task_tag nvarchar(34),task_cond nvarchar(3344),status int default -1,CreateTime datetime,updateTime datetime,path nvarchar(333),cod char(4),explain1 nvarchar(2000),explain2 nvarchar(2000));"""
    task_ins="""insert into db2.dbo.dc_S2_taskinfo(uid,uname,task_tag,task_cond,CreateTime) values(%s,'%s','%s','%s',getdate())"""
    task_upd="""update db2.dbo.dc_S2_taskinfo set updateTime=getdate(),status=%s,path='%s',cod='%s',explain1='%s' where id = %s """
    q_task="select status,datediff(second,CreateTime,getdate()) as dur,path,cod,explain1 from db2.dbo.dc_S2_taskinfo where id=%s"
    list_task="select *,datediff(second,CreateTime,updateTime) as dur from db2.dbo.dc_S2_taskinfo where %s order by CreateTime desc"

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
        sec=dt.seconds+dt.microseconds/1000000 ; mi=int(sec/60) ; takens=" TIME Taken:: %s min %.6f sec" %(mi,sec%60)
        print("toc at:: %s" %datetime.datetime.now()+" ( %s )" %takens)
        return sec,takens


def do_upgrade_crea(mye,ups,cres=''):
    mye.c_conn(MSSQLs_BI_R_ENV)
    try: return mye.sql_engine().execute(ups).rowcount
    except Exception as err:
        print(err)
        if err.args[0] and cres!='':
            mye.getdata(cres);return mye.sql_engine().execute(ups).rowcount
        else:
            print(err);return 0


def add_task(uid,uname,task_tag,task_cond):
    ins=wi.task_ins %(uid,uname,task_tag,task_cond)
    do_upgrade_crea(my,ins,wi.task_cres)
    sel="SELECT max(id) as maxid from db2.dbo.dc_S2_taskinfo"
    tid = my.c_conn(MSSQLs_BI_R_ENV).getdata_dictslist(sel)[0]['maxid']
    my.quit()
    return tid


def update_task(status,id,path,cod,res=''):
    upd=wi.task_upd %(status,path,cod,res,id)
    do_upgrade_crea(my,upd)


def regist_usr(ename,emid,email=''):
    # ups=wi.ln_upd %('' if email=='' else ",email='%s'" %email, emid)
    # ins=wi.ln_ins %(emid,ename,email)
    # cres=wi.ln_cres %(emid,ename,email)
    # if do_upgrade_crea(my,ups,cres) == 0 : do_upgrade_crea(my,ins,cres)
    return login_user(User(ename,emid))


@login_manager.user_loader
def load_user(user_id):
    usr=User('AnonymousUser',-1,False,True)
    return usr


@login_manager.unauthorized_handler
def unauthorized():
    print(request.environ)
    return redirect(url_for(login_manager.login_view,next=request.environ['PATH_INFO']))
    # return redirect('http://bidata.zhenai.com/sso.php?referer=http://'+request.environ['HTTP_HOST']+request.environ['PATH_INFO'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
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
    return render_template('login.html', base_dict=WBASE)


@app.route("/plotdtbyuid/<path:uids>")
@login_required
def plotdtbyuid(uids='-2'):
    uids = uids.split(',')
    if len(uids) > 9:
        return 'too many uids you want,take it easy. ~.~ '
    Le = np.ceil(np.sqrt(len(uids)))
    fig = plt.figure(figsize=(14, 11))  # figsize=(10,6)

    for i,uid in enumerate(uids):
        df = user_order_detail(uid)
        x_ = np.array(df.dt)
        x__ = x_.mean()
        pl = fig.add_subplot(int('%d%d%s' %(Le,Le,i+1)))
        sn.distplot(x_, color="#988CBE", bins=16, rug=True, ax=pl)
        pl.plot([0, 0], [0, 2], color='#000000')
        pl.plot([x__, x__], [0, 2], color='#009900', label='mean')
        ybound = pl.properties()['ybound']
        pl.annotate('mean of delta_d:%2.3f \n wcount: %d' % (x__,x_.__len__()), xy=(x__, 0)
                    , xytext=(x__, 0.6 * ybound[1])
                    , bbox=dict(boxstyle='sawtooth', fc="w")
                    , arrowprops=dict(arrowstyle="-|>"
                                      , connectionstyle="arc,rad=0.5", fc='r'))  # "-|>"代表箭头头上是实心的
        pl.set_title(u'plot distributing: delta_d of uid=%s' % uid)
        pl.set_xlabel('delta_d')
        pl.set_ylabel('Rate(p)')
        pl.grid(True)
        pl.axis([-1, x_.max() + 1] + list(ybound))
    fig.savefig(wi.dpath+'/1.png')
    return redirect('http://120.25.245.164:3334/.data/1.png')


@app.route("/shortcut/<path:arg>")
@login_required
def shortcut(arg=""):
    wpath = "http://%s:%s/shortcut/" %(WBASE['WEBserver'],WBASE['WEB_PORT'])
    #print(dir(session),'\n',session.items())
    #arg = re.sub(ppath[1:],"",arg)
    ppath_now = wi.ppath + arg ;wpath_now = wpath + arg
    #wi.ppath_now = ppath_now;
    # column_name={};titles={};ins_title={}
    status, res = subprocess.getstatusoutput("cat %s/sqlbs.pycon" % ppath_now)
    if status == 0:
        res = re.sub('\n', ' ', res)
        wi.sqlb = eval('{%s}' %(res,))
        wi.sqlall.update(wi.sqlb)
        cal_ex = re.compile("(\S+ \S+ )\S*_i_\S* ")
        kss = {k:re.findall(cal_ex,c) for k,c in wi.sqlb.items()}
        grs = {k:re.findall(wi.group_re,c)[-1].split(",") if re.findall(wi.group_re,c) else [] for k,c in wi.sqlb.items()}
        # ins = {x:x for x in kss.keys()}    # load tag alias
        # for x in kss.values(): ins.update({y:y for y in x })  # load condition alias
        # for x in grs.values(): ins.update({y:y for y in x})    # load group by alias
        # titles_s = copy.deepcopy(ins)  #
        # for x in ins:
        #    for yk,yv in column_name.items(): ins[x] = re.sub(yk,yv,ins[x])
        # for x in titles_s:
        #    for yk,yv in titles.items(): titles_s[x] = re.sub(yk,yv,titles_s[x])
        # ins.update(ins_title)
        ss = render_template("tags.html", base_dict=WBASE, tags=kss, grs=grs)  # , ins=ins, titles_s=titles_s)
        return ss
    status, res = subprocess.getstatusoutput("ls -a " + ppath_now+"/")
    # print(ppath_now,status,res)
    if status==0:
        return render_template("cdpath.html",path=wpath_now,conts=res.split("\n"))
    status, res = subprocess.getstatusoutput("cat " + ppath_now )
    if status == 0:
        return res
    return "%s:%s" %(status,res)


def task_thread(tid,con,cond):
    cond=json.loads(cond)  #
    try:
        exs = wi.sqlall[con].split("|")
    except:
        return redirect('/shortcut/sqlbanks')
    ex = exs[0]
    try:
        grb_ass = json.loads(exs[1])  # group by associate;
    except Exception as err:
        grb_ass = {}
    # ex = re.sub('\n',' ',ex)
    group_para = cond.pop('group by ') if 'group by ' in cond.keys() else []
    for ck, cv in cond.items():
        print(ck, cv)
        for c in re.findall(r'and '+ck+"\S*_i_\S*",ex):
            conx = '' if (cv == '') else re.sub('_i_', cv, c)
            ex = ex.replace(r'%s' % c,conx)
            print(c,conx)
    if group_para:
        group_c = ','.join([gk for gk,gv in group_para.items() if gv == '1'])
        for g in re.findall(wi.group_re,ex):
            ex = ex.replace(g,group_c)
        for g in [gk for gk,gv in group_para.items() if gv == '0']:
            ex = ex.replace(' %s,' %g, ' ')
            if g in grb_ass:
                ex = ex.replace(grb_ass[g], ' ')
    print("ex!!!!!::::", ex, current_user, tid, con, cond)
    print(con[:])

    path_x = '%s/%s' %(wi.dpath,tid)
    cod = "utf8"
    status, res = (0, '-')
    if con[:2] == "DW":
        # status, res = subprocess.getstatusoutput("""mysql -h100.99.107.242 -uweicheche_data -pW1Pcxp7di0YBIdu5 bimodels -e "%s" > %s """ %(ex,path_x))
        try:
            my.c_conn(MYSQL_BI_RW_ENV).to_dataframe(ex).to_csv(path_x,sep='\t')
        except Exception as err:
            status, res = (1, ';'.join(err.args).replace("'",'|'))
    if con[:3] == 'WOB':
        try:
            my.c_conn(MYSQL_PRODUCT_R_ENV).to_dataframe(ex).to_csv(path_x,sep='\t')
        except Exception as err:
            status, res = (1, ';'.join(err.args).replace("'",'|'))
    elif con[:2] == "H_":
        log_file = "%s_%s" %(wi.hql_log,wi.log_num)
        wi.log_num += 1
        rdir = "/data/home/Alina/hqlbase/"+str(random.randint(0,0x1000))+".hql2"
        status, res = my.hive_sql2(ex,tmpf=log_file,tos=" > "+path_x,rdir=rdir)
        if status == 0:
            cod = "utf8"
    if con[:3]=="hxb":
        try:
            my.c_conn('hxb').to_dataframe(ex).to_csv(path_x,sep='\t',index=False)
        except Exception as err:
            status, res = (1, ';'.join(err.args).replace("'",'|'))
    if con[:3]=="xqj":
        try:
            my.c_conn('hjqs').to_dataframe(ex).to_csv(path_x,sep='\t',index=False)
        except Exception as err:
            status, res = (1, ';'.join(err.args).replace("'",'|'))
    else:
        # status, res = subprocess.getstatusoutput("""mysql -h100.115.75.20 -uweicheche_data -pW1Pcxp7di0YBIdu5 bimodels -e "%s" > %s """ %(ex,path_x))
        try:
            my.c_conn(MSSQLs_BI_R_ENV).to_dataframe(ex).to_csv(path_x, sep='\t', index=False)
        except Exception as err:
            status, res = (1, ';'.join(err.args).replace("'",'|'))
    # print('update_task!!!****',status,tid,path_x,cod,res)
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
        t1 = threading.Thread(target=task_thread,args=(tid,con,cond))
        t1.setDaemon(True)
        t1.start()
    except Exception as err:
        print(err, vars(err))
    return json.dumps({'next': url_for('v_table', taskid=tid, dpath=wi.dpath+'/%s' % tid), 'menunum':'menu2'})


@app.route("/sqlrestart/<tid>", methods=['GET'])
@login_required
def sqlrestart(tid):
    my.c_conn(MYSQL_BI_RW_ENV)
    my.sql_engine('update db2.dbo.dc_S2_taskinfo set CreateTime=GETDATE() where id = %s' % tid)
    taskinfo = my.getdata_dictslist('select * from db2.dbo.dc_S2_taskinfo where id = %s' % tid)
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
    ss = render_template("v_tab_uu.html", base_dict=WBASE, lines=lines, xlsn=pat, tas=wi.tas)
    return ss



@app.route("/task_mamt", methods=['GET', 'POST'])
@login_required
def task_mamt():
    para = request.values.to_dict()
    if para == {}:
        return render_template("task_Management.html",base_dict=WBASE,user=current_user.name)
    be = ['convert(varchar(8),CreateTime,112)>=' + para['be'] if 'be' in para else wi.yesterday]
    ed = ['convert(varchar(8),CreateTime,112)<=' + para['ed']] if 'ed' in para else []
    tag = ["task_tag like '%%%s%%'" % para['tag']] if 'tag' in para else []
    name = ["uname like '%%%s%%' " % para['name']] if 'name' in para else []
    wherec = ' and '.join(be + ed + tag + name)
    task_data = my.c_conn(MSSQLs_BI_R_ENV).getdata_dictslist(wi.list_task % wherec)
    return render_template("task_Management.html", base_dict=WBASE, task_data=task_data, user=current_user.name)

@app.route("/bi_reshape/",methods=['POST'])
@login_required
def bi_reshape():
    print("successful")
    print(request)
    return json.dumps({"download": "http://120.25.245.164:8186/ReadMe", "update": "/"})

if __name__ == "__main__":
    # my = my_(MYSQL_BI_RW_ENV)
    my = ms_(MSSQLs_BI_R_ENV)
    wi = WebInstance()
    app.run(port=int(WBASE['WEB_PORT']), host='0.0.0.0', debug=True, threaded=True)
