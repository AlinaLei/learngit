#! /usr/local/bin/python3
# coding=utf-8
import os,sys,time,re,subprocess
sys.path.append('../')
from DBbase.hcomponents import *


def pkill_bypid(Pid):
    _ = subprocess.getstatusoutput("pkill -P -9 %s; kill -9 %s" % (Pid, Pid))


def grep_pid(keywords):
    if type(keywords) is list:
        greps = ' | '.join(["grep '%s'" % x for x in keywords])
    else:
        greps = "grep '%s'" % keywords
    grepcmd = "ps ajx | grep -v 'grep' | %s | awk '{print $2}'" %greps
    status, res = subprocess.getstatusoutput(grepcmd)
    if status == 0:
        return re.findall('\d+', res)


def get_file_updatedt(filename):
    status, res = subprocess.getstatusoutput("((dt=`date +%%s`-`stat -c %%Y %s`));echo $dt" %filename)
    print(filename, res)
    if status == 0:
        return int(res)


def get_url_return(url):
    status, res = subprocess.getstatusoutput("curl --connect-timeout 5 -m 10 -L %s 2> /dev/null" % url)
    print(url, res)
    return status == 0 and len(res) > 2


# def send_wechat_warning(err_msg):
#     status, res = subprocess.getstatusoutput('php %s/Qywechat.php -m="%s" > /tmp/Qywechat.err' % (sys.path[-1], err_msg))
#     print(err_msg, status, res)
#     if status:
#         err_msg_short = re.sub('\s*', '', err_msg)
#         _ = subprocess.getstatusoutput("sh %s/wechat.sh '%s' 2> /dev/null" % (sys.path[-1], err_msg_short))


def osfork_quit_parent(forknnum=1):
    try:
        pid = os.fork()
        # 子进程的pid一定为0，父进程大于0
        if pid:
            # print('now exit because get pid=%s,which means not the child process' % pid)
            sys.exit(0)
        return pid
    except OSError as err:
        print("error #%s:%s" % (forknnum, str(err)))
        sys.exit(1)


PARA = dict(mode='sf_pid', lourl='', cmddir=os.getcwd(), interval=300, runtimes=0)
# mode 守护模式:
#   sf_pid -- pid的存在以及符合grep appcmd;
#   sf_log -- 根据日志文件的更新, 一段时间没更新了则任务重启并通知
#      sf_log 更新:日志会跟上runtimes 代表重启的次数
#   sf_url -- 以get方式检测url/api的响应(需要对应设置一个迅速的hello响应)
# lourl: sf-log 下对应日志文件 可以用相对/绝对路径 相对(cmddir)路径; sf_url下为对应的url路径
# cmddir：执行appcmd的目录 默认在当前目录 不在当前目录的请指定
#  interval: 检测间隔 默认300s 不可传入 只能手动修改

# input: filename appcmd mode lourl
if sys.argv.__len__() >= 2:
    appcmd = sys.argv[1]  # appcmd:  被守护的命令 最好不要包含单引号
    appcmd_short = re.sub('\s*', '', appcmd[:16])
    if sys.argv.__len__() == 3:
        for s in sys.argv[2].split('&'):
            print(s)
            if s:
                v,k = s.split('=')
                PARA.update({v: k})
        if PARA['mode'] == 'sf_log':
            appcmd = appcmd + ' > %(lourl)s_%(runtimes)s 2>&1'
else:
    print('daemon should have some args ')
    sys.exit(0)
Interval = int(PARA['interval'])
print('sys.argv:',sys.argv)
# res = re.match('(.*)/(.*?py)', sys.argv[0])
# if res:
#     if res.group(1)[0] == '/':
#         shield_path = res.group(1)
#     else:
#         shield_path = os.getcwd() + '/' + res.group(1)
# else :
#     shield_path = os.getcwd()
# sys.path.append(shield_path)
# print("PARA:%s" % PARA,"shield_path:%s" % sys.path[-1])
print("%s||pid(%s)||ppid(%s)" % (">>loli", os.getpid(), os.getppid()))
# m = re.match('\w*\s*(/\S+)/(\S+)',appcmd)
# if m :
#    dirpath = m.group(1)
#    app = m.group(2)
# else:
#    dirpath = os.getcwd()
#    app = re.split('\s+',appcmd)[-1]
# fullapppath = dirpath+'/'+app

pid = osfork_quit_parent(1)
print("%s||forkpidreturn=%s||pid(%s)||ppid(%s)" % ("* lolita",pid,os.getpid(),os.getppid()))

os.chdir(PARA['cmddir'])
os.umask(0)                 # 设置文件模式创建屏蔽字
os.setsid()                 # 甩掉控制终端

# 第二次fork 保证子进程不是会话首进程
pid = osfork_quit_parent(2)
print("%s||forkpidreturn=%s||pid(%s)||ppid(%s)" % ("** little lolita",pid,os.getpid(),os.getppid()))


def kill_deamon():
    # send_wechat_warning("测试:daemon(%s)正尝试自杀" % (sys.argv[0]))
    status, res = subprocess.getstatusoutput("ps ajxf | grep 'python3 %s' | grep '%s' | awk '{print $2}' | xargs kill -15" % (sys.argv[0], appcmd))
    print(status, res)


def check_out(cmd_pid):
    if PARA['mode'] == 'sf_pid':
        print(grep_pid(appcmd), cmd_pid)
        if str(cmd_pid) in grep_pid(appcmd %PARA):
            return 0
        else:
            return '{%s}(pid=%s)已挂....' %(appcmd %PARA, cmd_pid)
    if PARA['mode'] == 'sf_log':
        dt = get_file_updatedt('%(lourl)s_%(runtimes)s' %PARA)
        if dt < Interval:
            return 0
        else:
            appcmd_now = appcmd %PARA
            PARA['runtimes'] += 1
            return '{%s}(pid=%s)的持续输出日志已%ss未更新....' % (appcmd_now, cmd_pid, dt)
    if PARA['mode'] == 'sf_url':
        if get_url_return(PARA['lourl']):
            return 0
        else:
            return '服务{%s}(pid=%s)的api无响应...' % (appcmd %PARA, cmd_pid)


if __name__ == "__main__":
    do_seconds = 8002368000
    dd_days = do_seconds / 24 / 3600
    print("此守护进程会持续运行%s天..." % dd_days)

    for f in [sys.stdout, sys.stderr]:
        f.flush()  # 刷新缓冲区
    # print调试可以注释下段 但实际使用时守护进程脱离会话则一定不能注释
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())

    P_ = subprocess.Popen(appcmd % PARA, shell=True)
    send_wechat_warning("{%s}(pid=%s)||守护开始!时间:%7.2f天....." % (appcmd % PARA, P_.pid, dd_days))
    while(do_seconds):
        time.sleep(Interval)
        do_seconds -= Interval
        dd_days = do_seconds / 24 / 3600
        check_res = check_out(P_.pid)
        if check_res:
            send_wechat_warning(check_res)
            pkill_bypid(P_.pid)
            P_ = subprocess.Popen(appcmd % PARA, shell=True)
            if P_.pid > 0:
                send_wechat_warning(">>>>重启{%s}(pid=%s)ok!! | runtime:%s | 守护剩余%7.2f天" %(appcmd %PARA, P_.pid, PARA['runtimes'], dd_days))
