import pandas as pd
import json


def find_shape_from_file(file_name):

    data = pd.read_csv(file_name)
    all_shapes = list()

    record_num = int(data.describe().ix[0,0])
    for i in range(record_num):
        record = data.ix[i,:]
        a = (json.loads(record['外轮廓']))
        all_shapes.append(a)
    return all_shapes


def find_shape_from_result_file(file_name):

    data = pd.read_csv(file_name)
    all_shapes = list()

    record_num = int(data.describe().ix[0,0])
    for i in range(record_num):
        record = data.ix[i,:]
        a = (json.loads(record['零件外轮廓线坐标']))
        all_shapes.append(a)

    return all_shapes


def input_polygon(file_path):
    
    all_shapes_list = find_shape_from_file(file_path)
    shapes = list()
    for i in range(0, len(all_shapes_list)):
        shapes.append(list(all_shapes_list[i]))

    return shapes

