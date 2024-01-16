from random import uniform

class Bubble():
    
    def __init__(self, move_sequence=None, move_sequence_length=10, base_color="pink"):
        
        self.base_color = base_color
        self.radius = 5

        # simulation values
        self.x = 0
        self.y = 0
        self.color = self.base_color 
        self.disabled = False
        self.won = False
        self.move_sequence_index = 0

        self.step_size = 10

        self.initialize_move_sequence(move_sequence, move_sequence_length)

    def initialize_move_sequence(self, move_sequence, move_sequence_length):
        if move_sequence is None:
            self.move_sequence = [(uniform(-1, 1), uniform(-1, 1)) for _ in range(move_sequence_length)]
        else:
            self.move_sequence = move_sequence

    def init(self, x, y):
        self.x = x
        self.y = y
        self.color = self.base_color
        self.disabled = False
        self.won = False
        self.move_sequence_index = 0

    def move(self):
        if self.disabled:
            return
        
        if len(self.move_sequence) > self.move_sequence_index:
            dx, dy = self.move_sequence[self.move_sequence_index]
            self.x += dx * self.step_size
            self.y += dy * self.step_size
            self.move_sequence_index += 1
        else:
            self.disabled = True


    def draw(self, canvas):
        canvas.create_circle(self.x, self.y, self.radius, color=self.color)
