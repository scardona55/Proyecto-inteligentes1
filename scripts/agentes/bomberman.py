from mesa import Agent
import random
from collections import deque
import heapq
from .camino import Camino
from .muro_metal import MuroMetal
from .roca_destructible import RocaDestructible
from .salida import Salida
from .globo import Globo  # Asegúrate de tener la clase Globo definida

class Bomberman(Agent):
    def __init__(self, unique_id, model, algoritmo='random', vida=1, beam_width = 3):
        super().__init__(unique_id, model)
        self.stack = [] 
        self.visitados = set()
        self.queue = deque()
        self.priorityqueue = []
        self.costos = {}  # Diccionario para almacenar costos acumulados
        self.algoritmo = algoritmo
        self.visit_count = 0  # Contador de pasos
        self.vida = vida  # Nueva propiedad de vida
        self.beam_width = beam_width
        self.camino = []

    def seleccionar_algoritmo(self):
        if self.algoritmo == 'random':
            self.step2()
        elif self.algoritmo == 'profundidad':
            self.step()
        elif self.algoritmo == 'amplitud':
            self.step3()
        elif self.algoritmo == 'costouniforme':
            self.stepUniformCost()
        elif self.algoritmo == 'Bean':
            self.stepBeamSearch()
        elif self.algoritmo == 'Hill':
            self.stepHillClimbing()
        else:
            raise ValueError("Algoritmo no válido. Elija 'random', 'profundidad', 'amplitud' o 'Bean Search' o 'Hill'.")

    def marcar_casilla(self, posicion):
        """Marca la casilla en la que está Bomberman con el número de paso."""
        agentes_en_casilla = self.model.grid.get_cell_list_contents(posicion)
        for agente in agentes_en_casilla:
            if isinstance(agente, Camino):
                self.visit_count += 1
                agente.mark_as_visited(self.visit_count)
                break

    def recibir_daño(self, cantidad):
        """Reduce la vida de Bomberman y detiene el juego si la vida llega a 0."""
        self.vida -= cantidad
        print(f"Bomberman recibió {cantidad} de daño. Vida restante: {self.vida}")
        if self.vida <= 0:
            print("¡Bomberman ha perdido toda su vida!")
            self.model.running = False
    
    def die(self):
        """Maneja la muerte del Bomberman y finaliza el juego."""
        print("¡Bomberman ha muerto!")
        self.model.running = False

    def interaccion_con_globo(self, posicion):
        """Verifica si hay un globo en la posición actual y reduce la vida."""
        agentes_en_casilla = self.model.grid.get_cell_list_contents(posicion)
        for agente in agentes_en_casilla:
            if isinstance(agente, Globo):
                self.recibir_daño(1)
                return True
        return False

    def step2(self):
        #Movimientos random
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        random.shuffle(movimientos)

        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)
                self.marcar_casilla(nueva_posicion)
                
                if self.interaccion_con_globo(nueva_posicion):
                    # Si hay interacción con el globo, ya se ha reducido la vida
                    if self.vida <= 0:
                        return

                for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                    if isinstance(agente, Salida):
                        print("¡Bomberman ha llegado a la salida!")
                        self.model.running = False
                break

    def step(self):
        #Profundidad
        if self.pos not in self.visitados:
            self.stack.append(self.pos)
            self.visitados.add(self.pos)

        if self.stack:
            posicion_actual = self.stack[-1]
            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            hay_hijos = False

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                if nueva_posicion not in self.visitados:
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        self.model.grid.move_agent(self, nueva_posicion)
                        self.marcar_casilla(nueva_posicion)
                        self.stack.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)
                        hay_hijos = True

                        if self.interaccion_con_globo(nueva_posicion):
                            if self.vida <= 0:
                                return

                        for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                            if isinstance(agente, Salida):
                                print("¡Bomberman ha llegado a la salida!")
                                self.model.running = False
                        break

            if not hay_hijos:
                self.stack.pop()
                if self.stack:
                    posicion_anterior = self.stack[-1]
                    self.model.grid.move_agent(self, posicion_anterior)

    def step3(self):
        #Anchura
        if not self.queue and self.pos not in self.visitados:
            self.queue.append(self.pos)
            self.visitados.add(self.pos)

        if self.queue:
            posicion_actual = self.queue.popleft()
            self.model.grid.move_agent(self, posicion_actual)
            self.marcar_casilla(posicion_actual)

            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                if nueva_posicion not in self.visitados:
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        self.queue.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)

                        if self.interaccion_con_globo(nueva_posicion):
                            if self.vida <= 0:
                                return

                        for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                            if isinstance(agente, Salida):
                                print("¡Bomberman ha llegado a la salida!")
                                self.model.grid.move_agent(self, nueva_posicion)
                                self.marcar_casilla(nueva_posicion)
                                self.model.running = False
                                return
    
    def stepBeamSearch(self):
        """Algoritmo de Beam Search que mueve a Bomberman paso a paso."""
        # Si la cola está vacía, inicializa la búsqueda
        if not self.priorityqueue:
            initial_state = (self.heuristic(self.pos), self.pos)
            heapq.heappush(self.priorityqueue, initial_state)

        # Realiza un único movimiento en cada paso
        if self.priorityqueue:
            # Limitar la búsqueda al ancho del haz
            current_level = []
            for _ in range(min(self.beam_width, len(self.priorityqueue))):
                _, posicion_actual = heapq.heappop(self.priorityqueue)

                # Chequear si Bomberman llegó a la salida
                if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(posicion_actual)):
                    print("¡Bomberman ha llegado a la salida!")
                    self.model.running = False
                    return

                # Añadir la posición actual a visitados y mover Bomberman
                self.visitados.add(posicion_actual)
                self.model.grid.move_agent(self, posicion_actual)
                self.marcar_casilla(posicion_actual)

                # Evaluar interacciones con enemigos
                if self.interaccion_con_globo(posicion_actual):
                    if self.vida <= 0:
                        return

                # Generar posiciones adyacentes y añadirlas al nivel actual de búsqueda
                movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
                for movimiento in movimientos:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    # Verificar si la posición es válida
                    if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                        continue

                    # Evitar obstáculos
                    contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
                    if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                        continue

                    # Calcular heurística y añadir a la cola de prioridad
                    heuristic_score = self.heuristic(nueva_posicion)
                    heapq.heappush(current_level, (heuristic_score, nueva_posicion))

            # Retener solo los mejores nodos según el ancho del haz
            self.priorityqueue = heapq.nsmallest(self.beam_width, current_level)

    def heuristic(self, posicion):
        """Función heurística para estimar la distancia a la salida."""
        salida_pos = self.model.salida_pos
        return abs(posicion[0] - salida_pos[0]) + abs(posicion[1] - salida_pos[1])

    def stepUniformCost(self):
        if not self.priorityqueue:
            heapq.heappush(self.priorityqueue, (0, self.pos))
            self.costos[self.pos] = 0

        if not self.priorityqueue:
            self.model.running = False
            return

        while self.priorityqueue:
            costo_acumulado, posicion_actual = heapq.heappop(self.priorityqueue)

            if posicion_actual in self.visitados:
                continue

            self.visitados.add(posicion_actual)
            self.model.grid.move_agent(self, posicion_actual)
            self.marcar_casilla(posicion_actual)

            if self.interaccion_con_globo(posicion_actual):
                if self.vida <= 0:
                    return

            for agente in self.model.grid.get_cell_list_contents(posicion_actual):
                if isinstance(agente, Salida):
                    print("¡Bomberman ha llegado a la salida!")
                    self.model.running = False
                    return

            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            penalizaciones = [0, 1, 2, 3]

            for i, movimiento in enumerate(movimientos):
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)

                if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                    continue

                nuevo_costo = costo_acumulado + 10 + penalizaciones[i]

                if nueva_posicion not in self.costos or nuevo_costo < self.costos[nueva_posicion]:
                    self.costos[nueva_posicion] = nuevo_costo
                    heapq.heappush(self.priorityqueue, (nuevo_costo, nueva_posicion))

            return

    def stepHillClimbing(self):
        """Algoritmo de Hill Climbing con retroceso que mueve a Bomberman paso a paso."""

        # Marca la posición actual como visitada y mueve a Bomberman
        self.visitados.add(self.pos)
        self.marcar_casilla(self.pos)

        # Verifica si Bomberman ha llegado a la salida
        if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(self.pos)):
            print("¡Bomberman ha llegado a la salida!")
            self.model.running = False
            return

        # Checa interacciones con enemigos
        if self.interaccion_con_globo(self.pos):
            if self.vida <= 0:
                return

        # Genera posiciones adyacentes y calcula sus heurísticas
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        vecinos = []
        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            # Asegúrate de que la posición es válida y no visitada
            if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                continue

            # Verifica que no haya obstáculos en la nueva posición
            contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
            if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                continue

            # Calcular la heurística y añadir la posición a la lista de vecinos
            heuristic_score = self.heuristic(nueva_posicion)
            vecinos.append((heuristic_score, nueva_posicion))

        # Si no hay vecinos, retrocede al último estado (backtracking)
        if not vecinos:
            if self.camino:  # Camino guarda el historial de posiciones visitadas para retroceder
                self.pos = self.camino.pop()  # Retrocede a la posición anterior
                print("Retrocediendo a la posición:", self.pos)
            return

        # Ordena los vecinos por heurística y elige el mejor
        vecinos.sort(key=lambda x: x[0])
        mejor_vecino = vecinos[0]

        # Guarda la posición actual en el historial antes de moverse
        self.camino.append(self.pos)
        nueva_pos = mejor_vecino[1]

        # Verificación antes de mover a Bomberman
        if self.pos != nueva_pos:
            try:
                # Mueve a Bomberman a la nueva posición
                self.model.grid.move_agent(self, nueva_pos)
                self.pos = nueva_pos  # Actualiza la posición de Bomberman
                print(f"Bomberman se ha movido a {self.pos} con una heurística de {mejor_vecino[0]}")
            except ValueError as e:
                print(f"Error moviendo a Bomberman a {nueva_pos}: {e}")
        else:
            print(f"Bomberman ya está en la posición {self.pos}, no es necesario moverlo.")
