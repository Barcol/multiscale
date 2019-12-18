import copy
import random


class EnergyMatrix:
    def __init__(self, type_of_distribution: str, gb_value: int, cell_value: int, gb_board):
        self.type_of_distribution = type_of_distribution
        self.gb_value = gb_value
        self.cell_value = cell_value
        self.gb_board = copy.deepcopy(gb_board)

    def dispose_energy(self):
        for row in range(self.gb_board.get_height()):
            for pixel in range(self.gb_board.get_width()):
                random_percentage = round(random.uniform(0.9, 1.1), 1)
                if self.type_of_distribution == "hetero":
                    if self.gb_board.board[row][pixel].state == 0:
                        self.gb_board.flip_cell_value((pixel, row), round(self.gb_value * random_percentage, 2))
                    else:
                        self.gb_board.flip_cell_value((pixel, row), round(self.cell_value * random_percentage, 2))
                else:
                    self.gb_board.flip_cell_value((pixel, row), round(self.cell_value * random_percentage, 2))
