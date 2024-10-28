from mesa import Agent

class Camino(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.visit_number = None

    def mark_as_visited(self, number):
        if self.visit_number is None:
            self.visit_number = number

    def step(self):
        pass
