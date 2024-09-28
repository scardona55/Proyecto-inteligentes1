from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida
import random

class MiModelo(Model):
    def __init__(self, ancho, alto):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)

        #Crear y ubicar al bomberman
        bomberman = Bomberman(1, self)
        self.schedule.add(bomberman)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(bomberman, (x, y))

        # Crear y ubicar un muro de metal
        muro_metal = MuroMetal(2, self)
        self.schedule.add(muro_metal)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(muro_metal, (x, y))

        # Crear y ubicar una roca destructible
        roca = RocaDestructible(3, self)
        self.schedule.add(roca)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(roca, (x, y))

        # Crear y ubicar la salida
        salida = Salida(4, self)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.grid.place_agent(salida, (x, y))

    def step(self):
        self.schedule.step()
