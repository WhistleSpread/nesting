# -*- coding: utf-8 -*-
import copy
import random 
from tools import nfp_utls
from settings import ROTATIONS,POPULATION_SIZE, MUTA_RATE


class genetic_algorithm():

    def __init__(self, segments_sorted_list, bin_info_dic):
        """
        初始化参数，根据参数生成基因群
        :param segments_sorted_list:
        segments_sorted_list 基本的数据结构是一个list, 而且是有序的list，按照面积从大到小排列
        这个list的每一个元素也是一个list[第几个零件，这个零件的shape], 而shape信息中包含有 points, p_id, area，
        这三个都是以键值对的形式存在，并且point的值是一个list,这个list的每个元素都是一个点{x:, y:}

        :param bin_polygon: 就是offset_bin 画布，板材什么的 这个offset_bin的内容主要包含有：
        {'width': 20000, 'points': [{'y': 0, 'x': 0}, {'y': 1600, 'x': 0}, {'y': 1600, 'x': 20000}, {'y': 0, 'x': 20000}], 
            'p_id': '-1', 'height': 1600})
        """
        self.populationSize = POPULATION_SIZE
        self.mutationRate = MUTA_RATE
        self.bin_info_dic = bin_info_dic

        placement_order = copy.deepcopy(segments_sorted_list)
        angles = [0]*len(placement_order)

        # placement
        self.individual = {'placement_order': placement_order, 'rotation': angles}
        self.population = [self.individual]

        for i in range(1, self.populationSize):
            mutated_individual = self.mutate(self.individual)
            self.population.append(mutated_individual)              # 这个种群中有3个individual, 每个individual代表一个顺序，也就是一个解

    def random_angle(self, shape, angle):
        """
        :param shape:  point of one segment
        :param angle:  angle of one segment
        :return: angle or random_angle one of (0, 180)
        """
        if angle == 0:
            r_angle = 180
        else:
            r_angle = 0

        rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], r_angle)
        if rotate_part['length'] < self.bin_info_dic['length'] and rotate_part['width'] < self.bin_info_dic['width']:
            return r_angle
        return angle

    def mutate(self, individual):
        clone = {
            'placement_order': individual['placement_order'][:],
            'rotation': individual['rotation'][:]
        }

        for i in range(0, len(clone['placement_order'])):
            if random.random() < self.mutationRate:              #如果产生的随机数小于设置的变异概率，那么就发生变异
                if i+1 < len(clone['placement_order']):
                    clone['placement_order'][i], clone['placement_order'][i+1] = clone['placement_order'][i+1], clone['placement_order'][i]

            if random.random() < self.mutationRate:             # 如果产生的随机数要小于设置的变异概率，就随机变换角度
                clone['rotation'][i] = self.random_angle(clone['placement_order'][i], clone['rotation'][i])

        return clone

    def generation(self):

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