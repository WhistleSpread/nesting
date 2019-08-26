# -*- coding: utf-8 -*-

import Polygon
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def draw_polygon(solution, rates, bin_bounds, bin_shape):
    """
    """

    base_width = 150
    base_height = base_width * bin_bounds['width'] / bin_bounds['length']

    num_bin = len(solution)

    fig_height = num_bin * base_height

    fig1 = Figure(figsize=(base_width, fig_height))

    # FigureCanvas(fig1)
    # 果然把这个地方改了就可以画出来了
    fig1 = plt.figure(figsize=(base_width, fig_height))
    # fig1 = plt.figure()
    fig1.suptitle('Polygon packing', fontweight='bold')

    i_pic = 1  # 记录图片的索引
    for shapes in solution:
        # 坐标设置
        ax = plt.subplot(num_bin, 1, i_pic, aspect='equal')
        # ax = fig1.set_subplot(num_bin, 1, i_pic, aspect='equal')
        ax.set_title('Num %d bin, rate is %0.4f' % (i_pic, rates[i_pic-1]))
        i_pic += 1
        
        # 为什么原来他在这里要-10， +50呢？奇怪？？
        # ax.set_xlim(bin_bounds['x'] - 10, bin_bounds['length'] + 50)
        # ax.set_ylim(bin_bounds['y'] - 10, bin_bounds['width'] + 50)
        
        # 设置轴的长度和宽度
        ax.set_xlim(bin_bounds['x'], bin_bounds['length'])
        ax.set_ylim(bin_bounds['y'], bin_bounds['width'])

        print("x_lim = ", (bin_bounds['x'] , bin_bounds['length'] ))
        print("x_lim = ", (bin_bounds['y'] , bin_bounds['width'] )) 

        # 绘制板材，用绿色表示
        output_obj = list()
        output_obj.append(patches.Polygon(bin_shape.contour(0), fc='green'))

        # 
        for s in shapes:
            output_obj.append(patches.Polygon(s.contour(0), fc='yellow', lw=1, edgecolor='m'))

        # 一起输出
        for p in output_obj:
            ax.add_patch(p)

    plt.show()
    # fig1.save()


def draw_result(shift_data, polygons, bin_polygon, bin_bounds):

    """
    从结果中得到平移旋转的数据，把原始图像移到到目标地方，然后保存结果
    :param shift_data: 平移旋转数据
    :param polygons: 原始图形数据
    :param bin_polygon:
    :param bin_bounds:
    :return:
    """

    # 生产多边形类
    shapes = list()
    for polygon in polygons:
        contour = [[p['x'], p['y']] for p in polygon['points']]
        shapes.append(Polygon.Polygon(contour))

    bin_shape = Polygon.Polygon([[p['x'], p['y']] for p in bin_polygon['points']])

    # 这里的shape_area 应该就是总的面积吧
    shape_area = bin_shape.area(0)

    solution = list()
    rates = list()

    for s_data in shift_data:
        # 一个循环代表一个容器的排版
        tmp_bin = list()
        total_area = 0.0
        for move_step in s_data:
            if move_step['rotation'] > 0:
            # if move_step['rotation'] < 0:
                # 坐标原点旋转
                shapes[int(move_step['p_id'])].rotate(math.pi / 180 * move_step['rotation'], 0, 0)
            # 平移
            shapes[int(move_step['p_id'])].shift(move_step['x'], move_step['y'])
            tmp_bin.append(shapes[int(move_step['p_id'])])
            total_area += shapes[int(move_step['p_id'])].area(0)
            print(shapes[int(move_step['p_id'])].boundingBox())
            # print("bounds = ", dir(shapes[int(move_step['p_id'])]))
        # 当前排版的利用率
        rates.append(total_area / shape_area)
        solution.append(tmp_bin)
    
    print("total area = ", total_area)
    print("shape area = ", shape_area)
    print("rates = ", rates)

    # 显示结果
    draw_polygon(solution, rates, bin_bounds, bin_shape)