# -*- coding:utf-8 -*-
import numpy as np
import math
from itertools import chain

#指定ファイルの内容をチャンネルごと（列ごと）に分割
def file_parse(filehead, filename):
#整形対象ファイル読み込み
    rfn = open(filehead + filename, "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

    for i, row in enumerate(segcontent):
        if row == "$data":
            data_num = i + 1
            break

    segcontent2 = []
    for row in segcontent[data_num:]:
        if row == "":
            break
        segcontent2.append(row.split(","))

    #ndarrayで転置
    segcontent3 = np.array(segcontent2).T.astype("float").tolist()

    #L2ノルムを導出
    return_content = []
    for i in range(len(segcontent3[0])):
        sum = 0
        for j in range(len(segcontent3[1:])):
            sum += pow(segcontent3[j + 1][i], 2)
        norm = math.sqrt(sum)
        return_content.append(norm)

    return return_content

#cos類似度
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

#key-pointsの選択，局所特徴ベクトルを返り値へ
def selkey(vec):
    key_points = []
    KPflag = False
    sigma = 1
    epsilon = 0.1
    t = 0
    for i, row in enumerate(vec[1:-1]):
        #選別方法1
        u = (vec[(i + 1) - 1] + vec[(i + 1)] + vec[(i + 1) + 1]) / 3
        if abs(u - vec[(i + 1)]) > sigma:
            KPflag = True

        #選別方法2
        dv1 = vec[(i + 1) - 1] - vec[(i + 1)]
        dv2 = vec[(i + 1)] - vec[(i + 1) + 1]
        if abs(dv1 - dv2) < epsilon:
            KPflag = True

        if KPflag == True:
            key_points.append(i + 1)

        KPflag = False

    print(key_points)

    #局所ベクトル構築
    f = []
    fi = []
    ffi = []
    for i in key_points:
        fi.append(vec[i])
        if t != 0:
            for j in range(t):
                fi.append(vec[i + j + 1])
                fi.insert(0, vec[i - j - 1])

        if t == 0:
            ffi.append(vec[i])
        else:
            for j in range(t):
                ffi.append(vec[i + (j + 1)] - vec[i + (j + 1) - 1])
                ffi.insert(0, vec[i - (j + 1) + 1] - vec[i - (j + 1)])

        f.append(fi)
        f.append(ffi)

    return f #list(chain.from_iterable(f)) #内包のレベルを一つ下げる

#A-LTK関数（再帰的に計算）
def altk(vec1, vec2):
    #信号両方の大きさが0の場合，無限大
    if len(vec1) == 0 and len(vec2) == 0:
        return float("inf")
    #信号どちらかの大きさが０の場合，0
    if len(vec1) == 0 or len(vec2) == 0:
        return 0
    else:
        #信号の先頭同士でコサイン類似度計算
        #print(vec1[1])
        sim = cos_sim(vec1[0], vec2[0]) + \
              max(altk(vec1, vec2[1:]), \
              altk(vec1[1:], vec2), \
              altk(vec1[1:], vec2[1:]))
        return sim

def calc_sim(fh, fn1, fn2):
    #セグメンテーションしたファイルを食わせる（そのままのファイルを処理させると激重）
    content1 = file_parse(fh, fn1)
    content2 = file_parse(fh, fn2)

    #print(fn1, "and", fn2)

    altk_dis = altk(selkey(content1), selkey(content2))
    #result = dtw_dis / (len(content1) + len(content2))

    return altk_dis #各チャンネルの距離リスト
