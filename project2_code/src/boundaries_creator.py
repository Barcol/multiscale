import glob

from src.board import Board
from src.drawing_component import DrawingComponent
from PIL import Image


class BoundariesCreator:
    def __init__(self, png_path):
        self.png_path = png_path
        self.board = Board(10, 10)
        self.new_board = Board(10, 10)
        self.colors = {}
        self.actual_color_key = 0

    def decode_image(self):
        img = Image.open(self.png_path)
        width, height = img.size
        self.board = Board(width, height)
        self.new_board = Board(width, height)
        self.board.prepare_empty_board()
        self.prepare_colors_hash(img, height, width)
        for row in range(height):
            for pixel in range(width):
                pixel_color_values = img.getpixel((row, pixel))
                for color_key, color_value in self.colors.items():
                    if color_value == [x for x in pixel_color_values]:
                        self.actual_color_key = color_key
                self.board.board[pixel][row].state = self.actual_color_key

    def prepare_colors_hash(self, image, height, width):
        color_index = 0
        for row in range(height):
            for pixel in range(width):
                pixel_color_values = image.getpixel((row, pixel))
                if [x for x in pixel_color_values] not in self.colors.values():
                    self.colors[color_index] = [x for x in pixel_color_values]
                    color_index += 1

    def calculate_boundaries(self):
        self.new_board.prepare_empty_board()
        for row in range(self.board.get_height()):
            for pixel in range(self.board.get_width()):
                neighbours_list = self.board.find_all_neighbours((row, pixel))
                self.new_board.flip_cell_value((row, pixel), self.decide_if_boundary((row, pixel), neighbours_list))

    def decide_if_boundary(self, coordinates, neighbours):
        x, y = coordinates
        other_states_counter = 0
        for neighbour in neighbours:
            if neighbour.state != self.board.board[y][x].state:
                other_states_counter += 1
        if other_states_counter > 1:
            return 0
        return 1

    def create_image(self):
        db = DrawingComponent(path="boundaries")
        db.create_png(self.new_board, {0: [1, 1, 1],
                                       1: [250, 250, 250]})

