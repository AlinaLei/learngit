from numba import jit
import numpy as np
import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
config1 = tf.ConfigProto()
config1.gpu_options.allow_growth = True
config1.allow_soft_placement = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.02


def add_layer(inputs, in_size, out_size, activation_function=None, name='', with_scope=False):
    # add one more layer and return the output of this layer
    # 可以加任意的层数 为DL打好基础
    if with_scope:
        # 大部件，定义层 layer，里面有 小部件 with定义的部件可以在tensorbord里看到
        with tf.name_scope('layer'):
            # 区别：小部件
            with tf.name_scope('weights'):
                Weights = tf.Variable(tf.random_normal([in_size, out_size]), name='W'+name)
            with tf.name_scope('biases'):
                biases = tf.Variable(tf.zeros([1, out_size]) + 0.1, name='b'+name)
            # with tf.name_scope('Wx_plus_b'):
    else:
        Weights = tf.Variable(tf.random_normal([in_size, out_size]), name='W'+name)
        biases = tf.Variable(tf.zeros([1, out_size]) + 0.1, name='b'+name)

    Wx_plus_b = tf.add(tf.matmul(inputs, Weights), biases)
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b, )
    return Weights,biases,outputs


# L1正则化函数
def w11(W):
    return tf.sqrt(tf.reduce_sum(tf.square(W), 1))
def L1_loss(W):
    return tf.reduce_sum(w11(W))
def LN(W,n=0.5):  # https://www.zhihu.com/question/62605106
    return tf.reduce_sum(tf.pow(w11(W),n))


@jit()
def nth_ladder_create(mat, n=3, col=-1):  # 构造阶梯属性以实现RNN n阶数 col被选做构成阶梯的列(属性)
    mat_ = mat[n:, :]
    for i in range(1, n+1):
        mat_ = np.hstack((mat[n-i:-i, col], mat_))
    return mat_


class tensor_con():
    # 初始化network ie. hidenlayer_nodes=[2], lay_func=[tf.nn.sigmoid,None]
    # hidenlayer_nodes: 列表分别代表每个隐藏层节点数 lay_func:列表表示是每层激活函数 None 表示没有激活函数
    def __init__(self,input_nodes, hidenlayers_nodes, lay_func, learnrate=0.1, Regu=None, name=''):
        # self.name = ''.join([str(x) for x in ([input_nodes] + hidenlayers_nodes + [lay_func[-1].split('.')[-1]])])
        self.name = name
        self.hidenlayer_num = len(hidenlayers_nodes)
        self.initflag = 0
        self.fit_times = 0
        with tf.name_scope('yinput'):
            self.yinput = tf.placeholder(tf.float32, [None, 1], name='y_input')

        cli = [input_nodes] + hidenlayers_nodes + [1]
        with tf.name_scope('xinput'):
            self.xinput = tf.placeholder(tf.float32, [None, cli[0]], name='x_input')

        self.alllayers = [self.xinput]  # all layers   input + hidenlayer + predictlayer
        self.layersW = []  # all layer weights
        self.layersb = []  # all layer biases
        for i in range(self.hidenlayer_num + 1):
            w, b, o = add_layer(self.alllayers[-1], cli[i], cli[i + 1]
                                , activation_function=eval(lay_func[i]), name=self.name )
            self.alllayers += [o]
            self.layersW += [w]
            self.layersb += [b]

        # Regularization 正则化约束 and loss
        with tf.name_scope('Regularization'):
            self.regu = eval(Regu+'(self.layersW[0])') if Regu else tf.constant(0, tf.float32)
        # with tf.device('/gpu:0'):
        with tf.name_scope('loss'):
            self.l1 = tf.reduce_mean(tf.abs(tf.subtract(self.alllayers[-1], self.yinput)), reduction_indices=[0])  # reduction_indices是指沿tensor的哪些维度求和
            self.loss = self.l1 + self.regu

        # train
        # with tf.device('/gpu:0'):
        with tf.name_scope('train'):
            self.train_step = tf.train.AdamOptimizer(learning_rate=0.05).minimize(self.loss)
            # self.train_step = tf.train.MomentumOptimizer(learnrate,momentum = 0.01).minimize(self.loss)
            # self.train_step = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(self.loss)
        # tf sess init
        self.sess = tf.Session(config=config1)
        self.sessinit()

    def sessinit(self, layersw=None):
        if layersw:
            for i in range(len(layersw)):
                self.layersW[i] = tf.Variable(layersw[i], name='W_'+self.name)
        self.sess.run(tf.global_variables_initializer())
        self.initflag = 1
        return self

    def get_tfvalue(self,val='self.layersW'):
        if type(val) is str:
            val = val if val[:4] == 'self' else 'self.'+val
            return self.sess.run(eval(val))
        else:
            return self.sess.run(val)

    def datainit(self, mat, test_size=1, y_col=-1):
        if y_col == -1:
            self.x_data = mat[:, :y_col]
        else:
            self.x_data = np.hstack((mat[:, :y_col],mat[:, y_col+1:]))
        self.y_data = mat[:, y_col:]
        self.yp_data = -mat[:, y_col:]  # 初始化一个全量y的输出值,后面会被改变
        self.Xnormtp = None
        self.Ynormtp = None

        self.len = len(self.y_data)
        if test_size > 0:
            return self.sieve_ind(test_size)
        else:
            return 'error input test_size!!!'

    def sieve_ind(self, sieve=0.2):
        if sieve >= 1:
            self.train_ind = list(range(0, self.len - int(sieve)))
            self.test_ind = list(range(self.len - int(sieve), self.len))
            return self
        else:
            p = np.random.random(self.len) < sieve
            self.test_ind = np.where(p)[0].tolist()
            self.train_ind = np.where(p == False)[0].tolist()
            if self.test_ind and self.train_ind:
                return self
            else:
                return self.sieve_ind(sieve)
    
    def pure_fitwith_be(self, beind_array, batch_size=100):  # beind_array 长度就是次数，数值就是每次起点索引
        # for beind in beind_array:  change to gaint feed
        while beind_array.__len__():
            batch_arr,beind_array = beind_array[:batch_size], beind_array[batch_size:]
            xtraining_data = np.vstack((self.x_data[self.train_ind, :][beind:, :] for beind in batch_arr))
            ytraining_data = np.vstack((self.y_data[self.train_ind, :][beind:, :] for beind in batch_arr))
            self.sess.run(self.train_step, feed_dict={self.xinput: xtraining_data, self.yinput: ytraining_data})

    # 使用Cross-validation 当结束条件 一般用在测试集和验证集都很多时
    def networkfit_withCross(self, times=1000, batch_train_lp=0, op_oerr=0.00003, op_otimes=1, eprint=False, lprint=False):
        # batch_train_lp  批学习控制参数  此处是为了变向加重近期样本的权重（加强他们对学习结果的影响）.
        if self.train_ind.__len__() < 500 or self.test_ind.__len__() < 100:
            # print('sample_size(%s,%s) is too small !!' %(self.train_ind.__len__(),self.test_ind.__len__()))
            withCross = False
        else:
            withCross = True
        if self.fit_times == 0:
            self.sessinit()
        self.fit_times += 1
        self.mse = 9999
        standard_feed = {self.xinput: self.x_data[self.train_ind, :],
                         self.yinput: self.y_data[self.train_ind, :]}
        print_form = 'iter:%s||last_loss:%s||loss(%s)=train(%s)+cross(%s)||Relu:%s||st:%s'
        i, st = 0, 0  # i:times计数, st:fitstop_otimes计数
        mse_cross, mse_train, mse = 0.0, 0.0, 0.0
        for i in range(times):

            if withCross:
                self.pure_fitwith_be([0, 0])
                mse_cross = self.sess.run(self.loss, feed_dict={self.xinput: self.x_data[self.test_ind, :],
                                                                self.yinput: self.y_data[self.test_ind, :]})
            else:
                arr_tmp = (np.random.random(99) - 1 / (batch_train_lp + 1)) * len(self.train_ind)
                beind_array = np.clip(arr_tmp, 0, len(self.train_ind) - 1).astype('int')
                self.pure_fitwith_be(beind_array, batch_size=40)

            mse_train = self.sess.run(self.loss, feed_dict=standard_feed)
            mse = mse_cross + mse_train
            delta_mse = mse - self.mse
            if op_oerr > delta_mse > -op_oerr:
                st += 1
            elif delta_mse > 10 * op_oerr:
                st += 2
            elif st > 0:
                st -= .5
            if eprint:
                print(print_form %(i, self.mse, mse, mse_train, mse_cross,'',st))

            self.mse = mse
            if st > op_otimes or mse < op_oerr * 100:
                break

        if lprint:
            Relu_num = self.sess.run(self.regu, feed_dict=standard_feed)
            print(print_form % (i, self.mse, mse, mse_train, mse_cross, Relu_num, st))
        return self

    def netpredict(self, do_inverse=True):
        # self.yp_data = self.sess.run(self.alllayers[-1], feed_dict={self.xinput: self.x_data})
        for i in self.test_ind:
            self.yp_data[i, :] = self.sess.run(self.alllayers[-1], feed_dict={self.xinput: self.x_data[i, :]})
        if do_inverse:
            self.Inverse_normaliz()
        return self.yp_data

    def net_save_restore(self, save_path, sr_type='save'):
        a_saver = tf.train.Saver(self.layersW + self.layersb)
        if sr_type == 'save':
            a_saver.save(self.sess, save_path)
        else:
            a_saver.restore(self.sess, save_path)

    def normalizx(self, tp='dev_Max'):
        self.Xnormtp = tp
        if tp == 'dev_Max':
            self.xMdata = np.abs(self.x_data).max(0)
            if (self.xMdata == 0).any(): self.xMdata[self.xMdata == 0] = 1
            self.x_data = self.x_data / self.xMdata
        elif tp == 'rel_n11':
            self.xMdata = self.x_data.max(0) - self.x_data.min(0)
            self.xdelta = self.x_data.min(0)
            self.x_data = (self.x_data - self.xdelta) / self.xMdata
        return self

    def normalizy(self, tp='dev_Max'):
        self.Ynormtp = tp
        if tp == 'dev_Max':
            self.yMdata = np.abs(self.y_data).max(0)
            if (self.yMdata == 0).any(): self.yMdata[selfy.Mdata == 0] = 1
            self.y_data = self.y_data / self.yMdata
        elif tp == 'rel_n11':
            self.yMdata = self.y_data.max(0) - self.y_data.min(0)
            self.ydelta = self.y_data.min(0)
            self.y_data = (self.y_data - self.ydelta) / self.yMdata
        return self

    def Inverse_normaliz(self, onlyy=True):
        if onlyy == False:
            if self.Xnormtp == 'dev_Max':
                self.x_data = self.x_data * self.xMdata
            elif self.Xnormtp == 'rel_n11':
                self.x_data = self.x_data * self.xMdata + self.xdelta

        if self.Ynormtp == 'dev_Max':
            self.y_data = self.y_data * self.yMdata
            self.yp_data *= self.yMdata
            self.Ynormtp = None
        elif self.Ynormtp == 'rel_n11':
            self.y_data = self.y_data * self.yMdata + self.ydelta
            self.yp_data = self.yp_data * self.yMdata + self.ydelta
            self.Ynormtp = None
        return self

    def __del__(self):
        try:
            self.sess.close()
        except Exception as err:
            print(' tensor_con.__del__: ',err)
