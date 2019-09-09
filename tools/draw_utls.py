# -*- coding: utf-8 -*-

import Polygon
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import csv


def draw_original_polygon(shapes, bin_bounds, bin_shape):

    num_bin = len(shapes)

    fig1 = plt.figure()
    fig1.suptitle('original Polygons', fontweight='bold')

    ax = plt.subplot()
    ax.set_xlim(bin_bounds['x'], bin_bounds['length'])                                           # 设置轴的长度和宽度
    ax.set_ylim(bin_bounds['y'], bin_bounds['width'])

    output_obj = list()
    output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))  
    for segment in shapes:
        output_obj.append(patches.Polygon(segment, fc='yellow'))               # 绘制零件，用黄色表示
    print("len(output_obj) = ", len(output_obj))
    for p in output_obj:                                                                        # 一起输出
        ax.add_patch(p)
        print("p = ", p)


    # fig = plt.gcf()
    # # fig.set_size_inches(18.5, 10.5, forward=True)
    # # fig.savefig("nesting2.png", dpi=1000, bbox_inches='tight')
    # fig.savefig("nesting3.png", dpi=1000, bbox_inches='tight')
    # plt.show()

    plt.rcParams['savefig.dpi'] = 3000 #图片像素
    plt.rcParams['figure.dpi'] = 3000 #分辨率

    my_x_ticks = np.arange(bin_bounds['x'], bin_bounds['length'], 250)
    my_y_ticks = np.arange(bin_bounds['y'], bin_bounds['width'], 250)
    plt.xticks(my_x_ticks)
    plt.yticks(my_y_ticks)

    fig = plt.gcf()
    fig.set_size_inches(220, 3.5, forward=True)
    # fig.savefig("nesting2.png", dpi=1000, bbox_inches='tight')
    fig.savefig("nesting3.png", dpi=100, bbox_inches='tight')
    
    plt.show()

def draw_result_polygons(shapes, bin_bounds, bin_shape):

    fig1 = plt.figure(); fig1.suptitle('original Polygons', fontweight='bold')

    ax = plt.subplot()
    ax.set_xlim(bin_bounds['x'], bin_bounds['length'])
    ax.set_ylim(bin_bounds['y'], bin_bounds['width'])

    output_obj = list()
    output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))  
    for segment in shapes:
        output_obj.append(patches.Polygon(segment, fc='yellow'))               # 绘制零件，用黄色表示
    print("len(output_obj) = ", len(output_obj))
    for p in output_obj:                                                                        # 一起输出
        ax.add_patch(p)
        print("p = ", p)


    # fig = plt.gcf()
    # # fig.set_size_inches(18.5, 10.5, forward=True)
    # # fig.savefig("nesting2.png", dpi=1000, bbox_inches='tight')
    # fig.savefig("nesting3.png", dpi=1000, bbox_inches='tight')
    # plt.show()

    plt.rcParams['savefig.dpi'] = 3000 #图片像素
    plt.rcParams['figure.dpi'] = 3000 #分辨率

    my_x_ticks = np.arange(bin_bounds['x'], bin_bounds['length'], 250)
    my_y_ticks = np.arange(bin_bounds['y'], bin_bounds['width'], 250)
    plt.xticks(my_x_ticks)
    plt.yticks(my_y_ticks)

    fig = plt.gcf()
    fig.set_size_inches(220, 3.5, forward=True)
    fig.savefig("nesting_result.png", dpi=500, bbox_inches='tight')
    plt.show()


def draw_polygon(solution, rates, bin_bounds, bin_shape):

    num_bin = len(solution)
    fig1 = plt.figure()
    fig1.suptitle('Polygon packing', fontweight='bold')

    i_pic = 1                                                                                       # 记录图片的索引
    for shapes in solution:
        # 坐标设置
        # print("shapes = ", shapes)
        # print(type(shapes))
        # print(shapes[0].contour(0))

        ax = plt.subplot(num_bin, 1, i_pic, aspect='equal')
        # ax = fig1.set_subplot(num_bin, 1, i_pic, aspect='equal')
        ax.set_title('Num %d bin, rate is %0.4f' % (i_pic, rates[i_pic-1]))
        i_pic += 1
        
        ax.set_xlim(bin_bounds['x'], bin_bounds['length'])                                           # 设置轴的长度和宽度
        ax.set_ylim(bin_bounds['y'], bin_bounds['width'])

        output_obj = list()
        output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))                        # 绘制板材，用绿色表示

        for s in shapes:
            output_obj.append(patches.Polygon(s.contour(0), fc='yellow'))      # 绘制零件，用黄色表示

        for p in output_obj:                                                                        # 一起输出
            ax.add_patch(p)

    # plt.rcParams['figure.figsize'] = (800.0, 4.0)
    plt.rcParams['savefig.dpi'] = 3000 #图片像素
    plt.rcParams['figure.dpi'] = 3000 #分辨率

    my_x_ticks = np.arange(bin_bounds['x'], bin_bounds['length'], 500)
    my_y_ticks = np.arange(bin_bounds['y'], bin_bounds['width'], 250)
    plt.xticks(my_x_ticks)
    plt.yticks(my_y_ticks)

    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5, forward=True)
    # fig.savefig("nesting2.png", dpi=1000, bbox_inches='tight')
    fig.savefig("nesting3.png", dpi=1000, bbox_inches='tight')
    
    plt.show()


def draw_result(shift_data, shapes, bin_polygon, bin_bounds, min_length):        # 从结果中得到平移旋转的数据，把原始图像移到到目标地方，然后保存结果

    segments_cord_list = list()
    for segment in shapes:
        contour = [[p['x'], p['y']] for p in segment['points']]
        segments_cord_list.append(Polygon.Polygon(contour))

    bin_shape = Polygon.Polygon([[p['x'], p['y']] for p in bin_polygon['points']])      # 板材坐标
    # print("bin_shape = ", bin_shape)

    solution = list()
    rates = list()
    to_csv_list = list()

    def take_first(elem):
        return elem[0]

    for s_data in shift_data:                                # 一个循环代表一个容器的排版, 因为可能分多个容器来排版
        tmp_bin = list()
        total_area = 0.0
        
        for move_step in s_data:

            # print("int(move_step['p_id']) = ", int(move_step['p_id']))

            segments_cord_list[int(move_step['p_id'])].shift(move_step['x'], move_step['y'])

            to_csv_list.append((int(move_step['p_id']), segments_cord_list[int(move_step['p_id'])]))
            # print("to_csv_list = ", to_csv_list)

            tmp_bin.append(segments_cord_list[int(move_step['p_id'])])
            total_area += segments_cord_list[int(move_step['p_id'])].area(0)

        to_csv_list.sort(key=take_first)
        print("to_csv_list = ", to_csv_list)


        # with open("test.csv", "w", encoding='utf-8-sig') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow(["下料批次号","零件号","面料号","零件外轮廓线坐标"])
        #     for item in to_csv_list:
        #         a = list()
        #         for point in item[1].contour(0):
        #             t =list(point)
        #             a.append(t)
        #         if item[0] <= 10:
        #             seg_num = "s00000" + str(item[0]+1)
        #         elif item[0] <= 100:
        #             seg_num = "s0000" + str(item[0]+1)
        #         else:
        #             seg_num = "s000" + str(item[0]+1)
        #         writer.writerow(["L0002", seg_num, 1, a])
        

        with open("test2.csv", "w", encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["下料批次号","零件名","面料号","零件外轮廓线坐标"])
            for item in to_csv_list:
                a = list()
                for point in item[1].contour(0):
                    t = list(point)
                    a.append(t)
                if item[0] <= 10:
                    seg_num = "s00000" + str(item[0]+1)
                elif item[0] <= 100:
                    seg_num = "s0000" + str(item[0]+1)
                else:
                    seg_num = "s000" + str(item[0]+1)
                writer.writerow(["L0003", seg_num, "M0003", a])


        # 当前排版的利用率
        rates.append(total_area / (min_length * bin_bounds['width']))
        print("rates = ", rates)
        solution.append(tmp_bin)

    # print("solution = ", solution)
    

    # 显示结果
    draw_polygon(solution, rates, bin_bounds, bin_shape)