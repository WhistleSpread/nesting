# -*- coding: utf-8 -*-
import copy
import random
from tools import nfp_utls
from settings import POPULATION_SIZE, MUTA_RATE


class genetic_algorithm():

    def __init__(self, segments_sorted_list, container):

        self.populationSize = POPULATION_SIZE
        self.mutationRate = MUTA_RATE
        self.container = container

        placement_order = copy.deepcopy(segments_sorted_list)
        angles = [0] * len(placement_order)

        self.individual = {'placement_order': placement_order, 'rotation': angles}
        self.population = [self.individual]

        for i in range(1, self.populationSize):
            mutated_individual = self.mutate_individual(self.individual)
            self.population.append(mutated_individual)

    def random_angle(self, shape, angle):
        """
        :param shape:  point of one segment
        :param angle:  angle of one segment
        :return: angle or random_angle one of (0, 180)
        """

        def valid_rotate(shape, angle):
            rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
            if rotate_part['x'] < self.container['length'] and rotate_part['y'] < self.container['width']:
                return True
            else:
                return False

        if angle == 0:
            if valid_rotate(shape, 180):
                return 180
            return 0
        else:
            if valid_rotate(shape, 0):
                return 0
            return 180
        # return 0
        ##########################################################################################

        # angle_list = [180, 0]
        # # 查看选择后图形是否能放置在里面
        # for angle in angle_list:
        #     # rotate_polygon 就是用来旋转多边形, 传入到是多边形到点到坐标，以及角度angle
        #     rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
        #     # 是否判断旋转出界,没有出界可以返回旋转角度,rotate 只是尝试去转，没有真正改变图形坐标
        #     if rotate_part['length'] < self.container['length'] and rotate_part['width'] < self.container['width']:
        #         return angle
        # return 0


    ##################################################################################################################

    def mutate_individual(self, individual):
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

        for i in range(2, len(clone['placement_order'])):
            if random.random() < self.mutationRate:
                if i + 1 < len(clone['placement_order']):
                    clone['placement_order'][i], clone['placement_order'][i + 1] = clone['placement_order'][i + 1], \
                                                                                   clone['placement_order'][i]

            if random.random() < self.mutationRate:
                clone['rotation'][i] = self.random_angle(clone['placement_order'][i], clone['rotation'][i])

        return clone

    ##################################################################################################################




    def generation(self):
        """

        :return:
        """
        # 适应度 从大到小排序

        # self.select()
        # self.mutate()

        print("self.population = ", self.population)
        print(len(self.population))
        self.population = sorted(self.population, reverse=True, key=lambda a: a['fitness'])

        # for i in self.population:
        #     print("fitness= ", i['fitness'])
        new_population = self.population[:int(0.25 * len(self.population))]

        # new_population = [self.population[0]]
        while len(new_population) < self.populationSize:
            male = self.random_weighted_individual()
            female = self.random_weighted_individual(male)

            children = self.mate(male, female)

            new_population.append(self.mutate_individual(children[0]))

            if len(new_population) < self.populationSize:
                new_population.append(self.mutate_individual(children[1]))

        self.population = new_population


    def select(self):
        self.population = sorted(self.population, reverse=True, key=lambda a: a['fitness'])
        new_population = self.population[:int(0.5 * len(self.population))]

        for i in range(len(self.population)):
            if i < int(0.25 * len(self.population)):
                continue
            else:
                while i != len(self.population) - 1:
                    index = random.randint(int(0.5 * len(self.population)), len(self.population) - 1)
                    new_population.append(self.population[index])
                    break

        for i in range(len(new_population)):
            print("in select new_pop = ", new_population[i]['fitness'])

        self.population = new_population

    # def cross(self):
    #     rate = random.random()
    #     if rate > pcl and rate < pch:
    #
    #         while len(self.population) < self.populationSize:
    #
    #             male = self.random_weighted_individual()
    #             female = self.random_weighted_individual(male)
    #
    #             children = self.mate(male, female)
    #
    #             new_population.append(self.mutate(children[0]))
    #
    #             if len(new_population) < self.populationSize:
    #                 new_population.append(self.mutate(children[1]))

    def mutate(self):
        for individual in self.population:
            new_population = list()
            rate = random.random()
            if rate < MUTA_RATE:
                clone = {
                    'placement_order': individual['placement_order'][:],
                    'rotation': individual['rotation'][:]
                }

                for i in range(0, len(clone['placement_order'])):
                    if random.random() < self.mutationRate:
                        if i + 1 < len(clone['placement_order']):
                            clone['placement_order'][i], clone['placement_order'][i + 1] = clone['placement_order'][
                                                                                               i + 1], \
                                                                                           clone['placement_order'][i]
                    if random.random() < self.mutationRate:
                        clone['rotation'][i] = self.random_angle(clone['placement_order'][i], clone['rotation'][i])
                new_population.append(clone)
            else:
                new_population.append(individual)




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
            upper += 2 * weight * float(pop_len - i) / pop_len
        return pop[0]

    def mate(self, male, female):
        """

        :param male:
        :param female:
        :return:
        """
        cutpoint = random.randint(0, len(male['placement_order']) - 1)
        gene1 = male['placement_order'][:cutpoint]
        rot1 = male['rotation'][:cutpoint]

        gene2 = female['placement_order'][:cutpoint]
        rot2 = female['rotation'][:cutpoint]

        def contains(gene, shape_id):
            for i in range(0, len(gene)):
                if gene[i][0] == shape_id:
                    return True
            return False

        for i in range(len(female['placement_order']) - 1, -1, -1):
            if not contains(gene1, female['placement_order'][i][0]):
                gene1.append(female['placement_order'][i])
                rot1.append(female['rotation'][i])

        for i in range(len(male['placement_order']) - 1, -1, -1):
            if not contains(gene2, male['placement_order'][i][0]):
                gene2.append(male['placement_order'][i])
                rot2.append(male['rotation'][i])

        return [{'placement_order': gene1, 'rotation': rot1}, {'placement_order': gene2, 'rotation': rot2}]
