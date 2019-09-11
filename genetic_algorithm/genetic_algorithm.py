# -*- coding: utf-8 -*-
import copy
import random 
from tools import nfp_utls
from settings import POPULATION_SIZE, MUTA_RATE


class genetic_algorithm():

    def __init__(self, segments_sorted_list, bin_info_dic):
        """
        :param segments_sorted_list:
            [
            [1, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            [2, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ...
            [314, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ]

        :param bin_info_dic = self.container :
            {
                'points':[{'x':, 'y': }, {'x':, 'y':}, {'x':, 'y':}, {'x':, 'y':}],
                'p_id':-1,
                'length': ,
                'width':
            }
        :return
        self.individual =
            {
                'placement_order':
                [
                [1, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
                [2, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
                ...
                [314, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
                ]
                'rotation': [0, 0, ..., 0]
            }
        self.population = [{self.individual}, {self.individual_2}, ...{self.individual_size}]
        """

        self.populationSize = POPULATION_SIZE
        self.mutationRate = MUTA_RATE
        self.bin_info_dic = bin_info_dic

        placement_order = copy.deepcopy(segments_sorted_list)
        angles = [0]*len(placement_order)

        self.individual = {'placement_order': placement_order, 'rotation': angles}
        self.population = [self.individual]

        for i in range(1, self.populationSize):
            mutated_individual = self.mutate(self.individual)
            self.population.append(mutated_individual)

    def random_angle(self, shape, angle):
        """
        :param shape:  point of one segment
        :param angle:  angle of one segment
        :return: angle or random_angle one of (0, 180)
        """


        # 为什么用这种算法最后有的零件不显示出来呢？奇怪？
        # 这个函数改了后，算法的收敛性慢了好多；

        # def valid_rotate(shape, angle):
        #     rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
        #     if rotate_part['length'] < self.bin_info_dic['length'] and rotate_part['width'] < self.bin_info_dic['width']:
        #         return True
        #     else:
        #         return False

        # if angle == 0:
        #     if valid_rotate(shape, 180):
        #         return 180
        #     return 0
        # else:
        #     if valid_rotate(shape, 0):
        #         return 0
        #     return 180

        # 感觉这里到angle_list 就直接设置成[0, 180]就好了

        angle_list = [0, 180]
        # 查看选择后图形是否能放置在里面
        for angle in angle_list:
            # rotate_polygon 就是用来旋转多边形, 传入到是多边形到点到坐标，以及角度angle
            rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
            # 是否判断旋转出界,没有出界可以返回旋转角度,rotate 只是尝试去转，没有真正改变图形坐标
            if rotate_part['length'] < self.bin_info_dic['length'] and rotate_part['width'] < self.bin_info_dic['width']:
                return angle
        return 0

    def mutate(self, individual):
        """
        :param individual:
        {
            'placement_order':
            [
            [1, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            [2, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ...
            [314, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ]
            'rotation': [0, 0, ..., 0]
        }

        :return: clone :
        {
            'placement_order':
            [
            [3, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            [8, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ...
            [264, {area: , p_id: , points:[{'x': , 'y': }]},... {area: , p_id: , points:[{'x': , 'y': }]}],
            ]
            'rotation': [0, 0, ..., 0]
        }
        """

        clone = {
            'placement_order': individual['placement_order'][:],
            'rotation': individual['rotation'][:]
        }

        for i in range(0, len(clone['placement_order'])):
            if random.random() < self.mutationRate:
                if i+1 < len(clone['placement_order']):
                    clone['placement_order'][i], clone['placement_order'][i+1] = clone['placement_order'][i+1], clone['placement_order'][i]

            if random.random() < self.mutationRate:
                clone['rotation'][i] = self.random_angle(clone['placement_order'][i], clone['rotation'][i])

        return clone

    def generation(self):
        """

        :return:
        """
        # 适应度 从大到小排序
        # print("self.population = ", self.population)
        self.population = sorted(self.population, key=lambda a: a['fitness'])
        new_population = [self.population[0]]
        while len(new_population) < self.populationSize:
            male = self.random_weighted_individual()
            female = self.random_weighted_individual(male)
            # 交集下一代
            children = self.mate(male, female)

            # 轻微突变
            new_population.append(self.mutate(children[0]))

            if len(new_population) < self.populationSize:
                new_population.append(self.mutate(children[1]))

        # print 'new :', new_population

        self.population = new_population

    def random_weighted_individual(self, exclude=None):
        """

        :param exclude:
        :return:
        """
        pop = self.population
        if exclude and pop.index(exclude) >= 0:
            pop.remove(exclude)

        rand = random.random()
        lower = 0
        weight = 1.0 / len(pop)
        upper = weight
        pop_len = len(pop)
        for i in range(0, pop_len):
            if (rand > lower) and (rand < upper):
                return pop[i]
            lower = upper
            upper += 2 * weight * float(pop_len-i)/pop_len
        return pop[0]

    def mate(self, male, female):
        """

        :param male:
        :param female:
        :return:
        """
        cutpoint = random.randint(0, len(male['placement_order'])-1)
        gene1 = male['placement_order'][:cutpoint]
        rot1 = male['rotation'][:cutpoint]

        gene2 = female['placement_order'][:cutpoint]
        rot2 = female['rotation'][:cutpoint]

        def contains(gene, shape_id):
            for i in range(0, len(gene)):
                if gene[i][0] == shape_id:
                    return True
            return False

        for i in range(len(female['placement_order'])-1, -1, -1):
            if not contains(gene1, female['placement_order'][i][0]):
                gene1.append(female['placement_order'][i])
                rot1.append(female['rotation'][i])

        for i in range(len(male['placement_order'])-1, -1, -1):
            if not contains(gene2, male['placement_order'][i][0]):
                gene2.append(male['placement_order'][i])
                rot2.append(male['rotation'][i])

        return [{'placement_order': gene1, 'rotation': rot1}, {'placement_order': gene2, 'rotation': rot2}]