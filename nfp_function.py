# -*- coding: utf-8 -*-

import json
import copy
from genetic_algorithm import genetic_algorithm
from tools import placement_worker, nfp_utls
import pyclipper

from settings import SPACING, ROTATIONS, BIN_WIDTH, POPULATION_SIZE, MUTA_RATE


class Nester:
    def __init__(self, container=None, shapes=None):

        self.container = container
        self.shapes = shapes
        self.total_segments_area = 0
        self.results = list()                           # storage for the different results
        self.nfp_cache = {}
        self.config = {
            'curveTolerance': 0.3,                      # 允许的最大误差转换贝济耶和圆弧线段。在SVG的单位。更小的公差将需要更长的时间来计算
            'spacing': SPACING,                         # 组件间的间隔
            'rotations': ROTATIONS,                     # 旋转的颗粒度，360°的n份，如：4 = [0, 90 ,180, 270]
            'populationSize': POPULATION_SIZE,          # 基因群数量
            'mutationRate': MUTA_RATE,                  # 变异概率
            'useHoles': False,                          # 是否有洞，暂时都是没有洞
            'exploreConcave': False                     # 寻找凹面，暂时是否
        }

        self.GA = None       
        self.best = None  
        self.worker = None                              # 根据NFP结果，计算每个图形的移动数据
        self.container_bounds = None                    # 容器的最小包络矩形作为输出图的坐标

    def set_segments(self, segments_lists):
        """
        :param segments_lists: [[point of segment 1], [], ..., [point of segment 314]]
        :return:
        self.shapes: a list of dictionary, with each dictionary contain information of each segment
        self.shapes: [{area: , p_id: , points:[{'x': , 'y': }...]},... {area: , p_id: , points:[{'x': , 'y': }...]}]
        self.total_segments_area : total area of all segments
        """

        self.shapes = []
        p_id = 1; total_area = 0

        for segment_cord in segments_lists:
            shape = {'area': 0, 'p_id': str(p_id), 'points': [{'x': p[0], 'y': p[1]} for p in segment_cord]}
            p_id = p_id + 1
            seg_area = nfp_utls.polygon_area(shape['points'])
            if seg_area > 0:                                        # 因为设置的是顺时针，所以用公式计算的面积应该小于0
                shape['points'].reverse()                           # 确定多边形的线段方向, 多边形方向为逆时针时，S < 0 ;多边形方向为顺时针时，S > 0
            shape['area'] = abs(seg_area)
            total_area += shape['area']
            self.shapes.append(shape)

        self.total_segments_area = total_area

    def set_container(self, container):
        """
        :param container: BIN_NORMAL = [[0, 0], [0, BIN_WIDTH], [BIN_LENGTH, BIN_WIDTH], [BIN_LENGTH, 0]]
        :return:
        self.container:
        {
            'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
            'p_id':-1,
            'length': ,
            'width':
        }

        self.container_bounds =
        {   'x': xmin,
            'y': ymin,
            'length': xmax - xmin,
            'width': ymax - ymin
        }
        bottom-left point ('x', 'y')  length and width of this rectangle container
        """

        if not self.container:
            self.container = {}

        self.container['points'] = [{'x': p[0], 'y':p[1]} for p in container]
        self.container['p_id'] = '-1'
        a = nfp_utls.get_polygon_bounds(self.container['points'])
        self.container['length'] = a['length']
        self.container['width'] = a['width']
        self.container_bounds = a

    def run(self):
        """
        1. preprocess points of each segment, use function polygon_offset to update segment['points']
        2. reorder segment_list in  in descending order of area
        3. arrange new data structure, [[order, segment],..., [order, segment]]
        :return:
        segments_sorted_list :
        [
        [1, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        [2, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        ...
        [314, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        ]

        call self.launch_workers(segments_sorted_list)
        """
        if not self.container:
            print("Empty container. Aborting")
            return
        if not self.shapes:
            print("Empty shapes. Aborting")
            return

        segments_sorted_list = list()
        for i in range(0, len(self.shapes)):                # 这里修改一下，从1开始比较好
            segment = copy.deepcopy(self.shapes[i])
            segment['points'] = self.polygon_offset(segment['points'], self.config['spacing'])
            segments_sorted_list.append([str(i), segment])

        segments_sorted_list = sorted(segments_sorted_list, reverse=True, key=lambda o_segment: o_segment[1]['area'])

        return self.launch_workers(segments_sorted_list)

    def launch_workers(self, segments_sorted_list):
        """
        call genetic method
        :param segments_sorted_list:
        sorted in the order of area
        [
        [1, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        [2, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        ...
        [314, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
        ]

        :param bin_info_dic = self.container :
        {
            'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
            'p_id':-1,
            'length': ,
            'width':
        }

        :return:
        self.GA :

        """
        if self.GA is None:
            bin_info_dic = copy.deepcopy(self.container)
            self.GA = genetic_algorithm.genetic_algorithm(segments_sorted_list, bin_info_dic)
        else:
            self.GA.generation()
        
        for i in range(0, self.GA.populationSize):
            result_info_dic = self.find_fitness(self.GA.population[i])
            self.GA.population[i]['fitness'] = result_info_dic['fitness']
            self.results.append(result_info_dic)

        if len(self.results) > 0:
            best_result = self.results[0]

            for p in self.results:
                if p['fitness'] < best_result['fitness']:
                    best_result = p

            if self.best is None or best_result['fitness'] < self.best['fitness']:
                self.best = best_result

    def find_fitness(self, individual):
        """
        get fitness of an individual, a solution, a place order
        :param individual: a solution
        self.individual =
            {
                'placement_order':
                [
                    [2, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
                    [5, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
                    ...
                    [245, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
                ]
                'rotation': [0, 0, ..., 0]
            }
        place_order_list =
            [
                [2, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
                [5, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
                ...
                [245, {area: , p_id: , points:[{'x': , 'y': }...{'x': 'y': }]}],
            ]

        combined_order_angle_list =
            [
                [2, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
                [5, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
                ...
                [245, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
            ]

        key = {
                'A': '-1',                                                         # -1 stand for the container
                'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
            }

        key = {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }

        nfp_pairs =
        [
            {
            'A': {
                    'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
                    'p_id':-1,
                    'length': ,
                    'width':
                }

            'B': {area: , p_id: , points:[{'x': , 'y': }...]}

            'key': {
                'A': '-1',                                                         # -1 stand for the container
                'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？,其实不用这么算的
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
                }

            },

            ......

        ]

        nfp_pairs =
        [
        {
            'A': {area: , p_id: , points:[{'x': , 'y': }...]},

            'B': {area: , p_id: , points:[{'x': , 'y': }...]},

            'key': {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }
        }
        ......
        ]



        :return
        result_info_dic =
        {
            'placements': all_placements,
            'fitness': fitness,
            'paths': paths,
            'area': bin_area,
            'min_length':min_length
        }

        """

        place_order_list = copy.deepcopy(individual['placement_order'])
        rotation_list = copy.deepcopy(individual['rotation'])

        ids = [p[0] for p in place_order_list]                          # order of segments

        for i in range(0, len(place_order_list)):
            place_order_list[i].append(rotation_list[i])
        
        combined_order_angle_list = copy.deepcopy(place_order_list)

        nfp_pairs = list(); new_cache = dict()
        for i in range(0, len(combined_order_angle_list)):              # get IFR inner fit Rectangle
            segment_i = combined_order_angle_list[i]
            key = {
                'A': '-1',                                              # -1 stand for the container
                'B': segment_i[0],                                      # segment_i[0] is the index of segment_i, 这个是每个一individual中的顺序啊？这个不太行
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
            }

            tmp_json_key = json.dumps(key)

            if not (tmp_json_key in self.nfp_cache.keys()):
                nfp_pairs.append({
                    'A': self.container,
                    'B': segment_i[1],                                  # segment_i[1] is coords of segment_i
                    'key': key
                })
            else:
                new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]  # update new_cache

            for j in range(0, i):                                       # get nfp of seg_i and seg_j
                placed_segment_j = combined_order_angle_list[j]

                key = {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }
                tmp_json_key = json.dumps(key)

                if not (tmp_json_key in self.nfp_cache.keys()):
                    nfp_pairs.append({
                        'A': placed_segment_j[1],
                        'B': segment_i[1],
                        'key': key
                    })
                else:
                    new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]

        self.nfp_cache = new_cache                                      # 每一轮,也就是对每一个解过后，更新一次nfp_cache
        self.worker = placement_worker.PlacementWorker(self.container,
                                                       combined_order_angle_list,
                                                       ids, rotation_list,
                                                       self.config, self.nfp_cache)

        pair_list = list()
        for pair in nfp_pairs:
            pair_list.append(self.process_nfp(pair))                    # 这个地方计算nfp_pair花了好久啊？;nfp_pair 有49455，这个也太多了吧? 时间最多了
        return self.generate_nfp(pair_list)

    def process_nfp(self, pair):
        """
        compute to get no fit polygon of two segment

        :param pair:
        {
            'A': {
                    'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
                    'p_id':-1,
                    'length': ,
                    'width':
                }

            'B': {area: , p_id: , points:[{'x': , 'y': }...]}

            'key': {
                'A': '-1',                                                         # -1 stand for the container
                'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？,其实不用这么算的
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
                }
        },

        :param pair :

        {
            'A': {area: , p_id: , points:[{'x': , 'y': }...]},

            'B': {area: , p_id: , points:[{'x': , 'y': }...]},

            'key': {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }
        }

        :return:
        nfp_rectangle
        nfp :
        [[{'x': , 'y': },{'x': , 'y': },{'x': , 'y': },{'x': , 'y': }]]
        nfp_polygon
        nfp :
        [[{'x': 'y': }...{'x':, 'y':}]]

        :return:
        {
            'key': {
                'A': '-1',                                                         # -1 stand for the container
                'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？,其实不用这么算的
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
                }

            'value': [[{'x': , 'y': },{'x': , 'y': },{'x': , 'y': },{'x': , 'y': }]]
        }

        {
            'key': {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }

            'value': [[{'x': 'y': }...{'x':, 'y':}]]
        }

        """

        # 考虑有没有洞和凹面
        search_edges = self.config['exploreConcave']
        use_holes = self.config['useHoles']

        A = copy.deepcopy(pair['A'])
        A['points'] = nfp_utls.rotate_polygon(A['points'], pair['key']['A_rotation'])['points']             # 旋转后的A
        B = copy.deepcopy(pair['B'])
        B['points'] = nfp_utls.rotate_polygon(B['points'], pair['key']['B_rotation'])['points']             # 旋转后的B

        if pair['key']['inside']:
            # inner fit rectangle
            if nfp_utls.is_rectangle(A['points'], 0.0001):
                nfp = nfp_utls.nfp_rectangle(A['points'], B['points'])
            else:
                nfp = nfp_utls.nfp_polygon(A, B, True, search_edges)

            # ensure all interior NFPs have the same winding direction
            if nfp and len(nfp) > 0:
                for i in range(0, len(nfp)):
                    if nfp_utls.polygon_area(nfp[i]) > 0:
                        nfp[i].reverse()
            else:
                pass
                print('NFP Warning:', pair['key'])

        else:
            # no fit polygon
            if search_edges:
                # 处理凹面
                nfp = nfp_utls.nfp_polygon(A, B, False, search_edges)
            else:
                # 使用Minkowski_difference和求两个零件的nfp
                nfp = minkowski_difference(A, B)

            # 检查NFP多边形是否合理
            if nfp is None or len(nfp) == 0:
                pass
                # print('error in NFP 260')
                # print('NFP Error:', pair['key'])
                # print('A;', A)
                # print('B:', B)
                return None

            for i in range(0, len(nfp)):
                # if search edges is active, only the first NFP is guaranteed to pass sanity check
                if not search_edges or i == 0:
                    if abs(nfp_utls.polygon_area(nfp[i])) < abs(nfp_utls.polygon_area(A['points'])):
                        pass
                        # print('error in NFP area 269')
                        # print('NFP Area Error: ', abs(nfp_utls.polygon_area(nfp[i])), pair['key'])
                        # print('NFP:', json.dumps(nfp[i]))
                        # print('A: ', A)
                        # print('B: ', B)
                        nfp.pop(i)
                        return None

            if len(nfp) == 0:
                return None
            # for outer NFPs, the first is guaranteed to be the largest.
            # Any subsequent NFPs that lie inside the first are hole
            for i in range(0, len(nfp)):
                if nfp_utls.polygon_area(nfp[i]) > 0:
                    nfp[i].reverse()

                if i > 0:
                    if nfp_utls.point_in_polygon(nfp[i][0], nfp[0]):
                        if nfp_utls.polygon_area(nfp[i]) < 0:
                            nfp[i].reverse()

            # generate nfps for children (holes of parts) if any exist
            # 有洞的暂时不管
            if use_holes and len(A) > 0:
                pass
        return {'key': pair['key'], 'value': nfp}

    def generate_nfp(self, nfp_list):
        """
        计算图形的转移量和适应值
        :param nfp_list:
        [
        {
            'key': {
                'A': '-1',                                                         # -1 stand for the container
                'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？,其实不用这么算的
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
                }

            'value': [[{'x': , 'y': },{'x': , 'y': },{'x': , 'y': },{'x': , 'y': }]]
        }
        ,

        {
            'key': {
                    'A': placed_segment_j[0],
                    'B': segment_i[0],
                    'inside': False,
                    'A_rotation': rotation_list[j],
                    'B_rotation': rotation_list[i]
                }

            'value': [[{'x': 'y': }...{'x':, 'y':}]]
        }

        ]

        :return:
        {
            'placements': all_placements,
            'fitness': fitness,
            'paths': paths,
            'area': bin_area,
            'min_length':min_length
        }

        """
        if nfp_list:
            for i in range(0, len(nfp_list)):
                if nfp_list[i]:
                    key = json.dumps(nfp_list[i]['key'])
                    self.nfp_cache[key] = nfp_list[i]['value']                   # 在这里不同的key对应不同的nfp多边形value

        self.worker.nfpCache = copy.deepcopy(self.nfp_cache)
        return self.worker.place_paths()

    def polygon_offset(self, polygon, offset):
        """
        :param polygon:
        [{'x': , 'y': }...{'x': 'y': }]
        :param offset: 5
        :return:
        """
        polygon = [[p['x'], p['y']] for p in polygon]

        miter_limit = 2
        co = pyclipper.PyclipperOffset(miter_limit, self.config['curveTolerance'])
        co.AddPath(polygon, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        result = co.Execute(1*offset)

        result = [{'x': p[0], 'y':p[1]} for p in result[0]]
        return result


def minkowski_difference(A, B):
    """
    两个多边形的相切空间
    http://www.angusj.com/delphi/clipper/documentation/Docs/Units/ClipperLib/Functions/MinkowskiDiff.htm
    :param A:
    :param B:
    :return:
    """
    Ac = [[p['x'], p['y']] for p in A['points']]
    Bc = [[p['x'] * -1, p['y'] * -1] for p in B['points']]
    solution = pyclipper.MinkowskiSum(Ac, Bc, True)
    largest_area = None
    clipper_nfp = None
    for p in solution:
        p = [{'x': i[0], 'y':i[1]} for i in p]
        sarea = nfp_utls.polygon_area(p)
        if largest_area is None or largest_area > sarea:
            clipper_nfp = p
            largest_area = sarea

    clipper_nfp = [{
                    'x': clipper_nfp[i]['x'] + Bc[0][0] * -1,
                    'y':clipper_nfp[i]['y'] + Bc[0][1] * -1
                   } for i in range(0, len(clipper_nfp))]
    return [clipper_nfp]




