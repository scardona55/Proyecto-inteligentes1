from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida
import random

class MiModelo(Model):
    def __init__(self, mapa=None, ancho=10, alto=10):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)

        if mapa is not None:
            self.cargar_mapa(mapa)
        else:
            # Si no se proporciona un mapa, se crea uno aleatoriamente
            self.crear_mapa_aleatorio(ancho, alto)

    def crear_mapa_aleatorio(self, ancho, alto):
        for y in range(alto):
            for x in range(ancho):
                if random.random() < 0.2:  # Porcentaje de obstáculos
                    if random.random() < 0.5:
                        muro_metal = MuroMetal(self.next_id(), self)
                        self.schedule.add(muro_metal)
                        self.grid.place_agent(muro_metal, (x, y))
                    else:
                        roca = RocaDestructible(self.next_id(), self)
                        self.schedule.add(roca)
                        self.grid.place_agent(roca, (x, y))

        # Colocar Bomberman en una posición aleatoria
        bomberman = Bomberman(self.next_id(), self)
        self.schedule.add(bomberman)
        self.grid.place_agent(bomberman, self._posicion_aleatoria_libre())

        # Crear y ubicar la salida en una posición aleatoria
        salida = Salida(self.next_id(), self)
        self.grid.place_agent(salida, self._posicion_aleatoria_libre())

    def cargar_mapa(self, mapa):
        salida_generada = False
        for y, fila in enumerate(mapa):
            for x, celda in enumerate(fila):
                if celda == 'C':
                    continue
                elif celda == 'C_b':
                    bomberman = Bomberman(self.next_id(), self)
                    self.schedule.add(bomberman)
                    self.grid.place_agent(bomberman, (x, y))
                elif celda == 'M':
                    muro_metal = MuroMetal(self.next_id(), self)
                    self.schedule.add(muro_metal)
                    self.grid.place_agent(muro_metal, (x, y))
                elif celda == 'R':
                    roca = RocaDestructible(self.next_id(), self)
                    self.schedule.add(roca)
                    self.grid.place_agent(roca, (x, y))
                elif celda == 'S' and not salida_generada:
                    salida = Salida(self.next_id(), self)
                    self.schedule.add(salida)
                    self.grid.place_agent(salida, (x, y))
                    salida_generada = True

    def _posicion_aleatoria_libre(self):
        """Devuelve una posición aleatoria que no esté ocupada por otro agente."""
        while True:
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            if self.grid.is_cell_empty((x, y)):
                return (x, y)

    def step(self):
        self.schedule.step()
