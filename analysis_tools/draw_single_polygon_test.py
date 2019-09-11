import cv2
import numpy as np 
import matplotlib.pyplot as plt

def draw_polygon(point_list, name):
    # 声明一个画布
    canvas = np.ones((500, 1000, 3), dtype="uint8")
    canvas *= 255
    points = np.array(point_list, np.int32)
    points = points.reshape((-1,1,2))
    print("points after reshape")

    # print(points)
    cv2.polylines(canvas, pts=[points], isClosed=True, color=(0,0,255), thickness=3)
    cv2.imshow("polylines", canvas)
    cv2.imwrite("polylines"+ name + ".png", canvas)
    cv2.waitKey(0)

# polygon = [{'x':0, 'y':0}, {'x':0, 'y':100}, {'x':100, 'y':100},{'x':200, 'y':100}, {'x':100, 'y':0}]
# polygon = [[p['x'], p['y']] for p in polygon]
# draw_polygon(polygon, "1")

# polygon = [{'x':0, 'y':0}, {'x':0, 'y':100}, {'x':100, 'y':100},{'x':200, 'y':100}, {'x':100, 'y':0}]
# offset = 10
# offseted_polygon = polygon_offset(polygon, offset)
# print("offseted_polygon = ", offseted_polygon)
# draw_polygon(offseted_polygon, "2")

def draw_polygon():
    a = np.array([[[10,10], [100,10], [100,100], [10,100]]], dtype = np.int32)
    b = np.array([[[100,100], [200,230], [150,200], [100,220]]], dtype = np.int32)
    c = np.array([[[10,10], [10,100], [100,100], [150,50], [100, 10]]], dtype = np.int32)
    d = [[10,10], [10,100], [100,100], [150,50], [100, 10]]
    # d = polygon_offset(d, 7)
    d = np.array(d, np.int32)
    d = d.reshape((-1,1,2))

    im = np.zeros([240, 320], dtype = np.uint8)

    # cv2.polylines(im, a, 1, 255)
    # cv2.polylines(im, b, 1, 255)
    cv2.fillPoly(im, c, 255)
    cv2.polylines(im, pts=[d], isClosed=True, color=(255,255, 0), thickness=1)
    # cv2.polylines(im, d, 1, 134)

    # cv2.fillPoly(im, b, 255)
    plt.imshow(im)
    plt.show()