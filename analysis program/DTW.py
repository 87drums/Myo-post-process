# -*- coding:utf-8 -*-
import numpy as np
import math

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

def calc_sim(fh, fn1, fn2):
    #セグメンテーションしたファイルを食わせる（そのままのファイルを処理させると激重）
    content1 = file_parse(fh, fn1)
    content2 = file_parse(fh, fn2)

    #print(fn1, "and", fn2)

    dtw_dis = dtw(content1, content2)
    result = dtw_dis / (len(content1) + len(content2))
    """#複数次元のベクトルを求める場合
    result = []
    for i in range(1, len(content1)):
        dtw_dis = dtw(content1[i], content2[i])
        result.append(dtw_dis / (len(content1[i]) + len(content2[i])))
        #print("start ch" + str(i))
        #print( "ch" + str(i) + "distance = " + str(dtw(content1[i], content2[i])) )
    """
    return result #各チャンネルの距離リスト
