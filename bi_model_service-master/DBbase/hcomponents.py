import time,datetime,pickle,re,os,subprocess
import numpy as np
import logging
import calendar

PRO_NAME = 'bi_model_service'
# PRO_PATH = re.match('.*'+PRO_NAME, os.getcwd()).group(0)
PRO_PATH = os.path.dirname(os.getcwd())


def relative_path(path):
    """Returns a path relative from this file"""
    dirname=os.path.dirname(os.path.realpath('_file_'))
    path=os.path.join(dirname,path)
    return os.path.normpath(path)


def x_inlist_index(x,data_list):
    # 一般来讲list是一组数，需要从小到大排列好.
    # re_in = [-1, -1]
    # for i in range(len(data_list)):
    #     if x >= data_list[i]:
    #         re_in[0] = i
    #     else:
    #         re_in[1] = i
    #         break
    # return re_in
    bound_arr = np.array(data_list + [np.inf])
    delta = bound_arr - x
    ind = len(delta[delta < 0]) 
    return ind if delta[ind] == 0 else ind - 1


def speed_find_sev(data, sev, base_list=None):
    # base_list 基点,如果传入要保证data[base_list]是已经排好的,且base_list按索引顺序由小往大排。
    if 1 > sev > 0:
        sev = int(sev * len(data))
    ebase_list = [-1] + (base_list if base_list else []) + [len(data)]
    if sev in ebase_list:
        return data[sev],base_list
    left_ind = x_inlist_index(sev, ebase_list) 
    left, right = ebase_list[left_ind], ebase_list[left_ind+1]  # 确定左右基点
    if right - left > 2:
        rand_ind = left + 1  # rand_ind = random.randint(left + 1, right - 1)
        rand_x = data[rand_ind]
        i = left + 1
        # print(i, rand_ind, end='>>')
        while(i < right):
            if i < rand_ind and data[i] > rand_x:
                rand_ind -= 1
                data[right:right] = [data.pop(i)]
                right -= 1
                continue
            elif i > rand_ind and data[i] < rand_x:
                data[rand_ind:rand_ind] = [data.pop(i)]
                rand_ind += 1
            i += 1
        ebase_list[left_ind + 1: left_ind + 1] = [rand_ind]
        # print(data,rand_ind)
    else:
        ebase_list[left_ind + 1: left_ind + 1] = [sev]
    base_list = ebase_list[1:-1]
    return speed_find_sev(data, sev, base_list=base_list)


def day_forpast(d=0, h=0, ss="%Y%m%d"):
    t1 = datetime.datetime.now() + datetime.timedelta(days=d, hours=h)
    if ss == 'stamp':
        return time.mktime(t1.timetuple())
    elif ss == 'Timestamp':
        return t1
    else:
        return t1.strftime(ss)


def time_replace(rep_dict=None, ss='stamp'):     # 任意置换当前时间的 rep_dict使用如下格式{'year':2020,'month':5,'day':31,'hour':23,'minute':59,'second':59}
    if rep_dict is None:
        rep_dict = {}
    now = datetime.datetime.now()
    re_now = now.replace(**rep_dict)
    if ss == 'stamp':
        return time.mktime(re_now.timetuple())
    elif ss == 'Timestamp':
        return re_now
    else:
        return re_now.strftime(ss)


def lastnday_of_month(ym_dict=None, n=0, ss='stamp'):  # 某月的(倒数)第-n天
    if ym_dict is None:
        ym_dict = {}
    now = datetime.datetime.now()
    cyear = ym_dict['year'] if 'year' in ym_dict else now.year
    cmonth = ym_dict['month'] if 'month' in ym_dict else now.month
    days = calendar.monthrange(cyear, cmonth)
    ym_dict.update({'day': days[-1] + n})
    return time_replace(ym_dict, ss)


def send_wechat_warning(err_msg):
    sheild_path = PRO_PATH + '/Shield'
    status, res = subprocess.getstatusoutput('php %s/Qywechat.php -m="%s" > /tmp/Qywechat.err' % (sheild_path, err_msg))
    print(err_msg, status, res)
    if status:
        err_msg_short = re.sub('\s*', '', err_msg)
        _ = subprocess.getstatusoutput("sh %s/wechat.sh '%s' 2> /dev/null" % (sheild_path, err_msg_short))


def iter_mkdir(path):
    # 能够迭代的建立文件夹 path = /A/B/C/ 则会用迭代的方式先保证/A/B/存在 ;最好以/结尾 若path = /A/B/C/asdf 则只新建文件夹到/A/B/C/
    path = re.match('(.*)/+', path).group(1)
    if path:
        try:
            os.mkdir(path)
            print('successful mkdir (%s)' %path)
        except Exception as err:
            print(err)
            if err.args[0] == 2:
                iter_mkdir(path)
                os.mkdir(path)
            else:
                print('no need to (iter)mkdir~')


def path_exist(path):
    return os.path.exists(path)


class v_holder():
    def __init__(self, va=''):
        self.vals = va

    def store(self,path):
        try:
            pickle.dump(self.vals,open(path, 'wb'))
        except Exception as err:
            print(err)
            iter_mkdir(path)
            pickle.dump(self.vals, open(path, 'wb'))
        return self

    def pickup(self,path):
        try:
            self.vals = pickle.load(open(path, 'rb'))
        except Exception as err:
            # iter_mkdir(path)
            print(err,path)
        return self.vals


class Timer_:
    def __init__(self, num=1):
        self.num = num
        self.extradata = []
        self.tictoc = []
        self.alltoc = []
        self.initpoint = time.time()
        self.ticpoint = time.time()
        self.stopoint = -1

    def tic(self):
        self.ticpoint = time.time()
        return self

    def toc(self, withinittic=False):
        self.tictoc.append(time.time() - self.ticpoint)
        self.alltoc.append(time.time() - self.initpoint)
        if withinittic:
            self.tic()
        return self

    def add_exd(self, exd):
        if type(exd) is list:
            self.extradata += exd
        else:
            self.extradata.append(exd)

    def stop(self):
        self.stopoint = time.time()

    def sleep(self, n=0.1):
        time.sleep(n)
        return self

    def runtime_delay(self, deltasecond=1):
        if deltasecond < 0:
            print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), '需要等待%s秒以继续....' % (-deltasecond), )
            self.sleep(-deltasecond)
        return self


class Logger:
    def __init__(self, name):
        # super(Logger, self).__init__()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(20)
        self.file_handler = None
        self.formatter_ = None
        self.with_date = '0'
        self.filename = name

    def set_format(self,formatss):
        self.formatter_ = logging.Formatter(formatss)
        return self

    def set_file(self,filename=''):
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
        filename = '%s_%s' % (self.filename, self.with_date)
        self.file_handler = logging.FileHandler(filename)
        self.file_handler.formatter = self.formatter_
        # self.file_handler.setFormatter(self.formatter_)
        self.logger.addHandler(self.file_handler)
        return self

    def set_date(self,date_now):
        if date_now == self.with_date:
            pass
        else:
            self.with_date = date_now
            self.set_file()
        return self

    def set_level_info(self):
        pass

    def do_info(self, content):
        self.logger.info(content)
        return self


class SqlHandler:
    # sql特殊形式handler，定制一种特殊的更灵活的sql应用方式，目前依赖：
    # 1.sqls中含有多个group by目前只关注最后一个group by
    # 2.条件写法间具备唯一性

    def __init__(self, sqls, auto_anal=True):
        sqls = re.sub('\n', ' \n', sqls)
        self.sqls = sqls
        self.group_res = ''
        self.group_list = []
        exs = sqls.split("|")
        self.ex = exs[0]
        self.grb_ass = {}   # group by associate;
        if len(exs) > 1:
            try:
                self.grb_ass = eval(exs[1])     # groupby associate：被group by 牵扯的列，不能是最后一列，满足' %s,'
            except Exception as err:
                print(err)
        if auto_anal:
            self.getsql_con().getsql_group()

    def getsql_con(self):
        CAL_REX = re.compile("(\S+ \S+ )\S*_i_\S* ")
        CAL_REXA = re.compile("\S+ \S+ \S*_i_\S* ")
        self.cont_list = re.findall(CAL_REX, self.sqls)         # 条件列表(不包含_i_)
        self.cont_lista = re.findall(CAL_REXA, self.sqls)       # 条件列表(包含_i_)
        for con, cona in zip(self.cont_list, self.cont_lista):
            if con not in cona:
                print('cons check not pass! 这几乎不可能被打印出来')
        return self

    def getsql_group(self):
        GROUP_REX = re.compile("group by (\S+?)[;\s]")
        res = re.findall(GROUP_REX, self.sqls)
        if res:
            self.group_res = res[-1]
            self.group_list = res[-1].split(",")
        return self

    def render_sqls(self, cond):
        ex = self.ex
        cond = cond.copy()
        group_para = cond.pop('group by ') if 'group by ' in cond.keys() else []
        full_cond = {x: '' for x in self.cont_list}
        full_cond.update(cond)
        cont_dict = {con: cona for con, cona in zip(self.cont_list, self.cont_lista)}
        for ck, cv in full_cond.items():
            cv = str(cv)
            if ck in cont_dict:
                for x in ['and ', 'set ']:
                    conx = '' if (cv == '') else x + cont_dict[ck].replace('_i_', cv)  # 用replace则可以完全抛弃add_transferm函数
                    ex = ex.replace(x + cont_dict[ck], conx)

        if group_para and self.group_res:
            group_c = ','.join([gk for gk, gv in group_para.items() if gv == '1'])
            ex = ex.replace(self.group_res, group_c)
            for g in [gk for gk, gv in group_para.items() if gv == '0']:
                if g in self.grb_ass:
                    ex = ex.replace(self.grb_ass[g], ' ')
                    for col in self.grb_ass[g].split(','):
                        ex = ex.replace(' %s,' % col, '')
        # self.render_ex = ex
        return ex
