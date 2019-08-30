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
        self.shapes_max_length = 0                      
        self.results = list()                           # storage for the different results
        self.nfp_cache = {}                             # 缓存中间计算结果
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
        self.worker = None                              # 根据NFP结果，计算每个图形的转移数据
        self.container_bounds = None                    # 容器的最小包络矩形作为输出图的坐标

    def set_segments(self, segments_lists):

        if not isinstance(segments_lists, list):
            segments_lists = [segments_lists]
        if not self.shapes:
            self.shapes = []

        p_id = 0
        total_area = 0

        for segment_cord in segments_lists:

            shape = {
                'area': 0,
                'p_id': str(p_id),
                'points': [{'x': p[0], 'y': p[1]} for p in segment_cord]
            }

            area = nfp_utls.polygon_area(shape['points'])
            if area > 0:                                    # 因为设置的是顺时针，所以应该小于0
                shape['points'].reverse()                   # 确定多边形的线段方向, 多边形方向为逆时针时，S < 0 ;多边形方向为顺时针时，S > 0
            shape['area'] = abs(area)

            total_area += shape['area']
            self.shapes.append(shape)

        self.shapes_max_length = total_area / BIN_WIDTH * 3         # 更新一下面料的长度

    def set_container(self, container):

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
        run(): Runs a nesting operation. Returns a list of lists of
        shapes, each primary list being one filled container, or None
        if the operation failed.
        try Multi threading, and check exception
        """

        if not self.container:
            print("Empty container. Aborting")
            return
        if not self.shapes:
            print("Empty shapes. Aborting")
            return

        segments_sorted_list = list()
        for i in range(0, len(self.shapes)):
            segment = copy.deepcopy(self.shapes[i])
            segment['points'] = self.polygon_offset(segment['points'], self.config['spacing'])  #调用polygon_offset 来设置零件之间的间距, 得到新的points,不懂
            segments_sorted_list.append([str(i), segment])

        segments_sorted_list = sorted(segments_sorted_list, reverse=True, key=lambda face: face[1]['area'])
        return self.launch_workers(segments_sorted_list)

    def launch_workers(self, segments_sorted_list):
        """
        主过程，根据生成的基因组，求适应值，找最佳结果
        这个list的每一个元素也是一个list[第几个零件，这个零件的shape], 而shape信息中包含有 points, p_id, area，
        这三个都是以键值对的形式存在，并且point的值是一个list,这个list的每个元素都是一个点{x:, y:}
        """
        if self.GA is None:
            bin_info_dic = copy.deepcopy(self.container)

            """
            # 首先它也是一个字典，key-value, key 分别有 points, p_id, width, height, 其实这里应该改成是length, width
            # 这里需要修改一些，因为在比赛的时候，我们的bin的边距是为0的，并不是spaceing 5mm
            # print("offset_bin_before = ", offset_bin)
            # 在运行的时候把这一行注释掉运行看看，这个是边界没有考虑偏移量的版本
            # offset_bin['points'] = self.polygon_offset(self.container['points'], self.config['spacing'])

            # print("offset_bin_after = ", offset_bin)
            
            从这个结果可以看出，这个地方的polygon_offset 算法是有问题的 可以先不考虑offset来运行一遍，之后再修改，考虑
            这个offset， 这个很明显就有错误！！！
            
            ('offset_bin_before = ', 
            {'width': 20000, 'points': [{'y': 0, 'x': 0}, {'y': 1600, 'x': 0}, {'y': 1600, 'x': 20000}, {'y': 0, 'x': 20000}], 
            'p_id': '-1', 'height': 1600})
            ('polygon = ', [[0, 0], [0, 1600], [20000, 1600], [20000, 0]])
            ('offset_bin_after = ', {'width': 20000, 'points': 

            [{'y': -4, 'x': 20003}, {'y': 0, 'x': 20005}, {'y': 1600, 'x': 20005}, {'y': 1603, 'x': 20004}, 
            {'y': 1605, 'x': 20000}, {'y': 1605, 'x': 0}, {'y': 1604, 'x': -3}, 
            {'y': 1600, 'x': -5}, {'y': 0, 'x': -5}, {'y': -3, 'x': -4}, 
            {'y': -5, 'x': 0}, {'y': -5, 'x': 20000}],
             'p_id': '-1', 'height': 1600})
            """
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
        """

        place_order_list = copy.deepcopy(individual['placement_order'])
        rotation_list = copy.deepcopy(individual['rotation'])

        ids = [p[0] for p in place_order_list]                          # order of segments

        for i in range(0, len(place_order_list)):
            place_order_list[i].append(rotation_list[i])
        
        combined_order_angle_list = copy.deepcopy(place_order_list)

        nfp_pairs = list()
        new_cache = dict()

        for i in range(0, len(combined_order_angle_list)):              # get IFR inner fit Rectangle
            segment_i = combined_order_angle_list[i]
            key = {
                'A': '-1',                                              # -1 stand for the container
                'B': segment_i[0],                                      # segment_i[0] is the index of segment_i
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
                new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]

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

            # with open("中间结果.json", "a") as f:
            #     f.write("new_cache" + str(new_cache))
            #     f.write("nfp_pairs" + str(nfp_pairs))

            # print("nfp_pairs = ", nfp_pairs)
            # print("len(nfp_pairs)", len(nfp_pairs))
            # print("new_cache = ", new_cache)

        self.nfp_cache = new_cache                                      # 每一轮,也就是对每一个解过后，更新一次nfp_cache
        # with open("中间结果.json", "a") as f:
        #     f.write("self.nfp_cache" + str(self.nfp_cache))

        self.worker = placement_worker.PlacementWorker(self.container, combined_order_angle_list, ids, rotation_list,
                                                       self.config, self.nfp_cache)

        pair_list = list()
        for pair in nfp_pairs:
            pair_list.append(self.process_nfp(pair))                    # 这个地方计算nfp_pair花了好久啊？;nfp_pair 有49455，这个也太多了吧? 时间最多了
            with open("pair_list.json", "a") as f:
                f.write("pair_list" + str(pair_list)+"\n")
        return self.generate_nfp(pair_list)

    def process_nfp(self, pair):
        """
        计算所有图形两两组合的相切多边形（NFP）
        """
        if pair is None or len(pair) == 0:
            return None

        # 考虑有没有洞和凹面
        search_edges = self.config['exploreConcave']
        use_holes = self.config['useHoles']

        A = copy.deepcopy(pair['A'])
        A['points'] = nfp_utls.rotate_polygon(A['points'], pair['key']['A_rotation'])['points']             # 旋转后的A
        B = copy.deepcopy(pair['B'])
        B['points'] = nfp_utls.rotate_polygon(B['points'], pair['key']['B_rotation'])['points']             # 旋转后的B

        if pair['key']['inside']:                                                                           # 内切多边形
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
                # print('NFP Warning:', pair['key'])

        else:
            if search_edges:                                                                                 # 外切多边形
                nfp = nfp_utls.nfp_polygon(A, B, False, search_edges)
            else:
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
        :param nfp_list: nfp多边形数据list
        :return:
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
        offset 表示偏移量, 这个偏移量其实就是组件间的间隔，在本次比赛中设置的5mm
        polygon 是shape['points'],就是一个list,list中的每个元素都是一个字典{x:,y:}
        不过这个函数貌似有问题，这个库用的不好
        """
        # is_list 是一个flag, 表示是不是一个列表, 不过这里设置这个flag有什么作用呢？

        is_list = True
        # 这个函数就是做一个转换，将本来list中是dict的形式转换成list中是小的2元list的形式
        if isinstance(polygon[0], dict):
            polygon = [[p['x'], p['y']] for p in polygon]
            is_list = False

        # print("polygon = ", polygon)

        # 这里使用了库pyclipper的, 就是为了保证零件之间的距离为5，这个地方我没有看懂
        # 因为这个pyclipper库没怎么看明白

        miter_limit = 2
        co = pyclipper.PyclipperOffset(miter_limit, self.config['curveTolerance'])
        co.AddPath(polygon, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        result = co.Execute(1*offset)
        # print("result = ", result)

        # 这个操作就是把它变回去，从list变回到字典的情况中去；而且这个is_list 根本就没用嘛
        if not is_list:
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




