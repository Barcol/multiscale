import random


class CoordinationBoard:
    def __init__(self, width, height):
        self.board = [[(x, y) for x in range(width)] for y in range(height)]
        self.values_already_used = [[0 for _ in range(width)] for _ in range(height)]

    def draw_random_coordinates(self):
        if len(self.board) != 0:
            self.get_rid_of_empty_rows()
            row = random.choice(self.board)
            x, y = row.pop(random.randint(0, len(row) - 1))
            self.values_already_used[y][x] = "X"
            return x, y
        else:
            return 10, 10

    def get_rid_of_empty_rows(self):
        for row_index, row in enumerate(self.board):
            if len(row) == 0:
                self.board.pop(row_index)

    def is_full(self):
        for row in self.values_already_used:
            for value in row:
                if value == 0:
                    return False
        return True
