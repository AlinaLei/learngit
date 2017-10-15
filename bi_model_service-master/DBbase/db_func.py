import re,datetime,time,pymysql,json,pymssql
import pandas as pd
from sqlalchemy import create_engine
import sys
sys.path.append('../.setting')
import config


def day_forpast(d=0, h=0, ss="%Y%m%d"):
    t1 = datetime.datetime.now()+datetime.timedelta(days=d,hours=h)
    if ss == 'stamp':
        return time.mktime(t1.timetuple())
    elif ss== 'Timestamp':
        return t1
    else:
        return t1.strftime(ss)


class my_():
    def __init__(self,name=-1):
        self.db_dic = {'ho': '', 'pt': 3306, 'cset': 'utf8'}
        self.conn = None
        self.cur = None
        self.engs = ''
        self.sh_for_load = ''
        self.table = ''
        self.cset = ''
        self.c_conn(name=name)

    def c_conn(self, name=1):  # change or create conn
        try:
            if name in config.AccessKey_dict:
                self.db_dic.update(config.AccessKey_dict[name])
            else:
                return

            self.conn = pymysql.connect(host=self.db_dic['ho'], user=self.db_dic['us'], passwd=self.db_dic['pwd']
                                      , port=self.db_dic['pt'], db=self.db_dic['db'], charset=self.db_dic['cset'])

            self.cur = self.conn.cursor()

            self.engs = "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (self.db_dic['us'], self.db_dic['pwd']
                                        , self.db_dic['ho'], self.db_dic['pt'], self.db_dic['db'], self.db_dic['cset'])
            self.sh_for_load = 'mysql -h%s -u%s -p%s -P%s %s --local-infile=1 -e "%%s" ' % (self.db_dic['ho']
                                        , self.db_dic['us'], self.db_dic['pwd'], self.db_dic['pt'], self.db_dic['db'])
            return self
        except Exception as err:
            print(err)
            # self.c_conn(name)

    def get_atable(self, sql):
        if self.table == '':
            RES = re.findall('from\s+(.*?)\s+', sql)
            if RES:
                self.table = RES[0]
    
    def getdata(self, sqls):
      if type(sqls) is list:
         for sql in sqls:
            self.cur.execute(sql)
      else :
         self.cur.execute(sqls)
         self.get_atable(sqls)
      rows = self.cur.fetchall()
      self.conn.commit()
      return rows

    def to_dataframe(self, sqls):
        df = pd.read_sql(sqls,self.conn)
        self.get_atable(sqls)
        self.conn.commit()        
        return df

    def df_upd_tosql(self, df, batch=666, table=''):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        df = df.fillna('Null')  # df的空值插入值
        dfcolist = df.columns.get_level_values(0)
        cols = ','.join(dfcolist)
        valst = ','.join(['%s=VALUES(%s)' %(x,x) for x in dfcolist])
        resu = []
        while(df.__len__()>0):
            ind = df.index[:batch]
            values = ','.join(['(%s)'% ','.join([str(df.loc[i,c]) for c in dfcolist])  for i in ind])
            sqls= 'INSERT INTO %s (%s) VALUES %s ON DUPLICATE KEY UPDATE %s' %(table,cols,values,valst)
            resu += [self.sql_engine(sqls).rowcount]
            df = df.drop(ind)
        return resu

    def sql_engine(self, sqls=None, echo=False):
        eng=create_engine(self.engs, echo=echo,encoding=self.db_dic['cset'])
        # eng.execute('SET NAMES utf8')
        # eng.execute('SET CHARACTER SET utf8')
        # eng.execute('SET character_set_connection=%s;' %self.db_dic['cset'])
        # eng.execute("SHOW VARIABLES LIKE '%character%';")
        if sqls:
            return eng.execute(sqls)
        else:
            return eng

    def add_partition_gener(self,pname,pvalue,table='',type=1):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        if type == 1:
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES LESS THAN (%s));"
            try:
                return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue)).rowcount
            except Exception as err:
                # print(err)
                pass
        if type == 'list':
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES IN (%s));"
            try:
                return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue)).rowcount
            except Exception as err:
                # print(err)
                pass

    def quit(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as err:
            pass
            # print(err)

    def __del__(self):
        self.quit()


class ms_():
    def __init__(self, name):
        self.db_dic = {'ho': '', 'pt': 1433, 'cset': 'UTF-8'}
        self.conn = None
        self.cur = None
        self.engs = ''
        self.sh_for_load = ''
        self.table = ''
        self.cset = ''
        self.c_conn(name=name)

    def c_conn(self, name=1):  # change or create conn
        try:
            if name in config.AccessKey_dict:
                self.db_dic.update(config.AccessKey_dict[name])
            else:
                return
            self.conn = pymssql.connect(server=self.db_dic['ho'], user=self.db_dic['us'], password=self.db_dic['pwd']
                                        , port=self.db_dic['pt'], database=self.db_dic['db'], charset=self.db_dic['cset'])
            self.cur = self.conn.cursor()
            self.engs = "mssql+pymssql://%s:%s@%s:%s/%s?charset=%s" % (self.db_dic['us'], self.db_dic['pwd']
                                                                       , self.db_dic['ho'], self.db_dic['pt'],
                                                                       self.db_dic['db'], self.db_dic['cset'])
            self.sh_for_load = 'mssql -h%s -u%s -p%s -P%s %s --local-infile=1 -e "%%s" ' % (self.db_dic['ho']
                                                                                            , self.db_dic['us'],
                                                                                            self.db_dic['pwd'],
                                                                                            self.db_dic['pt'],
                                                                                            self.db_dic['db'])
            return self
        except Exception as err:
            print(err)
            # self.c_conn(name)

    def get_atable(self, sql):
        if self.table == '':
            RES = re.findall('from\s+(.*?)\s+', sql)
            if RES:
                self.table = RES[0]

    def getdata(self, sqls):
        if type(sqls) is list:
            for sql in sqls:
                self.cur.execute(sql)
        else:
            self.cur.execute(sqls)
            self.get_atable(sqls)
        rows = self.cur.fetchall()
        self.conn.commit()
        return rows

    def to_dataframe(self, sqls):
        df = pd.read_sql(sqls, self.conn)
        self.get_atable(sqls)
        self.conn.commit()
        return df

    def df_upd_tosql(self, df, batch=666, table=''):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        df = df.fillna('Null')  # df的空值插入值
        dfcolist = df.columns.get_level_values(0)
        cols = ','.join(dfcolist)
        valst = ','.join(['%s=VALUES(%s)' % (x, x) for x in dfcolist])
        resu = []
        while (df.__len__() > 0):
            ind = df.index[:batch]
            values = ','.join(['(%s)' % ','.join([str(df.loc[i, c]) for c in dfcolist]) for i in ind])
            sqls = 'INSERT INTO %s (%s) VALUES %s ON DUPLICATE KEY UPDATE %s' % (table, cols, values, valst)
            resu += [self.sql_engine(sqls).rowcount]
            df = df.drop(ind)
        return resu

    def sql_engine(self, sqls=None, echo=False):
        eng = create_engine(self.engs, echo=echo, encoding=self.db_dic['cset'])
        # eng.execute('SET NAMES utf8')
        # eng.execute('SET CHARACTER SET utf8')
        # eng.execute('SET character_set_connection=%s;' %self.db_dic['cset'])
        # eng.execute("SHOW VARIABLES LIKE '%character%';")
        if sqls:
            return eng.execute(sqls)
        else:
            return eng

    def add_partition_gener(self, pname, pvalue, table='', type=1):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        if type == 1:
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES LESS THAN (%s));"
            try:
                return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue)).rowcount
            except Exception as err:
                # print(err)
                pass
        if type == 'list':
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES IN (%s));"
            try:
                return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue)).rowcount
            except Exception as err:
                # print(err)
                pass

    def quit(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as err:
            pass
            # print(err)

    def __del__(self):
        self.quit()

