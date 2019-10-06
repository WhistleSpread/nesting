# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import csv
import time
import os
from settings import BIN_LENGTH, BIN_WIDTH


def makedir():
    date = time.strftime("%Y%m%d", time.localtime())
    print("date = ", date)
    path_a = "./output_files/submit_" + date + "/DatasetA/"
    path_b = "./output_files/submit_" + date + "/DatasetB/"
    if not os.path.exists(path_a):
        os.makedirs(path_a)
        os.makedirs(path_b)
    return path_a


def output_csv(filepath, filename, to_csv_list):

    if filename == "L0002":
        fabric_num = 1
    elif filename == "L0003":
        fabric_num = "M0003"
    elif filename == "L0004":
        fabric_num = "M0004"
    elif filename == "L0005":
        fabric_num = "M0005"
    else:
        print("fabric num error!")
        return

    with open(filepath + filename + ".csv", "w", encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["下料批次号", "零件号", "面料号", "零件外轮廓线坐标"])
        for item in to_csv_list[:-2]:
            a = list()
            for point in item[1]:
                t = list(point)
                a.append(t)
            if item[0] + 1 < 10:
                seg_num = "s00000" + str(item[0] + 1)
            elif item[0] + 1 < 100:
                seg_num = "s0000" + str(item[0] + 1)
            else:
                seg_num = "s000" + str(item[0] + 1)
            writer.writerow([filename, seg_num, fabric_num, a])


def output_png(solution, rates, bin_shape, filename):

    fig1 = plt.figure();
    fig1.suptitle('Polygon packing', fontweight='bold')

    ax = plt.subplot(aspect='equal')
    ax.set_title('rate is %0.4f' % rates)
    ax.set_xlim(0, BIN_LENGTH)  # 设置轴的长度和宽度
    ax.set_ylim(0, BIN_WIDTH)

    output_obj = list()
    output_obj.append(patches.Polygon(bin_shape, fc='green'))  # 绘制板材，用绿色表示

    for s in solution:
        output_obj.append(patches.Polygon(s, fc='yellow'))  # 绘制零件，用黄色表示

    output_obj.append(patches.Circle((800.0, 0.0), 100.0, fc='red'))
    output_obj.append(patches.Circle((2000.0, 400.0), 80.0, fc='red'))

    output_obj.append(patches.Circle((1000.0, 1200.0), 50.0, fc='blue'))
    output_obj.append(patches.Circle((2000.0, 400.0), 80.0, fc='blue'))

    for p in output_obj:
        ax.add_patch(p)

    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.rcParams['figure.dpi'] = 500   # 分辨率

    my_x_ticks = np.arange(0, BIN_LENGTH, 500); plt.xticks(my_x_ticks)
    my_y_ticks = np.arange(0, BIN_WIDTH, 250);  plt.yticks(my_y_ticks)

    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5, forward=True)
    fig.savefig("./output_files/"+filename + ".png", dpi=500, bbox_inches='tight')
    plt.show()


def output_result(shift_data, shapes, bin_polygon, fitness, filename):
    print("shift_data = ", shift_data)
    segments_cord_list = list()
    for segment in shapes:
        segment = [[p['x'], p['y']] for p in segment['points']]
        segments_cord_list.append(segment)

    bin_shape = [(point['x'], point['y']) for point in bin_polygon['points']]
    to_csv_list = list()
    solution = list()

    for move_step in shift_data:
        for point in segments_cord_list[int(move_step['p_id'])]:
            point[0] += move_step['x']
            point[1] += move_step['y']

        to_csv_list.append((int(move_step['p_id']), segments_cord_list[int(move_step['p_id'])]))
        solution.append(segments_cord_list[int(move_step['p_id'])])

    def take_first(elem):
        return elem[0]

    to_csv_list.sort(key=take_first)    # print("to_csv_list = ", to_csv_list)
    filepath = makedir()
    output_csv(filepath, filename, to_csv_list)

    rates = float(fitness)
    print("rates = ", rates)

    output_png(solution, rates, bin_shape, filename)









