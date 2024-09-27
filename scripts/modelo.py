from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible
import random

class MiModelo(Model):
    def __init__(self, ancho, alto):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)

        # Crear y ubicar a Bomberman (agente que se mueve)
        bomberman = Bomberman(1, self)
        self.schedule.add(bomberman)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(bomberman, (x, y))

        # Crear y ubicar un muro de metal (agente que no se mueve)
        muro_metal = MuroMetal(2, self)
        self.schedule.add(muro_metal)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(muro_metal, (x, y))

        # Crear y ubicar una roca destructible (agente que no se mueve)
        roca = RocaDestructible(3, self)
        self.schedule.add(roca)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(roca, (x, y))

    def step(self):
        # Avanzar un paso para todos los agentes
        self.schedule.step()
