
import scipy as sp
import numpy as np
# import math

from sklearn.linear_model import LinearRegression
# sklearn.linear_model.LinearRegression   http://www.ppvke.com/Blog/archives/19208
from sklearn.cluster import KMeans


# LinearRegression http://blog.csdn.net/viewcode/article/details/8794401
def SSE(y_test, y):
    return (sp.square(y_test - y)).sum()


def RMSE(y_test, y): #均方误差根
    return sp.sqrt(sp.mean(sp.square(y_test - y)))


def SSR(y_test, y):
    return (sp.square(y_test- y.mean())).sum()


def SST(y):
    return (sp.square(y- y.mean())).sum()


def R2(y_test, y): # # coefficient of determination 决定系数 #http://blog.sciencenet.cn/blog-651374-975670.html
    return 1 - SSE(y_test, y) / SST(y)


def nth_ladder_create(mat,n=3,col=3): #构造阶梯属性 n阶数 col被选做构成阶梯的列(属性)
    mat_=mat[n:,:]
    for i in range(1,n+1):
        mat_=np.hstack((mat[n-i:-i,col], mat_))
    return mat_

"""
# sigmoid function
def nonlin(X, deriv=False):
    if (deriv == True):
        return nonlin(X) * (1 - nonlin(X))
    return 1 / (1 + np.exp(-X))


def nlin(X, deriv=False):
    if (deriv == True):
        return np.tile(1, X.shape)
    return X


class myLR(LinearRegression):
    def __init__(self, mat):
        super(myLR, self).__init__()
        self.mat=mat

    def normaliz(self,tp='dev_Max'):
        self.tp = tp
        if self.tp == 'dev_Max':
            self.Mdata = self.mat.max(0)
            if (self.Mdata==0).any() : self.Mdata[self.Mdata==0] = 1
            self.mat = self.mat/self.Mdata
        elif self.tp == 'rel_n11':
            self.Mdata = self.mat.max(0) - self.mat.min(0)
            self.delta = self.mat.mean(0)
            self.mat = (self.mat - self.delta) / self.Mdata
        return self

    def Inverse_normaliz(self):
        #print('Inverse later')
        if self.yp_test > 1 or self.yp_test < 0:
            self.yp_test = abs(self.yp_test - np.round(self.yp_test))
        if self.tp == 'dev_Max':
            self.ypo_test = self.yp_test * self.Mdata[:, -1]
        elif self.tp == 'rel_n11':
            self.ypo_test = self.yp_test * self.Mdata[:, -1] + self.delta[:, -1]
        return self

    def nth_ladder(self, n=3, col=-1):
        self.mat_ = self.mat[n:, :]
        for i in range(1, n + 1):
            self.mat_ = np.hstack((self.mat[n - i:-i, col], self.mat_))
        self.mat = self.mat_
        return self

    def devide(self, test_size=1):
        self.y_train = self.mat[:-test_size, -1]
        self.x_train = self.mat[:-test_size, :-1]
        self.y_test = self.mat[-test_size:, -1]
        self.x_test = self.mat[-test_size:, :-1]
        return self

    def myfit(self):
        self.fit(self.x_train,self.y_train)
        self.yp_train = self.predict(self.x_train)
        self.yp_test = self.predict(self.x_test)
        # self.ypo_train = self.yp_train*self.Mdata[:,-1]
        self.Inverse_normaliz()  #测试样本Inverse_normaliz
        return self

    def bpnetworkinit(self, hidenlayer_nodes=[2], test_size=1, lay_func=[nonlin,nlin,nlin]):  # 验证猜想 初始化BP hidenlayer_nodes 是列表分别代表每个隐藏层节点数
        self.hidenlayer_num = len(hidenlayer_nodes)
        cli = [self.x_train.shape[1] + 1] + hidenlayer_nodes + [1]
        self.syn = [] # layers_weight
        for si in [(cli[i],cli[i+1]) for i in range(self.hidenlayer_num+1)]:
            self.syn += [2 * np.random.random(si) - 1]
        self.x_train= np.hstack((self.x_train, np.tile(1, (self.x_train.shape[0],1))))
        self.x_test = np.hstack((self.x_test, np.tile(1, (self.x_test.shape[0], 1))))
        return self

    def bpnetworkfit(self, times = 50000, learnrate = 0.01, batch_train_lp = 0 , fitstop_oerr = -0.0000034 ,fitstop_otimes = 1):
        y = np.array(self.y_train)
        st = 0  # fitstop_otimes计数
        self.mse = 9999
        for j in range(times):

            lay = [np.array(self.x_train)] # Feed forward through layers 0, 1, and 2
            for i in range(self.hidenlayer_num+1):
                lay += [nonlin(np.dot(lay[i], self.syn[i]))]

            l_error = [y - lay[-1]] # how much did we miss the target value?

            mse = np.mean(np.abs(l_error[0])) # how to stop train
            if (0 > mse - self.mse > fitstop_oerr ): #  or mse - self.mse > 0.000002) and j > 10:
                st +=1
                if st >= fitstop_otimes:
                     # print(mse - self.mse,self.mse,j,st)
                     break
            else : st = 0
            self.mse = mse
            if self.mse < 0.005 :
                # print(self.mse,j)
                break

            if batch_train_lp > 0 :
                batch_beind = int((np.random.random(2).max() - 2/(batch_train_lp+1))*self.x_train.__len__())
                batch_beind = batch_beind if batch_beind > 0 else 0

                l_error[0] = l_error[0][batch_beind:]

                for i in range(lay.__len__()):
                    lay[i] = lay[i][batch_beind:]


            l_delta = [l_error[-1] * nonlin(lay[-1], deriv=True)]
            for i in range(self.hidenlayer_num):
                l_error = [l_delta[-1-i].dot(self.syn[-1-i].T)] + l_error
                l_delta = [l_error[-2-i] * nonlin(lay[-2-i], deriv=True)] + l_delta
            for i in range(self.hidenlayer_num+1):
                self.syn[i] += lay[i].T.dot(l_delta[i]) * learnrate

            # how much did each l1 value contribute to the l2 error (according to the weights)?
            # l1_error = l2_delta.dot(self.syn[1].T)
            # in what direction is the target l1?
            # were we really sure? if so, don't change too much.
            #l1_delta = l1_error * nonlin(lay[1], deriv=True)

            # self.syn[1] += lay[1].T.dot(l2_delta)*learnrate
            # self.syn[0] += lay[0].T.dot(l1_delta)*learnrate

        # predict

        return self
    def bppredict(self):
        self.r_lay = [np.array(self.x_test)]
        for i in range(self.hidenlayer_num + 1):
            self.r_lay += [nonlin(np.dot(self.r_lay[i], self.syn[i]))]
        self.yp_test = self.r_lay[-1][0]
        self.Inverse_normaliz()

        return self.yp_test,self.ypo_test

    def rmse(self):
        return RMSE(self.yp_train, self.y_train),RMSE(self.yp_test, self.y_test)

    def r2(self):
        return R2(self.yp_train, self.y_train)

"""