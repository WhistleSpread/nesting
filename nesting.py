# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import draw_utls, nfp_utls, input_utls
from settings import BIN_LENGTH, BIN_NORMAL


def content_loop_rate(best, n, loop_time=20):
    """
    固定迭代次数:到了一定的迭代次数就停止
    """
    res = best
    run_time = loop_time
    while run_time:
        n.run()
        best = n.best
        # print best['fitness']
        if best['fitness'] <= res['fitness']:
            res = best
            # print 'change', res['fitness']
        run_time -= 1
    draw_utls.draw_result(res['placements'], n.shapes, n.container, n.container_bounds)


def set_target_loop(best, nest):
    """
    把所有图形全部画出来就退出
    :param best: 一个运行结果
    :param nest: Nester class
    :return:
    """
    res = best
    total_area = 0
    rate = None
    num_placed = 0
    while True:
        nest.run()
        best = nest.best
        if best['fitness'] <= res['fitness']:
            res = best
            for s_data in res['placements']:
                tmp_total_area = 0.0
                tmp_num_placed = 0

                for move_step in s_data:
                    tmp_total_area += nest.shapes[int(move_step['p_id'])]['area']
                    tmp_num_placed += 1

                tmp_rates = tmp_total_area / abs(nfp_utls.polygon_area(nest.container['points']))

                if num_placed < tmp_num_placed or total_area < tmp_total_area or rate < tmp_rates:
                    num_placed = tmp_num_placed
                    total_area = tmp_total_area
                    rate = tmp_rates
        # 全部图形放下才退出
        if num_placed == len(nest.shapes):
            break
    # 画图
    draw_utls.draw_result(res['placements'], nest.shapes, nest.container, nest.container_bounds)


if __name__ == '__main__':
    n = Nester()
    s = input_utls.input_polygon('./data/test3.csv')
    n.add_objects(s)

    if n.shapes_max_length > BIN_LENGTH:
        # 更新后的面料长度比原来的容器，也就是bin的长度长的话，就更新bin的长度
        # 也就是更新相应的坐标
        BIN_NORMAL[2][0] = n.shapes_max_length
        BIN_NORMAL[3][0] = n.shapes_max_length


    # 选择面布
    n.add_container(BIN_NORMAL)
    # 运行计算
    n.run()

    # 设计退出条件
    best = n.best
    print("best = ", best)
    # 放置在一个容器里面
    set_target_loop(best, n)    # T6

    # # 循环特定次数
    # content_loop_rate(best, n, loop_time=2)   # T7 , T4



