from mesa import Agent
from .camino import Camino
from .muro_metal import MuroMetal
from .roca_destructible import RocaDestructible

class Bomba(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = 3  # Tiempo hasta explotar

    def step(self):
        self.timer -= 1
        if self.timer <= 0:
            self.explode()

    def explode(self):
        # Obtener vecinos y destruir objetos
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=True)
        for neighbor in neighbors:
            cell_contents = self.model.grid.get_cell_list_contents([neighbor])
            for obj in cell_contents:
                if isinstance(obj, (RocaDestructible, Bomba)):
                    self.model.grid.remove_agent(obj)
                    print(f"Objeto destruido en {neighbor}: {type(obj).__name__}")
                    
                    # Si el objeto es una roca destructible, colocar un camino en su lugar
                    if isinstance(obj, RocaDestructible):
                        camino = Camino(self.model.next_id(), self.model)
                        self.model.schedule.add(camino)
                        self.model.grid.place_agent(camino, neighbor)

        # Remover la bomba después de la explosión
        self.model.grid.remove_agent(self)
        print(f"Bomba explotó en {self.pos}")


