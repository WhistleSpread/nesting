import pandas as pd
import json

def find_shape_from_file(file_name):

    data = pd.read_csv(file_name)
    # print("data = ", data)
    all_shapes = list()

    record_num = int(data.describe().ix[0,0])
    for i in range(record_num):
        record = data.ix[i,:]
        # print(record['外轮廓'])
        a = (json.loads(record['外轮廓']))
        all_shapes.append(a)
        # print("all_shapes = ", all_shapes)
        # print(type(record))
        # all_shapes.append(int(record['外轮廓']))
    return all_shapes

def input_polygon(file_path):
    datas = find_shape_from_file(file_path)
    shapes = list()
    for i in range(0, len(datas)):
        shapes.append(list(datas[i]))

    return shapes

