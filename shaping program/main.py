# -*- coding:utf-8 -*-
import motion_timestamp as MT
import MYO_conversion as MC

if __name__ == "__main__":
    #整形対象フォルダ指定
    fnheader = "../20180930_some_move/1/other/" #file name header
    start = 1
    end = 1

    print("folder:", fnheader)

    sel = input("1:ラベリング前　2:ラベリング後 >>")

#ラベリング前処理
    if sel == "1":
        while start <= end:
            #整形関数呼び出し
            MT.mt1(fnheader + str(start) + "/")
            MC.mc1(fnheader + str(start) + "/")

            start += 1

#ラベリング後処理
        """
        実行に際しての必要事項
        ・ラベリング前処理を実行済み
        ・sync playにてアノテーションをlabelとして書き出し済み
        ・各動作のズレ時間（adjust time）を検証，テキストにて保存済み
        """
    elif sel == "2":
        #ズレ時間ファイル読み込み
        rfn = open(fnheader + "adjust_time.txt", "r") #read file name
        adjust_times = rfn.read()
        rfn.close()
        adjust_time = adjust_times.split("\n")

        while start <= end:
            #adjust_time = input("MYO adjust time(ms) >>")

            #整形関数呼び出し
            MT.mt2(fnheader + str(start) + "/")
            MC.mc2(fnheader + str(start) + "/", int(adjust_time[start - 1]))

            start += 1
