#-*- coding:utf-8-*-
import numpy as np
import datetime as dt
import label_read as lr
import Ndarray_normalization as nn

x_sum_minus = 0 * 60 * 1000 #日をまたいだ時用　ミリ秒単位

"""
emg1に関しては計測時，スタックしたデータを一気に受信しているのか，同じタイムスタンプが重なる現象が
あるので，刻み幅を計算し，最初のタイムスタンプに刻み幅を加算していく形式でタイムスタンプを再設定
blutooth通信の遅延をadjust_timeとしてタイムスタンプへ減算
"""
########################ラベリング前##########################
#筋電位信号
def emg_conversion1(fnheader):
    #日付またいだ時用
    twentyfour_hours = 86400000
    stradding_flag = False

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

        if x_sum <= 4:
            stradding_flag = True

        if stradding_flag == False:
            writecontent = str(x_sum - x_sum_minus) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        elif stradding_flag == True:
            writecontent = str(twentyfour_hours + x_sum - x_sum_minus)

        for col in row.split(",")[1:]:
            writecontent = writecontent + "," + col
        writecontent += "\n"
        wfn.write(writecontent)

    wfn.close()

#加速度，角速度
def ag_conversion1(fnheader, filename):
    #日付またいだ時用
    twentyfour_hours = 86400000
    stradding_flag = False

#整形対象ファイル読み込み
    rfn = open(fnheader + filename + ".csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#書き込み
    wfn = open(fnheader + filename + ".dat", "w") #write file name

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

        if x_sum <= 19:
            stradding_flag = True

        if stradding_flag == False:
            writecontent = str(x_sum - x_sum_minus) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
        elif stradding_flag == True:
            writecontent = str(twentyfour_hours + x_sum - x_sum_minus)

        for col in row.split(",")[1:]:
            writecontent = writecontent + "," + col
        writecontent += "\n"
        wfn.write(writecontent)

    wfn.close()

#ラベリング前処理
def mc1(fnheader):
#整形関数読み出し
    emg_conversion1(fnheader)
    ag_conversion1(fnheader, "accelerometer1")
    ag_conversion1(fnheader, "gyro1")

########################ラベリング後##########################
#筋電位信号
def emg_conversion2(fnheader, adjust_time):
#ラベル情報読み込み
    seg_inf = lr.lr(fnheader)

#整形対象ファイル読み込み
    rfn = open(fnheader + "emg1.csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

    #最初と最後のタイムスタンプ取得→データ数で割って刻み幅計算
    ftimestamp = int(segcontent[1].split(",")[0]) / 1000 #初期時間 first timestamp　msへ変換
    #最後のタイムスタンプで，重なっている部分は除外し計算
    ltimestamp = int(segcontent[len(segcontent) - 2].split(",")[0]) / 1000 #最終時間 last timestamp　msへ変換 最後に空文字入ってるため-2
    for i, row in enumerate(reversed(segcontent[:-1])):
        if (int(row.split(",")[0]) / 1000) != ltimestamp:
            calc_size = i
            break

    time_stride = float("%3.4f" % ((ltimestamp - ftimestamp) / float(len(segcontent) - 3 - calc_size))) #刻み幅，ms単位 ファイルの最初と最後からサンプリングレート計算，刻み幅を厳密に設定→誤差少なくなる？

    print("emg刻み幅(ms)：", time_stride) #刻み幅確認（ms）

#分割書き込み タグがstart-endの組で１分割なので/2
    for i in range(int(len(seg_inf)/2)):
        ####現状仮に，伸筋がch.1,2,8　屈筋がch.3,4,5,6,7としてファイル分け
        #pr_wfn = open(fnheader + "segdata/emg_pr1-" + str(i + 1) + ".dat", "w") #伸筋write file name
        #fl_wfn = open(fnheader + "segdata/emg_fl1-" + str(i + 1) + ".dat", "w") #屈筋write file name
        pr_wfn = open(fnheader + "segdata/" + str(i + 1) + "/emg_pr1.dat", "w") #伸筋write file name
        fl_wfn = open(fnheader + "segdata/" + str(i + 1) + "/emg_fl1.dat", "w") #屈筋write file name

        #ヘッダー書き込み内容
        pr_writecontents = "$interval " + str(time_stride) + "\n$var time msec\n$var emg1 short\n$var emg2 short\n$var emg8 short\n\n$data\n" #header
        pr_wfn.write(pr_writecontents)

        fl_writecontents = "$interval " + str(time_stride) + "\n$var time msec\n$var emg3 short\n$var emg4 short\n$var emg5 short\n$var emg6 short\n$var emg7 short\n\n$data\n" #header
        fl_wfn.write(fl_writecontents)

        start = 0 #セグメントstart行数
        end = 0 #セグメントend行数
        seg = []

        #日付またいだ時用
        twentyfour_hours = 86400000
        stradding_flag = False

        for j, row in enumerate(segcontent):
            if row is "":
                break

            rowcon = row.split(",") #row content
            seg.append(rowcon)

            #計測日の00：00：00からの経過時間をmsで計算
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(ftimestamp + (time_stride * j)) / 1000.0))) #ms単位をs単位へ
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)  + int(adjust_time) - x_sum_minus

            #日付跨いだ時用の処理
            if x_sum <= 0:
                stradding_flag = True
            if stradding_flag == True:
                x_sum += twentyfour_hours

            if seg_inf[i * 2][0] <= x_sum and start == 0:
                start = j
                #print(i + 1, "start", x_sum , seg_inf[i * 2][0], i * 2, start)
            if seg_inf[i * 2 + 1][0] <= x_sum:
                end = j + 1 #配列指定用　endなので+1
                #print(i + 1, "end", x_sum , seg_inf[i * 2 + 1][0], i * 2 + 1, end)
                break

        #タイムスタンプとデータ部で分ける
        #print(fnheader + "segdata/" + str(i + 1), start, seg[start],type(seg[start]))
        try:
            nor_seg_t = np.array(seg[start:end]).T.astype("float64")[0].tolist() #タイムスタンプ
        except ValueError:
            print(fnheader + "segdata/" + str(i + 1), start, seg[start],type(seg[start]))
            exit()
        nor_seg_d = nn.aii(np.array(seg[start:end]).T.astype("float64")[1:]).tolist() #データ部

        #伸筋データ
        pr_nor_seg = []
        pr_nor_seg.append(nor_seg_t)

        #屈筋データ
        fl_nor_seg = []
        fl_nor_seg.append(nor_seg_t)

        #各筋データへ該当チャンネル追加
        for i, row in enumerate(nor_seg_d):
            #k-meansとかでクラス分けしてやるならこのif文の条件式を上手く使う説
            if (i + 1 == 1) or (i + 1 == 2) or (i + 1 == 8):
                pr_nor_seg.append(row)
            else:
                fl_nor_seg.append(row)

        pr_nor_data = np.array(pr_nor_seg).T.tolist() #伸筋全体転置し直し
        fl_nor_data = np.array(fl_nor_seg).T.tolist() #屈筋全体転置し直し

        #伸筋内容書き出し
        for j, row in enumerate(pr_nor_data):
            if row[0] is "":
                break

            #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(ftimestamp + (time_stride * (j + start))) / 1000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)  + int(adjust_time) - x_sum_minus
            #writecontent = str(int(ftimestamp + (time_stride * j))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す

            #タイムスタンプ書き込みデータ追加
            #pr_writecontents = str(x_sum)
            if stradding_flag == False:
                pr_writecontents = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
            elif stradding_flag == True:
                pr_writecontents = str(twentyfour_hours + x_sum)

            for col in row[1:]:
                pr_writecontents = pr_writecontents + "," + str(col)
            pr_writecontents += "\n"
            pr_wfn.write(pr_writecontents)

        pr_wfn.close()

        #屈筋内容書き出し
        for j, row in enumerate(fl_nor_data):
            if row[0] is "":
                break

            #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(ftimestamp + (time_stride * (j + start))) / 1000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)  + int(adjust_time) - x_sum_minus
            #writecontent = str(int(ftimestamp + (time_stride * j))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す

            #タイムスタンプ書き込みデータ追加
            #fl_writecontents = str(x_sum)
            if stradding_flag == False:
                fl_writecontents = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
            elif stradding_flag == True:
                fl_writecontents = str(twentyfour_hours + x_sum)

            for col in row[1:]:
                fl_writecontents = fl_writecontents + "," + str(col)
            fl_writecontents += "\n"
            fl_wfn.write(fl_writecontents)

        fl_wfn.close()

#加速度，角速度
def ag_conversion2(fnheader, filename, adjust_time):
#ラベル情報読み込み
    seg_inf = lr.lr(fnheader)

#整形対象ファイル読み込み
    rfn = open(fnheader + filename + ".csv", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("\n")

#分割書き込み タグがstart-endの組で１分割なので/2
    for i in range(int(len(seg_inf)/2)):
        #wfn = open(fnheader + "segdata/" + filename + "-" + str(i + 1) + ".dat", "w") #write file name
        wfn = open(fnheader + "segdata/" + str(i + 1) + "/" + filename + ".dat", "w") #write file name

        #ヘッダー書き込み内容
        writecontents = "$interval 20\n$var time msec\n$var x short\n$var y short\n$var z short\n\n$data\n" #header
        wfn.write(writecontents)

        start = 0 #セグメントstart行数
        end = 0 #セグメントend行数
        seg = []

        #日付またいだ時用
        twentyfour_hours = 86400000
        stradding_flag = False

        for j,row in enumerate(segcontent[1:]):
            if row is "":
                break

            rowcon = row.split(",") #row content
            seg.append(rowcon)

            #計測日の00：00：00からの経過時間をmsで計算
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(rowcon[0]) / 1000000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)  + int(adjust_time) - x_sum_minus

            #日付跨いだ時用の処理
            if x_sum <= 0:
                stradding_flag = True
            if stradding_flag == True:
                x_sum += twentyfour_hours

            if seg_inf[i * 2][0] <= x_sum and start == 0:
                start = j
                #print(i + 1, "start", seg_inf[i][0], x_sum, start)
            if seg_inf[i * 2 + 1][0] <= x_sum:
                end = j + 1 #配列指定用　endなので+1
                #print(i + 1, "end", seg_inf[i+1][0], x_sum, end)
                break

        nor_seg = []
        nor_seg_t = np.array(seg[start:end]).T[1:].astype("float64")[0].tolist() #タイムスタンプ
        nor_seg_d = nn.aii(np.array(seg[start:end]).T[1:].astype("float64")).tolist() #データ部
        nor_seg.append(nor_seg_t)
        nor_seg.append(nor_seg_d)

        nor_data = np.array(nor_seg).T.tolist() #全体転置し直し

        #内容書き出し
        for row in segcontent[start:end]:
            if row.split(",")[0] is "":
                break

            #計測当日の0：00：00からの経過時間へ変換(ms) fromtimestampの引数は秒単位，μ秒を秒（小数点第三位でmsまで表現）へ変換
            x = dt.datetime.fromtimestamp(float("%.3f" % (int(row.split(",")[0]) / 1000000.0)))
            x_sum = ((x.hour * 60 * 60) + (x.minute * 60) + (x.second)) * 1000 + int(x.microsecond / 1000)  + int(adjust_time) - x_sum_minus
            #writecontent = str(int(ftimestamp + (time_stride * i))) # + (9 * 60 * 60 * 1000)) #初期時間に時間スライド分と9時間分（ms）足す

            #タイムスタンプ書き込みデータ追加
            #writecontent = str(x_sum)
            if stradding_flag == False:
                writecontent = str(x_sum) #str(int(float(rowcon[1]) + shift_t)) #1つ目，ags,を削除
            elif stradding_flag == True:
                writecontent = str(twentyfour_hours + x_sum)

            for col in row.split(",")[1:]:
                writecontent = writecontent + "," + col
            writecontent += "\n"
            wfn.write(writecontent)

        wfn.close()

#ラベリング後処理
def mc2(fnheader, adjust_time):
#整形関数読み出し
    emg_conversion2(fnheader, adjust_time)
    ag_conversion2(fnheader, "accelerometer1", adjust_time)
    ag_conversion2(fnheader, "gyro1", adjust_time)
