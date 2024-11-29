from mesa import Agent

class RocaDestructible(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_destructible = True  # Indica que puede ser destruida
