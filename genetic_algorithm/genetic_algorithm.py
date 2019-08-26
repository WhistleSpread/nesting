# -*- coding: utf-8 -*-
import copy
import random 
from tools import nfp_utls
from settings import ROTATIONS,POPULATION_SIZE, MUTA_RATE


class genetic_algorithm():
    def __init__(self, adam, bin_polygon):
        """
        初始化参数，根据参数生成基因群
        :param adam:
        这里传入的参数adam 就是faces,基本的数据结构是一个list, 而且是有序的list，按照面积从大到小排列
        这个list的每一个元素也是一个list[第几个零件，这个零件的shape], 而shape信息中包含有 points, p_id, area，
        这三个都是以键值对的形式存在，并且point的值是一个list,这个list的每个元素都是一个点{x:, y:}

        :param bin_polygon: 就是offset_bin 画布，板材什么的 这个offset_bin的内容主要包含有：
        {'width': 20000, 'points': [{'y': 0, 'x': 0}, {'y': 1600, 'x': 0}, {'y': 1600, 'x': 20000}, {'y': 0, 'x': 20000}], 
            'p_id': '-1', 'height': 1600})
        """
        self.bin_bounds = bin_polygon['points']
        print(self.bin_bounds)

        self.bin_bounds = {
            'length': bin_polygon['length'],
            'width': bin_polygon['width'],
        }

        self.populationSize = POPULATION_SIZE
        self.mutationRate = MUTA_RATE

        # 这里只选取了bin_bounds width和height， points和p_id都忽略掉了
        self.bin_polygon = bin_polygon

        # 这个表示每个零件能旋转的角度
        # 在这个比赛中，每个零件要么旋转零度，要么旋转180度

       

        # 这里把adam深拷贝到shapes里面,所以这个shapes里面数据结构是一个list, 而且是有序的list，按照面积从大到小排列
        # 这个list的每一个元素也是一个list[第几个零件，这个零件的shape], 而shape信息中包含有 points, p_id, area，
        # 这三个都是以键值对的形式存在，并且point的值是一个list,这个list的每个元素都是一个点{x:, y:}
        shapes = copy.deepcopy(adam)

        angles = [0]*len(shapes)

        # 这里最开始的初始旋转角度随便设置就好了；
        # for shape in shapes:
        #     # 遍历每一个零件，为每一个随机的选择一个旋转角度，这个旋转角度可以是0，可以是180,只要满足在板材里面？
        #     angles.append(self.random_angle(shape))

        # print("angles = ", angles)


        # 初始解，这里的population 应该是一个individual，图形顺序和图形旋转的角度作为基因编码,这个就是一个解，这个解应该是合法的shapes 可是这样一来，这个shapes不一定合法啊？
        self.population = [{'placement': shapes, 'rotation': angles}]
        # print("self.population = ", self.population)

        for i in range(1, self.populationSize):
            # 这里，我设置了populationSize = 3
            # 对种群中每个个体遍历，产生变异, 这里只能是population[0]，因为只有这一个解；
            # print("self.population[i] = ", self.population[0])
            mutant = self.mutate(self.population[0])
            self.population.append(mutant)
        
        # 这里得到的是一个种群，这个种群中有3个individual, 每个individual代表一个顺序，也就是一个解
        # print("self.population = ", self.population)

    def random_angle(self, shape):
        """
        如果全部都是(0, 180)的话，那么这个函数就没有必要了
        随机旋转角度的选取
        :param shape:
        :return:
        """

        """
        angle_list = list()
        # 在配置信息中rotation = 1 表示不能旋转
        for i in range(0, self.config['rotations']):
            angle_list.append(i * (360/self.config['rotations']))

        print("angle_list = ", angle_list)
        # 打乱顺序
        def shuffle_array(data):
            for i in range(len(data)-1, 0, -1):
                j = random.randint(0, i)
                data[i], data[j] = data[j], data[i]
            return data

        angle_list = shuffle_array(angle_list)
        """

        # 感觉这里到angle_list 就直接设置成[0, 180]就好了
        angle_list = [0, 180] 
        # 查看选择后图形是否能放置在里面
        for angle in angle_list:
            # rotate_polygon 就是用来旋转多边形, 传入到是多边形到点到坐标，以及角度angle
            rotate_part = nfp_utls.rotate_polygon(shape[1]['points'], angle)
            # 是否判断旋转出界,没有出界可以返回旋转角度,rotate 只是尝试去转，没有真正改变图形坐标
            if rotate_part['length'] < self.bin_bounds['length'] and rotate_part['width'] < self.bin_bounds['width']:
                return angle
        return 0

    def mutate(self, individual):
        # 这个变异是针对单个个体的变异,针对individual的变异;
        clone = {
            'placement': individual['placement'][:],
            'rotation': individual['rotation'][:]
        }

        for i in range(0, len(clone['placement'])):
            # 在这里是遍历每一个零件
            # 这里是对排列顺序进行变异操作
            if random.random() < 0.01 * self.mutationRate:
                #如果产生的随机数小于设置的变异概率，那么就发生变异
                if i+1 < len(clone['placement']):
                    # 顺序的变异，两两互换位置
                    print("交换了交换了")
                    print("exchange", (i, i+1))
                    clone['placement'][i], clone['placement'][i+1] = clone['placement'][i+1], clone['placement'][i]
            # print("clone = ", clone)

            # 这里是对零件的旋转角度进行变异
            if random.random() < 0.01 * self.mutationRate:
                # 如果产生的随机数要小于设置的变异概率，就随机变换角度
                clone['rotation'][i] = self.random_angle(clone['placement'][i])
        return clone

    def generation(self):
        """
        有了种群，于是开始繁衍
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
        cutpoint = random.randint(0, len(male['placement'])-1)
        gene1 = male['placement'][:cutpoint]
        rot1 = male['rotation'][:cutpoint]

        gene2 = female['placement'][:cutpoint]
        rot2 = female['rotation'][:cutpoint]

        def contains(gene, shape_id):
            for i in range(0, len(gene)):
                if gene[i][0] == shape_id:
                    return True
            return False

        for i in range(len(female['placement'])-1, -1, -1):
            if not contains(gene1, female['placement'][i][0]):
                gene1.append(female['placement'][i])
                rot1.append(female['rotation'][i])

        for i in range(len(male['placement'])-1, -1, -1):
            if not contains(gene2, male['placement'][i][0]):
                gene2.append(male['placement'][i])
                rot2.append(male['rotation'][i])

        return [{'placement': gene1, 'rotation': rot1}, {'placement': gene2, 'rotation': rot2}]