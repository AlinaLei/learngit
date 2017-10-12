import time,pickle,re,os


def iter_mkdir(path):
    # 能够迭代的建立文件夹 path = /A/B/C/ 则会用迭代的方式先保证/A/B/存在 ;最好以/结尾 若path = /A/B/C/asdf 则只新建文件夹到/A/B/C/
    path = re.match('(.*)/+',path).group(1)
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


class v_holder():
    def __init__(self, va='value_holder'):
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
        self.vals = pickle.load(open(path, 'rb'))
        return self.vals


class Timer_():
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

    def toc(self):
        self.tictoc.append(time.time() - self.ticpoint)
        self.alltoc.append(time.time() - self.initpoint)
        return self

    def add_exd(self, exd):
        if type(exd) is list:
            self.extradata += exd
        else:
            self.extradata.append(exd)

    def stop(self):
        self.stopoint = time.time()

    def sleep(self,n=0.1):
        time.sleep(n)