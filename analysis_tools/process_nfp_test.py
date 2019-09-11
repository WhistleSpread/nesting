import copy

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

    if pair is None or len(pair) == 0:
        return None

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
