import glob
import random

from PIL import Image
from tqdm import tqdm

from src.board import Board
from src.coordination_board import CoordinationBoard
from src.drawing_component import DrawingComponent


class Nucleons:
    def __init__(self, main_board, nucleon_adding, gb_board=None):
        self.nucleon_board = Board(10, 10)
        self.main_board = main_board
        self.bg_board = gb_board
        self.drawer = DrawingComponent(path="nucleons")
        self.taken_list = []
        self.colors = {0: [254, 254, 254]}
        self.nucleon_number = 0
        self.last_frame = sorted(glob.glob('temp/*'))[-1]
        if nucleon_adding == "beginning":
            self.increment = 0
        elif nucleon_adding == "constant":
            self.increment = 1
        elif nucleon_adding == "growing":
            self.increment = 2
        self.y = self.main_board.get_height()
        self.x = self.main_board.get_width()
        self.nucleon_board = Board(self.y, self.x)
        self.nucleon_board.prepare_empty_board()
        self.nucleon_coordination_board = CoordinationBoard(self.main_board.width, self.main_board.height)

    def put_nucleons(self, nucleon_number):
        self.nucleon_number = nucleon_number
        if self.bg_board is None:
            for nucleon_index in range(nucleon_number):
                random_pick = (random.randint(1, self.x), random.randint(1, self.y))
                self.nucleon_board.flip_cell_value(random_pick, 666 - nucleon_index)
                self.colors[666 - nucleon_index] = [random.randint(1, 255), 10, 10]
        else:
            for nucleon_index in range(nucleon_number):
                coordination_board = CoordinationBoard(self.main_board.width, self.main_board.height)
                if not coordination_board.is_full():
                    random_pick = coordination_board.draw_random_coordinates()
                    while self.bg_board.board[random_pick[1]][random_pick[0]].state != 0:
                        random_pick = coordination_board.draw_random_coordinates()
                    self.nucleon_board.flip_cell_value(random_pick, 666 - nucleon_index)
                    self.colors[666 - nucleon_index] = [random.randint(1, 255), 10, 10]

    def set_looping(self, iterations):
        self.bg_board = None
        for _ in tqdm(range(int(iterations))):
            self.iterate()
            self.put_actual_nucleon_state_on_last_frame()
            self.drawer.create_png(self.nucleon_board, self.colors)
            if self.increment == 0:
                pass
            elif self.increment == 1:
                self.put_nucleons(self.nucleon_number)
            elif self.increment == 2:
                self.nucleon_number += self.nucleon_number
                self.put_nucleons(self.nucleon_number)

    def put_actual_nucleon_state_on_last_frame(self):
        old_pictures = len(glob.glob('temp/*'))
        img = Image.open(self.last_frame)
        width, height = img.size
        for y in range(height):
            for x in range(width):
                if self.nucleon_board.board[y][x].state != 0:
                    img.putpixel((x, y), tuple(self.colors[self.nucleon_board.board[y][x].state]))
        img.save("temp/picture{}.png".format(old_pictures), "PNG")

    def iterate(self):
        coordination_board = CoordinationBoard(self.main_board.width, self.main_board.height)
        self.taken_list = []
        while not coordination_board.is_full():
            random_pick = coordination_board.draw_random_coordinates()
            if self.nucleon_board.value_is_in_range(random_pick) and self.cell_not_calculated_this_iteration(
                    random_pick):
                if self.nucleon_board.board[random_pick[1]][random_pick[0]].state == 0:
                    neighbours_list = self.nucleon_board.find_neighbours(random_pick)
                    self.nucleon_board.flip_cell_value(random_pick, self.decide_of_new_cell_state(random_pick,
                                                                                                  neighbours_list))

    def cell_not_calculated_this_iteration(self, coords):
        if coords in self.taken_list:
            return False
        else:
            return True

    def decide_of_new_cell_state(self, cell_coords, neighbours):
        x, y = cell_coords
        for neighbour in neighbours:
            if neighbour.state != 0:
                return neighbour.state
        energy = self.calculate_energy(self.nucleon_board.board[y][x].state, neighbours)
        new_random_cell_state = neighbours[random.randint(0, len(neighbours) - 1)].state
        new_energy = self.calculate_energy(new_random_cell_state, neighbours)
        if new_energy - energy >= 0:
            return new_random_cell_state
        else:
            return self.decide_of_new_cell_state((x, y), neighbours)

    @staticmethod
    def calculate_energy(state: int, neighbours):
        energy = 8
        for neighbour in neighbours:
            if neighbour.state == state:
                energy -= 1
        return energy
