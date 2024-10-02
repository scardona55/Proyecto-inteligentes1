from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida
import random


class MiModelo(Model):
    def __init__(self, ancho, alto, porcentaje_obstaculos=0.2):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)

        # Crear y ubicar al Bomberman
        bomberman = Bomberman(1, self)
        self.schedule.add(bomberman)
        x, y = self._posicion_aleatoria_libre()
        self.grid.place_agent(bomberman, (x, y))

        # Calcular el número máximo de muros y rocas en función del tamaño del mapa y el porcentaje
        num_celdas = ancho * alto
        max_obstaculos = int(num_celdas * porcentaje_obstaculos)

        # Crear y ubicar muros de metal
        for i in range(2, 2 + max_obstaculos // 2):  # mitad de los obstáculos serán muros
            muro_metal = MuroMetal(i, self)
            self.schedule.add(muro_metal)
            x, y = self._posicion_aleatoria_libre()
            self.grid.place_agent(muro_metal, (x, y))

        # Crear y ubicar rocas destructibles
        for i in range(2 + max_obstaculos // 2, 2 + max_obstaculos):  # la otra mitad serán rocas
            roca = RocaDestructible(i, self)
            self.schedule.add(roca)
            x, y = self._posicion_aleatoria_libre()
            self.grid.place_agent(roca, (x, y))

        # Crear y ubicar la salida
        salida = Salida(2 + max_obstaculos, self)  # Corregido: Añadido 'self' como el modelo
        x, y = self._posicion_aleatoria_libre()
        self.grid.place_agent(salida, (x, y))

    def _posicion_aleatoria_libre(self):
        """Devuelve una posición aleatoria que no esté ocupada por otro agente."""
        while True:
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            if self.grid.is_cell_empty((x, y)):
                return x, y

    def step(self):
        self.schedule.step()
