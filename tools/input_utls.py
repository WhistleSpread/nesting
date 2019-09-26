import pandas as pd
import json


def read_csv(file_path, column_name):
    """

    :param file_path:
    :param column_name:
    :return:
    """
    data = pd.read_csv(file_path)
    result = list()
    record_num = int(data.describe().ix[0, 0])
    for i in range(record_num):
        record = data.ix[i,:]
        a = (json.loads(record[column_name]))
        result.append(a)
    return result


def get_shapes(file_path):
    shapes = read_csv(file_path, "外轮廓")
    return shapes


def get_shapes_from_result(file_path):
    shapes = read_csv(file_path, "零件外轮廓线坐标")
    return shapes


