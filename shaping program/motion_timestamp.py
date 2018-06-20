#-*- coding:utf-8-*-
import datetime as dt
import time
"""
time.logを手動で編集
1行目をPC時間
2行目をtsnd121のローカル時間
と定義，それぞれ
年/月/日 時:分:秒（小数点第三位，msまで表現）
に変更
"""
def shift_time(fnheader):
    #timestamp read
    tfn = open(fnheader + "time.log", "r")
    content = tfn.read()
    tfn.close()

    segcontent = content.split("\n")

    FMT = '%Y/%m/%d %H:%M:%S.%f'

    timeA = dt.datetime.strptime(segcontent[0], FMT)
    timeB = dt.datetime.strptime(segcontent[1], FMT)
    tdelta = timeA - timeB
    #print(tdelta.days, tdelta.seconds)

    shift_t = int(((tdelta.days * 24 * 60 * 60) + tdelta.seconds + (tdelta.microseconds / 1000000.0) - (9 * 60 * 60)) * 1000) #ms単位に変更，GMTに変更で-9時間

    #tsdnの仕様で，タイムスタンプが計測日の00：00：00からの経過時間となっているため，計測日であるtimeBと,unix時間開始の1970~~の差を計算
    #print(timeB.month, timeB.day)
    timeA2 = dt.datetime.strptime(str(timeB.year) + "/" + str(timeB.month) + "/" + str(timeB.day) + " 00:00:00.000", FMT)
    timeB2 = dt.datetime.strptime("1970/01/01 00:00:00.000", FMT)

    tdelta2 = timeA2 - timeB2

    shift_t2 = int(((tdelta2.days * 24 * 60 * 60) + tdelta2.seconds + (tdelta2.microseconds / 1000000.0)) * 1000)

    shift_t += shift_t2

    return shift_t

if __name__ == "__main__":
    fnheader = "../20180601_pretest/5. paper fan/" #file name header

    shift_t = shift_time(fnheader)

#整形対象ファイル読み込み
    filename = fnheader + "motion"

    rfn = open(filename + ".log", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#書き込み
    wfn = open(filename + "tsum.dat", "w") #write file name

    writecontents = "$interval 1\n$var time msec\n$var ax short\n$var ay short\n$var az short\n$var gx short\n$var gy short\n$var gz short\n\n$data\n" #header
    wfn.write(writecontents)

    for row in segcontent:
        if row is "":
            break

        rowcon = row.split(",") #row content

        #計測日の00：00：00からの経過時間をmsで計算
        x = dt.datetime.fromtimestamp(float("%.3f" % (int(float(rowcon[1]) + shift_t) / 1000.0)))
        #print(x.hour, x.minute, x.second, x.microsecond)
        x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)

        writecontent = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        #writecontent = str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        writecontent += "," + rowcon[2] + "," + rowcon[3] + "," + rowcon[4] +  "," + rowcon[5] +  "," + rowcon[6] + "," + rowcon[7] + "\n"
        wfn.write(writecontent)

    wfn.close()
