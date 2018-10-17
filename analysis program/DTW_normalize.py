# -*- coding:utf-8 -*-
import numpy as np
import math

"""
DTW距離の最大値と最小値で正規化
DTW_min/DTW_max
最小値が最大値に近づけば近づくほど0～1の間で値が大きくなる
"""

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

    #L2ノルムを導出　複数次元ベクトルに対して，各次元の二乗和の平方根を取る
    return_content = []
    for i in range(len(segcontent3[0])):
        sum = 0
        for j in range(len(segcontent3[1:])):
            sum += pow(segcontent3[j + 1][i], 2)
        norm = math.sqrt(sum)
        return_content.append(norm)

    #print(return_content[0])
    return return_content

#dtw関数
def dtw(vec1, vec2):
    d = np.zeros([len(vec1)+1, len(vec2)+1]) #-1列-1行分を定義して
    d[:] = np.inf #全ての要素に無限を代入
    d[0, 0] = 0
    for i in range(1, d.shape[0]):
        for j in range(1, d.shape[1]):
            cost = abs(vec1[i-1]-vec2[j-1])
            d[i, j] = cost + min(d[i-1, j], d[i, j-1], d[i-1, j-1])
    return d[-1][-1]

#dtw距離の最大値関数
def dtw_max(vec1, vec2):
    d = np.zeros([len(vec1)+1, len(vec2)+1]) #-1列-1行分を定義して
    d[:] = 0 #全ての要素に0を代入
    for i in range(1, d.shape[0]):
        for j in range(1, d.shape[1]):
            cost = abs(vec1[i-1]-vec2[j-1]) #差の絶対値取得
            d[i, j] = cost + max(d[i-1, j], d[i, j-1], d[i-1, j-1])
    return d[-1][-1] #最大行，最大列がDTW距離の値

def calc_sim(fh, fn1, fn2, fn, calc_times):
    #セグメンテーションしたファイルを食わせる（そのままのファイルを処理させると激重）
    content1 = file_parse(fh, fn1)
    content2 = file_parse(fh, fn2)

    #content1の大きさ分だけサイズを取って，シフトしていって比較するのであれば
    #ここでfor文とって，距離の最小値になったcontent2の時間を抽出？
    #処理を軽くしたかったらその時の最小値より大きくなったら計算止める処理をする？
    dtw_result = [1,0,0] #最小値変数

    shift_ms = 100 #shift ms
    #サンプリングレート50Hz
    if fn == "accelerometer1.dat" or fn == "gyro1.dat":
        shift_l = int(shift_ms / 20) #shift length n * 20 ms
    #サンプリングレート200Hz
    elif fn == "emg_pr1.dat" or fn == "emg_fl1.dat":
        shift_l = int(shift_ms / 5) #shift length n * 5 ms
    #サンプリングレート1kHz
    else:
        shift_l = shift_ms #shift length n * 1 ms

    window_l = len(content1) #window length
    window_s = shift_l * calc_times #window start
    window_e = window_s + window_l #window end
    end_flag = False

    if window_e <= len(content2):
        dtw_dis = dtw(content1, content2[window_s:window_e]) \
                / dtw_max(content1, content2[window_s:window_e])
        dtw_result = [dtw_dis, window_s, window_e]

        window_s += shift_l
        window_e = window_s + window_l
    #content2のデータ長よりもはみ出した時の処理
    else:
        dtw_result = [2, 0, 0] #最大距離以上の値を返す→最小値候補から除外
        end_flag = True

    return [dtw_result, end_flag] #各チャンネルの距離リスト
