from mesa import Agent
import random
from collections import deque
import heapq
from .camino import Camino
from .muro_metal import MuroMetal
from .roca_destructible import RocaDestructible
from .salida import Salida
from .globo import Globo  # Asegúrate de tener la clase Globo definida
from collections import defaultdict
from heapq import heappop, heappush

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
        elif self.algoritmo == 'A*':
            self.Aestrella()
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
        # Si la cola de prioridad está vacía, inicializa la búsqueda
        if not self.priorityqueue:
            initial_state = ([self.pos], self.heuristic(self.pos))  # [path, costo]
            heapq.heappush(self.priorityqueue, initial_state)

        # Realiza un único movimiento en cada paso
        if self.priorityqueue:
            # Limitar la búsqueda al ancho del haz
            current_level = []
            for _ in range(min(self.beam_width, len(self.priorityqueue))):
                path, _ = heapq.heappop(self.priorityqueue)
                posicion_actual = path[-1]  # Última posición en el camino

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

                    # Calcular heurística y añadir el nuevo camino extendido
                    new_path = path + [nueva_posicion]
                    heuristic_score = self.heuristic(nueva_posicion)
                    heapq.heappush(current_level, (new_path, heuristic_score))

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
        """Algoritmo de Hill Climbing por niveles y marcas. Explora cada rama por niveles y regresa al nivel principal si no encuentra solución."""

        # Inicializamos la estructura de niveles y marcas
        if not hasattr(self, 'niveles'):
            self.niveles = {0: [self.pos]}  # Nivel 0 es el nodo origen
            self.marca_actual = 1  # Primera marca
            self.nivel_actual = 0  # Comienza en el nivel 0
            self.visitados = set()  # Conjunto para guardar posiciones visitadas

        # Marcamos la posición actual como visitada
        self.visitados.add(self.pos)
        self.marcar_casilla(self.pos)

        # Verificamos si Bomberman ha encontrado la salida
        if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(self.pos)):
            print("¡Bomberman ha llegado a la salida!")
            self.model.running = False
            return

        # Genera las posiciones adyacentes y calcula sus heurísticas
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        vecinos = []
        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            # Aseguramos que la posición es válida, no visitada, y no tiene obstáculos
            if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                continue
            contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
            if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                continue

            # Calcular la heurística y añadir la posición a la lista de vecinos
            heuristic_score = self.heuristic(nueva_posicion)
            vecinos.append((heuristic_score, nueva_posicion))

        # Si hay vecinos, marcamos el siguiente nivel y agregamos los vecinos al nuevo nivel
        if vecinos:
            vecinos.sort(key=lambda x: x[0])  # Ordena los vecinos por la heurística
            mejor_vecino = vecinos[0]
            
            # Actualizamos el nivel actual y la marca actual
            self.nivel_actual += 1
            self.niveles[self.nivel_actual] = [vecino[1] for vecino in vecinos]
            self.marca_actual += 1

            # Avanza a la mejor opción en este nivel
            nueva_pos = mejor_vecino[1]
            self.model.grid.move_agent(self, nueva_pos)
            self.pos = nueva_pos
            print(f"Bomberman se ha movido a {self.pos} en el nivel {self.nivel_actual} con marca {self.marca_actual}")

        # Si no hay vecinos válidos, retrocedemos al nivel principal anterior
        else:
            while self.nivel_actual > 0:
                self.nivel_actual -= 1
                if self.niveles[self.nivel_actual]:
                    # Recuperamos la posición de la marca anterior no explorada
                    siguiente_posicion = self.niveles[self.nivel_actual].pop(0)
                    if siguiente_posicion != self.pos:
                        try:
                            self.model.grid.move_agent(self, siguiente_posicion)
                            self.pos = siguiente_posicion
                            print(f"Retrocediendo a la posición {self.pos} en el nivel {self.nivel_actual}")
                            break
                        except ValueError as e:
                            print(f"Error al mover a Bomberman a {siguiente_posicion}: {e}")
            else:
                print("No hay más posiciones válidas para explorar.")


    def Aestrella(self):
        # A* Search
        if not hasattr(self, 'came_from'):
            self.came_from = {}  # Diccionario para reconstruir el camino
            self.g_score = {}    # Costo actual desde el inicio hasta n
            self.f_score = {}    # Costo estimado total
            self.open_set = []   # Lista de nodos por explorar
            self.contador_nums = []  # Lista para almacenar todos los valores de tentative_g_score
            
            # Inicializar valores para la posición inicial
            start = self.pos
            self.g_score[start] = 0
            self.f_score[start] = self.heuristic(start)
            heapq.heappush(self.open_set, (self.f_score[start], start))
            
        if self.open_set:
            # Obtener el nodo con menor f_score
            current = heapq.heappop(self.open_set)[1]
            
            # Si llegamos a la salida
            if current == self.model.salida_pos:
                print("¡Bomberman ha llegado a la salida!")
                self.model.running = False
                
                # Contar la frecuencia de cada valor en contador_nums
                frequency_count = defaultdict(int)
                for value in self.contador_nums:
                    frequency_count[value] += 1
                
                # Imprimir las frecuencias
                for value, count in frequency_count.items():
                    print(f"{value} - {count}")
                return
                
            # Explorar vecinos
            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for movimiento in movimientos:
                nueva_posicion = (current[0] + movimiento[0], current[1] + movimiento[1])
                
                # Verificar si la posición es válida
                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue
                    
                # Verificar si hay obstáculos
                if any(isinstance(agente, (MuroMetal, RocaDestructible)) 
                    for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                    continue
                    
                # Calcular nuevo g_score
                tentative_g_score = self.g_score[current] + 10  # Costo de movimiento = 10
                self.contador_nums.append(tentative_g_score)  # Guardar el valor en la lista
                
                # Si encontramos un mejor camino
                if nueva_posicion not in self.g_score or tentative_g_score < self.g_score[nueva_posicion]:
                    # Actualizar el camino y los scores
                    self.came_from[nueva_posicion] = current
                    self.g_score[nueva_posicion] = tentative_g_score
                    self.f_score[nueva_posicion] = tentative_g_score + self.heuristic(nueva_posicion)
                    
                    # Agregar a open_set si no está ya
                    if not any(pos == nueva_posicion for score, pos in self.open_set):
                        heapq.heappush(self.open_set, (self.f_score[nueva_posicion], nueva_posicion))
                    
            # Mover al agente
            if current != self.pos:
                self.model.grid.move_agent(self, current)
                self.marcar_casilla(current)
                
                # Verificar interacción con globo
                if self.interaccion_con_globo(current):
                    if self.vida <= 0:
                        return
                    
        # Si no hay camino posible
        else:
            print("No se encontró un camino hacia la salida")
            self.model.running = False