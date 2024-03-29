import datetime
import random
import math
import numpy as np
from PIL import Image
import imageio
from colour import Color
import os
from shutil import copyfile


class Cell:

    def __init__(self, ident, timestamp, state):
        self.id = ident
        self.timestamp = timestamp
        self.state = state

    def find_id(self):
        x, y = self.id.split(':')
        return int(x), int(y)

    def change_state(self, timestamp, state):
        self.timestamp = timestamp
        self.state = state


class CaSpace:

    def __init__(self, first_dim, second_dim, grains, prob=0):
        self.init_time = datetime.datetime.now()
        self.space = np.array(
            [[Cell(str(i) + ':' + str(j), self.init_time, 0) for i in range(second_dim)] for j in range(first_dim)])
        self.grains = grains
        self.generate_grains(self.grains)
        self.empty_cells = (first_dim * second_dim) - self.grains
        self.probability = prob

    def generate_grains(self, grains):
        for cell_num in range(grains):
            random_row = random.randrange(0, self.space.shape[0], 1)
            sample_cell = np.random.choice(self.space[random_row], 1)
            sample_cell = sample_cell[0]
            while sample_cell.state != 0:
                random_row = random.randrange(0, self.space.shape[0], 1)
                sample_cell = np.random.choice(self.space[random_row], 1)
                sample_cell = sample_cell[0]
            sample_cell.change_state(self.init_time, cell_num)

    def get_neighbours(self, cell):
        x, y = cell.find_id()
        length = self.space.shape[1]
        width = self.space.shape[0]
        if length == 0 or width == 0 or x < 0 or x >= length or y < 0 or y >= width:
            return []
        neighs = [(i, j) for i in range(y - 1, y + 2) if 0 <= i < width for j in range(x - 1, x + 2) if 0 <= j < length]
        neighbours = []
        for neigh in neighs:
            neighbours.append(self.space[neigh[0], neigh[1]])
        return neighbours

    def get_nearest_neighbours(self, cell):
        neighs = self.get_neighbours(cell)
        i, j = cell.find_id()
        neighbours = []
        for neigh in neighs:
            x, y = neigh.find_id()
            if abs(x - i) + abs(y - j) <= 1:
                neighbours.append(self.space[y, x])
        return neighbours

    def get_further_neighbours(self, cell):
        neighs = self.get_neighbours(cell)
        i, j = cell.find_id()
        neighbours = []
        for neigh in neighs:
            x, y = neigh.find_id()
            if abs(x - i) + abs(y - j) > 1 or abs(x - i) + abs(y - j) == 0:
                neighbours.append(self.space[y, x])
        return neighbours

    def get_neighbours_square(self, cell, dist):
        x, y = cell.find_id()
        length = self.space.shape[1]
        width = self.space.shape[0]
        if length == 0 or width == 0 or x < 0 or x >= length or y < 0 or y >= width:
            return []
        neighs = [(i, j) for i in range(y - dist, y + dist + 1) if 0 <= i < width for j in range(x - dist, x + dist + 1)
                  if 0 <= j < length]
        neighbours = []
        for neigh in neighs:
            neighbours.append(self.space[neigh[0], neigh[1]])
        return neighbours

    def get_neighbours_round(self, cell, radius):
        x, y = cell.find_id()
        length = self.space.shape[1]
        width = self.space.shape[0]
        if length == 0 or width == 0 or x < 0 or x >= length or y < 0 or y >= width or radius < 2:
            return []
        neighs = [(i, j) for i in range(y - radius, y + radius + 1) if 0 <= i < width for j in
                  range(x - radius, x + radius + 1) if (0 <= j < length)]
        neighbours = []
        for neigh in neighs:
            i, j = neigh
            if round(math.sqrt((j - x) ** 2 + (i - y) ** 2), 4) < round(radius, 4):
                neighbours.append(self.space[neigh[0], neigh[1]])
        return neighbours

    def check_empty_neighbours(self, cell):
        neighbours = self.get_neighbours(cell)
        flag = True
        for neighbour in neighbours:
            if neighbour.state != 0:
                flag = False
        return flag

    def decide_changing(self, cell, neighbours, limit, time):
        grains = [0 for i in range(self.grains)]
        for i in range(1, self.grains + 1):
            for neighbour in neighbours:
                if neighbour.state == i and neighbour.timestamp < time:
                    grains[i] = grains[i] + 1
        if grains == [0 for i in range(self.grains)]:
            return True
        for i in range(self.grains):
            if grains[i] >= limit:
                cell.change_state(time, i)
                self.empty_cells = self.empty_cells - 1
                return False
        return True

    def build_grains(self):
        time = datetime.datetime.now()
        if self.probability == 0:
            for cell in self.space.flat:
                if cell.state != 0:
                    continue
                elif self.check_empty_neighbours(cell):
                    continue
                else:
                    neighbours = self.get_neighbours(cell)
                    grains = [0 for i in range(self.grains)]
                    for i in range(1, self.grains + 1):
                        for neighbour in neighbours:
                            if neighbour.state == i and neighbour.timestamp < time:
                                grains[i] = grains[i] + 1
                    if grains == [0 for i in range(self.grains)]:
                        continue
                    new_grain = 0
                    for i in range(self.grains):
                        if grains[i] >= new_grain:
                            new_grain = i
                    cell.change_state(time, new_grain)
                    self.empty_cells = self.empty_cells - 1
        else:
            for cell in self.space.flat:
                if cell.state != 0:
                    continue
                elif self.check_empty_neighbours(cell):
                    continue
                else:
                    neighbours = self.get_neighbours(cell)
                    if self.decide_changing(cell, neighbours, 5, time):
                        neighbours = self.get_nearest_neighbours(cell)
                        if self.decide_changing(cell, neighbours, 3, time):
                            neighbours = self.get_further_neighbours(cell)
                            if self.decide_changing(cell, neighbours, 3, time):
                                neighbours = self.get_neighbours(cell)
                                grains = [0 for i in range(self.grains)]
                                for i in range(1, self.grains + 1):
                                    for neighbour in neighbours:
                                        if neighbour.state == i and neighbour.timestamp < time:
                                            grains[i] = grains[i] + 1
                                if grains == [0 for i in range(self.grains)]:
                                    continue
                                new_grain = 0
                                for i in range(self.grains):
                                    if grains[i] >= new_grain:
                                        new_grain = i
                                random_number = random.random() * 100
                                if random_number <= self.probability:
                                    cell.change_state(time, new_grain)
                                    self.empty_cells = self.empty_cells - 1
                                else:
                                    continue

    def fill_space(self, name, inclusions):
        inc_type, inc_n, inc_p, inc_r = inclusions
        counter = 0

        if inc_n > 0:
            self.generate_inclusions_randomly(inc_n, inc_r, inc_type)

        self.export_image(str(name) + str(counter))
        while self.empty_cells >= 0:
            self.build_grains()

            print(counter, self.empty_cells)
            counter = counter + 1
            self.export_image(str(name) + str(counter))

        self.export_image(name)
        self.export_txt(name)
        copyfile('./static/temp/' + str(name) + '.png', './static/temp/temp.png')
        out = open('./static/temp/' + str(name) + '.png', 'wb')
        out.write(open('./static/temp/temp.png', 'rb').read())
        out.write('\n'.encode('utf-8'))
        out.write(open('./static/temp/' + str(name) + '.txt', "rb").read())
        out.close()
        os.remove('./static/temp/temp.png')
        self.export_gif(name, counter)

    def export_txt(self, name):
        with open('./static/temp/' + str(name) + '.txt', 'w') as file:
            file.write(str(self.space.shape[1]) + ' ' + str(self.space.shape[0]) + ' ' + str(self.grains - 1) + '\n')
            for cell in self.space.flat:
                x, y = cell.find_id()
                file.write(str(x) + ' ' + str(y) + ' ' + str(cell.state) + ' ' + str(cell.id) + '\n')

    def export_image(self, name):
        red = Color("red")
        blue = Color("blue")
        white = Color("white")
        black = Color("black")
        gold = Color("gold")
        rgb_gold = []
        for part in gold.rgb:
            part = part * 255
            rgb_gold.append(part)
        rgb_black = []
        for part in black.rgb:
            part = part * 255
            rgb_black.append(part)
        rgb_white = []
        for part in white.rgb:
            part = part * 255
            rgb_white.append(part)
        colours = list(red.range_to(blue, int(self.grains)))
        image = np.zeros([self.space.shape[1], self.space.shape[0], 3], dtype=np.uint(8))
        for grain in range(self.grains + 1):
            rgb = []
            for part in colours[grain - 1].rgb:
                part = part * 255
                rgb.append(part)
            for cell in self.space.flat:
                if cell.state == grain:
                    x, y = cell.find_id()
                    image[x, y] = rgb
                if cell.state == 999:
                    x, y = cell.find_id()
                    image[x, y] = rgb_black
                if cell.state == 500:
                    x, y = cell.find_id()
                    image[x, y] = rgb_gold
        img = Image.fromarray(image.astype('uint8'))
        img = img.resize((self.space.shape[1] * 3, self.space.shape[0] * 3))
        img.save('./static/temp/' + str(name) + '.png')

    def export_gif(self, name, counter):
        images = []
        if counter == 0:
            counter = 1
        for i in range(0, counter):
            images.append(imageio.imread('./static/temp/' + str(name) + str(i) + '.png'))
        if not images:
            return 0
        imageio.mimsave('./static/temp/' + str(name) + '.gif', images)
        for i in range(counter):
            os.remove('./static/temp/' + str(name) + str(i) + '.png')

    def import_txt(self, name):
        with open('./static/temp/' + str(name), 'r') as file:
            lines = file.readlines()
            init = lines[0].split(' ')
            self.__init__(int(init[1]), int(init[0]), int(init[2]))
            self.empty_cells = -1
            for line in lines[1:]:
                line = line.split(' ')
                self.space[int(line[1]), int(line[0])].state = int(line[2])

    def check_for_inclusions(self, cell, dist, inc_type):
        if inc_type is True:
            neighbours = self.get_neighbours_round(cell, dist + 1)
        else:
            neighbours = self.get_neighbours_square(cell, dist + 1)
        for cell in neighbours:
            if cell.state == 999:
                return True
        return False

    def grow_cell_inclusion(self, cell, timestamp, dist, inc_type):
        if inc_type is True:
            neighbours = self.get_neighbours_round(cell, dist)
        else:
            neighbours = self.get_neighbours_square(cell, dist)
        for neighbour in neighbours:
            neighbour.change_state(timestamp, 999)
            self.empty_cells = self.empty_cells - 1

    def find_random_cell(self, dist):
        length = self.space.shape[1]
        width = self.space.shape[0]
        sample_cell = np.random.choice(self.space.flat, 1)
        sample_cell = sample_cell[0]
        x, y = sample_cell.find_id()
        while x - dist < 0 and x + dist >= length and y - dist < 0 and y + dist >= width:
            sample_cell = np.random.choice(self.space.flat, 1)
            sample_cell = sample_cell[0]
            x, y = sample_cell.find_id()
        return sample_cell

    def find_cell_for_inclusion(self, dist, inc_type):
        cell = self.find_random_cell(dist)
        while self.check_for_inclusions(cell, dist, inc_type):
            cell = self.find_random_cell(dist)
        return cell

    def generate_inclusions_randomly(self, number, radius, inc_type):
        start, stop = radius
        now = datetime.datetime.now()
        for i in range(number):
            if start == stop:
                rad = start
            else:
                rad = random.choice(range(start, stop + 1))
            inclusion = self.find_cell_for_inclusion(rad, inc_type)
            self.grow_cell_inclusion(inclusion, now, rad, inc_type)

    def find_all_grains(self, grain_num):
        all_grains = []
        for cell in self.space.flat:
            if cell.state == grain_num:
                all_grains.append(cell)
        return all_grains

    def dualphase(self, grain_num, name):
        timestamp = datetime.datetime.now()
        for i in range(grain_num):
            grain = random.choice([j for j in range(self.grains)])
            all_cells = self.find_all_grains(grain)
            for cell in all_cells:
                cell.change_state(timestamp, 500)
        for cell in self.space.flat:
            if cell.state != 500 and cell.state != 999:
                cell.change_state(timestamp, 0)
                self.empty_cells = self.empty_cells + 1
        self.empty_cells = self.empty_cells - 20
        self.grains = self.grains - grain_num
        self.generate_grains(self.grains)
        self.fill_space(name, [0, 0, 0, 0])

    def check_if_cell_on_boundary(self, cell):
        neighbours = self.get_neighbours(cell)
        for neighbour in neighbours:
            if neighbour.state != cell.state and cell.state != 999:
                return True
        return False
