from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida, Camino
import random

class MiModelo(Model):
    def __init__(self, mapa=None, ancho=10, alto=10, algoritmo='random'):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)
        self.algoritmo = algoritmo 

        if mapa is not None:
            self.cargar_mapa(mapa)
        else:
            self.crear_mapa_aleatorio(ancho, alto)

    def crear_mapa_aleatorio(self, ancho, alto):

        # Colocar Bomberman en una posición aleatoria libre
        bomberman = Bomberman(self.next_id(), self)
        self.schedule.add(bomberman)
        posicion_bomberman = self._posicion_aleatoria_libre()
        self.grid.place_agent(bomberman, posicion_bomberman)
        
        # Asegurar que Bomberman esté sobre un camino
        camino_bomberman = Camino(self.next_id(), self)
        self.schedule.add(camino_bomberman)
        self.grid.place_agent(camino_bomberman, posicion_bomberman)

        # Crear y ubicar la salida en una posición aleatoria libre
        salida = Salida(self.next_id(), self)
        self.schedule.add(salida)
        posicion_salida = self._posicion_aleatoria_libre()
        self.grid.place_agent(salida, posicion_salida)

        # Asegurar que la salida esté sobre un camino
        camino_salida = Camino(self.next_id(), self)
        self.schedule.add(camino_salida)
        self.grid.place_agent(camino_salida, posicion_salida)

        # Ahora generamos los demás elementos del mapa aleatoriamente
        for y in range(alto):
            for x in range(ancho):
                if (x, y) == posicion_bomberman or (x, y) == posicion_salida:
                    # Si es la posición de Bomberman o de la salida, ya colocamos sus caminos
                    continue
                if random.random() < 0.2:  # Porcentaje de obstáculos
                    if random.random() < 0.5:
                        muro_metal = MuroMetal(self.next_id(), self)
                        self.schedule.add(muro_metal)
                        self.grid.place_agent(muro_metal, (x, y))
                    else:
                        roca = RocaDestructible(self.next_id(), self)
                        self.schedule.add(roca)
                        self.grid.place_agent(roca, (x, y))
                else:
                    # Añadimos un agente Camino en cada espacio no ocupado por obstáculos
                    camino = Camino(self.next_id(), self)
                    self.schedule.add(camino)
                    self.grid.place_agent(camino, (x, y))

    def cargar_mapa(self, mapa):
        salida_generada = False
        for y, fila in enumerate(mapa):
            for x, celda in enumerate(fila):
                if celda == 'C':
                    camino = Camino(self.next_id(), self)
                    self.schedule.add(camino)
                    self.grid.place_agent(camino, (x, y))
                elif celda == 'C_b':
                    camino = Camino(self.next_id(), self)
                    self.schedule.add(camino)
                    self.grid.place_agent(camino, (x, y))

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
        posiciones_libres = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height) if self.grid.is_cell_empty((x, y))]
        
        if not posiciones_libres:
            raise ValueError("No hay posiciones libres disponibles en el mapa.")
        
        print(f"Posiciones libres disponibles: {len(posiciones_libres)}")
        
        return random.choice(posiciones_libres)

    def step(self):
        for agente in self.schedule.agents:
            if isinstance(agente, Bomberman):
                if self.algoritmo == 'random':
                    agente.step2() 
                elif self.algoritmo == 'profundidad':
                    agente.step() 
                elif self.algoritmo == 'amplitud':
                    agente.step3() 
                elif self.algoritmo == 'costouniforme':
                    agente.stepUniformCost() 
            else:
                agente.step()