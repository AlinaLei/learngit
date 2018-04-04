import re,time,pymysql,json
import pandas as pd
from sqlalchemy import create_engine
import sys
if 'config' not in dir():
    sys.path.append('../.settings')
    # sys.path.append('../DBbase')
    import config
if 'Timer_' not in dir():
    from hcomponents import *


class my_():

    def __init__(self, name=''):
        self.db_dic = {'ho': '', 'pt': 3306, 'cset': 'utf8'}
        self.conn = None
        self.cur = None
        self.engs = ''
        # self.sh_for_load = ''
        self.table = ''
        self.db = ''
        self.tablename = ''
        self.cset = ''
        self.name = ''
        self.engs_stment = "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s"
        self.wait = 4  # 为了闪断地令人蛋碎的mysql
        self.module = pymysql
        self.c_conn(name)

    def wait_for_anothert(self, errflag, err):
        boob = self.wait < 19
        if boob:
            # 1507 - Error in list of partitions to DROP
            if type(err.args[0]) is int and err.args[0] in [1062, 1507]:
                print(err.args[0], 'err_num pass')
                return False
            for x in ['already exists', "doesn't exist", 'Duplicate ', 'error in your SQL', 'partitions to DROP']:
                if type(err.args[0]) is str and re.findall(x, err.args[0]):  # ex_exceptions 不再继续等待重做的例外
                    print(x, err.args[0], 'pass')
                    return False

            print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'Exception:flag(%s):' %errflag)
            print('   ', err, 'waiting for %s .... ' % self.wait, )
            time.sleep(self.wait)
            self.wait += 1
        else:
            self.quit('重连了太多次,aborted！')
        return boob

    def c_conn(self, name=''):  # change or create conn
        try:
            if name in config.AccessKey_dict:
                self.db_dic.update(config.AccessKey_dict[name])
                self.name = name
            elif name == '' and self.name:
                return self.c_conn(self.name)
            else:
                return 0

            self.conn=self.module.connect(host=self.db_dic['ho'], user=self.db_dic['us'], passwd=self.db_dic['pwd']
                                      , port=self.db_dic['pt'], db=self.db_dic['db'], charset=self.db_dic['cset'])
            self.cur = self.conn.cursor(self.module.cursors.DictCursor)
            self.engs = self.engs_stment % (self.db_dic['us'], self.db_dic['pwd']
                                        , self.db_dic['ho'], self.db_dic['pt'], self.db_dic['db'], self.db_dic['cset'])
            # self.sh_for_load = 'mysql -h%s -u%s -p%s -P%s %s --local-infile=1 -e "%%s" ' % (self.db_dic['ho']
            #                             , self.db_dic['us'], self.db_dic['pwd'], self.db_dic['pt'], self.db_dic['db'])
            return self
        except Exception as err:
            if self.wait_for_anothert('c_conn',err):
                return self.c_conn(name)

    def get_atable(self, sql):
        if self.table == '':
            RES = re.findall('from\s+(.*?)\s+', sql)
            if RES:
                self.table = RES[0]
        return self.table
    
    def getdata(self, sqls):
        try:
            if type(sqls) is list:
                for sql in sqls[:-1]:
                    self.cur.execute(sql)
                sqls = sqls[-1]
            self.cur.execute(sqls)
            self.conn.commit()
            self.get_atable(sqls)
            rows = self.cur.fetchall()
            return rows
        except Exception as err:
            if self.wait_for_anothert('getdata', err):
                return self.c_conn().getdata(sqls)

    def predo_sqls(self,sqls):
        # 长sql预处理,输入是长字符的sql,多段sql之间可以是;分割,处理前面的并返回最后一段sql
        sqlslist = sqls.split(';')
        while len(re.sub('\s', '', sqlslist[-1])) < 6:  # 去掉长度很小的无效sql
            sqlslist.pop(-1)
        for sql in sqlslist[:-1]:  # 去掉长度很小的无效sql
            if len(re.sub('\s', '', sql)) > 6:
                _ = self.getdata(sql)
        return sqlslist[-1]

    def to_dataframe(self, sqls):
        #  sqlslist   允许用;间隔多个sql,并可返回最后一个sql的返回结果去转换成dataframe
        sqls = self.predo_sqls(sqls)
        try:
            df = pd.read_sql(sqls, self.conn)
            self.conn.commit()
            self.get_atable(sqls)
            return df
        except Exception as err:
            if self.wait_for_anothert('to_dataframe', err):
                return self.c_conn().to_dataframe(sqls)
            else:
                return pd.DataFrame([])

    def df_upd_tosql(self, df, batch=666, table=''):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        df = df.fillna('Null')  # df的空值插入值 用inplace=True会报异常(解释待定)
        dfcolist = df.columns.get_level_values(0)
        cols = ','.join(dfcolist)
        valst = ','.join(['%s=VALUES(%s)' % (x, x) for x in dfcolist])
        resu = []
        while(df.__len__()>0):
            ind = df.index[:batch]
            values = ','.join(['(%s)' % ','.join([str(df.loc[i, c]) for c in dfcolist]) for i in ind])
            sqls = 'INSERT INTO %s (%s) VALUES %s ON DUPLICATE KEY UPDATE %s' %(table,cols,values,valst)
            resu += [self.sql_engine(sqls)]
            df.drop(ind, inplace=True)
        return resu

    def di_upd_tosql(self, di, table=''):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        colist, valist = [], []
        for k, v in di.items():
            colist += [k]
            valist += [str(v)]
        cols = ','.join(colist)
        vals = ','.join(valist)
        valst = ','.join(['%s=VALUES(%s)' % (x, x) for x in colist])
        sqls = 'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (table, cols, vals, valst)
        return self.sql_engine(sqls)

    def sql_engine(self, sqls=None, echo=False):
        try:
            eng = create_engine(self.engs, echo=echo, encoding=self.db_dic['cset'])
            # eng.execute('SET NAMES utf8')
            # eng.execute('SET CHARACTER SET utf8')
            # eng.execute('SET character_set_connection=%s;' %self.db_dic['cset'])
            # eng.execute("SHOW VARIABLES LIKE '%character%';")
            if sqls:
                sqls = self.predo_sqls(sqls)
                return eng.execute(sqls).rowcount
            else:
                return eng
        except Exception as err:
            if self.wait_for_anothert('sql_engine', err):
                return self.c_conn().sql_engine(sqls)

    def add_partition_gener(self, pname, pvalue, table='', tp=1):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        if tp == 1:
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES LESS THAN (%s));"
            return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue))

        if tp == 'list':
            ADD_PARTITION_gener1 = "ALTER TABLE %s ADD PARTITION (PARTITION p%s VALUES IN (%s));"
            return self.sql_engine(ADD_PARTITION_gener1 % (table, pname, pvalue))

    def drop_partition(self, pname, table=''):
        if table == '':
            table = self.table
            if table == '':
                return 'No table specified ~'
        return self.sql_engine('alter table %s drop PARTITION %s' % (table, pname))

    def get_partiotion(self,db_tablename):  # db_tablename 需要是库.表名格式传入
        self.db, self.tablename = db_tablename.split('.')
        sqls = """SELECT  TABLE_SCHEMA,TABLE_NAME,partition_name,partition_expression,partition_description,table_rows  
                  FROM  INFORMATION_SCHEMA.partitions WHERE TABLE_SCHEMA = '%s' and TABLE_NAME='%s'""" % (self.db,self.tablename)
        return self.to_dataframe(sqls)

    def init_bigtable_bypart(self, sqls):
        self.get_atable(sqls)
        df_part = self.get_partiotion(self.table)
        df_list = []
        print('总分区数：', df_part.partition_name.__len__())
        for part in df_part.partition_name:
            print('%s partition (%s)' %(self.table,part))
            part_sqls = sqls.replace(self.table,'%s partition (%s)' %(self.table,part))
            df_list += self.to_dataframe(part_sqls)
        return df_list

    def quit(self, message=''):
        try:
            if message:
                print(message)
            # self.cur.close()
            self.conn.close()
        except Exception as err:
            print(day_forpast(0, ss='%Y-%m-%d %H:%M:%S'), 'Exception:flag(quit):', err.args[0])

    # def __del__(self):
    #     self.quit()


class ms_(my_):
    def __init__(self, name=''):
        super(ms_, self).__init__()
        self.db_dic = {'ho': '', 'pt': 1433, 'cset': 'UTF-8'}
        self.engs_stment = "mssql+pymssql://%s:%s@%s:%s/%s?charset=%s"
        self.module = pymssql

    def getdata_(self, sqls):
        if type(sqls) is list:
            for sql in sqls:
                self.cur.execute(sql)
        else:
            self.cur.execute(sqls)
            self.get_atable(sqls)
        rows = self.cur.fetchall()
        self.conn.commit()
        return rows

    def getdata(self, sql):
        df = self.to_dataframe(sql)
        return json.loads(df.to_json(orient='records'))