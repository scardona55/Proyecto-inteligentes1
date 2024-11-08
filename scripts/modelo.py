from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agentes import Bomberman, MuroMetal, RocaDestructible, Salida, Camino, Globo
import random

class MiModelo(Model):
    def __init__(self, mapa=None, ancho=10, alto=10, algoritmo='random', cantidad_globos=3):
        super().__init__()
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)
        self.algoritmo = algoritmo
        self.cantidad_globos = cantidad_globos  # Cantidad de enemigos Globo a generar
        self.bomberman = None  # Atributo para almacenar la referencia a Bomberman
        self.salida_pos = None
        

        if mapa is not None:
            self.cargar_mapa(mapa)
        else:
            self.crear_mapa_aleatorio(ancho, alto)

    def crear_mapa_aleatorio(self, ancho, alto):
        # Colocar Bomberman en una posición aleatoria libre
        self.bomberman = Bomberman(self.next_id(), self)  # Almacena la referencia
        self.schedule.add(self.bomberman)
        posicion_bomberman = self._posicion_aleatoria_libre()
        self.grid.place_agent(self.bomberman, posicion_bomberman)
        
        # Asegurar que Bomberman esté sobre un camino
        camino_bomberman = Camino(self.next_id(), self)
        self.schedule.add(camino_bomberman)
        self.grid.place_agent(camino_bomberman, posicion_bomberman)

        # Crear y ubicar la salida en una posición aleatoria libre
        salida = Salida(self.next_id(), self)
        self.schedule.add(salida)
        posicion_salida = self._posicion_aleatoria_libre()
        self.grid.place_agent(salida, posicion_salida)
        self.salida_pos = posicion_salida

        # Asegurar que la salida esté sobre un camino
        camino_salida = Camino(self.next_id(), self)
        self.schedule.add(camino_salida)
        self.grid.place_agent(camino_salida, posicion_salida)

        # Generar enemigos Globo en posiciones aleatorias libres
        for _ in range(self.cantidad_globos):
            globo = Globo(self.next_id(), self)
            self.schedule.add(globo)
            posicion_globo = self._posicion_aleatoria_libre()
            self.grid.place_agent(globo, posicion_globo)
            
            # Asegurar que Globo esté sobre un camino
            camino_globo = Camino(self.next_id(), self)
            self.schedule.add(camino_globo)
            self.grid.place_agent(camino_globo, posicion_globo)

        # Generar otros elementos del mapa aleatoriamente
        for y in range(alto):
            for x in range(ancho):
                if (x, y) in [posicion_bomberman, posicion_salida, *[globo.pos for globo in self.schedule.agents if isinstance(globo, Globo)]]:
                    continue  # Evitar posiciones ya ocupadas por Bomberman, salida o globos
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
                    # Añadir un agente Camino en cada espacio no ocupado por obstáculos
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

                    self.bomberman = Bomberman(self.next_id(), self)  # Almacena la referencia
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
        """Devuelve una posición aleatoria que no esté ocupada por otro agente."""
        posiciones_libres = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height) if self.grid.is_cell_empty((x, y))]
        
        if not posiciones_libres:
            raise ValueError("No hay posiciones libres disponibles en el mapa.")
        
        return random.choice(posiciones_libres)

    def step(self):
        """Ejecuta un paso de la simulación, seleccionando el algoritmo de movimiento para Bomberman y Globo."""
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
                    agente.Aestrella()
            elif isinstance(agente, Globo):
                agente.mover_aleatorio()
            else:
                agente.step()

    def verificar_destruccion_roca(self):
        for agent in self.schedule.agents:
            if isinstance(agent, RocaDestructible) and agent.pos in self.posiciones_afectadas_por_bomba:
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
