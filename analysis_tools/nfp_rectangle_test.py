import cv2
import numpy as np 
import matplotlib.pyplot as plt


def nfp_rectangle(A, B):
    """
    :param A: [{'x': , 'y': }...{'x': , 'y': }]
    :param B: [{'x': , 'y': }...{'x': , 'y': }]
    :return:
    """
    # the first point of polygon A
    min_ax = A[0]['x']; min_ay = A[0]['y']
    max_ax = A[0]['x']; max_ay = A[0]['y']

    for point in A[1:]:
        if point['x'] < min_ax: min_ax = point['x']
        if point['x'] > max_ax: max_ax = point['x']
        if point['y'] < min_ay: min_ay = point['y']
        if point['y'] > max_ay: max_ay = point['y']

    # the first point of polygon B
    min_bx = B[0]['x']; min_by = B[0]['y']
    max_bx = B[0]['x']; max_by = B[0]['y']

    for point in B[1:]:
        if point['x'] < min_bx: min_bx = point['x']
        if point['x'] > max_bx: max_bx = point['x']
        if point['y'] < min_by: min_by = point['y']
        if point['y'] > max_by: max_by = point['y']

    # 要求b的length要小于a的length
    # 要求b的width要要与a的width
    # 也就是说矩形b比矩形a要小？ 为什么有这个要求？
    if max_bx - min_bx > max_ax - min_ax:
        return None
    if max_by - min_by > max_ay - min_ay:
        return None

    return [[
        {'x': min_ax-min_bx+B[0]['x'], 'y': min_ay-min_by+B[0]['y']},
        {'x': max_ax-max_bx+B[0]['x'], 'y': min_ay-min_by+B[0]['y']},
        {'x': max_ax-max_bx+B[0]['x'], 'y': max_ay-max_by+B[0]['y']},
        {'x': min_ax-min_bx+B[0]['x'], 'y': max_ay-max_by+B[0]['y']}
    ]]



A = [{'x':300, 'y':300}, {'x':300, 'y':800}, {'x':800, 'y':800}, {'x':800, 'y':300}]
B = [{'x':10, 'y':10}, {'x':10, 'y':100}, {'x':100, 'y':100}, {'x':100, 'y':10}]

nfp_rec = nfp_rectangle(A, B)

print("nfp_rectangle = ", nfp_rec)
# [[{'x': 300, 'y': 300}, {'x': 710, 'y': 300}, {'x': 710, 'y': 710}, {'x': 300, 'y': 710}]]

A = [[p['x'], p['y']] for p in A]
A = np.array(A, np.int32)
A = A.reshape((-1,1,2))

B = [[p['x'], p['y']] for p in B]
B = np.array(B, np.int32)
B = B.reshape((-1,1,2))

rec = [[p['x'], p['y']] for p in nfp_rec[0]]
rec = np.array(rec, np.int32)
rec = rec.reshape((-1,1,2))

im = np.zeros([1000, 1000], dtype = np.uint8)
cv2.fillPoly(im, A, 255)
cv2.fillPoly(im, B, 255)
cv2.fillPoly(im, rec, 255)

plt.imshow(im)
plt.show()

