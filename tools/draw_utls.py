# -*- coding: utf-8 -*-

import Polygon
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def draw_polygon(solution, rates, bin_bounds, bin_shape):

    num_bin = len(solution)
    fig1 = plt.figure()
    fig1.suptitle('Polygon packing', fontweight='bold')

    i_pic = 1                                                                                       # 记录图片的索引
    for shapes in solution:
        # 坐标设置
        ax = plt.subplot(num_bin, 1, i_pic, aspect='equal')
        # ax = fig1.set_subplot(num_bin, 1, i_pic, aspect='equal')
        ax.set_title('Num %d bin, rate is %0.4f' % (i_pic, rates[i_pic-1]))
        i_pic += 1
        
        ax.set_xlim(bin_bounds['x'], bin_bounds['length'])                                           # 设置轴的长度和宽度
        ax.set_ylim(bin_bounds['y'], bin_bounds['width'])

        output_obj = list()
        output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))                        # 绘制板材，用绿色表示

        for s in shapes:
            output_obj.append(patches.Polygon(s.contour(0), fc='yellow', lw=1, edgecolor='m'))      # 绘制零件，用黄色表示

        for p in output_obj:                                                                        # 一起输出
            ax.add_patch(p)
    plt.show()


def draw_result(shift_data, polygons, bin_polygon, bin_bounds, min_length):                                     # 从结果中得到平移旋转的数据，把原始图像移到到目标地方，然后保存结果

    shapes = list()
    for polygon in polygons:
        contour = [[p['x'], p['y']] for p in polygon['points']]
        shapes.append(Polygon.Polygon(contour))

    bin_shape = Polygon.Polygon([[p['x'], p['y']] for p in bin_polygon['points']])      # 板材坐标
    print("bin_shape = ", bin_shape)

    solution = list()
    rates = list()
    for s_data in shift_data:                                                           # 一个循环代表一个容器的排版, 因为可能分多个容器来排版

        tmp_bin = list()
        total_area = 0.0
        
        for move_step in s_data:
            shapes[int(move_step['p_id'])].shift(move_step['x'], move_step['y'])
            tmp_bin.append(shapes[int(move_step['p_id'])])
            total_area += shapes[int(move_step['p_id'])].area(0)

        # 当前排版的利用率
        rates.append(total_area / (min_length * bin_bounds['width']))
        print("rates = ", rates)
        solution.append(tmp_bin)
    

    # 显示结果
    draw_polygon(solution, rates, bin_bounds, bin_shape)