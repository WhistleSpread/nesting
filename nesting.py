# -*- coding: utf-8 -*-
from nfp_function import Nester
from tools import output_utls, input_utls
from settings import BIN_NORMAL
import time


def nesting(filepath, result_file_name):

    shapes = input_utls.get_shapes(filepath)

    n = Nester()
    n.set_segments(shapes)
    n.set_container(BIN_NORMAL)

    n.run()

    result = n.best
    output_utls.output_result(result['placements'], n.shapes, n.container, result['fitness'], result_file_name)

        
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
    nesting(filepath5, "L0005")
    # nesting(filepath_test2, "L0002")
    end = time.time()

    print('Running time: %s Seconds' % (end - start))
    print('Running time: %s Minus' % ((end - start) / 60))












