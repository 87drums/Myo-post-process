#-*- coding:utf-8-*-
"""
ログデータで書き出し時に改行されなかった時用のプログラムです～
今となっては無用の産物(笑)

以下は本当は自動でやってもいい部分だけど，ファイルの内容確認も兼ねてあえて手動でやってください．

整形前ファイル，最初のreadmemdata xを手動で消す
整形後のファイル最初に，二重で”ags,”が書き込まれる仕組みなので，手動で消す
"""

if __name__ == "__main__":
#整形対象ファイル読み込み
    filename = "../drum tap/motion"

    rfn = open(filename + ".log", "r") #read file name
    content = rfn.read()
    rfn.close()

    segcontent = content.split("ags,")

#書き込み
    wfn = open(filename + "ln.log", "w") #write file name

    for row in segcontent:
        wfn.write("ags," + row)

    wfn.close()
