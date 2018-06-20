#-*- coding:utf-8-*-
import datetime as dt

"""
emg1に関しては計測時，スタックしたデータを一気に受信しているのか，同じタイムスタンプが重なる現象が
あるので，刻み幅を計算し，最初のタイムスタンプに刻み幅を加算していく形式でタイムスタンプを再設定
"""

#筋電位信号
def emg_conversion(filename):
    #整形対象ファイル読み込み
    rfn = open(filename + "emg1.csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#書き込み
    wfn = open(filename + "emg1.dat", "w") #write file name

    #ヘッダー書き込み内容
    writecontents = "$interval 5\n$var time msec\n$var emg1 short\n$var emg2 short\n$var emg3 short\n$var emg4 short\n$var emg5 short\n$var emg6 short\n$var emg7 short\n$var emg8 short\n\n$data\n" #header
    wfn.write(writecontents)

    #最初と最後のタイムスタンプ取得→データ数で割って刻み幅計算
    ftimestamp = int(segcontent[1].split(",")[0]) / 1000 #初期時間 first timestamp　msへ変換
    #最後のタイムスタンプで，重なっている部分は除外し計算
    ltimestamp = int(segcontent[len(segcontent) - 2].split(",")[0]) / 1000 #最終時間 last timestamp　msへ変換 最後に空文字入ってるため-2
    for i, row in enumerate(reversed(segcontent[:-1])):
        if (int(row.split(",")[0]) / 1000) != ltimestamp:
            calc_size = i
            break

    time_stride = float("%3.4f" % ((ltimestamp - ftimestamp) / float(len(segcontent) - 3 - calc_size))) #刻み幅，ms単位 ファイルの最初と最後からサンプリングレート計算，刻み幅を厳密に設定→誤差少なくなる？

    print(time_stride)#刻み幅確認（ms）

    #内容書き出し
    for i, row in enumerate(segcontent[1:]):
        if row.split(",")[0] is "":
            break

        #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
        x = dt.datetime.fromtimestamp(float("%.3f" % (int(ftimestamp + (time_stride * i)) / 1000.0)))

        x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)
        #writecontent = str(int(ftimestamp + (time_stride * i))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す
        writecontent = str(x_sum)
        for col in row.split(",")[1:]:
            writecontent = writecontent + "," + col
        writecontent += "\n"
        wfn.write(writecontent)

    wfn.close()

#加速度，角速度
def ag_conversion(filehead, filename):
#整形対象ファイル読み込み
    rfn = open(filehead + filename + ".csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#書き込み
    wfn = open(filehead + filename + ".dat", "w") #write file name

    #ヘッダー書き込み内容
    writecontents = "$interval 20\n$var time msec\n$var x short\n$var y short\n$var z short\n\n$data\n" #header
    wfn.write(writecontents)

    #内容書き出し
    for i, row in enumerate(segcontent[1:]):
        if row.split(",")[0] is "":
            break

        #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
        x = dt.datetime.fromtimestamp(float("%.3f" % (int(row.split(",")[0]) / 1000000.0)))

        x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)
        #writecontent = str(int(ftimestamp + (time_stride * i))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す
        writecontent = str(x_sum)
        for col in row.split(",")[1:]:
            writecontent = writecontent + "," + col
        writecontent += "\n"
        wfn.write(writecontent)

    wfn.close()

if __name__ == "__main__":
#整形対象フォルダ指定
    filename = "../20180601_pretest/5. paper fan/"

#整形関数読み出し
    emg_conversion(filename)
    ag_conversion(filename, "accelerometer1")
    ag_conversion(filename, "gyro1")
