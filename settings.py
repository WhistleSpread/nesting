# -*- coding: utf-8 -*-

POPULATION_SIZE = 1   # 种群中的个体数目
# NUATATION = 0
MUTA_RATE = 0.2         # 变异概率
ROTATIONS = 1           # 旋转选择， 1： 不能旋转

CURVETOLERANCE = 0.3                    # 允许的最大误差转换贝济耶和圆弧线段。在SVG的单位。更小的公差将需要更长的时间来计算

# 单位都是MM(毫米)
SPACING = 7     # 图形间隔空间

# 面料尺寸,长度为20000,宽度为1600
# BIN_LENGTH = 220000
# BIN_WIDTH = 3500

BIN_LENGTH = 20000
BIN_WIDTH = 1600
BIN_NORMAL = [[0, 0], [0, BIN_WIDTH], [BIN_LENGTH, BIN_WIDTH], [BIN_LENGTH, 0]]



