# -*- coding:utf-8 -*-
import numpy as np

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
    return_content = np.array(segcontent2).astype(float).T.tolist()

    return return_content

#dtw関数
def dtw(vec1, vec2):
    d = np.zeros([len(vec1)+1, len(vec2)+1])
    d[:] = np.inf
    d[0, 0] = 0
    for i in range(1, d.shape[0]):
        for j in range(1, d.shape[1]):
            cost = abs(vec1[i-1]-vec2[j-1])
            d[i, j] = cost + min(d[i-1, j], d[i, j-1], d[i-1, j-1])
    return d[-1][-1]

if __name__ == "__main__":
    filehead = "../20180601_pretest/"

    #セグメンテーションしたファイルを食わせる（そのままのファイルを処理させると激重）
    content1 = file_parse(filehead, "1. single tap/emg1.dat")
    content2 = file_parse(filehead, "2. double tap/emg1.dat")

    for i in range(len(content1)):
        print("start ch" + str(i + 1))
        print( "ch" + str(i + 1) + "distance = " + str(dtw(content1[i], content2[i])) )
