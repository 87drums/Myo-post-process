#-*- coding:utf-8-*-
import numpy as np
import datetime as dt
import time
import label_read as lr
import Ndarray_normalization as nn

x_sum_minus = 0 * 60 * 1000 #日をまたいだ時用　ミリ秒単位

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

    #print(tdelta.days, tdelta.seconds, tdelta.microseconds)
    shift_t = int(((tdelta.days * 24 * 60 * 60) + tdelta.seconds + (tdelta.microseconds / 1000000.0) - (9 * 60 * 60)) * 1000) #ms単位に変更，GMTに変更で-9時間

    #tsdnの仕様で，タイムスタンプが計測日の00：00：00からの経過時間となっているため，計測日であるtimeBと,unix時間開始の1970~~の差を計算
    #print(timeB.month, timeB.day)
    timeA2 = dt.datetime.strptime(str(timeB.year) + "/" + str(timeB.month) + "/" + str(timeB.day) + " 00:00:00.000", FMT)
    timeB2 = dt.datetime.strptime("1970/01/01 00:00:00.000", FMT)

    tdelta2 = timeA2 - timeB2

    shift_t2 = int(((tdelta2.days * 24 * 60 * 60) + tdelta2.seconds + (tdelta2.microseconds / 1000000.0)) * 1000)

    shift_t += shift_t2

    return shift_t

###########################ラベリング前処理###########################
def mt1(fnheader):
    #日付またいだ時用
    twentyfour_hours = 86400000
    stradding_flag = False

    shift_t = shift_time(fnheader)

#整形対象ファイル読み込み
    rfn = open(fnheader + "motion.log", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#書き込み
    wfn = open(fnheader + "motiontsum.dat", "w") #write file name

    writecontents = "$interval 1\n$var time msec\n$var ax short\n$var ay short\n$var az short\n$var gx short\n$var gy short\n$var gz short\n\n$data\n" #header
    wfn.write(writecontents)

    for row in segcontent:
        if row is "":
            break

        rowcon = row.split(",") #row content

        #計測日の00：00：00からの経過時間をmsで計算
        x = dt.datetime.fromtimestamp(float("%.3f" % (int(float(rowcon[1]) + shift_t) / 1000.0)))
        x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000) - x_sum_minus

        if x_sum <= 0:
            stradding_flag = True

        if stradding_flag == False:
            writecontent = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        elif stradding_flag == True:
            writecontent = str(twentyfour_hours + x_sum)

        #writecontent = str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        writecontent += "," + rowcon[2] + "," + rowcon[3] + "," + rowcon[4] +  "," + rowcon[5] +  "," + rowcon[6] + "," + rowcon[7] + "\n"
        wfn.write(writecontent)

    wfn.close()

###########################ラベリング後処理###########################
def mt2(fnheader):
    shift_t = shift_time(fnheader)

#ラベル情報読み込み
    end_inf = lr.lr(fnheader)

#整形対象ファイル読み込み
    rfn = open(fnheader + "motion.log", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#分割書き込み
    for i in range(int(len(end_inf)/2)):
        #ac_wfn = open(fnheader + "segdata/tsnd_ac" + str(i + 1) + ".dat", "w") #write file name
        #gy_wfn = open(fnheader + "segdata/tsnd_gy" + str(i + 1) + ".dat", "w") #write file name
        ac_wfn = open(fnheader + "segdata/" + str(i + 1) + "/tsnd_ac.dat", "w") #write file name
        gy_wfn = open(fnheader + "segdata/" + str(i + 1) + "/tsnd_gy.dat", "w") #write file name

        ac_writecontent = "$interval 1\n$var time msec\n$var ax short\n$var ay short\n$var az short\n\n$data\n" #accel header
        ac_wfn.write(ac_writecontent)

        gy_writecontent = "$interval 1\n$var time msec\n$var gx short\n$var gy short\n$var gz short\n\n$data\n" #gyro header
        gy_wfn.write(gy_writecontent)

        start = 0 #セグメントstart行数
        end = 0 #セグメントend行数
        seg = []

        #日付またいだ時用
        twentyfour_hours = 86400000
        stradding_flag = False

        #セグメント行数の取得
        for j, row in enumerate(segcontent):
            if row is "":
                break

            rowcon = row.split(",") #row content
            seg.append(rowcon)

            #計測日の00：00：00からの経過時間をmsで計算
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(float(rowcon[1]) + shift_t) / 1000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000) - x_sum_minus

            #日付跨いだ時用の処理
            if x_sum <= 0:
                stradding_flag = True
            if stradding_flag == True:
                x_sum += twentyfour_hours

            if end_inf[i * 2][0] <= x_sum and start == 0:
                start = j
                #print(i + 1, "start", end_inf[i][0], x_sum, start)
            if end_inf[i * 2 + 1][0] <= x_sum:
                end = j + 1 #配列指定用　endなので+1
                #print(i + 1, "end", end_inf[i+1][0], x_sum, end)
                break

        #タイムスタンプとデータ部で分ける
        #print(end_inf[7], x_sum)
        try:
            nor_seg_t = np.array(seg[start:end]).T[1:].astype("float64")[0].tolist() #タイムスタンプ
        except IndexError:
            print(fnheader + "segdata/" + str(i + 1), start, end, seg[start],type(seg[start]))
            exit()
        #print(np.array(seg[start:end]).T[1:].astype("float64")[1:4], np.array(seg[start:end]).T[1:].astype("float64")[4:7])
        nor_seg_a = nn.aii(np.array(seg[start:end]).T[1:].astype("float64")[1:4]).tolist() #加速度
        nor_seg_g = nn.aii(np.array(seg[start:end]).T[1:].astype("float64")[4:7]).tolist() #角速度

        #加速度データ
        ac_nor_seg = []
        ac_nor_seg.append(nor_seg_t)
        for row in nor_seg_a:
            ac_nor_seg.append(row)

        #角速度データ
        gy_nor_seg = []
        gy_nor_seg.append(nor_seg_t)
        for row in nor_seg_g:
            gy_nor_seg.append(row)

        #print(len(nor_seg_a), len(nor_seg_g))

        #print(nor_seg)

        ac_nor_data = np.array(ac_nor_seg).T.tolist() #ac全体転置し直し
        gy_nor_data = np.array(gy_nor_seg).T.tolist() #gy全体転置し直し
        #print(nor_data)

        #accel 時間書き換え，ファイル書き込み
        for row in ac_nor_data:
            if row is "":
                break

            rowcon = row #row content

            #計測日の00：00：00からの経過時間をmsで計算
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(float(row[0]) + shift_t) / 1000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000) - x_sum_minus

            #タイムスタンプ書き込みデータ追加
            #ac_writecontent = str(x_sum)
            if stradding_flag == False:
                ac_writecontent = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
            elif stradding_flag == True:
                ac_writecontent = str(twentyfour_hours + x_sum)

            #データ部書き込みデータ追加
            for row2 in row[1:]:
                ac_writecontent += "," + str(row2)
            ac_writecontent += "\n"
            #書き込み
            ac_wfn.write(ac_writecontent)

        ac_wfn.close()

        #gyro 時間書き換え，ファイル書き込み
        for row in gy_nor_data:
            if row is "":
                break

            rowcon = row #row content

            #計測日の00：00：00からの経過時間をmsで計算
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(float(row[0]) + shift_t) / 1000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000) - x_sum_minus

            #タイムスタンプ書き込みデータ追加
            #gy_writecontent = str(x_sum)
            if stradding_flag == False:
                gy_writecontent = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
            elif stradding_flag == True:
                gy_writecontent = str(twentyfour_hours + x_sum)

            #データ部書き込みデータ追加
            for row2 in row[1:]:
                gy_writecontent += "," + str(row2)
            gy_writecontent += "\n"
            #書き込み
            gy_wfn.write(gy_writecontent)

        gy_wfn.close()
