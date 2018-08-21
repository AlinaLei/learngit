# !/usr/bin/env python3
 
import tensorflow as tf
import pandas as pd
import numpy as np
 
def read_data(filename):#读取数据
    data=pd.read_csv(filename)
    return data
 
def handle_data(data):
    y_data=data['label'].values.ravel() #获取标签数据
    data.drop(labels='label',axis=1,inplace=True) #Image 数据
    return data,y_data
def train_val_split(x_data,y_data):
    large=x_data.shape[0]
    print(large)
    x_train=x_data.iloc[:large-200,].div(255.0)#由于数据值范围在0-255，部分值差异太大，故进行0-1标准化
    y_train=y_data[:large-200,].astype(np.float32) #需要保证数据类型一致性
    x_val=x_data.iloc[large-200:,].div(255.0)#由于数据值范围在0-255，部分值差异太大，故进行0-1标准化，此为验证Images数据，用来验证后面的模型的准确率
    y_val=y_data[large-200:,].astype(np.float32)#此为Label数据，用来验证后面模型的准确率
    return x_train,y_train,x_val,y_val
#one_hot编码
def one_hot(data):
    num_class=len(np.unique(data))#获取label的个数，这里我们的手写识别数字范围是0~9，所以num_class=10
    print(num_class)
    num_lables=data.shape[0]
    index_offset=np.arange(num_lables)*num_class
    lables_one_hot=np.zeros((num_lables,num_class))
    print(data.ravel())
    lables_one_hot.flat[index_offset+data.ravel()]=1
    return lables_one_hot
 
def train_model(x_train,y_train,x_val,y_val,n): #训练模型并保存模型 此处模型用的softmax回归模型训练y=w*x+b
    x=tf.placeholder("float",[None,784])
    w=tf.Variable(tf.zeros([784,10]),name='w')
    b=tf.Variable(tf.zeros([1,10]),name='b')  #在这里的时候需要保证矩阵的维度在进行 y=x*w+b后直接都是一致的，否则会报错 这里维度为[none,10]=[none,784]*[784,10]+[1,10]
    y=tf.nn.softmax(tf.matmul(x,w)+b) #定义模softmax 函数 这里需要注意我们在模型训练的时候y值存储的是0,1值，比如如果label为5，则在实际中的标识为[0,0,0,0,1,0,0,0,0,0],softmax 激活函数通常用在分类问题中
    y_=tf.placeholder("float",[None,10])
    cross_entropy=-tf.reduce_sum(y_*tf.log(y)) #设置交叉熵
    train_step=tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
    init=tf.global_variables_initializer()
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))  # argmax(y,1)这个函数是用来获取每一行y中最大值的下标，和One_hot原理上相同,tf.equal用来返回预测值和实际值一样则为True,反之为False
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))  #计算正确率
    sess=tf.Session() #创建Session对话的时候需要先初始化
    sess.run(init) #初始化sess
    n_batch=int(len(x_train)/100) #设置迭代参数，这里把迭代次数设置的比较小，后面是可以对应调整的
    saver=tf.train.Saver() #用来保存模型
    for i in range(n):#设置迭代次数
        for count in range(n_batch):
            batch_xs=x_train[count*100:(count+1)*100] #设置分批次获取数据
            batch_ys=y_train[count*100:(count+1)*100] #设置分批次获取标签数据
            sess.run(train_step,feed_dict={x:batch_xs,y_:batch_ys}) # 训练模型
        #saver.save(sess,'model/my_minist_model',global_step=i) #保存模型到本地设置没迭代一次就保存一次
        accuracy_n=sess.run(accuracy, feed_dict={x: x_val, y_: y_val})
        print("第"+str(i+1)+'轮，准确率为：'+str(accuracy_n)) #通过验证数据来的到模型的准确率
    #print(sess.run(w)) #查看经过训练后的w
    print(sess.run(b)) #查看经过训练后的b
 
def load_model():#加载整个模型的构造
    with tf.Session() as sess:
        saver=tf.train.import_meta_graph('model/my_minist_model-417.meta')
        saver.restore(sess,tf.train.latest_checkpoint('model/'))
        w=sess.run('w:0')
        b=sess.run('b:0')
        print(sess.run(fetches,feed_dict=None))
 
def load_data(data,filename):#此处只加载模型的参数
    try:
        reader=tf.train.NewCheckpointReader(filename)
        variables=reader.get_variable_to_shape_map()
        x=tf.placeholder("float",[None,784])
        w=reader.get_tensor('w')
        b=reader.get_tensor('b')
        y = tf.nn.softmax(tf.matmul(x, w) + b) #沿用之前训练的时候的softmax函数
        with tf.Session() as sess:
            y_pre=sess.run(y,feed_dict={x:data})
            y_=tf.argmax(y_pre,1) #获取最终结果，由于之前我们的y 存储的是0，1值，这里我们需要获取对应的0,1值对应的数字，如果如果为[0,0,0,0,1,0,0,0,0,0]，这里我们通过argmax会直接转换为5
            result=y_.eval() #tensor变量转换为array
            pd.DataFrame({'ImageId':np.arange(len(result))+1,'Label':result}).to_csv('../minist/result.csv',index=False) #输出到CSV文件
            print(y_.eval())
    except Exception as e:
        print(str(e))
 
#神经网络模型
class CNN():
    def __init__(self):
        pass
 
    # 权重初始化，在初始化中加入少量噪声，来打破对称性以及避免后面的0梯度
    def weight_variable(self,shape,name=False):
        initial=tf.truncated_normal(shape,stddev=0.1)
        return tf.Variable(initial,name=name)
 
    # 初始化偏置量，由于使用的是ReLU神经元，此处用较小的正数来初始化偏置项，避免神经元节点输出恒为0的问题
    def bias_variable(self,shape,name=False):
        initial=tf.constant(0.1,shape=shape)
        return tf.Variable(initial,name=name)
 
    #生成feature map
    def conv2d(self,x,w):
        return tf.nn.conv2d(x,w,strides=[1,1,1,1],padding='SAME')
 
    #对feature map 做降维过程,从而减少网格中的参数和计算量，避免过拟合
    def max_pool_2x2(self,x,name=False):
        return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME',name=name)
 
    def train_cnn(self,x_train,y_train,x_val,y_val,n):
        #占位符
        x=tf.placeholder('float',[None,784],name='x')
        y_=tf.placeholder('float',[None,10],name='y_')
        keep_prob = tf.placeholder("float",name='keep_prob')
        x_image = tf.reshape(x, [-1, 28, 28, 1],name='x_image')
        #第一层卷积
        with tf.variable_scope('layer1-conv1'):
            w_conv1=self.weight_variable([5,5,1,32],name='w_conv1')
            b_conv1=self.bias_variable([32],name='b_conv1')
            h_conv1=tf.nn.relu(self.conv2d(x_image,w_conv1)+b_conv1,name='h_conv1')
 
        with tf.name_scope('layer2-pool1'):
            h_pool1=self.max_pool_2x2(h_conv1,name='h_pool1')
        #第二层卷积
        with tf.variable_scope('layer3-conv2'):
            w_conv2=self.weight_variable([5,5,32,64],name='w_conv2')
            b_conv2=self.bias_variable([64],name='b_conv2')
            h_conv2=tf.nn.relu(self.conv2d(h_pool1,w_conv2)+b_conv2,name='h_conv2')
 
        with tf.name_scope('layer4-pool2'):
            h_pool2=self.max_pool_2x2(h_conv2,name='h_pool2')
        #密集连接层
        with tf.variable_scope('layer5-fc1'):
            w_fc1=self.weight_variable([7*7*64,1024],name='w_fc1')
            b_fc1=self.bias_variable([1024],name='b_fc1')
            h_pool2_flat=tf.reshape(h_pool2,[-1,7*7*64],name='h_pool2_flat')
            h_fc1=tf.nn.relu(tf.matmul(h_pool2_flat,w_fc1)+b_fc1,name='h_fc1')
            #dropout
            h_fc1_drop=tf.nn.dropout(h_fc1,keep_prob,name='h_fc1_drop')
        #输出层
        with tf.variable_scope('layer6-fc2'):
            w_fc2=self.weight_variable([1024,10],name='w_fc2')
            b_fc2=self.bias_variable([10],name='b_fc2')
        #定义预测目标
        y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop,w_fc2)+b_fc2)
        #创建saver
        saver = tf.train.Saver(tf.global_variables())  # 用来保存模型
        tf.add_to_collection('pred_network',y_conv)
        cross_entropy=-tf.reduce_sum(y_*tf.log(y_conv))
        train_step=tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
        correct_prediction=tf.equal(tf.argmax(y_,1),tf.argmax(y_conv,1))
        accuracy=tf.reduce_mean(tf.cast(correct_prediction,'float'))
        init = tf.global_variables_initializer()
        sess=tf.Session() #初始化Session
        sess.run(init)
        n_batch=int(len(x_train)/100)
 
        for i in range(n):
            for count in range(n_batch):
                batch_xs=x_train[count*100:(count+1)*100]
                batch_ys=y_train[count*100:(count+1)*100]
                sess.run(train_step,feed_dict={x:batch_xs,y_:batch_ys,keep_prob:1.0})
            accuracy_n=sess.run(accuracy,feed_dict={x:x_val,y_:y_val,keep_prob:1.0})
            print("第"+str(i+1)+"轮，准确率为："+str(accuracy_n))
        saver.save(sess, 'CNNmodel/my_minist_cnn')  # 保存模型到本地设置
 
    def load_cnn_model(self,data, filename):  # 此处只加载模型
        try:
            """
            reader = tf.train.NewCheckpointReader(filename)
            variables = reader.get_variable_to_shape_map()
            for i in variables:
                print(i)
            """
            with tf.Session() as sess: # 初始化Session
                new_saver= tf.train.import_meta_graph(filename)
                new_saver.restore(sess,'CNNmodel/my_minist_cnn')
                #获取预测目标公式
                y_conv=tf.get_collection('pred_network')[0]
                graph=tf.get_default_graph()
                #获取初始化的配置
                x=graph.get_operation_by_name('x').outputs[0]
                keep_prob=graph.get_operation_by_name('keep_prob').outputs[0]
                batch=int(len(data)/100)
                print(batch)
                result=[]
                for i in range(batch): #分批次预测数据结果，不然一次输入矩阵太大会内存不足
                    batch_x=data[i*100:(i+1)*100]
                    y_pre=sess.run(y_conv,feed_dict={x:batch_x,keep_prob:1.0})
 
                    result_= tf.argmax(y_pre, 1)
                    result_tran=result_.eval().tolist() # tensor变量转换为array 然后平铺为list
                    result=result+result_tran  #list相加
                pd.DataFrame({'ImageId': np.arange(len(result)) + 1, 'Label': result}).to_csv('../minist/result1.csv',index=False)  # 输出到CSV文件
 
        except Exception as e:
            print(str(e))
 
 
if __name__=='__main__':
    train=read_data('F:\\kaggle\\minist\\train.csv')
 
    data,y_data=handle_data(train)
    y=one_hot(y_data)# 通过one_hot编码，把shape变为（？，10）
    print(y.shape)
    x_train,y_train,x_val,y_val=train_val_split(data,y)
    print(x_train.shape,y_train.shape,x_val.shape,y_val.shape)
    cnn=CNN()
    cnn.train_cnn(x_train=x_train,y_train=y_train,x_val=x_val,y_val=y_val,n=10)
    #train_model(x_train,y_train,x_val,y_val,8)
    
 
 
