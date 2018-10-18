#-*- coding:utf-8 -*-
import numpy as np
import DTW_normalize as DTW
import A_LTK
import math
import label_read as lr

#ファイルヘッダー，比較するフォルダ1と2を指定
def all_calc(filehead, fol1, fol2, fn, calc_times):
    fn1 = fol1 + fn
    fn2 = fol2 + fn
    #DTWで類似度
    #return DTW.calc_sim(filehead, fn1, fn2)
    #A-LTKで類似度
    return DTW.calc_sim(filehead, fn1, fn2, fn, calc_times)

#別の動作同士の比較
def different_com(filehead, fol1, fol2, calc_times, min_times, min, end_flag):
    result = [] #[0]:accelerometer [1]:emg [2]:gryo [3]:motion

    fn = "" #file name

    #MYO加速度計算 50Hz
    #print("myo acce")
    fn = "accelerometer1.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #MYO角速度計算 50Hz
    #print("myo gyro")
    fn = "gyro1.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #MYO筋電屈筋計算 200Hz
    #print("myo 屈筋")
    fn = "emg_pr1.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #MYO筋電伸筋計算 200Hz
    #print("myo 伸筋")
    fn = "emg_fl1.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #tsnd加速度計算 1kHz
    #print("tsnd acce")
    fn = "tsnd_ac.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #tsnd角速度計算 1kHz
    #print("tsnd gyro")
    fn = "tsnd_gy.dat"
    result.append(all_calc(filehead, fol1, fol2, fn, calc_times))

    #正規化やらなにやらしたDTW距離の合計値計算
    total_sum = 0

    #ノルムを取った場合
    for i, row in enumerate(result):
        if row[1] == True:
            end_flag = True
        elif i == 0:
            total_sum += row[0][0] #/ 10
        elif i == 1:
            total_sum += row[0][0] #/ 1000
        elif i == 2 or i == 3:
            total_sum += row[0][0] #/ 2.8
        else:
            total_sum += row[0][0]
    result.append(total_sum)
    """
    print("肘加速度:", result[0] )#/ 10)
    print("肘角速度:", result[1] )#/ 1000)
    print("屈筋筋電:", result[2] )#/ 2.8)
    print("伸筋筋電:", result[3] )#/ 2.8)
    print("手首加速度:", result[4])
    print("手首角速度:", result[5])
    print("合計:", total_sum)
    """

    if min > total_sum and end_flag == False:
        min = total_sum
        min_times = calc_times
    calc_times += 1

    return calc_times, min_times, min, end_flag, result

def identical_com(filehead, fol, file_num):
    result_sum = [0] * 7

    #平均計算母数用のカウント変数
    calc_num = 0 #file_num Combination 2の組み合わせの総数　今回は計算ごとに+1する手法

    for i in range(file_num - 1):
        for j in range(file_num)[i + 1:]:
            result_list = [] #[0]:accelerometer [1]:emg [2]:gryo [3]:motion
            fn = "" #file name

            fol1 = fol + str(i + 1) + "/" #accelerometer1-1.dat"
            fol2 = fol + str(j + 1) + "/"

            #MYO加速度計算
            fn = "accelerometer1.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #MYO角速度計算
            fn = "gyro1.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #MYO筋電屈筋計算
            fn = "emg_pr1.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #MYO筋電伸筋計算
            fn = "emg_fl1.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #tsnd加速度計算
            fn = "tsnd_ac.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #tsnd角速度計算
            fn = "tsnd_gy.dat"
            result_list.append(all_calc(filehead, fol1, fol2, fn))

            #print(fol1, "and", fol2)

            #正規化やらなにやらしたDTW距離の合計値計算
            total_sum = 0

            #ノルムを取った場合
            for k, row in enumerate(result_list):
                if k == 0:
                    result_sum[k] += row #/ 10 #重み
                    total_sum += row #/ 10
                elif k == 1:
                    result_sum[k] += row #/ 1000
                    total_sum += row #/ 1000
                elif k == 2 or k == 3:
                    result_sum[k] += row #/ 2.8
                    total_sum += row #/ 2.8
                else:
                    result_sum[k] += row
                    total_sum += row

            result_sum[len(result_sum) - 1] += total_sum
            calc_num += 1
            #print("合計:", total_sum)

    result_ave = [0] * 7 #resultの平均
    for i,row in enumerate(result_sum):
        result_ave[i] = row / calc_num
    print(result_ave)
    return result_ave

if __name__ == "__main__":
#別の動作同士の比較
    filehead = "../20180930_some_move/"
    fol1 = filehead + "1/target/2/segdata/1/" #target motion
    fol2 = filehead + "1/other/2/"

    result_fname = fol1 + " vs " + fol2

    wfn = open(filehead + result_fname + ".txt", "w")

    #ラベル情報読み込み
    end_inf = lr.lr(fol2)

    #分割書き込み
    for i in range(int(len(end_inf)/2)):
        fol = fol2 + "segdata/" + str(i+1) + "/" #compare motions

        print(fol1, "and", fol)
        wfn.write(fol1, "and", fol, "\n")

        calc_times = 0
        min_times = 0
        min = 6 #最大1のパラメータ6つ→最大値6を設定
        end_flag = False

        while end_flag == False:
            calc_times, min_times, min, end_flag, result = different_com(filehead, fol1, fol, calc_times, min_times, min, end_flag)

        calc_times, min_times, min, end_flag, result = different_com(filehead, fol1, fol, min_times, min_times, min, end_flag)
        print(result)
        wfn.write(result, "\n")

    """
    filehead = "../20180930_some_move/1/basis/" #各動作が収納されているフォルダ指定
    fol_num = 7 #比較するフォルダ（動作）の総数
    file_num = 7 #比較するファイルの総数
    result_ave = [0] * 7 #結果の平均変数
    for i in range(fol_num):
        print(i + 1)
        fol = str(i + 1) + "/segdata/" #accelerometer1-1.dat"

        #同じ動作同士の比較
        for j, row in enumerate(identical_com(filehead, fol, file_num)):
            result_ave[j] += row
    #print(result_sum, "/", fol_num, "=", result_sum / fol_num)
    print("肘加速度:", result_ave[0] / fol_num)
    print("肘角速度:", result_ave[1] / fol_num)
    print("屈筋筋電:", result_ave[2] / fol_num)
    print("伸筋筋電:", result_ave[3] / fol_num)
    print("手首加速度:", result_ave[4] / fol_num)
    print("手首角速度:", result_ave[5] / fol_num)
    print("合計:", result_ave[6] / fol_num)
    """
