# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import output_utls, input_utls
from settings import BIN_NORMAL
import time
import pyclipper
from tools.nfp_utls import rotate_polygon


def nesting(filepath, result_file_name):

    shapes = input_utls.get_shapes(filepath)

    n = Nester()
    n.set_segments(shapes)
    n.set_container(BIN_NORMAL)
    n.run()
    result = n.best

    # output_utls.output_result(result['placements'], n.shapes, n.container, result['fitness'], result_file_name)

    ##################################

    angle_list = list()
    for p_id in range(1, 16):
        for combined_shape in result["solution"]:
            if combined_shape[1]["p_id"] == str(p_id):
                angle_list.append(combined_shape[2])
                break

    rotated_shapes = list()
    polygon_list = []
    for shape in n.shapes:
        polygon = []
        for point in shape["points"]:
            point = {"x": point["x"], "y": point["y"]}
            polygon.append(point)
        polygon_list.append(polygon)

    for i in range(0, len(polygon_list)):
        rotated_shapes.append(rotate_polygon(polygon_list[i], angle_list[i]))

    output_utls.output_result(result['placements'], rotated_shapes, n.container, result['fitness'], result_file_name)


if __name__ == '__main__':

    filepath2 = "./data/L0002_lingjian.csv"
    filepath3 = "./data/L0003_lingjian.csv"
    filepath4 = "./data/L0004_lingjian.csv"
    filepath5 = "./data/L0005_lingjian.csv"
    filepath_test1 = "./data/test_4.csv"
    filepath_test2 = "./data/test_13.csv"

    # cProfile.run("nesting(filepath_test2, 'L0002')")

    start = time.time()
    # nesting(filepath2, "L0002")
    # nesting(filepath3, "L0003")
    # nesting(filepath4, "L0004")
    # nesting(filepath5, "L0005")
    nesting(filepath_test2, "L0002")
    end = time.time()

    print('Running time: %s Seconds' % (end - start))
    print('Running time: %s Minus' % ((end - start) / 60))


def polygon_offset(polygon, offset, CURVETOLERANCE):
    """
    :param polygon: [{'x': , 'y': }...{'x': 'y': }]
    :param offset: 5
    :return:
    """
    polygon = [[p['x'], p['y']] for p in polygon]

    miter_limit = 2
    co = pyclipper.PyclipperOffset(miter_limit, CURVETOLERANCE)
    co.AddPath(polygon, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    result = co.Execute(1*offset)

    result = [{'x': p[0], 'y':p[1]} for p in result[0]]
    return result











