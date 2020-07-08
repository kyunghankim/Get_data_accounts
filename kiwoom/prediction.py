
# import libraries
import os
# import tensorflow as tf
import pandas as pd
import keras
import numpy as np
#from keras.layers import Embedding
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Bidirectional
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import math
from sklearn.metrics import mean_squared_error

Dbpath = 'C:/Users/ilike/Database/'
filename = 'samsung-minute202007040849'

samsung_minute = pd.read_csv(Dbpath+filename+'.csv')
samsung_open = samsung_minute['open']

open_arr = samsung_open.values[::1].astype('float32')

#dataset만들기
look_back=1
def create_dataset(dataset,look_back=1):
    dataX, dataY=[], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append(dataset[i+look_back])
    return np.array(dataX),np.array(dataY)    #데이터셋으로 바꾸기

#fit을 위한 reshape
open_arr = open_arr.reshape(-1,1)
plt.grid(True)
plt.plot(open_arr)

# scaling작업
scaler = MinMaxScaler(feature_range=(0, 1))
ss_trsf = scaler.fit_transform(open_arr)

# train/test size
train_size = int(len(ss_trsf)*0.7)
test_size = len(ss_trsf) - train_size

# train/test 나누기
train, test = ss_trsf[0:train_size], ss_trsf[train_size:len(ss_trsf)]

trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)

# [sample,feature]에서 [samples,time steps,features]로 바꿈
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

# BiLSTM만들기
model = Sequential()
model.add(Bidirectional(LSTM(4, input_shape=(1, look_back))))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
# 학습시키기
model.fit(trainX, trainY, epochs=50, batch_size=5, verbose=2)

# 예측하기
testPredict = model.predict(testX)

# inverse scale로 가격으로 바꾸어줌
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform(testY)

# RMSE 구하기
testScore = math.sqrt(mean_squared_error(testY,testPredict))

# 마지막날 종가예측 (확인안해봄)
lastX = open_arr[-1]
lastX = np.reshape(lastX, (1, 1, 1))
lastY = model.predict(lastX)
lastY = scaler.inverse_transform(lastY)
# 데이터 입력 마지막 다음날 종가 예측
print('마지막날 종가 예측: %d' % lastY)

# 그래프 그리기
plt.grid(True)
plt.plot(testY) #파란선
plt.plot(testPredict)
plt.show()