#-*- coding:utf-8-*-
import numpy as np
import datetime as dt
import label_read as lr
import Ndarray_normalization as nn

#筋電位信号
def emg_conversion1(fnheader):
#整形対象ファイル読み込み
    rfn = open(fnheader + "emg1.csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

    #最初と最後のタイムスタンプ取得→データ数で割って刻み幅計算
    ftimestamp = int(segcontent[1].split(",")[0]) / 1000 #初期時間 first timestamp　msへ変換
    #最後のタイムスタンプで，重なっている部分は除外し計算
    ltimestamp = int(segcontent[len(segcontent) - 2].split(",")[0]) / 1000 #最終時間 last timestamp　msへ変換 最後に空文字入ってるため-2
    for j, row in enumerate(reversed(segcontent[:-1])):
        if (int(row.split(",")[0]) / 1000) != ltimestamp:
            calc_size = j
            break

    time_stride = float("%3.4f" % ((ltimestamp - ftimestamp) / float(len(segcontent) - 3 - calc_size))) #刻み幅，ms単位 ファイルの最初と最後からサンプリングレート計算，刻み幅を厳密に設定→誤差少なくなる？

    print("emg刻み幅(ms)：", time_stride) #刻み幅確認（ms）

    wfn = open(fnheader + "emg1.dat", "w") #write file name

    #ヘッダー書き込み内容
    writecontents = "$interval " + str(time_stride) + "\n$var time msec\n$var emg1 short\n$var emg2 short\n$var emg3 short\n$var emg4 short\n$var emg5 short\n$var emg6 short\n$var emg7 short\n$var emg8 short\n\n$data\n" #header
    wfn.write(writecontents)

    #内容書き出し
    for i, row in enumerate(segcontent[1:]):
        if row.split(",")[0] is "":
            break

        #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
        x = dt.datetime.fromtimestamp(float("%.3f" % (int(ftimestamp + (time_stride * i)) / 1000.0)))

        x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)
        #writecontent = str(int(ftimestamp + (time_stride * j))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す
        writecontent = str(x_sum)
        for col in row.split(",")[1:]:
            writecontent = writecontent + "," + col
        writecontent += "\n"
        wfn.write(writecontent)

    wfn.close()

if __name__ == "__main__":
    fnheader = "../20180806_test/1/"

    emg_conversion1(fnheader)
