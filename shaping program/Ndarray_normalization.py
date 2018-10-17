#-*- coding:utf-8-*-
#numpy 配列の正規化 zscore と max-min
import numpy as np

#ありのままの値みたいのよ as it is
def aii(x, axis = None):
    return x

#Z-scoreで正規化
def zscore(x, axis = None):
    xmean = x.mean(axis=axis, keepdims=True)
    xstd  = np.std(x, axis=axis, keepdims=True)
    zscore = (x-xmean)/xstd
    return zscore

#max-minで正規化
def maxmin(x, axis = None):
    x_max = x.max(axis = axis)
    x_min = x.min(axis = axis)

    mmscore = (x - x_min)/(x_max - x_min)
    return mmscore
