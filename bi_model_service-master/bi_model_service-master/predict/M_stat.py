
from scipy import optimize
# , stats, integrate
import numpy as np
import sympy as syp
import random
import re

x = syp.Symbol('x')
namd = syp.Symbol('R_')
k = syp.Symbol('k')
# pdf-probability density function:概率密度函数    cdf-Cumulative Distribution Function 分布函数
wb_pdf = k/namd*(x/namd)**(k-1)*np.e**(-(x/namd)**k)  # 威布尔分布
rl_pdf = wb_pdf.subs(k, 2)   # 瑞利分布 pdf
#rl_cdf=syp.integrate(rl_pdf,(x,0,x))  # 注意syp和scipy下都有integrate方法
rl_cdf = 1.0 - 1.0*np.e**(-(x/namd)**2) # 瑞利分布 cdf

# 符号函数func化,变成可调用(callable)函数，或通过求得CDF手写，它试用于帮忙推导CDF的过程
sf=re.sub('x','x.astype(np.float64)',str(rl_cdf))
#sf=re.sub('2.71\d+','np.e',sf)
#print('rl_CDF=lambda x,R_:%s' %sf)
rl_CDF=0;exec('rl_CDF=lambda x,R_:%s' %sf)

#e_CDF=lambda x,lam:1-np.e**(-lam*x) 

#生成[a,b]内满足均匀分布的随机数
rand_ab = lambda a=0, b=1: (b-a)*random.random()+a

max_dt = 66.6


def arr_nearest(mat,P,with_sort=True):  # 返回arrry中最接近n的元素arrn和其位置indx      with_sort=True 未排序的还没写  需要用到快排的思想(可以不用全排)
    res = np.argwhere(mat == P)
    if len(res) > 0:
        return P,res[0,0]
    L = len(mat)
    lr = (0, L-1)  # 区间
    st = int(rand_ab(*lr))
    mat_ = mat*(1 if mat[st + 1] >= mat[st] else -1) - P
    while(True):
        if mat_[st+1] > 0 > mat_[st] :
            break
        elif mat_[st+1] > 0 :
            lr = (lr[0],st)
        else :
            lr = (st,lr[1])
        st = int(rand_ab(*lr))
    if mat_[st+1] < -mat_[st]:
        return mat[st+1], st+1
    else: 
        return mat[st], st


def rand_cdf(cdf, leng=1, dx=0.1):  # 通过模拟求解CDF来生成分布 #syp.solve(cdf-rand_ab()) can not do this
    randlist = []
    X = np.linspace(0,dx*(leng*10-1),leng*10)
    Y = np.array([cdf.evalf(subs={x: x1}, n=4) for x1 in X])

    while(len(randlist)<leng):
        P = rand_ab()
        while(P>Y[-1]):
            st = X[-1]+dx
            X_ = np.linspace(st,st+dx*(leng*10-1),leng*10)
            Y_ = np.array([cdf.evalf(subs={x: x1}, n=4) for x1 in X_])
            X = np.hstack((X,X_))
            Y = np.hstack((Y,Y_))
        tem, ind = arr_nearest(Y,P)
        randlist.append(X[ind])
    return randlist


def rand_pdf(pdf, leng=1, m=100):
    X=np.array(range(1, m))
    cdf=syp.integrate(pdf,(x, 0, x))
    print(pdf, cdf)
    Y=np.array([cdf.subs(x,i)/i for i in X])
    xm=X[Y==Y.max()][-1]+2   #最优二分位置
    ym=cdf.subs(x, xm)
    yield xm, ym
    randlist=[];w=ym/(1-ym)*(m-xm)/(xm-0); print(w)
    while(len(randlist)<leng):
        if rand_ab()<ym: 
            r1=rand_ab(0,xm)
            if pdf.subs(x,r1)>rand_ab(): randlist.append(r1)
        else : 
            r1=rand_ab(xm,m); print(r1, pdf.subs(x,r1)*w)
            if (pdf.subs(x,r1)*w)>rand_ab(): randlist.append(r1)
    randarray=np.array(randlist)
    predict=randarray.mean()
    yield predict, cdf.subs(x,predict), randarray #预测值，分布概率，预测列表


# cdf 函数拟合
from numba import *
@jit()
def cdffit(x_, CDF):
    x_.sort()
    y_=np.linspace(0, 1, len(x_)+1)
    y=y_[:-1]
    #print(x,y)
    popt, pcov=optimize.curve_fit(CDF, x_, y, p0=(6))
    return popt, pcov


# 基于统计的预测
def stat_pre(x_,rand_status=False):
    center_dt_avg = 6.6  # 看作所有样本的均值,首5次内加油的用户参考值
    x_x = x_[x_<max_dt/2]
    x_x = np.hstack((center_dt_avg, x_x))
    scal = (abs(x_x.mean()-center_dt_avg)+1)/(abs(x_x[-1]-center_dt_avg)+1)
    center_dt_avg = (x_x.mean() + x_x[-1]*scal)/(scal+1)
    if x_.__len__() < 6:
        return center_dt_avg, len(x_), 'dt_avg'

    try:
        namd_, p_1 = cdffit(x_, rl_CDF)
    except Exception as err:
        print(err)
        return center_dt_avg, len(x_), 'dt_avg'

    if float(p_1) <= 1:
        #fg = rand_pdf(rl_pdf.subs(namd, namd_), 20)
        #xym = fg.__next__()
        #predict,P,randarray = fg.__next__()
        cdf = rl_cdf.subs(namd, namd_)
        if rand_status == False:
            x_arr = np.linspace(0, max_dt/2, 334)
            x1,p =  center_dt_avg, 0
            for x1 in x_arr:
                p = cdf.evalf(subs={x: x1}, n=4)
                if p > 0.56:
                    break
            return x1, float(p), str(cdf)
            # y_arr = np.array([cdf.evalf(subs={x: x1}, n=4) for x1 in x_arr])
            # void_, ind = arr_nearest(y_arr, 0.6)
            # predict = x_arr[ind]
            # return predict,cdf.subs(x, predict)
    else:
        return center_dt_avg, len(x_), float(p_1)

if __name__ == "__main__":
    print('hello M_stat! predict based on statistics')