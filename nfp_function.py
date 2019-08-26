# -*- coding: utf-8 -*-

import math
import json
import random
import copy
# from Polygon import Polygon
import Polygon
from genetic_algorithm import genetic_algorithm
from tools import placement_worker, nfp_utls, draw_utls
import pyclipper

from settings import SPACING, ROTATIONS, BIN_WIDTH, POPULATION_SIZE, MUTA_RATE


class Nester:
    def __init__(self, container=None, shapes=None):
        """
        Nester([container,shapes]): Creates a nester object with a container
           shape and a list of other shapes to nest into it. Container and
           shapes must be Part.Faces.
           Typical workflow:
           n = Nester() # creates the nester
           n.add_container(object) # adds a doc object as the container
           n.add_objects(objects) # adds a list of doc objects as shapes
           n.run() # runs the nesting
           n.show() # creates a preview (compound) of the results
        """

        self.container = container  # 承载组件的容器
        self.shapes = shapes        # 组件信息
        self.shapes_max_length = 0   # 在一般无限长的布，设计一个布的尺寸
        self.results = list()  # storage for the different results
        self.nfp_cache = {}     # 缓存中间计算结果
        # 遗传算法的参数
        self.config = {
            'curveTolerance': 0.3,  # 允许的最大误差转换贝济耶和圆弧线段。在SVG的单位。更小的公差将需要更长的时间来计算
            'spacing': SPACING,           # 组件间的间隔
            'rotations': ROTATIONS,         # 旋转的颗粒度，360°的n份，如：4 = [0, 90 ,180, 270]
            'populationSize': POPULATION_SIZE,    # 基因群数量
            'mutationRate': MUTA_RATE,      # 变异概率
            'useHoles': False,       # 是否有洞，暂时都是没有洞
            'exploreConcave': False  # 寻找凹面，暂时是否
        }

        self.GA = None        # 遗传算法类
        self.best = None      # 记录最佳结果
        self.worker = None    # 根据NFP结果，计算每个图形的转移数据
        self.container_bounds = None   # 容器的最小包络矩形作为输出图的坐标

    def add_objects(self, objects):
        """
        add_objects(objects): adds polygon objects to the nester
        """
        # print("objects = ", objects)

        if not isinstance(objects, list):
            # isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type(), 只不过会考虑继承; # 判断objects是不是个list, 如果不是个list,就要套上一个[]
            objects = [objects]
        if not self.shapes:
            self.shapes = []

        p_id = 0
        total_area = 0

        for obj in objects:
            # 这里obj表示每一个单独的零件， objects表示所有零件组成的list
            # 调用了一个clean_polygon函数，
            # points = self.clean_polygon(obj)

            points = obj
            shape = {
                'area': 0,
                'p_id': str(p_id),
                'points': [{'x': p[0], 'y': p[1]} for p in points]
            }

            # 确定多边形的线段方向
            area = nfp_utls.polygon_area(shape['points'])
            # 多边形方向为逆时针时，S < 0 ;多边形方向为顺时针时，S > 0
            # 因为这里是顺时针方向，所以是小于零；
            # print("area = ", area)
            if area > 0:
                shape['points'].reverse()

            shape['area'] = abs(area)
            # total_area 计算的是到目前为止加入零件的总面积
            total_area += shape['area']
            self.shapes.append(shape)

        # 每次经过一个object list之后就更新一下面料的长度
        # 这个是为了计算总的面料的长度，所需面料的长度
        self.shapes_max_length = total_area / BIN_WIDTH * 3

    def add_container(self, container):
        """
        add_container(object): adds a polygon objects as the container
        container 为容器，为一个字典， container 为一个矩形的容器
        """
        if not self.container:
            self.container = {}

        # 感觉这里的数据都非常的感觉，不需要使用clean_polygon函数
        # container = self.clean_polygon(container)

        # container是一个字典，key-value, points 表示这个container中所有的点
        self.container['points'] = [{'x': p[0], 'y':p[1]} for p in container]
        # print('container[points] = ', self.container['points'])
        # 第一次运行的结果[{'y': 0, 'x': 0}, {'y': 1600, 'x': 0}, {'y': 1600, 'x': 20000}, {'y': 0, 'x': 20000}]
        self.container['p_id'] = '-1'

        xbinmax = self.container['points'][0]['x']
        xbinmin = self.container['points'][0]['x']
        ybinmax = self.container['points'][0]['y']
        ybinmin = self.container['points'][0]['y']
        print((xbinmax, xbinmin, ybinmax, ybinmin))
        # 第一次运行结果(0, 0, 0, 0)
        # 不过为什么是这个样子呢？

        # 这里是在遍历container的四个角，找到最大的x和最小的x,最大的y和最小的y;
        for point in self.container['points']:
            if point['x'] > xbinmax:
                xbinmax = point['x']
            elif point['x'] < xbinmin:
                xbinmin = point['x']
            if point['y'] > ybinmax:
                ybinmax = point['y']
            elif point['y'] < ybinmin:
                ybinmin = point['y']
        print((xbinmax, xbinmin, ybinmax, ybinmin))
        # (20000, 0, 1600, 0)

        self.container['length'] = xbinmax - xbinmin
        self.container['width'] = ybinmax - ybinmin

        # 容器的最小包络矩形作为输出图的坐标 
        self.container_bounds = nfp_utls.get_polygon_bounds(self.container['points'])
        # print("self.container = ", self.container)

    def clear(self):
        """clear(): Removes all objects and shape from the nester"""
        self.shapes = None

    def run(self):
        """
        run(): Runs a nesting operation. Returns a list of lists of
        shapes, each primary list being one filled container, or None
        if the operation failed.
        如果开多线程，可以在这里设计检查中断信号
        """
        # 检查一下是否有container,是否有shapes
        if not self.container:
            print("Empty container. Aborting")
            return
        if not self.shapes:
            print("Empty shapes. Aborting")
            return
        

        # and still identify the original face, so we can calculate a transform afterwards
        # 这里的faces是个什么东西？
        faces = list()
        # 这里的len(self.shapes)就是待排零件的个数，在这里，遍历每一个零件
        for i in range(0, len(self.shapes)):
            # 深度拷贝每一个零件, 关于每一个shape的数据结构，在add_objects里面可以看到，是一个字典;
            shape = copy.deepcopy(self.shapes[i])
            # shape是一个字段，有三个key-value, 分别是points, area, p_id, 一个shape就是一个零件
            # 这里通过调用polygon_offset 来设置零件之间的间距, 通过这一步的处理，得到新的points
            # 不过说实话，这里怎么处理的我没有看明白
            shape['points'] = self.polygon_offset(shape['points'], self.config['spacing'])

            # 这里faces 是一个list, 每个list的元素是一个2元的list[str(i), shape], 表示第i个零件
            # 以及这里零件的点的坐标
            faces.append([str(i), shape])

        # print("faces = ", faces)

        # build a clean copy so we don't touch the original order by area
        # 对这些零件做一个排序，排序的标准是按照每一个shape的面积,从大到小的排序，大的在前面，小的在后面
        faces = sorted(faces, reverse=True, key=lambda face: face[1]['area'])
        return self.launch_workers(faces)

    def launch_workers(self, adam):
        """
        主过程，根据生成的基因组，求适应值，找最佳结果
        这里传入的参数adam 就是faces,基本的数据结构是一个list, 而且是有序的list
        这个list的每一个元素也是一个list[第几个零件，这个零件的shape], 而shape信息中包含有 points, p_id, area，
        这三个都是以键值对的形式存在，并且point的值是一个list,这个list的每个元素都是一个点{x:, y:}
        """

        if self.GA is None:
            # 首先深拷贝一个容器，回顾一下，self.container的数据结构
            # 首先它也是一个字典，key-value, key 分别有 points, p_id, width, height, 其实这里应该改成是length, width
            offset_bin = copy.deepcopy(self.container)
            # 这里需要修改一些，因为在比赛的时候，我们的bin的边距是为0的，并不是spaceing 5mm
            # print("offset_bin_before = ", offset_bin)

            # 在运行的时候把这一行注释掉运行看看，这个是边界没有考虑偏移量的版本
            # offset_bin['points'] = self.polygon_offset(self.container['points'], self.config['spacing'])

            # print("offset_bin_after = ", offset_bin)
            """
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

            # 这个地方应该是得到一个初始种群，也就是初始解;

            self.GA = genetic_algorithm.genetic_algorithm(adam, offset_bin)
        else:
            self.GA.generation()
        


        # 得到了一个种群以后，计算每一组基因的适应值
        # POPULATION_SIZE 表示种群的大小，每个种群中设置的是10个个体，每一个个体应该是一个解
        for i in range(0, self.GA.populationSize):
            print("计算 fitness now i = ", i) 
            # print("self.GA.population[i] = ", self.GA.population[i])
            # key有：rotation, placement
            res = self.find_fitness(self.GA.population[i])
            self.GA.population[i]['fitness'] = res['fitness']
            self.results.append(res)
        
        # 找最佳结果
        if len(self.results) > 0:
            best_result = self.results[0]

            for p in self.results:
                if p['fitness'] < best_result['fitness']:
                    best_result = p

            if self.best is None or best_result['fitness'] < self.best['fitness']:
                self.best = best_result
        print("launch workers done!!!!!!!!!!!")

    def find_fitness(self, individual):
        """
        求解适应值
        :param individual: 传入的是一个individual,也就是一个解
        :return:
        """

        place_list = copy.deepcopy(individual['placement'])
        rotations = copy.deepcopy(individual['rotation'])
        
        ids = [p[0] for p in place_list]
        # 这里的ids表示零件排列的顺序
        # print("ids = ", ids)

        for i in range(0, len(place_list)):
            place_list[i].append(rotations[i])

        # 这里将旋转的角度插入得到新的放置的list,
        # print("place_list = ", place_list)
        
        nfp_pairs = list()
        new_cache = dict()

        for i in range(0, len(place_list)):
            # 遍历每一个零件，注意place_list中也有角度信息
            # 容器和零件的内切多边形计算, 因为点必须是在容器和图形的内接多边形里面
            # 否则零件就超出容器了；

            # 用part 表示我们正在处理的零件
            part = place_list[i]

            # key
            key = {
                'A': '-1',
                'B': part[0],               # part[0]是顺序index
                'inside': True,             # 
                'A_rotation': 0,            # 零件A是固定的
                'B_rotation': rotations[i]  # 零件B就是这个零件旋转的角度
            }

            tmp_json_key = json.dumps(key)
            # print("tmp_json_key = ", tmp_json_key)


            # print("nfp_cache = ", nfp_cache)
            # nfp_cache 是一个key-value的形式，key就是前面的这个json,所以取名叫做json_key
            # value是一个[[四个坐标点{x: , y: }]]
            # print("not self.nfp_cache.has_key(tmp_json_key) = ", not self.nfp_cache.has_key(tmp_json_key))

            # if not self.nfp_cache.has_key(tmp_json_key):
            if not (tmp_json_key in self.nfp_cache.keys()):
                nfp_pairs.append({
                    'A': self.container,
                    'B': part[1], # part[1] 是点的坐标
                    'key': key
                })
            else:
                # 是否已经计算过结果
                new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]

            # print("nfp_pairs = ", nfp_pairs)

            # 图形与图形之间的外切多边形计算
            for j in range(0, i):
                # 在第i个之前的是已经放置好了的，放在place数组中
                placed = place_list[j]

                key = {
                    'A': placed[0],
                    'B': part[0],
                    'inside': False,
                    'A_rotation': rotations[j],
                    'B_rotation': rotations[i]
                }
                tmp_json_key = json.dumps(key)

                # nfp_cache缓存中间结果，是一个字典
                # if not self.nfp_cache.has_key(tmp_json_key):
                if not (tmp_json_key in self.nfp_cache.keys()):
                    nfp_pairs.append({
                        'A': placed[1],
                        'B': part[1],
                        'key': key
                    })
                else:
                    # 是否已经计算过结果
                    new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]

        # only keep cache for one cycle
        self.nfp_cache = new_cache

        # print("after one cycle nfp_cache = ", self.nfp_cache)
        # 计算图形的转移量和适应值的类
        self.worker = placement_worker.PlacementWorker(
             self.container, place_list, ids, rotations, self.config, self.nfp_cache)

        # 计算所有图形两两组合的相切多边形（NFP）
        pair_list = list()
        # print("len(nfp_pairs) = ", len(nfp_pairs))

        # 这个地方计算nfp_pair花了好久啊？？？？这个地方时间太久了;nfp_pair 有49455，这个也太多了吧
        # 对，这个地方是不是可以优化一下，太费时间了
        for pair in nfp_pairs:
            pair_list.append(self.process_nfp(pair))
        
        # 根据这些NFP，求解图形分布
        return self.generate_nfp(pair_list)

    def process_nfp(self, pair):
        """
        计算所有图形两两组合的相切多边形（NFP）
        :param pair: 两个组合图形的参数
        :return:
        """
        if pair is None or len(pair) == 0:
            return None
        # 考虑有没有洞和凹面
        search_edges = self.config['exploreConcave']
        use_holes = self.config['useHoles']

        # 图形参数
        A = copy.deepcopy(pair['A'])
        A['points'] = nfp_utls.rotate_polygon(A['points'], pair['key']['A_rotation'])['points']
        B = copy.deepcopy(pair['B'])
        B['points'] = nfp_utls.rotate_polygon(B['points'], pair['key']['B_rotation'])['points']

        if pair['key']['inside']:
            # 内切或者外切
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
            if search_edges:
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

    def generate_nfp(self, nfp):
        """
        计算图形的转移量和适应值
        :param nfp: nfp多边形数据
        :return:
        """
        if nfp:
            for i in range(0, len(nfp)):

                if nfp[i]:
                    key = json.dumps(nfp[i]['key'])
                    self.nfp_cache[key] = nfp[i]['value']

        # worker的nfp cache 只保留一次
        self.worker.nfpCache = copy.deepcopy(self.nfp_cache)
        # self.worker.nfpCache.update(self.nfpCache)
        return self.worker.place_paths()

    def show_result(self):
        """
        这个函数好像没有用啊
        """
        draw_utls.draw_result(self.best['placements'], self.shapes, self.container, self.container_bounds)

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

    # def clean_polygon(self, polygon):
        # """
        # 函数传入的是一个多边形
        # """
        # print("now in clean_polygon!!!!")
        # print("polygon = ", polygon)
        # # pyclipper.SimplifyPolygon的作用是：将一个多边形简化
        # simple = pyclipper.SimplifyPolygon(polygon, pyclipper.PFT_NONZERO)
        # print("simple = ", simple)

        # if simple is None or len(simple) == 0:
        #     return None
        # biggest = simple[0]
        # biggest_area = pyclipper.Area(biggest)
        # print("biggest_area = ", biggest_area)
        # print("len(simple) = ", len(simple))
        # for i in range(1, len(simple)):
        #     area = abs(pyclipper.Area(simple[i]))
        #     if area > biggest_area:
        #         biggest = simple[i]
        #         biggest_area = area

        # clean = pyclipper.CleanPolygon(biggest, self.config['curveTolerance'])
        # if clean is None or len(clean) == 0:
        #     return None
        # return clean





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




