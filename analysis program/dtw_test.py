# -*- coding:utf-8 -*-
import numpy as np

#dtw関数
def dtw(vec1, vec2):
    d = np.zeros([len(vec1)+1, len(vec2)+1])
    d[:] = np.inf
    d[0, 0] = 0
    for i in range(1, d.shape[0]):
        for j in range(1, d.shape[1]):
            cost = abs(vec1[i-1]-vec2[j-1])
            d[i, j] = cost + min(d[i-1, j], d[i, j-1], d[i-1, j-1])
    print(d)
    return d[-1][-1]

def create_con(num, size):
    signal = []
    for i in range(size):
        signal.append(float(num))

    return signal

def create_up(num, size):
    signal = []
    for i in range(size):
        signal.append(float(num + i))

    return signal

def create_down(num, size):
    signal = []
    for i in range(size):
        signal.append(float(size + num - i))

    return signal

if __name__ == "__main__":
    size1 = 4
    size2 = 4

    distance = dtw(create_up(0, size1), create_con(2, size2))
    print(create_up(0, size1), create_con(3, size2), distance)

    pass
