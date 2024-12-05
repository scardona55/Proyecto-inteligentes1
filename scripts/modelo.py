from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida, Camino, Globo
import random

class MiModelo(Model):
    def __init__(self, mapa=None, ancho=10, alto=10, algoritmo='random', cantidad_globos=3):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = SimultaneousActivation(self)
        self.algoritmo = algoritmo
        self.cantidad_globos = cantidad_globos
        self.bomberman = None
        self.salida_pos = None
        self.alto=alto
        self.ancho=ancho

        if mapa is not None:
            self.cargar_mapa(mapa)
        else:
            self.crear_mapa_aleatorio(ancho, alto)

    def recorrer_mundo_grilla(self):
        """Recorre todas las celdas de la grilla de abajo hacia arriba y devuelve una matriz con el contenido de cada celda."""

        # Crear una lista para almacenar las filas del mapa (esto es una matriz)
        mundo = [[None] * self.grid.width for _ in range(self.grid.height)]

        # Recorrer la grilla de abajo hacia arriba
        for y in range(self.grid.height - 1, -1, -1):  # Recorrer filas de abajo hacia arriba
            for x in range(self.grid.width):  # Recorrer columnas (ancho de la grilla)
                cell = self.grid.get_cell_list_contents((x, y))  # Obtener los agentes en la celda (x, y)
                
                # Determinar el tipo de agente y asignar el valor correspondiente en la matriz
                if any(isinstance(obj, Bomberman) for obj in cell):
                    mundo[y][x] = 'Bomberman'  # Asignar 'Bomberman' en la posición de la matriz
                elif any(isinstance(obj, Globo) for obj in cell):
                    mundo[y][x] = 'Globo'  # Asignar 'Globo'
                elif any(isinstance(obj, Salida) for obj in cell):
                    mundo[y][x] = 'Salida'  # Asignar 'Salida'
                elif any(isinstance(obj, MuroMetal) for obj in cell):
                    mundo[y][x] = 'MuroMetal'  # Asignar 'MuroMetal'
                elif any(isinstance(obj, RocaDestructible) for obj in cell):
                    mundo[y][x] = 'RocaDestructible'  # Asignar 'RocaDestructible'
                elif any(isinstance(obj, Camino) for obj in cell):
                    mundo[y][x] = 'Camino'  # Asignar 'Camino'
                else:
                    mundo[y][x] = 'Vacío'  # Asignar 'Vacío' si no hay nada en la celda

        # Invertir el orden de las filas de la matriz
        mundo.reverse()  # Esto invierte el orden de las filas

        # Retornar la matriz final
        return mundo



    def crear_mapa_aleatorio(self, ancho, alto):
        # Colocar Bomberman en una posición aleatoria libre
        self.bomberman = Bomberman(self.next_id(), self)
        self.schedule.add(self.bomberman)
        posicion_bomberman = self._posicion_aleatoria_libre()
        self.grid.place_agent(self.bomberman, posicion_bomberman)

        camino_bomberman = Camino(self.next_id(), self)
        self.schedule.add(camino_bomberman)
        self.grid.place_agent(camino_bomberman, posicion_bomberman)

        # Crear y ubicar la salida
        salida = Salida(self.next_id(), self)
        self.schedule.add(salida)
        posicion_salida = self._posicion_aleatoria_libre()
        self.grid.place_agent(salida, posicion_salida)
        self.salida_pos = posicion_salida

        camino_salida = Camino(self.next_id(), self)
        self.schedule.add(camino_salida)
        self.grid.place_agent(camino_salida, posicion_salida)

        # Generar enemigos Globo
        for _ in range(self.cantidad_globos):
            globo = Globo(self.next_id(), self)
            self.schedule.add(globo)
            posicion_globo = self._posicion_aleatoria_libre()
            self.grid.place_agent(globo, posicion_globo)

            camino_globo = Camino(self.next_id(), self)
            self.schedule.add(camino_globo)
            self.grid.place_agent(camino_globo, posicion_globo)

        # Generar obstáculos y caminos
        for y in range(alto):
            for x in range(ancho):
                if not self.grid.is_cell_empty((x, y)):
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

                    self.bomberman = Bomberman(self.next_id(), self)
                    self.schedule.add(self.bomberman)
                    self.grid.place_agent(self.bomberman, (x, y))
                elif celda == 'C_G':
                    camino = Camino(self.next_id(), self)
                    self.schedule.add(camino)
                    self.grid.place_agent(camino, (x, y))

                    globo = Globo(self.next_id(), self)
                    self.schedule.add(globo)
                    self.grid.place_agent(globo, (x, y))

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
                    self.salida_pos = (x, y)
                    salida_generada = True

    def _posicion_aleatoria_libre(self):
        posiciones_libres = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height) if self.grid.is_cell_empty((x, y))]
        if not posiciones_libres:
            raise ValueError("No hay posiciones libres disponibles en el mapa.")
        return random.choice(posiciones_libres)
    

    def step(self):
        """Realiza un paso en el juego, actualizando todos los agentes."""
        # Obtener el mapa actual antes de mover los agentes
        mapa = self.recorrer_mundo_grilla()
        print("\nEstado actual del mapa:")
        for fila in mapa:
            print(fila)

        # Iterar sobre todos los agentes y ejecutar sus pasos correspondientes
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
                elif self.algoritmo == 'Bean':
                    agente.stepBeamSearch()
                elif self.algoritmo == 'Hill':
                    agente.stepHillClimbing()
                elif self.algoritmo == 'A*':
                    agente.Aestrella(mapa)
                elif self.algoritmo == 'alfa-beta':
                    agente.mejor_movimiento(mapa)

            if isinstance(agente, Globo):
                agente.mejor_movimiento(mapa)  # Manejar movimiento individual y impresión dentro de la clase Globo

        # Después de mover todos los agentes, obtener el mapa actualizado
        mapa_actualizado = self.recorrer_mundo_grilla()
        print("\nEstado del mapa después del paso:")
        for fila in mapa_actualizado:
            print(fila)
