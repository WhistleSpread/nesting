
def get_polygon_bounds(polygon):
    """
    :param polygon: [{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}]
    :return: 返回左下角的点(x, y)，以及长度和宽度(length, width)
    """

    if polygon is None or len(polygon) < 3:
        return None

    x_max = polygon[0]['x']
    x_min = polygon[0]['x']
    y_max = polygon[0]['y']
    y_min = polygon[0]['y']

    for point in polygon:
        if point['x'] > x_max:
            x_max = point['x']
        elif point['x'] < x_min:
            x_min = point['x']
        if point['y'] > y_max:
            y_max = point['y']
        elif point['y'] < y_min:
            y_min = point['y']
        
    return {
        'x': x_min,
        'y': y_min,
        'length': x_max - x_min,
        'width': y_max - y_min
    }


def rotate_polygon(polygon, angle):
    """
    :param polygon:
    [{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}]
    :param angle:

    :return: rotated
    {
        'points': list(),
        'x' : ,
        'y' : ,
        'length' : ,
        'width' : ,
    }
    """

    rotated = {'points': list()}

    for point in polygon:
        x = point['x']
        y = point['y']
        if angle == 0:
            rotated['points'].append({
                'x': x , 'y': y
            })
        else:
            rotated['points'].append({
                'x': -x, 'y': -y
            })

    bounds = get_polygon_bounds(rotated['points'])
    rotated['x'] = bounds['x']
    rotated['y'] = bounds['y']
    rotated['length'] = bounds['length']
    rotated['width'] = bounds['width']
    return rotated

