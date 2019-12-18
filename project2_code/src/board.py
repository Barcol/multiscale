import random
from typing import Tuple

from src.cell import Cell


class Board:
    def __init__(self, width: int, height: int):
        self.board = []
        self.width = width
        self.height = height

    def prepare_first_board(self, grain_number: int):
        self.board = [[Cell(random.randint(1, grain_number)) for _ in range(self.width)] for _ in range(self.height)]

    def prepare_empty_board(self):
        self.board = [[Cell(0) for _ in range(self.width)] for _ in range(self.height)]

    def value_is_in_range(self, coordinates: Tuple[int, int]):
        return coordinates[0] < self.width and coordinates[1] < self.height

    def translate_coordinates(self, coords: Tuple[int, int]):
        x, y = coords
        if x == self.width:
            x = 0
        if y == self.height:
            y = 0
        return x, y

    def is_cell_mutable(self, coordinates: Tuple[int, int]):
        x, y = self.translate_coordinates((coordinates[0], coordinates[1]))
        return self.board[y][x].is_mutable

    def find_all_neighbours(self, coordinates: Tuple[int, int]):
        neighbours = []
        for x_inc in range(-1, 2):
            for y_inc in range(-1, 2):
                if x_inc == 0 and y_inc == 0:
                    pass
                x, y = self.translate_coordinates((coordinates[0] + x_inc, coordinates[1] + y_inc))
                neighbours.append(self.board[y][x])
        return neighbours

    def find_neighbours(self, coordinates: Tuple[int, int]):
        neighbours = []
        for x_inc in range(-1, 2):
            for y_inc in range(-1, 2):
                if x_inc == 0 and y_inc == 0:
                    pass
                x, y = self.translate_coordinates((coordinates[0] + x_inc, coordinates[1] + y_inc))
                if self.board[y][x].is_mutable:
                    neighbours.append(self.board[y][x])
        return neighbours

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def flip_cell_value(self, coords: Tuple[int, int], new_state: int):
        x, y = self.translate_coordinates(coords)
        self.board[y][x].flip_state(new_state)

    def not_full_yet(self):
        for x in range(self.width):
            for y in range(self.height):
                return self.board[x][y].state == 0
        return False

    def __str__(self):
        return "\n".join([str([self.board[y][x].state for x in range(self.width)]) for y in range(self.height)])

    def __len__(self):
        return self.width * self.height
