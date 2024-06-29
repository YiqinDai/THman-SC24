import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def Schedule_LBF_t():
    global X
    global Y
    global Z
    global p
    global P
    global P_total
    global bl

    if len(Y) == 0:
        Z.clear()
    else:
        ly = len(Y)
        tmp_P = P
        srI = 0
        srO = 0
        # print(rI)
        bf = [-10000 for j in range(0, N + 2)]
        for x in X:
            srI += zrI[x]
            srO += zrO[x]
        bl_tmp = []
        while 1:
            bl_tmp.clear()
            for y in Y:
                bl_tmp.append(bl[y])
            blmax = max(bl_tmp)
            # print(blmax)
            # print(bl_tmp)
            for y in Y:
                if srI + zrI[y] <= R_f:
                    if blmax == 0:
                        bfi = 1
                    else:
                        bfi = bl[y] / blmax
                else:
                    bfi = (bl[y] / blmax) - ((srI + zrI[y]) - max(R_f, srI)) / R_f
                if srO + zrO[y] <= W_f:
                    if blmax == 0:
                        bfo = 1
                    else:
                        bfo = bl[y] / blmax
                # elif (srO <= W_f and srO + rO[y] > W_f):
                #     if srO == 0:
                #         bfo = bl[y] / blmax
                #     else:
                #         bfo = bl[y] / blmax - alpha * ((srO + rO[y]) / W_f - 1)
                # else:
                #     bfo = bl[y] / blmax - alpha * (rO[y] / W_f)
                else:
                    # bfo = (bl[y] / blmax) * (W_f / (srO + rO[y]))
                    bfo = (bl[y] / blmax) - ((srO + zrO[y]) - max(W_f, srO)) / W_f
                bf[y] = min(bfi, bfo)

            Y_tmp = sorted(Y, key=lambda x: bf[Y[Y.index(x)]])
            schedule_flag = 0
            for i in range(ly - 1, -1, -1):
                if tmp_P >= p[Y_tmp[i]]:
                    # if schedule_task == 0 or (srI + rI[Y_tmp[i]] < 2 * R_f and srO + rO[Y_tmp[i]] < 2 * W_f):
                    if schedule_flag == 0:
                        Z.append(Y_tmp[i])
                        Y.remove(Y_tmp[i])
                        ly = len(Y)
                        tmp_P -= p[Y_tmp[i]]
                        schedule_flag = 1
                        srI += zrI[Y_tmp[i]]
                        srO += zrO[Y_tmp[i]]
                        break
            if schedule_flag == 0 or ly == 0:
                break
        Z = list(set(Z))
        Y = list(set(Y).difference(set(Z)))


def Schedule_HCF():
    global X
    global Y
    global Z
    global p
    global P
    global P_total
    global bl
    global bb_r
    global BB
    global I
    global rI
    global rO
    global rIb
    global rOb

    if len(Y) == 0:
        Z.clear()
    else:
        ly = len(Y)
        tmp_P = P
        srI = 0
        srO = 0
        srIb = 0
        srOb = 0
        bf = [-10000 for j in range(0, N + 2)]
        for x in X:
            srI += rI[x]
            srO += rO[x]
            srIb += rIb[x]
            srOb += rOb[x]
        bl_tmp = []
        while 1:
            bl_tmp.clear()
            for y in Y:
                bl_tmp.append(bl[y])
            blmax = max(bl_tmp)
            for y in Y:
                # calculate the rI/rIb and rO
                if y != 0 and y != N + 1 and FI[y] == 0 and BI[y] == 0:
                    for i in range(0, N + 2):
                        if DAG[i][y] == 1:
                            if bb_r[i] == 0 or i == 0:
                                FI[y] += E[i][y]
                            elif bb_r[i] == 1:
                                BI[y] += E[i][y]
                            else:
                                continue
                    if FI[y] + BI[y] != I[y]:
                        # print(y)
                        print(FI[y])
                        print(BI[y])
                        print(I[y])
                        print("111wrong!")
                    rI[y] = FI[y] / w[y]
                    rIb[y] = BI[y] / w[y]
                    rO[y] = O[y] / w[y]

                if blmax == 0:
                    bl_file_input = 1 - ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI)
                    bl_bb_input = 1 - ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb)
                    bl_file_output = 1 - ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO)
                    if BB >= O[y]:
                        bl_bb_output = 1 - ((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb)
                    else:
                        bl_bb_output = bl_file_output
                    b_without = min(bl_file_input, bl_bb_input, bl_file_output, 1)
                    b_with = min(bl_file_input, bl_bb_input, bl_bb_output, 1)
                else:
                    bl_file_input = (bl[y] / blmax) - ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI)
                    bl_bb_input = (bl[y] / blmax) - ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb)
                    bl_file_output = (bl[y] / blmax) - ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO)
                    if BB >= O[y]:
                        bl_bb_output = (bl[y] / blmax) - ((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb)
                    else:
                        bl_bb_output = bl_file_output
                    b_without = min(bl_file_input, bl_bb_input, bl_file_output, (bl[y] / blmax))
                    b_with = min(bl_file_input, bl_bb_input, bl_bb_output, (bl[y] / blmax))

                # if blmax == 0:
                #     bl_file_input = 1 - ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI)
                #     bl_bb_input = 1 - ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb)
                #     bl_file_output = 1 - ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO)
                #     if BB >= O[y]:
                #         bl_bb_output = 1 - ((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb)
                #     else:
                #         bl_bb_output = bl_file_output
                #     b_without = min(bl_file_input, bl_bb_input, bl_file_output, 1)
                #     b_with = min(bl_file_input, bl_bb_input, bl_bb_output, 1)
                # else:
                #     bl_file_input = (bl[y] / blmax) - ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI)
                #     bl_bb_input = (bl[y] / blmax) - ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb)
                #     bl_file_output = (bl[y] / blmax) - ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO)
                #     if BB >= O[y]:
                #         bl_bb_output = (bl[y] / blmax) - ((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb)
                #     else:
                #         bl_bb_output = bl_file_output
                #     b_without = min(bl_file_input, bl_bb_input, bl_file_output, (bl[y] / blmax))
                #     b_with = min(bl_file_input, bl_bb_input, bl_bb_output, (bl[y] / blmax))

                # if blmax == 0:
                #     if ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI) <= 0:
                #         bl_file_input = 1
                #     else:
                #         bl_file_input = 1 / (((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI) + 1)
                #     if ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb) <= 0:
                #         bl_bb_input = 1
                #     else:
                #         bl_bb_input = 1 / (((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb) + 1)
                #     if ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO) <= 0:
                #         bl_file_output = 1
                #     else:
                #         bl_file_output = 1 / (((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO) + 1)
                #     if BB >= O[y]:
                #         if ((srOb + rO[y]) / max(W_b, srOb)) / max(W_b, srOb) <= 0:
                #             bl_bb_output = 1
                #         else:
                #             bl_bb_output = 1 / (((srOb + rO[y]) / max(W_b, srOb)) / max(W_b, srOb) + 1)
                #     else:
                #         bl_bb_output = bl_file_output
                #     b_without = min(bl_file_input, bl_bb_input, bl_file_output, 1)
                #     b_with = min(bl_file_input, bl_bb_input, bl_bb_output, 1)
                # else:
                #     if ((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI) <= 0:
                #         bl_file_input = (bl[y] / blmax)
                #     else:
                #         bl_file_input = (bl[y] / blmax) / (((srI + rI[y]) - max(R_f, srI)) / max(R_f, srI) + 1)
                #     if ((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb) <= 0:
                #         bl_bb_input = (bl[y] / blmax)
                #     else:
                #         bl_bb_input = (bl[y] / blmax) / (((srIb + rIb[y]) - max(R_b, srIb)) / max(R_b, srIb) + 1)
                #     if ((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO) <= 0:
                #         bl_file_output = (bl[y] / blmax)
                #     else:
                #         bl_file_output = (bl[y] / blmax) / (((srO + rO[y]) - max(W_f, srO)) / max(W_f, srO) + 1)
                #     if BB >= O[y]:
                #         if ((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb) <= 0:
                #             bl_bb_output = (bl[y] / blmax)
                #         else:
                #             bl_bb_output = (bl[y] / blmax) / (((srOb + rO[y]) - max(W_b, srOb)) / max(W_b, srOb) + 1)
                #     else:
                #         bl_bb_output = bl_file_output
                #     b_without = min(bl_file_input, bl_bb_input, bl_file_output, (bl[y] / blmax))
                #     b_with = min(bl_file_input, bl_bb_input, bl_bb_output, (bl[y] / blmax))
                if b_with >= 0 and b_without >= 0:
                    if min(1, bb_ratio + 0.65) * b_with > b_without:
                        bf[y] = b_with
                        bb_r[y] = 1
                    else:
                        bf[y] = b_without
                        bb_r[y] = 0
                elif b_with < 0 and b_without < 0:
                    if b_with > b_without * min(1, bb_ratio + 0.65):
                        bf[y] = b_with
                        bb_r[y] = 1
                    else:
                        bf[y] = b_without
                        bb_r[y] = 0
                elif b_with >= 0 and b_without < 0:
                    bf[y] = b_with
                    bb_r[y] = 1
                else:
                    bf[y] = b_without
                    bb_r[y] = 0




            Y_tmp = sorted(Y, key=lambda x: bf[Y[Y.index(x)]])
            schedule_flag = 0
            for i in range(ly - 1, -1, -1):
                if tmp_P >= p[Y_tmp[i]]:
                    if schedule_flag == 0:
                        Z.append(Y_tmp[i])
                        Y.remove(Y_tmp[i])
                        ly = len(Y)
                        tmp_P -= p[Y_tmp[i]]
                        schedule_flag = 1
                        # srI += zrI[Y_tmp[i]]
                        # srO += zrO[Y_tmp[i]]
                        if Y_tmp[i] != 0 and Y_tmp[i] != N + 1:
                            # for j in range(0, N + 2):
                            #     if DAG[j][Y_tmp[i]] == 1:
                            #         if bb_r[j] == 0:
                            #             FI[Y_tmp[i]] += E[j][Y_tmp[i]]
                            #         elif bb_r[j] == 1:
                            #             BI[Y_tmp[i]] += E[j][Y_tmp[i]]
                            #         else:
                            #             continue
                            # rI[Y_tmp[i]] = float(FI[Y_tmp[i]] / w[Y_tmp[i]])
                            # rIb[Y_tmp[i]] = float(BI[Y_tmp[i]] / w[Y_tmp[i]])
                            if bb_r[Y_tmp[i]] == 1:
                                BB -= O[Y_tmp[i]]
                                BO[Y_tmp[i]] = O[Y_tmp[i]]
                                rO[Y_tmp[i]] = 0
                                rOb[Y_tmp[i]] = float(BO[Y_tmp[i]] / w[Y_tmp[i]])
                            else:
                                FO[Y_tmp[i]] = O[Y_tmp[i]]
                                rO[Y_tmp[i]] = float(FO[Y_tmp[i]] / w[Y_tmp[i]])
                                rOb[Y_tmp[i]] = 0
                            srI += rI[Y_tmp[i]]
                            srO += rO[Y_tmp[i]]
                            srIb += rIb[Y_tmp[i]]
                            srOb += rOb[Y_tmp[i]]
                        break
            if schedule_flag == 0 or ly == 0:
                break
        Z = list(set(Z))
        Y = list(set(Y).difference(set(Z)))


def Schedule_Baseline():
    global Y
    global Z
    global p
    global P

    if len(Y) == 0:
        Z.clear()
    else:
        ly = len(Y)
        tmp_P = P
        Y_tmp = Y
        for i in range(0, ly):
            if tmp_P >= p[Y_tmp[i]]:
                Z.append(Y_tmp[i])
                tmp_P -= p[Y_tmp[i]]
    Z = list(set(Z))
    Y = list(set(Y).difference(set(Z)))


def Schedule_LBF():
    global Y
    global Z
    global p
    global P

    if len(Y) == 0:
        Z.clear()
    else:
        ly = len(Y)
        tmp_P = P
        Y_tmp = sorted(Y, key=lambda x: bl[Y[Y.index(x)]])
        for i in range(ly - 1, -1, -1):
            if tmp_P >= p[Y_tmp[i]]:
                Z.append(Y_tmp[i])
                tmp_P -= p[Y_tmp[i]]
    Z = list(set(Z))
    Y = list(set(Y).difference(set(Z)))
    # print(Z)


def Getbl():
    global bl
    for i in range(N + 1, -1, -1):
        bl[i] = Getsinglebl(i)


def Getsinglebl(i):
    global DAG
    global w
    global bl
    if bl[i] != -1:
        return bl[i]
    m = 0
    for j in range(0, N + 2):
        if DAG[i][j] == 1:
            m = max(m, Getsinglebl(j))
    m += w[i]
    return m

def bb_dynamic_baseline(i):
    global W_f
    global BB
    global I
    global O
    global w
    global bb_r
    global DAG
    global X
    global Z
    global N
    sumrO = 0
    if i == N + 1:
        return 0
    else:
        for x in X:
            if bb_r[x] == 0:
                sumrO += rO[x]
        index = Z.index(i)
        for tmp_index in range(index + 1):
            if bb_r[Z[tmp_index]] == 0:
                sumrO += rO[Z[tmp_index]]
        if sumrO + O[i] / w[i] > W_f:
            if BB >= O[i]:
                BB -= O[i]
                bb_r[i] = 1
                return 1
            else:
                bb_r[i] = 0
        else:
            bb_r[i] = 0
            return 0


def bb_dynamic(i):
    global W_f
    global BB
    global I
    global O
    global w
    global bb_r
    global DAG
    global X
    global Z
    global N
    global sumE
    global BB_total
    global CCR
    sumrO = 0
    if i == N + 1:
        return 0
    else:
        for x in X:
            if bb_r[x] == 0:
                sumrO += rO[x]
        index = Z.index(i)
        for tmp_index in range(index + 1):
            if bb_r[Z[tmp_index]] == 0:
                sumrO += rO[Z[tmp_index]]
        # print('dynamic_total', BB_total)
        if CCR <= 1:
            if 1 * (sumrO + O[i] / w[i]) > W_f:
                # if min(1, 0.9) * (sumrO + O[i] / w[i]) > W_f:
                if BB > O[i]:
                    BB -= O[i]
                    bb_r[i] = 1
                    return 1
                else:
                    bb_r[i] = 0
            else:
                bb_r[i] = 0
                return 0
        else:
            if min(1, float(BB_total / sumE + 0.5)) * (sumrO + O[i] / w[i]) > W_f:
                # if min(1, 0.9) * (sumrO + O[i] / w[i]) > W_f:
                if BB >= O[i]:
                    BB -= O[i]
                    bb_r[i] = 1
                    return 1
                else:
                    bb_r[i] = 0
            else:
                bb_r[i] = 0
                return 0


def bb_compare(i):
    global W_f
    global BB
    global I
    global O
    global w
    global bb_r
    global DAG
    global X
    global Z
    global N
    sumrO = 0
    sumrOb = 0
    if i == N + 1:
        return 0
    else:
        # for x in X:
        #     if bb_r[x] == 0:
        #         sumrO += rO[x]
        #     else:
        #         sumrOb += rOb[x]
        # index = Z.index(i)
        # for tmp_index in range(index + 1):
        #     if bb_r[Z[tmp_index]] == 0:
        #         sumrO += rO[Z[tmp_index]]
        #     else:
        #         sumrOb += rOb[Z[tmp_index]]
        rO_tmp = O[i] / w[i]
        FI_tmp = BI_tmp = 0
        for j in range(0, N + 2):
            if DAG[j][i] == 1:
                if bb_r[j] == 0 or j == 0:
                    FI_tmp += E[j][i]
                elif bb_r[i] == 1:
                    BI_tmp += E[j][i]
                else:
                    continue
        # print(FI[i])
        rFI_tmp = FI_tmp / w[i]
        rBI_tmp = BI_tmp / w[i]
        # if sumrO == 0:
        #     wb = min(rO_tmp, W_f)
        # else:
        #     wb = min(rO_tmp, W_f * rO_tmp / sumrO)
        # if sumrOb == 0:
        #     wbb = min(rO_tmp, W_b)
        # else:
        #     wbb = min(rO_tmp, W_b * rO_tmp / sumrOb)
        # wb = min(rO_tmp, W_f)
        # wbb = min(rO_tmp, W_b)
        bb_r[i] = 0
        t1 = w[i]
        if rFI_tmp == 0:
            t2 = 0
        else:
            t2 = FI_tmp / min(rFI_tmp, R_f / (np.mean(p) / P))
        if rBI_tmp == 0:
            t3 = 0
        else:
            t3 = BI_tmp / min(rBI_tmp, R_b / (np.mean(p) / P))
        if rO_tmp == 0:
            t4 = 0
        else:
            t4 = O[i] / min(rO_tmp, W_f / (np.mean(p) / P))
        if rO_tmp == 0:
            t5 = 0
        else:
            t5 = O[i] / min(rO_tmp, W_b / (np.mean(p) / P))
        t_with = max(t1, t2, t3, t5)
        t_without = max(t1, t2, t3, t4)

        # if i == N + 1:
        #     return 0
        # else:
        #     if BB > O[i]:
        #         BB -= O[i]
        #         bb_r[i] = 1
        #         return 1
        #     else:
        #         bb_r[i] = 0
        #         return 0

        if t_with < t_without and BB >= O[i]:
            bb_r[i] = 1
            BB -= O[i]
            return 1
        bb_r[i] = 0
        return 0


def bb_baseline(i):
    global W_f
    global BB
    global I
    global O
    global w
    global bb_r
    global DAG
    global X
    global Z
    global N
    if i == N + 1:
        return 0
    else:
        if BB >= O[i]:
            BB -= O[i]
            bb_r[i] = 1
            return 1
        else:
            bb_r[i] = 0
            return 0


def bb_order(i):
    global BB
    global I
    global O
    global w
    global bb_r
    global N
    global bb_r_flag
    if i == N + 1:
        return 0
    BB_tmp = BB
    Node = [i for i in range(1, N + 1)]
    rIO = [0 for i in range(0, N + 2)]
    rIO[0] = 0
    rIO[N + 1] = 0
    # if bb_r_flag == 0:
    for j in range(1, N + 1):
        rIO[j] += O[j] / w[j]
        rIO[j] += I[j] / w[j]
    Node = sorted(Node, key=lambda x: rIO[x])
    # print(BB_total)
    for j in range(len(Node) - 1, -1, -1):
        if BB_tmp >= O[Node[j]]:
            BB_tmp -= O[Node[j]]
            bb_r[Node[j]] = 1
        else:
            bb_r[Node[j]] = 0
    # bb_r_flag = 1
    # print(rIO)
    # print(Node)
    # print(bb_r)
    return bb_r[i]
    # else:
    #     return bb_r[i]


def nobb(i):
    bb_r[i] = 0
    return 0


def bb_no_operation(i):
    return bb_r[i]


def allbb(i):
    if i == N + 1:
        return 0
    bb_r[i] = 1
    return 1


Results = []
N = 273
X = []
Y = []
Z = []
R_f = 6.2
W_f = 4.1
P = 16
R_b = 50
W_b = 50
N_total = 0
for bb_ratio in [0.1, 0.3, 0.5]:
    Results.clear()
    Y.clear()
    Z.clear()
    P = 16
    P_total = P
    bb_flag = 0
    zrI = [0 for j in range(0, N + 2)]
    zrO = [0 for j in range(0, N + 2)]
    bb_r = [-1 for j in range(0, N + 2)]
    bl = [-1 for j in range(0, N + 2)]
    w = [0 for j in range(0, N + 2)]
    DAG = [[0 for j in range(0, N + 2)] for i in range(0, N + 2)]
    p = [0 for j in range(0, N + 2)]
    bb_r_flag = 0
    BB = BB_total = 0
    for R in range(1, 51, 1):
        # for R in range(100, 101):
        print(R)
        # CCR = R / 10
        # print(CCR)
        time_1 = []
        time_2 = []
        time_3 = []
        time_4 = []
        time_5 = []
        time_6 = []
        time_7 = []
        time_8 = []
        time_9 = []
        time_x = []
        CCR_tmp = []
        for k in range(1, 51):
            # print(i)
            N_total = 0
            DAG = [[0 for j in range(0, N + 2)] for i in range(0, N + 2)]
            E = [[0 for j in range(0, N + 2)] for i in range(0, N + 2)]
            for i in range(1, N + 1):
                for j in range(i + 1, N + 1):
                    # if random.randint(0, int(N / 4) + 3) == 0:
                    if random.randint(0, int(N / 2)) == 0:
                        DAG[i][j] = 1
                    else:
                        DAG[i][j] = 0
            non_pre = [1 for i in range(0, N + 2)]
            non_suc = [1 for i in range(0, N + 2)]
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if DAG[j][i] == 1:
                        non_pre[i] = 0
                    if DAG[i][j] == 1:
                        non_suc[i] = 0
            for i in range(1, N + 1):
                if non_pre[i] == 1:
                    DAG[0][i] = 1
                if non_suc[i] == 1:
                    DAG[i][N + 1] = 1
            for i in range(0, N + 2):
                for j in range(0, N + 2):
                    if DAG[i][j] == 1:
                        # E[i][j] = random.randint(1, R)
                        if (i + j) % 2 != 0:
                            E[i][j] = 1
                        else:
                            E[i][j] = random.randint(int(3 / 4 * R), R)
            sumE = 0
            for i in range(0, N + 2):
                for j in range(0, N + 2):
                    if E[i][j] > 0:
                        sumE += E[i][j]
            BB = bb_ratio * sumE
            # print(BB)
            # if (i + j) % 2 != 0:
            #     E[i][j] = 1
            # else:
            #     E[i][j] = random.randint(R, 2 * R)
            BB_total = BB
            w = [0 for j in range(0, N + 2)]
            w[0] = 0
            w[N + 1] = 0
            for i in range(1, N + 1):
                w[i] = random.randint(10, 20)
            p = [0 for j in range(0, N + 2)]
            p[0] = 0
            p[N + 1] = 0
            pp = [1, 2, 4, 8]
            for i in range(1, N + 1):
                p[i] = pp[random.randint(0, 3)]
                # p[i] = 8
                N_total += p[i]
            # print("N_total = ", N_total)
            I = [0 for j in range(0, N + 2)]
            I[0] = 0
            I[N + 1] = 0
            for i in range(1, N + 1):
                for j in range(0, N + 2):
                    if DAG[j][i] == 1:
                        I[i] += E[j][i]
            # print(I)
            # print(E)
            O = [0 for j in range(0, N + 2)]
            O[0] = 0
            O[N + 1] = 0
            for i in range(1, N + 1):
                for j in range(0, N + 2):
                    if DAG[i][j] == 1:
                        O[i] += E[i][j]
            FI = [0 for j in range(0, N + 2)]
            FO = [0 for j in range(0, N + 2)]
            FI[0] = 0
            FI[N + 1] = 0
            FO[0] = 0
            FO[N + 1] = 0

            BI = [0 for j in range(0, N + 2)]
            BO = [0 for j in range(0, N + 2)]
            BI[0] = 0
            BI[N + 1] = 0
            BO[0] = 0
            BO[N + 1] = 0

            S = 2500000000
            CCR_current = []
            for i in range(1, N + 1):
                CCR_current.append(
                    max(I[i] / ((R_f * w[i]) * (np.mean(p) / P)), O[i] / ((W_f * w[i]) * ((np.mean(p) / P)))))
                CCR_tmp.append(max(I[i] / ((R_f * w[i]) * (np.mean(p) / P)), O[i] / ((W_f * w[i]) * ((np.mean(p) / P)))))
            V = np.var(CCR_current)
            CCR = np.mean(CCR_current)

            C = [0 for j in range(0, N + 2)]
            for i in range(0, (N + 2)):
                C[i] = w[i] * p[i] * S
            bl = [-1 for j in range(0, N + 2)]
            bl[N + 1] = 0
            blm = [-1 for j in range(0, N + 2)]
            blm[N + 1] = 0
            IOl = [-1 for j in range(0, N + 2)]
            IOl[N + 1] = 0
            bb_r_flag = 0
            Getbl()
            # Getblm()
            rI = [0 for j in range(0, N + 2)]
            rO = [0 for j in range(0, N + 2)]
            zrI = [0 for j in range(0, N + 2)]
            zrO = [0 for j in range(0, N + 2)]
            for i in range(0, (N + 2)):
                if w[i] == 0:
                    zrI[i] = zrO[i] = 0
                else:
                    zrI[i] = I[i] / w[i]
                    zrO[i] = O[i] / w[i]
            for H in range(0, 9):
                bb_r = [-1 for j in range(0, N + 2)]
                bb_r[0] = 0
                bb_r[N + 1] = 0
                BB = bb_ratio * sumE
                BB_total = BB
                C_tmp = [[0 for j in range(0, 2 * (N + 2) + 1)] for i in range(0, N + 2)]
                t = [0 for i in range(0, 2 * (N + 2) + 1)]
                s = [-1 for j in range(0, N + 2)]
                e = [-1 for j in range(0, N + 2)]
                X.clear()
                Y.clear()
                Z.clear()
                FI = [0 for j in range(0, N + 2)]
                FO = [0 for j in range(0, N + 2)]
                FI[0] = 0
                FI[N + 1] = 0
                FO[0] = 0
                FO[N + 1] = 0
                BI = [0 for j in range(0, N + 2)]
                BO = [0 for j in range(0, N + 2)]
                BI[0] = 0
                BI[N + 1] = 0
                BO[0] = 0
                BO[N + 1] = 0
                rI = [0 for j in range(0, N + 2)]
                rO = [0 for j in range(0, N + 2)]
                rIb = [0 for j in range(0, N + 2)]
                rOb = [0 for j in range(0, N + 2)]
                for i in range(0, N + 2):
                    if DAG[0][i] == 1:
                        Y.append(i)
                k = 1
                while len(X) != 0 or len(Y) != 0:
                    # print(k)
                    for x in X:
                        if e[x] == k:
                            X.remove(x)
                            P += p[x]
                            for i in range(0, N + 2):
                                if DAG[x][i] == 1:
                                    f = 1
                                    for o in range(0, N + 2):
                                        if DAG[o][i] == 1:
                                            if e[o] > 0 and e[o] <= k:
                                                f = 1
                                            else:
                                                f = 0
                                                break
                                    if f == 1:
                                        Y.append(i)
                    Z.clear()
                    if H == 0:
                        # B + B
                        Schedule_Baseline()
                    elif H == 1:
                        # B + S
                        Schedule_Baseline()
                    elif H == 2:
                        # B + O
                        Schedule_Baseline()
                    elif H == 3:
                        # L + B
                        Schedule_LBF()
                    elif H == 4:
                        # L + S
                        Schedule_LBF()
                    elif H == 5:
                        # L + O
                        Schedule_LBF()
                    elif H == 6:
                        # O + B
                        Schedule_LBF_t()
                    elif H == 7:
                        # O + S
                        Schedule_LBF_t()
                    elif H == 8:
                        # O + O
                        # Schedule_LBF_t()
                        Schedule_HCF()
                        # print(bb_r)
                    else:
                        print(H, 'wrong!')
                        Schedule_LBF_t()
                    for z in Z:
                        bb_flag = 0
                        if H == 0:
                            # B + B
                            bb_flag = bb_baseline(z)
                        elif H == 1:
                            # B + S
                            bb_flag = bb_order(z)
                        elif H == 2:
                            # B + O
                            bb_flag = bb_compare(z)
                        elif H == 3:
                            # L + B
                            bb_flag = bb_baseline(z)
                        elif H == 4:
                            # L + S
                            bb_flag = bb_order(z)
                        elif H == 5:
                            # L + O
                            bb_flag = bb_compare(z)
                        elif H == 6:
                            # O + B
                            bb_flag = bb_baseline(z)
                        elif H == 7:
                            # O + S
                            bb_flag = bb_order(z)
                        elif H == 8:
                            # O + 0
                            bb_flag = bb_no_operation(z)
                        else:
                            print(H, 'wrong!')
                            bb_flag = bb_order(z)

                        if z != 0 and z != N + 1:
                            if H != 8:
                                for i in range(0, N + 2):
                                    if DAG[i][z] == 1:
                                        if bb_r[i] == 0 or i == 0:
                                            FI[z] += E[i][z]
                                        elif bb_r[i] == 1:
                                            BI[z] += E[i][z]
                                        else:
                                            continue
                            if FI[z] + BI[z] != I[z]:
                                print(z)
                                print(FI[z])
                                print(BI[z])
                                print(I[z])
                                print("123wrong!")
                            rI[z] = FI[z] / w[z]
                            rIb[z] = BI[z] / w[z]
                            if bb_flag == 1:
                                BO[z] = O[z]
                                rOb[z] = BO[z] / w[z]
                            else:
                                FO[z] = O[z]
                                rO[z] = FO[z] / w[z]

                    if len(Z) == 1 and Z[0] == N + 1:
                        s[Z[0]] = k
                        e[Z[0]] = k + 1
                        t[k + 1] = t[k]
                        k = k + 1
                    else:
                        for z in Z:
                            s[z] = k
                            X.append(z)
                            P -= p[z]
                        #   modify rI[z] and rO[z]
                        ssumrI = 0
                        ssumrO = 0
                        ssumrIb = 0
                        ssumrOb = 0
                        End_tmp = [0 for j in range(0, N + 2)]
                        R_tmp = [0 for j in range(0, N + 2)]
                        W_tmp = [0 for j in range(0, N + 2)]
                        Rb_tmp = [0 for j in range(0, N + 2)]
                        Wb_tmp = [0 for j in range(0, N + 2)]
                        for x in X:
                            ssumrI += rI[x]
                            ssumrO += rO[x]
                            ssumrIb += rIb[x]
                            ssumrOb += rOb[x]
                        for x in X:
                            t_1 = p[x] * S
                            t_2 = 0
                            t_3 = 0
                            t_4 = 0
                            t_5 = 0
                            if ssumrI <= R_f:
                                R_tmp[x] = rI[x]
                            else:
                                R_tmp[x] = min((rI[x] / ssumrI) * R_f, rI[x])
                            if ssumrO <= W_f:
                                W_tmp[x] = rO[x]
                            else:
                                W_tmp[x] = min((rO[x] / ssumrO) * W_f, rO[x])

                            if ssumrIb <= R_b:
                                Rb_tmp[x] = rIb[x]
                            else:
                                Rb_tmp[x] = min((rIb[x] / ssumrIb) * R_b, rIb[x])
                            if ssumrOb <= W_b:
                                Wb_tmp[x] = rOb[x]
                            else:
                                Wb_tmp[x] = min((rOb[x] / ssumrOb) * W_b, rOb[x])

                            # here!!!!!!!!!!
                            if rI[x] != 0 and FI[x] != 0:
                                t_2 = (C[x] * R_tmp[x]) / FI[x]
                            else:
                                t_2 = 1000000000000000000
                            if rO[x] != 0 and FO[x] != 0:
                                t_3 = (C[x] * W_tmp[x]) / FO[x]
                            else:
                                t_3 = 1000000000000000000
                            if BI[x] != 0:
                                t_4 = (C[x] * Rb_tmp[x]) / BI[x]
                            else:
                                t_4 = 1000000000000000000
                            if BO[x] != 0:
                                t_5 = (C[x] * Wb_tmp[x]) / BO[x]
                            else:
                                t_5 = 1000000000000000000

                            End_tmp[x] = t[k] + (C[x] - (sum(C_tmp[x][i] for i in range(0, 2 * (N + 2) + 1)))) / \
                                         min(t_1, t_2, t_3, t_4, t_5)

                        min_End = 100000000
                        min_index = -1
                        # print(End_tmp)
                        for x in X:
                            if min_End > End_tmp[x]:
                                min_End = End_tmp[x]
                                min_index = x
                        # print(min_index)
                        t[k + 1] = End_tmp[min_index]
                        e[min_index] = k + 1
                        for x in X:
                            t_1 = p[x] * S
                            t_2 = 0
                            t_3 = 0
                            t_4 = 0
                            t_5 = 0
                            if rI[x] != 0 and FI[x] != 0:
                                t_2 = (C[x] * R_tmp[x]) / FI[x]
                            else:
                                t_2 = 1000000000000000000
                            if rO[x] != 0 and FO[x] != 0:
                                t_3 = (C[x] * W_tmp[x]) / FO[x]
                            else:
                                t_3 = 1000000000000000000
                            if BI[x] != 0:
                                t_4 = (C[x] * Rb_tmp[x]) / BI[x]
                            else:
                                t_4 = 1000000000000000000
                            if BO[x] != 0:
                                t_5 = (C[x] * Wb_tmp[x]) / BO[x]
                            else:
                                t_5 = 1000000000000000000
                            C_tmp[x][k] = (t[k + 1] - t[k]) * min(t_1, t_2, t_3, t_4, t_5)
                        k = k + 1
                if H == 0:
                    time_1.append(t[k - 1])
                elif H == 1:
                    time_2.append(t[k - 1])
                elif H == 2:
                    time_3.append(t[k - 1])
                elif H == 3:
                    time_4.append(t[k - 1])
                elif H == 4:
                    time_5.append(t[k - 1])
                elif H == 5:
                    time_6.append(t[k - 1])
                elif H == 6:
                    time_7.append(t[k - 1])
                elif H == 7:
                    time_8.append(t[k - 1])
                elif H == 8:
                    time_9.append(t[k - 1])
                else:
                    time_x.append(t[k - 1])

        print(np.mean(CCR_tmp))
        Results.append(np.mean(CCR_tmp))
        Results.append(np.mean(time_1))
        Results.append(np.mean(time_2))
        Results.append(np.mean(time_3))
        Results.append(np.mean(time_4))
        Results.append(np.mean(time_5))
        Results.append(np.mean(time_6))
        Results.append(np.mean(time_7))
        Results.append(np.mean(time_8))
        Results.append(np.mean(time_9))
        Results.append(np.mean(time_1) / np.mean(time_1))
        Results.append(np.mean(time_2) / np.mean(time_1))
        Results.append(np.mean(time_3) / np.mean(time_1))
        Results.append(np.mean(time_4) / np.mean(time_1))
        Results.append(np.mean(time_5) / np.mean(time_1))
        Results.append(np.mean(time_6) / np.mean(time_1))
        Results.append(np.mean(time_7) / np.mean(time_1))
        Results.append(np.mean(time_8) / np.mean(time_1))
        Results.append(np.mean(time_9) / np.mean(time_1))

    tp = pd.DataFrame(np.array(Results).reshape(50, 19))
    tp.to_excel(r'BB' + str(bb_ratio) +'.xlsx')



plt.rcParams['font.sans-serif'] = ['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
fig = plt.figure(figsize=(70, 16))

ax10 = fig.add_subplot(1, 3, 1)
ax11 = fig.add_subplot(1, 3, 2)
ax12 = fig.add_subplot(1, 3, 3)
ax10.set_ylim(0.9, 1.01)
ax11.set_ylim(0.86, 1.01)
ax12.set_ylim(0.80, 1.01)




C1 = []
C2 = []
C3 = []
C4 = []
C5 = []
C6 = []
C7 = []
C8 = []
C9 = []
C10 = []
# df = pd.read_excel('C:\\Users\\戴屹钦\\Desktop\\学习\\2022学习\\SC22\\5_HPDC\\data\\Results_256_0.1_c.xlsx')
df = pd.read_excel('BB0.1.xlsx')
C1_tmp = df[10].tolist()
C2_tmp = df[11].tolist()
C3_tmp = df[12].tolist()
C4_tmp = df[13].tolist()
C5_tmp = df[14].tolist()
C6_tmp = df[15].tolist()
C7_tmp = df[16].tolist()
C8_tmp = df[17].tolist()
C9_tmp = df[18].tolist()
C10_tmp = df[1].tolist()
# C6_tmp = df[6].tolist()
myccp = df[0].tolist()
x = 0.2
for i in range(0, len(myccp)):
    if myccp[i] >= x and myccp[i] < x + 0.1:
        C1.append(C1_tmp[i])
        C2.append(C2_tmp[i])
        C3.append(C3_tmp[i])
        C4.append(C4_tmp[i])
        C5.append(C5_tmp[i])
        C6.append(C6_tmp[i])
        C7.append(C7_tmp[i])
        C8.append(C8_tmp[i])
        C9.append(C9_tmp[i])
        C10.append(C10_tmp[i])
        x += 0.1
        if x >= 2.5:
            break
print(len(C1))
C1 = gaussian_filter1d(C1, sigma=2)
C2 = gaussian_filter1d(C2, sigma=2)
C3 = gaussian_filter1d(C3, sigma=2)
C4 = gaussian_filter1d(C4, sigma=2)
C5 = gaussian_filter1d(C5, sigma=2)
C6 = gaussian_filter1d(C6, sigma=2)
C7 = gaussian_filter1d(C7, sigma=2)
C8 = gaussian_filter1d(C8, sigma=2)
C9 = gaussian_filter1d(C9, sigma=2)

x = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4]

ax10.plot(x, C1, label="Baseline + Baseline", linestyle='-', linewidth=4, marker='^', markersize=20, color='#6D5C3D')
ax10.plot(x, C2, label="Baseline + SBA", linestyle='-', linewidth=4, marker='o', markersize=15, color='#A64036')
ax10.plot(x, C4, label="HEFT + Baseline", linestyle='-', linewidth=4, marker='s', markersize=15, color='#2E59A7')
ax10.plot(x, C5, label="HEFT + SBA", linestyle='-', linewidth=4, marker='v', markersize=20, color='#DB9C5E')
# ax10.plot(x, C6, label="HEFT + SAS", linestyle='-', linewidth=4, marker='<', markersize=20, color='gold')
# ax9.plot(x, C7, label="O+B", linestyle='-', linewidth=2, marker='s', markersize=7)
# ax9.plot(x, C8, label="O+S", linestyle='-', linewidth=2, marker='v', markersize=10)
ax10.plot(x, C6, label="SAS", linestyle='-', linewidth=4, marker='p', markersize=20, color='mediumpurple')
ax10.plot(x, C9, label="HCF", linestyle='-', linewidth=4, marker='*', markersize=25, color='#3D8E86')
ax10.grid()
# ax10.set_ylabel("Makespan (s)", fontsize=30)
ax10.set_xlabel("CCR (N/P = 16, BR = 0.1)", fontsize=75)
# ax10.legend(fontsize=20)
ax10.tick_params(labelsize=65)
ax10.set_zorder(2)
ax10.patch.set_alpha(0)
ax10.set_ylabel("Normalized \n workflow makespan", fontsize=85)
ax10x = ax10.twinx()
ax10x.set_yticks([])
ax10x.set_zorder(1)
ax10x.set_ylim(0, 2400)
ax10x.bar(x, C10, 0.07, color='#E3D599')
ax10x.tick_params(labelsize=65)

C1 = []
C2 = []
C3 = []
C4 = []
C5 = []
C6 = []
C7 = []
C8 = []
C9 = []
C10 = []
df = pd.read_excel('BB0.3.xlsx')
C1_tmp = df[10].tolist()
C2_tmp = df[11].tolist()
C3_tmp = df[12].tolist()
C4_tmp = df[13].tolist()
C5_tmp = df[14].tolist()
C6_tmp = df[15].tolist()
C7_tmp = df[16].tolist()
C8_tmp = df[17].tolist()
C9_tmp = df[18].tolist()
C10_tmp = df[1].tolist()
# C6_tmp = df[6].tolist()
myccp = df[0].tolist()
x = 0.2
for i in range(0, len(myccp)):
    if myccp[i] >= x and myccp[i] < x + 0.1:
        C1.append(C1_tmp[i])
        C2.append(C2_tmp[i])
        C3.append(C3_tmp[i])
        C4.append(C4_tmp[i])
        C5.append(C5_tmp[i])
        C6.append(C6_tmp[i])
        C7.append(C7_tmp[i])
        C8.append(C8_tmp[i])
        C9.append(C9_tmp[i])
        C10.append(C10_tmp[i])
        x += 0.1
        if x >= 2.5:
            break
print(len(C1))
C1 = gaussian_filter1d(C1, sigma=2)
C2 = gaussian_filter1d(C2, sigma=2)
C3 = gaussian_filter1d(C3, sigma=2)
C4 = gaussian_filter1d(C4, sigma=2)
C5 = gaussian_filter1d(C5, sigma=2)
C6 = gaussian_filter1d(C6, sigma=2)
C7 = gaussian_filter1d(C7, sigma=2)
C8 = gaussian_filter1d(C8, sigma=2)
C9 = gaussian_filter1d(C9, sigma=2)
x = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
C1 = gaussian_filter1d(C1, sigma=2)
C2 = gaussian_filter1d(C2, sigma=2)
C3 = gaussian_filter1d(C3, sigma=2)
C4 = gaussian_filter1d(C4, sigma=2)
C5 = gaussian_filter1d(C5, sigma=2)
C6 = gaussian_filter1d(C6, sigma=2)
C7 = gaussian_filter1d(C7, sigma=2)
C8 = gaussian_filter1d(C8, sigma=2)
C9 = gaussian_filter1d(C9, sigma=2)
ax11.plot(x, C1, label="Baseline + Baseline", linestyle='-', linewidth=4, marker='^', markersize=20, color='#6D5C3D')
ax11.plot(x, C2, label="Baseline + SBA", linestyle='-', linewidth=4, marker='o', markersize=15, color='#A64036')
ax11.plot(x, C4, label="HEFT + Baseline", linestyle='-', linewidth=4, marker='s', markersize=15, color='#2E59A7')
ax11.plot(x, C5, label="HEFT + SBA", linestyle='-', linewidth=4, marker='v', markersize=20, color='#DB9C5E')
# ax11.plot(x, C6, label="HEFT + SAS", linestyle='-', linewidth=4, marker='<', markersize=20, color='gold')
# ax9.plot(x, C7, label="O+B", linestyle='-', linewidth=2, marker='s', markersize=7)
# ax9.plot(x, C8, label="O+S", linestyle='-', linewidth=2, marker='v', markersize=10)
ax11.plot(x, C6, label="SAS", linestyle='-', linewidth=4, marker='p', markersize=20, color='mediumpurple')
ax11.plot(x, C9, label="HCF", linestyle='-', linewidth=4, marker='*', markersize=25, color='#3D8E86')
ax11.grid()
# ax11.set_ylabel("Normalized Makespan", fontsize=55)
ax11.set_xlabel("CCR (N/P = 16, BR = 0.3)", fontsize=75)
# ax11.set_yticks([])
ax11.set_zorder(2)
ax11.patch.set_alpha(0)
ax11x = ax11.twinx()
ax11x.set_zorder(1)
ax11x.set_ylim(0, 2400)
ax11x.set_yticks([])
ax11x.bar(x, C10, 0.07, color='#E3D599')
ax11.legend(fontsize=20)
ax11.tick_params(labelsize=75)

C1 = []
C2 = []
C3 = []
C4 = []
C5 = []
C6 = []
C7 = []
C8 = []
C9 = []
C10 = []
# df = pd.read_excel('C:\\Users\\戴屹钦\\Desktop\\学习\\2022学习\\SC22\\5_HPDC\\data\\Results_256_0.5_c.xlsx')
df = pd.read_excel('BB0.5.xlsx')
C1_tmp = df[10].tolist()
C2_tmp = df[11].tolist()
C3_tmp = df[12].tolist()
C4_tmp = df[13].tolist()
C5_tmp = df[14].tolist()
C6_tmp = df[15].tolist()
C7_tmp = df[16].tolist()
C8_tmp = df[17].tolist()
C9_tmp = df[18].tolist()
C10_tmp = df[1].tolist()
# C6_tmp = df[6].tolist()
myccp = df[0].tolist()
x = 0.2
for i in range(0, len(myccp)):
    if myccp[i] >= x and myccp[i] < x + 0.1:
        C1.append(C1_tmp[i])
        C2.append(C2_tmp[i])
        C3.append(C3_tmp[i])
        C4.append(C4_tmp[i])
        C5.append(C5_tmp[i])
        C6.append(C6_tmp[i])
        C7.append(C7_tmp[i])
        C8.append(C8_tmp[i])
        C9.append(C9_tmp[i])
        C10.append(C10_tmp[i])
        x += 0.1
        if x >= 2.5:
            break
print(len(C1))
C1 = gaussian_filter1d(C1, sigma=2)
C2 = gaussian_filter1d(C2, sigma=2)
C3 = gaussian_filter1d(C3, sigma=2)
C4 = gaussian_filter1d(C4, sigma=2)
C5 = gaussian_filter1d(C5, sigma=2)
C6 = gaussian_filter1d(C6, sigma=2)
C7 = gaussian_filter1d(C7, sigma=2)
C8 = gaussian_filter1d(C8, sigma=2)
C9 = gaussian_filter1d(C9, sigma=2)

x = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4]

ax12.plot(x, C1, label="Baseline + Baseline", linestyle='-', linewidth=4, marker='^', markersize=20, color='#6D5C3D')
ax12.plot(x, C2, label="Baseline + SBA", linestyle='-', linewidth=4, marker='o', markersize=15, color='#A64036')
ax12.plot(x, C4, label="HEFT + Baseline", linestyle='-', linewidth=4, marker='s', markersize=15, color='#2E59A7')
ax12.plot(x, C5, label="HEFT + SBA", linestyle='-', linewidth=4, marker='v', markersize=20, color='#DB9C5E')
# ax12.plot(x, C6, label="HEFT + SAS", linestyle='-', linewidth=4, marker='<', markersize=20, color='gold')
# ax9.plot(x, C7, label="O+B", linestyle='-', linewidth=2, marker='s', markersize=7)
# ax9.plot(x, C8, label="O+S", linestyle='-', linewidth=2, marker='v', markersize=10)
ax12.plot(x, C6, label="SAS", linestyle='-', linewidth=4, marker='p', markersize=20, color='mediumpurple')
ax12.plot(x, C9, label="HCF", linestyle='-', linewidth=4, marker='*', markersize=25, color='#3D8E86')
ax12.grid()
# ax12.set_ylabel("Makespan (s)", fontsize=30)
ax12.set_xlabel("CCR (N/P = 16, BR = 0.5)", fontsize=75)

# ax12.set_yticks([])
ax12.set_zorder(2)
ax12.patch.set_alpha(0)
ax12x = ax12.twinx()
ax12x.set_zorder(1)
ax12x.set_ylim(0, 2400)
ax12x.bar(x, C10, 0.07, color='#E3D599', label='Absolute makespan of Baseline + Baseline')

# ax12x.set_yticklabels([0, 10, 20, 30, 40], fontsize=18)
ax12x.set_ylabel("Absolute \n Makespan (s)", fontsize=75)
ax12x.tick_params(labelsize=65)
ax12.tick_params(labelsize=75)

ax11.legend(fontsize=75, ncol=6, bbox_to_anchor=(0.5, 1.25), loc='upper center')
# ax12x.legend(fontsize=65, ncol=6, bbox_to_anchor=(0.0, 1.23))
fig.subplots_adjust(left=0.08, right=0.93, bottom=0.16, top=0.85, wspace=0.06, hspace=0.45)
# fig.tight_layout()
plt.show()
# fig.savefig('C:\\Users\\戴屹钦\\Desktop\\学习\\2022学习\\SC22\\5_HPDC\\figure\\figure_new_2.eps')
