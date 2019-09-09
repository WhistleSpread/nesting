# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import draw_utls, input_utls
from settings import BIN_LENGTH, BIN_NORMAL
import cProfile
import time
import Polygon


def content_loop_rate(best, n, loop_times=20):
    """
    固定迭代次数:到了一定的迭代次数就停止
    这里设置的是循环迭代20次，个循环都是run()一次
    """
    result = best

    for i in range(loop_times):
        n.run()
        if n.best['fitness'] <= result['fitness']:
            result = n.best
    
    draw_utls.draw_result(result['placements'], n.shapes, n.container, n.container_bounds, result['min_length'])


def set_target_loop(best, nester):
    result = best; num_placed = 0

    while True:
        nester.run()
        if best['fitness'] <= result['fitness']:
            result = nester.best

            for s_data in result['placements']:
                num_placed = len(s_data)
                
        if num_placed == len(nester.shapes):
            break
    
    draw_utls.draw_result(result['placements'], nester.shapes, nester.container, nester.container_bounds, result['min_length'])

        
if __name__ == '__main__':

    start = time.time()

    n = Nester()
    shapes = input_utls.input_polygon('./data/L0002_lingjian.csv')
    # shapes = input_utls.input_polygon('./data/L0003_lingjian.csv')
    # shapes = input_utls.input_polygon('./data/test.csv')
    n.set_segments(shapes)


    # if n.shapes_max_length > BIN_LENGTH:
    #     # 更新后的面料长度比原来的容器，也就是bin的长度长的话，就更新bin的长度,也就是更新相应的坐标
    #     BIN_NORMAL[2][0] = n.shapes_max_length
    #     BIN_NORMAL[3][0] = n.shapes_max_length



    # n.set_container(BIN_NORMAL)

    # bin_bounds = n.container_bounds
    # bin_polygon = n.container
    # bin_shape = Polygon.Polygon([[p['x'], p['y']] for p in bin_polygon['points']])
    
    # # draw_utls.draw_original_polygon(shapes, bin_bounds, bin_shape)
    # result_shapes = input_utls.input_polygon('./data/L0002_lingjian.csv')
    # draw_utls.draw_result_polygons(result_shapes, bin_bounds, bin_shape)


    n.run()

    best = n.best
    # print("best = ", best)


    # 设置退出迭代的条件
    set_target_loop(best, n)                                # 放完所有零件

    # cProfile.run('set_target_loop(best, n)')
    # content_loop_rate(best, n, loop_times=2)              # 循环特定次数

    end = time.time()
    print('Running time: %s Seconds' % (end - start))
    print('Running time: %s Minus' % ((end - start)/60))




