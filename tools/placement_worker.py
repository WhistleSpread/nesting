# -*- coding: utf-8 -*-

import json
from tools.nfp_utls import almost_equal, rotate_polygon, get_polygon_bounds, polygon_area
import copy
import pyclipper


class PlacementWorker:
    def __init__(self, bin_polygon, combined_order_angle_paths, ids, rotations, config, nfp_cache):
        """

        :param bin_polygon:
        {
            'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
            'p_id':-1,
            'length': ,
            'width':
        }

        :param combined_order_angle_paths:
        [
            [1, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
            [2, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
            ...
            [314, {area: , p_id: , points:[{'x': , 'y': }...]}, 0],
        ]
        :param ids:
        [1, 2, 3, ..., 314]
        :param rotations:
        [0, 0, 0, ..., 0]

        :param config:
        {
            'curveTolerance': 0.3,                      # 允许的最大误差转换贝济耶和圆弧线段。在SVG的单位。更小的公差将需要更长的时间来计算
            'spacing': SPACING,                         # 组件间的间隔
            'rotations': ROTATIONS,                     # 旋转的颗粒度，360°的n份，如：4 = [0, 90 ,180, 270]
            'populationSize': POPULATION_SIZE,          # 基因群数量
            'mutationRate': MUTA_RATE,                  # 变异概率
            'useHoles': False,                          # 是否有洞，暂时都是没有洞
            'exploreConcave': False                     # 寻找凹面，暂时是否
        }

        :param nfp_cache:

        [
         {
            'A': '-1',                                                         # -1 stand for the container
            'B': segment_i[0],                                                 # 这个难不成是每一个解都要算一次吗？,其实不用这么算的
            'inside': True,
            'A_rotation': 0,
            'B_rotation': rotation_list[i]
        }  :  [[{'x': , 'y': },{'x': , 'y': },{'x': , 'y': },{'x': , 'y': }]]   # the value is just the nfp which is 2-d list
        ,
        {
            'A': placed_segment_j[0],
            'B': segment_i[0],
            'inside': False,
            'A_rotation': rotation_list[j],
            'B_rotation': rotation_list[i]
            } : 'value': [[{'x': 'y': }...{'x':, 'y':}]]
        }
        ......

        ]
        """

        self.bin_polygon = bin_polygon                                                              # 板材信息(四个点，长/宽)
        self.combined_order_angle_paths = copy.deepcopy(combined_order_angle_paths)                 # 一个摆放顺序
        self.ids = ids                                                                              # 图形原来的ID顺序
        self.rotations = rotations
        self.config = config
        self.nfpCache = nfp_cache or {}

    def place_paths(self):
        """
        1. according to the rotation angle to rotate polygon using function rotate_polygon and update point info
        2.

        path =
        [
            {
            'points': [{'x': , 'y': }...{'x': , 'y': }]},
            'rotation': ,       #  既然已经旋转过来了，为什么还要记录角度？
            'p_id': ,           #  这个应该是顺序，而不是id;
            },

            {
            'points': [],
            'rotation': ,
            'p_id': ,
            }

            ...
        ]

        :return:
        """

        paths = list()
        for i in range(0, len(self.combined_order_angle_paths)):
            p_id = self.combined_order_angle_paths[i][0]
            polygon = self.combined_order_angle_paths[i][1]['points']
            angle = self.combined_order_angle_paths[i][2]
            r = rotate_polygon(polygon, angle)
            r['rotation'] = angle
            r['p_id'] = p_id
            paths.append(r)

        all_placements = list()
        fitness = 0; bin_area = abs(polygon_area(self.bin_polygon['points']))
        min_length = None

        placed_segment_list = list()                        # 存放已经放置了的零件
        placements = list()
        fitness += 1                                        # fitness = 1

        for segment in paths:
            key = json.dumps({
                'A': '-1',
                'B': segment['p_id'],
                'inside': True,
                'A_rotation': 0,
                'B_rotation': segment['rotation']
            })

            inner_fit_rectangle = self.nfpCache.get(key)

            position = None
            if len(placed_segment_list) == 0:               # 最开始，没有放零件的时候
                for point in inner_fit_rectangle:
                    if position is None or (point['x'] - segment['points'][0]['x'] < position['x']):
                        position = {
                            'x': point['x'] - segment['points'][0]['x'],
                            'y': point['y'] - segment['points'][0]['y'],
                            'p_id': segment['p_id'],
                            'rotation': segment['rotation']
                        }

                placements.append(position)
                placed_segment_list.append(segment)
                continue

            clipper_bin_nfp = list()
            clipper_bin_nfp.append([[p['x'], p['y']] for p in inner_fit_rectangle])

            clipper = pyclipper.Pyclipper()

            for j in range(0, len(placed_segment_list)):
                p = placed_segment_list[j]
                key = json.dumps({
                    'A': p['p_id'],
                    'B': segment['p_id'],
                    'inside': False,
                    'A_rotation': p['rotation'],
                    'B_rotation': segment['rotation']
                })
                nfp = self.nfpCache.get(key)

                clone = [[point['x'] + placements[j]['x'], point['y'] + placements[j]['y']] for point in nfp]
                clone = pyclipper.CleanPolygon(clone)
                if len(clone) > 2:
                    clipper.AddPath(clone, pyclipper.PT_SUBJECT, True)

            combine_nfp = clipper.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
            clipper = pyclipper.Pyclipper()
            clipper.AddPaths(combine_nfp, pyclipper.PT_CLIP, True)
            clipper.AddPaths(clipper_bin_nfp, pyclipper.PT_SUBJECT, True)

            finalnfp = clipper.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
            finalnfp = pyclipper.CleanPolygons(finalnfp)

            for j in range(len(finalnfp)-1, -1, -1):
                if len(finalnfp[j]) < 3:
                    finalnfp.pop(j)
            if len(finalnfp) == 0:
                continue

            a = list()
            for polygon in finalnfp:
                for p in polygon:
                    a.append({'x': p[0], 'y': p[1]})

            finalnfp = a
            min_length = None; min_area = None; min_x = None

            for p_nf in finalnfp:
                all_points = list()
                # 这个地方改了 改成 for placed_segment in placed_segment_list:
                # for m in range(0, len(placed_segment_list)):
                for placed_segment in placed_segment_list:
                    for p in placed_segment['points']:
                        all_points.append({
                            'x': p['x']+placed_segment['x'],
                            'y': p['y']+placed_segment['y']
                        })

                # path 坐标
                shift_vector = {
                    'x': p_nf['x'] - segment['points'][0]['x'],
                    'y': p_nf['y'] - segment['points'][0]['y'],
                    'p_id': segment['p_id'],
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
                    position = shift_vector
                    min_x = shift_vector['x']

            if position:
                placed_segment_list.append(segment)
                placements.append(position)

        if min_length:
            fitness += min_length / bin_area

        if placements and len(placements) > 0:
            all_placements.append(placements)

        fitness += 2 * len(paths)

        print("min_length = ", min_length)
        return {'placements': all_placements, 'fitness': fitness, 'paths': paths,
                'area': bin_area, 'min_length':min_length}
