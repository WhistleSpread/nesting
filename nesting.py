# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import draw_utls, nfp_utls, input_utls
from settings import BIN_LENGTH, BIN_NORMAL
import cProfile


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
    """
    把所有图形全部画出来就退出
    """
    result = best; 
    num_placed = 0

    while True:
        nester.run()
        if best['fitness'] <= result['fitness']:
            result = nester.best

            for s_data in result['placements']:
                tmp_num_placed = 0
                for move_step in s_data:
                    tmp_num_placed += 1
                num_placed = tmp_num_placed
                
        if num_placed == len(nester.shapes):
            break
    
    draw_utls.draw_result(result['placements'], nester.shapes, nester.container, nester.container_bounds, result['min_length'])

        
if __name__ == '__main__':
    n = Nester()
    s = input_utls.input_polygon('./data/test.csv')
    n.set_segments(s)

    if n.shapes_max_length > BIN_LENGTH:
        # 更新后的面料长度比原来的容器，也就是bin的长度长的话，就更新bin的长度,也就是更新相应的坐标
        BIN_NORMAL[2][0] = n.shapes_max_length
        BIN_NORMAL[3][0] = n.shapes_max_length


    n.set_container(BIN_NORMAL)
    n.run()
    best = n.best
    print("best = ", best)

    # 设置退出迭代的条件
    set_target_loop(best, n)                                # 放完所有零件
    cProfile.run('set_target_loop(best, n)')
    # content_loop_rate(best, n, loop_times=2)              # 循环特定次数



