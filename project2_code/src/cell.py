class Cell:
    def __init__(self, state: int, is_mutable: bool = True):
        self.state = state
        self.is_mutable = is_mutable
        self.energy = 0

    def flip_state(self, new_state: int):
        if self.is_mutable:
            self.state = new_state
            if new_state == 999:
                self.is_mutable = False
