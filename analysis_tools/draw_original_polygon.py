import Polygon
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
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


# bin_bounds = n.container_bounds
# bin_polygon = n.container
# bin_shape = Polygon.Polygon([[p['x'], p['y']] for p in bin_polygon['points']])
# # draw_utls.draw_original_polygon(shapes, bin_bounds, bin_shape)
# result_shapes = input_utls.input_polygon('./data/L0002_lingjian.csv')
# draw_utls.draw_result_polygons(result_shapes, bin_bounds, bin_shape)

def draw_result_polygons(shapes, bin_bounds, bin_shape):
    """
    根据生成的csv文件绘制结果
    :param shapes:
    :param bin_bounds:
    :param bin_shape:
    :return:
    """

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

    plt.rcParams['savefig.dpi'] = 500 #图片像素
    plt.rcParams['figure.dpi'] = 500 #分辨率

    my_x_ticks = np.arange(bin_bounds['x'], bin_bounds['length'], 250)
    my_y_ticks = np.arange(bin_bounds['y'], bin_bounds['width'], 250)
    plt.xticks(my_x_ticks)
    plt.yticks(my_y_ticks)

    fig = plt.gcf()
    fig.set_size_inches(220, 3.5, forward=True)
    fig.savefig("nesting_result.png", dpi=500, bbox_inches='tight')
    plt.show()

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

