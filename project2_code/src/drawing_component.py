import itertools
import png


class DrawingComponent:
    def __init__(self, path="temp"):
        self.iterator = 0
        self.path = path

    def create_png(self, board, colors):
        if self.iterator <= 9:
            image_number = "0" + str(self.iterator)
        else:
            image_number = self.iterator
        image = open("{}/picture{}.png".format(self.path, image_number), 'wb')
        matrix = []
        for y in range(board.get_height()):
            row = []
            for x in range(board.get_width()):
                color_tuple = [x for x in colors[board.board[y][x].state]]
                row = row + color_tuple
            matrix.append(list(itertools.chain(row)))
        output = png.Writer(board.get_width(), board.get_height(), greyscale=False)
        output.write(image, matrix)
        image.close()
        self.iterator += 1
