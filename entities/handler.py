class Handler:
    def __init__(self):
        self.list = []

    def update_all(self):
        for entity in self.list:
            entity.update()

    def draw_all(self, surface, camera):
        for entity in self.list:
            entity.draw(surface, camera)
