# -*- coding: utf-8 -*-

from genetic_algorithm import genetic_algorithm
from tools import nfp_utls
from settings import SPACING, ROTATIONS, POPULATION_SIZE, MUTA_RATE, CURVETOLERANCE, BIN_LENGTH, BIN_WIDTH
import json
from tools.nfp_utls import almost_equal, rotate_polygon, get_polygon_bounds, polygon_area
import pyclipper
import copy


class Nester:
    def __init__(self, container=None, shapes=None, generation_num=1):

        self.container = container
        self.shapes = shapes
        self.total_segments_area = 0
        self.results = list()                           # storage for the different results
        self.nfp_cache = {}
        self.config = {
            'spacing': SPACING,                         # 组件间的间隔
            'rotations': ROTATIONS,                     # 旋转的颗粒度，360°的n份，如：4 = [0, 90 ,180, 270]
            'populationSize': POPULATION_SIZE,          # 基因群数量
            'mutationRate': MUTA_RATE,                  # 变异概率
        }
        self.GA = None
        self.generation = generation_num
        self.best = None
        self.solution = None

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

        # patch1 = [[200, 0], [400, 0], [400, 200], [200, 200]]
        # patch2 = [[100, 1000], [300, 1000], [300, 2000], [100, 2000]]

        patch1 = [[950, 1150], [1050, 1150], [1050, 1250], [950, 1250]]
        patch2 = [[1920, 320], [2080, 320], [2080, 480], [1920, 480]]

        patches = [patch1, patch2]

        for segment_cord in segments_lists:
            shape = {'area': 0, 'p_id': str(p_id), 'points': [{'x': p[0], 'y': p[1]} for p in segment_cord]}
            p_id = p_id + 1

            seg_area = nfp_utls.polygon_area(shape['points'])
            if seg_area > 0:                                        # 因为设置的是顺时针，所以用公式计算的面积应该小于0
                shape['points'].reverse()                           # 确定多边形的线段方向, 多边形方向为逆时针时，S < 0 ;多边形方向为顺时针时，S > 0

            shape['area'] = abs(seg_area)
            total_area += shape['area']
            self.shapes.append(shape)

        for patch in patches:
            shape = {'area': 0, 'p_id': str(p_id), 'points': [{'x': p[0], 'y': p[1]} for p in patch]}
            p_id = p_id + 1
            seg_area = nfp_utls.polygon_area(shape['points'])
            if seg_area > 0:
                shape['points'].reverse()

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

    def set_patches(self):
        pass



    def run(self):
        segments_sorted_list = list()
        for i in range(0, len(self.shapes)):
            segment = self.shapes[i]
            segment['points'] = polygon_offset(segment['points'], self.config['spacing'], CURVETOLERANCE)
            segments_sorted_list.append([str(i), segment])

        patches = segments_sorted_list[-2:]
        print("patches = ", patches)

        segments_sorted_list = sorted(segments_sorted_list[:-2], reverse=True, key=lambda o_segment: o_segment[1]['area'])

        segments_sorted_list = patches + segments_sorted_list





        ####################################################################################

        # generation = 0
        # if self.GA is None:
        #     container = self.container
        #     self.GA = genetic_algorithm.genetic_algorithm(segments_sorted_list, container)
        # else:
        #     while generation < self.generation:
        #         self.GA.generation()
        #         generation = generation + 1
        #         print("generation = ", generation)

        ####################################################################################

        generation = 0
        while generation < self.generation:
            if self.GA is None:
                container = self.container
                self.GA = genetic_algorithm.genetic_algorithm(segments_sorted_list, container)
            else:
                # for i in range(0, self.GA.populationSize):
                #     result_info_dic = self.find_fitness(self.GA.population[i])
                #     self.GA.population[i]['fitness'] = result_info_dic['fitness']

                for i in range(0, self.GA.populationSize):
                    result_info_dic = self.find_fitness(self.GA.population[i])
                    self.GA.population[i]['fitness'] = result_info_dic['fitness']
                    self.results.append(result_info_dic)

                if len(self.results) > 0:
                    best_result = self.results[0]

                    for p in self.results:
                        if p['fitness'] > best_result['fitness']:
                            best_result = p

                    if self.best is None or best_result['fitness'] > self.best['fitness']:
                        self.best = best_result

                self.GA.generation()

                generation = generation + 1
                print("generation = ", generation)
                print("self.best.fitness = ", self.best['fitness'])

        ####################################################################################

        # for i in range(0, self.GA.populationSize):
        #     result_info_dic = self.find_fitness(self.GA.population[i])
        #     self.GA.population[i]['fitness'] = result_info_dic['fitness']
        #     self.results.append(result_info_dic)
        #
        # if len(self.results) > 0:
        #     best_result = self.results[0]
        #
        #     for p in self.results:
        #         if p['fitness'] > best_result['fitness']:
        #             best_result = p
        #
        #     if self.best is None or best_result['fitness'] > self.best['fitness']:
        #         self.best = best_result

    def find_fitness(self, individual):
        """

        :param individual:
        :return:
        """

        place_order_list = copy.deepcopy(individual['placement_order'])
        rotation_list = copy.deepcopy(individual['rotation'])

        for i in range(0, len(place_order_list)):
            place_order_list[i].append(rotation_list[i])

        solution = place_order_list

        nfp_pairs = list(); new_cache = dict()

        for i in range(0, len(solution)):  # get IFR inner fit Rectangle keys
            segment_i = solution[i]
            key = {
                'A': '-1',  # -1 stand for the container
                'B': segment_i[0],  # segment_i[0] is the order of segment_i
                'inside': True,
                'A_rotation': 0,
                'B_rotation': rotation_list[i]
            }

            tmp_json_key = json.dumps(key)

            if not (tmp_json_key in self.nfp_cache.keys()):  # if didn't compute before ,the add this key
                nfp_pairs.append({
                    'A': self.container,
                    'B': segment_i[1],  # segment_i[1] is coords of segment_i
                    'key': key
                })
            else:
                new_cache[tmp_json_key] = self.nfp_cache[tmp_json_key]  # update new_cache

            for j in range(0, i):  # get nfp of seg_i and seg_j
                placed_segment_j = solution[j]

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

        self.nfp_cache = new_cache
        nfp_list = generate_nfp(nfp_pairs)

        for nfp in nfp_list:
            key = json.dumps(nfp['key'])
            self.nfp_cache[key] = nfp['value']

        nfp_cache = self.nfp_cache
        result = self.place_paths(solution, nfp_cache)

        return result

    def place_paths(self, solution, nfp_cache):
        """

        :param solution:
        :param nfp_cache:
        :return:
        """
        self.solution = solution

        paths = list()
        for combined_segment in solution:
            order = combined_segment[0]
            polygon = combined_segment[1]['points']
            angle = combined_segment[2]

            r = rotate_polygon(polygon, angle)
            r['rotation'] = angle
            r['order'] = order
            paths.append(r)

        a = list()
        for i in paths:
            a.append(i['rotation'])
        print("angle = ", a)


        fitness = 0; min_length = None

        placed_segment_list = list()  # 存放已经放置了的零件
        movements_list = list()
        for segment in paths:

            key = json.dumps({
                'A': '-1',
                'B': segment['order'],
                'inside': True,
                'A_rotation': 0,
                'B_rotation': segment['rotation']
            })

            inner_fit_rectangle = nfp_cache.get(key)
            # position = None

            movement = None

            ####################################################################################

            # if len(placed_segment_list) == 0:  # 最开始，没有放零件
            #     for point in inner_fit_rectangle:
            #         if movement is None or (point['x'] - segment['points'][0]['x'] < movement['x']):
            #             # 零件做下角的坐标加上这个position 就是ifp左下角的坐标
            #             movement = {
            #                 'x': point['x'] - segment['points'][0]['x'],
            #                 'y': point['y'] - segment['points'][0]['y'],
            #                 'p_id': segment['order'],
            #                 'rotation': segment['rotation']
            #             }
            #
            #     movements_list.append(movement)
            #     placed_segment_list.append(segment)
            #
            #     continue

            ####################################################################################

            ####################################################################################

            if len(placed_segment_list) < 2:
                for point in inner_fit_rectangle:
                    if movement is None or (point['x'] - segment['points'][0]['x'] < movement['x']):
                        # 零件做下角的坐标加上这个position 就是ifp左下角的坐标
                        movement = {
                            'x': 0,
                            'y': 0,
                            'p_id': segment['order'],
                            'rotation': segment['rotation']
                        }

                movements_list.append(movement)
                placed_segment_list.append(segment)

                continue
            ####################################################################################

            clipper_bin_nfp = list()
            clipper_bin_nfp.append([[p['x'], p['y']] for p in inner_fit_rectangle])

            clipper = pyclipper.Pyclipper()

            j = 0
            for placed_segment in placed_segment_list:
                """
                求待放的零件与已放了的零件的nfp
                """

                key = json.dumps({
                    'A': placed_segment['order'],
                    'B': segment['order'],
                    'inside': False,
                    'A_rotation': placed_segment['rotation'],
                    'B_rotation': segment['rotation']
                })

                nfp = nfp_cache.get(key)

                moved_nfp_bl = [[point['x'] + movements_list[j]['x'], point['y'] + movements_list[j]['y']] for point in nfp]
                moved_nfp_bl = pyclipper.CleanPolygon(moved_nfp_bl)
                j = j + 1

                if len(moved_nfp_bl) > 2:
                    clipper.AddPath(moved_nfp_bl, pyclipper.PT_SUBJECT, True)

            combine_nfp = clipper.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)

            clipper = pyclipper.Pyclipper()
            clipper.AddPaths(combine_nfp, pyclipper.PT_CLIP, True)
            clipper.AddPaths(clipper_bin_nfp, pyclipper.PT_SUBJECT, True)

            final_nfp = clipper.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
            final_nfp = pyclipper.CleanPolygons(final_nfp)

            for j in range(len(final_nfp) - 1, -1, -1):
                if len(final_nfp[j]) < 3:
                    final_nfp.pop(j)
            if len(final_nfp) == 0:
                continue

            candidate_bl_position = list()

            # a = list()
            for polygon in final_nfp:
                for p in polygon:
                    # 将所有可能放置的点都存放在一个list里面，这些点就是candidate position
                    candidate_bl_position.append({'x': p[0], 'y': p[1]})
                    # a.append({'x': p[0], 'y': p[1]})

            min_length = None; min_area = None;
            min_x = None

            for p_nf in candidate_bl_position:
                all_points = list()

                for m in range(0, len(placed_segment_list)):

                    for p in placed_segment_list[m]['points']:
                        all_points.append({
                            'x': p['x'] + movements_list[m]['x'],
                            'y': p['y'] + movements_list[m]['y']
                        })

                # path 坐标
                shift_vector = {
                    'x': p_nf['x'] - segment['points'][0]['x'],
                    'y': p_nf['y'] - segment['points'][0]['y'],
                    'p_id': segment['order'],
                    'rotation': segment['rotation'],
                }

                # 找新坐标后的最小矩形
                for point in segment['points']:
                    all_points.append({
                        'x': point['x'] + shift_vector['x'],
                        'y': point['y'] + shift_vector['y']
                    })

                rect_bounds = get_polygon_bounds(all_points)
                # weigh width more, to help compress in direction of gravity
                area = rect_bounds['length'] * 2 + rect_bounds['width']

                if (min_area is None or area < min_area or almost_equal(min_area, area)) and (
                        min_x is None or shift_vector['x'] <= min_x):
                    min_area = area
                    min_length = rect_bounds['length']
                    movement = shift_vector
                    min_x = shift_vector['x']

            if movement:
                placed_segment_list.append(segment)
                movements_list.append(movement)
                # placements.append(position)

        if min_length:
            fitness = self.total_segments_area / (min_length * BIN_WIDTH)
            print("fitness = ", fitness)

        print("min_length = ", min_length)

        return {'placements': movements_list, 'fitness': fitness, 'paths': paths,
                'min_length': min_length, 'solution': self.solution}

        # return {'placements': placements, 'fitness': fitness, 'paths': paths,'min_length': min_length}


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


def generate_nfp(nfp_paris):
    """
    :param nfp_paris:
    :return:
    """

    nfp_list = list()

    for pair in nfp_paris:
        poly_a = pair['A']

        poly_a['points'] = nfp_utls.rotate_polygon(poly_a['points'], pair['key']['A_rotation'])['points']
        poly_b = pair['B']
        poly_b['points'] = nfp_utls.rotate_polygon(poly_b['points'], pair['key']['B_rotation'])['points']

        if pair['key']['inside']:
            nfp = nfp_utls.nfp_rectangle(poly_a['points'], poly_b['points'])

            if nfp_utls.polygon_area(nfp) > 0:
                nfp.reverse()
        else:
            # pair['key']['inside'] == False , so compute no fit polygon between two segments
            # nfp = nfp_utls.nfp_polygon(poly_a, poly_b)    # 使用自己写的生成nfp的函数
            nfp = minkowski_difference(poly_a, poly_b)  # 使用 Minkowski_difference和求两个零件的nfp, 考虑用lib
            # print("nfp = ", nfp)

            if nfp_utls.polygon_area(nfp) > 0:
                nfp.reverse()

        nfp_list.append({'key': pair['key'], 'value': nfp})

    return nfp_list


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
    return clipper_nfp


def minkow(A, B):
    Ac = [[p['x'], p['y']] for p in A]
    Bc = [[p['x'] * -1, p['y'] * -1] for p in B]

    solution = pyclipper.MinkowskiSum(Ac, Bc, True)
    largest_area = None
    clipper_nfp = None

    for p in solution:
        p = [{'x': i[0], 'y': i[1]} for i in p]
        sarea = nfp_utls.polygon_area(p)
        if largest_area is None or largest_area > sarea:
            clipper_nfp = p
            largest_area = sarea

    clipper_nfp = [{
        'x': clipper_nfp[i]['x'] + Bc[0][0] * -1,
        'y': clipper_nfp[i]['y'] + Bc[0][1] * -1
    } for i in range(0, len(clipper_nfp))]
    return clipper_nfp

