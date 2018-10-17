#-*- coding:utf-8-*-
def lr(fnheader):
#ラベル情報読み込み
    lrn = open(fnheader + "label.csv", "r") #label file name
    lcontent = lrn.read()
    lrn.close()

    lsegcontent = lcontent.split("\n")

    seg_inf = []
    for row in lsegcontent[1:]: #csvファイルの１行目は列情報名なのでパス
        if row is "":
            break

        rowcon = row.split(",")

        #試行ごとの区切り情報であるend以外の情報破棄
        #時間をms単位に変更
        if rowcon[2] == "start" or rowcon[2] == "end":
            segt = rowcon[0].split(":")
            rowcon[0] = int((float(segt[0]) * 60 * 60 + float(segt[1]) * 60 + float(segt[2]))* 1000)
            seg_inf.append(rowcon)

    #print(len(seg_inf))

    return seg_inf
