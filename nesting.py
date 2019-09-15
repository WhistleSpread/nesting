# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import output_utls, input_utls
from settings import BIN_LENGTH, BIN_NORMAL
import time


def nesting(filepath, result_file_name):

    shapes = input_utls.input_polygon(filepath)

    n = Nester()
    n.set_segments(shapes)
    n.set_container(BIN_NORMAL)
    n.run()

    result = n.best
    output_utls.output_result(result['placements'], n.shapes, n.container, n.container_bounds,
                          result['min_length'], result_file_name)

        
if __name__ == '__main__':

    filepath1 = "./data/L0002_lingjian.csv"
    filepath2 = "./data/L0003_lingjian.csv"
    filepath3 = "./data/test2.csv"
    filepath4 = "./data/test3.csv"

    start = time.time()
    # nesting(filepath1, "L0002")
    # nesting(filepath2, "L0003")
    nesting(filepath3, "L0002")
    end = time.time()

    print('Running time: %s Seconds' % (end - start))
    print('Running time: %s Minus' % ((end - start) / 60))












