import copy
import random
from typing import Tuple, List

from src.board import Board
from src.coordination_board import CoordinationBoard


class Application:
    def __init__(self, board_dimension: Tuple[int, int], grain_number: int):
        self.board = Board(board_dimension[0], board_dimension[1])
        self.board.prepare_first_board(grain_number)
        self.new_board = Board(board_dimension[0], board_dimension[1])
        self.new_board.prepare_empty_board()

    def iterate(self):
        coordination_board = CoordinationBoard(self.board.width, self.board.height)
        while not coordination_board.is_full():
            random_pick = coordination_board.draw_random_coordinates()
            if (self.board.value_is_in_range(random_pick)
                    and self.cell_not_calculated_this_iteration(random_pick)):
                if self.board.is_cell_mutable(random_pick):
                    neighbours_list = self.board.find_neighbours(random_pick)
                    self.new_board.flip_cell_value(random_pick, self.decide_of_new_cell_state(random_pick,
                                                                                              neighbours_list))
                else:
                    self.new_board.board[random_pick[1]][random_pick[0]] = self.board.board[random_pick[1]][random_pick[0]]
        self.board = copy.deepcopy(self.new_board)
        self.new_board.prepare_empty_board()

    @staticmethod
    def calculate_energy(state: int, neighbours: List):
        energy = 8
        for neighbour in neighbours:
            if neighbour.state == state:
                energy -= 1
        return energy

    def decide_of_new_cell_state(self, cell_coords: Tuple[int, int], neighbours: List):
        x, y = cell_coords
        energy = self.calculate_energy(self.board.board[y][x].state, neighbours)
        new_random_cell_state = neighbours[random.randint(0, len(neighbours) - 1)].state
        new_energy = self.calculate_energy(new_random_cell_state, neighbours)
        if new_energy - energy <= 0:
            return new_random_cell_state
        else:
            return self.decide_of_new_cell_state((x, y), neighbours)

    def cell_not_calculated_this_iteration(self, coordinates: Tuple[int, int]):
        return self.new_board.board[coordinates[1]][coordinates[0]].state == 0

    def change_old_cells_state(self, type_of_substructure: str, number_of_old_grains: int, number_of_grains: int,
                               number_of_new_grains: int, colors):
        if number_of_old_grains > number_of_grains or number_of_old_grains < 1:
            number_of_old_grains = number_of_grains

        for new_grain_color_id in range(1, number_of_old_grains + 1):
            colors[999-new_grain_color_id] = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

        for y in range(self.board.get_height()):
            for x in range(self.board.get_width()):
                if self.board.board[y][x].state in range(1, number_of_old_grains + 1):
                    if type_of_substructure == "substructure":
                        self.board.board[y][x].flip_state(999)
                        self.board.board[y][x].is_mutable = False
                    elif type_of_substructure == "dual_phase":
                        self.board.board[y][x].flip_state(999 - self.board.board[y][x].state)
                        self.board.board[y][x].is_mutable = False
                else:
                    self.board.board[y][x].state = (random.randint(1, number_of_new_grains))
