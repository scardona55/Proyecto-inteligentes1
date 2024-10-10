from mesa import Agent, Model
import random
from collections import deque
import heapq


class Bomberman(Agent):
    def __init__(self, unique_id, model, algoritmo='random'):
        super().__init__(unique_id, model)
        self.stack = [] 
        self.visitados = set()
        self.queue = deque() 
        self.priorityqueue= []
        self.costos = {}  # Diccionario para almacenar costos acumulados
        self.algoritmo = algoritmo
        self.visit_count = 0  # Contador de pasos

    def seleccionar_algoritmo(self):
        if self.algoritmo == 'random':
            self.step2()
        elif self.algoritmo == 'profundidad':
            self.step()
        elif self.algoritmo == 'amplitud':
            self.step3()
        elif self.algoritmo == 'costouniforme':
            self.stepUniformCost()
        else:
            raise ValueError("Algoritmo no válido. Elija 'random', 'profundidad' o 'amplitud'.")

    def marcar_casilla(self, posicion):
        """Marca la casilla en la que está Bomberman con el número de paso."""
        agentes_en_casilla = self.model.grid.get_cell_list_contents(posicion)
        for agente in agentes_en_casilla:
            if isinstance(agente, Camino):
                self.visit_count += 1
                agente.mark_as_visited(self.visit_count)
                break

    def step2(self):
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        random.shuffle(movimientos)

        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)
                self.marcar_casilla(nueva_posicion)  # Marcar la nueva casilla con el paso actual

                for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                    if isinstance(agente, Salida):
                        print("¡Bomberman ha llegado a la salida!")
                        self.model.running = False
                break

    # Similar para step (profundidad) y step3 (amplitud)
    def step(self):
        if self.pos not in self.visitados:
            self.stack.append(self.pos)
            self.visitados.add(self.pos)

        if self.stack:
            posicion_actual = self.stack[-1]
            movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            hay_hijos = False

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                if nueva_posicion not in self.visitados:
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        self.model.grid.move_agent(self, nueva_posicion)
                        self.marcar_casilla(nueva_posicion)  # Marcar la nueva casilla
                        self.stack.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)
                        hay_hijos = True

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
        if self.pos not in self.visitados:
            self.queue.append(self.pos)
            self.visitados.add(self.pos)

        if self.queue:
            posicion_actual = self.queue[0]

            movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                if nueva_posicion not in self.visitados:
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        self.model.grid.move_agent(self, nueva_posicion)
                        self.marcar_casilla(nueva_posicion)  # Marcar la nueva casilla
                        self.queue.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)

                        for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                            if isinstance(agente, Salida):
                                print("¡Bomberman ha llegado a la salida!")
                                self.model.running = False

            self.queue.popleft()

    def stepUniformCost(self):
        print("Iniciando paso de búsqueda de costo uniforme")
        # Inicializar la cola de prioridad si está vacía
        if not self.priorityqueue:
            # Agregar la posición inicial a la cola de prioridad
            heapq.heappush(self.priorityqueue, (0, self.pos))
            self.costos[self.pos] = 0  # Costo acumulado para la posición inicial

        # Si la cola está vacía después de la inicialización, no hay más nodos para explorar
        if not self.priorityqueue:
            print("No hay más nodos para explorar.")
            self.model.running = False
            return

        # Repetir hasta encontrar un nodo no visitado o hasta que la cola esté vacía
        while self.priorityqueue:
            # Obtener el nodo con el costo acumulado más bajo
            costo_acumulado, posicion_actual = heapq.heappop(self.priorityqueue)

            # Si el nodo ya fue visitado, continuar con el siguiente
            if posicion_actual in self.visitados:
                continue

            # Marcar el nodo como visitado
            self.visitados.add(posicion_actual)

            # Mover el agente a la posición actual
            self.model.grid.move_agent(self, posicion_actual)
            self.marcar_casilla(posicion_actual)
            #self.visit_count += 1  # Incrementar el contador de pasos

            # Verificar si se ha llegado a la salida
            contenido_celda_actual = self.model.grid.get_cell_list_contents(posicion_actual)
            for agente in contenido_celda_actual:
                if isinstance(agente, Salida):
                    print("¡Bomberman ha llegado a la salida!")
                    self.model.running = False
                    return

            # Explorar los vecinos del nodo actual
            movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # Movimientos posibles
            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                # Verificar si la nueva posición está dentro de los límites
                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                # Obtener el contenido de la nueva celda
                contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)

                # Ignorar si hay un obstáculo
                if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                    continue

                nuevo_costo = costo_acumulado + 10  # Asumimos que el costo de cada movimiento es 10

                # Si la nueva posición no ha sido visitada o encontramos un costo menor
                if nueva_posicion not in self.costos or nuevo_costo < self.costos[nueva_posicion]:
                    self.costos[nueva_posicion] = nuevo_costo
                    heapq.heappush(self.priorityqueue, (nuevo_costo, nueva_posicion))

            # Terminar la función después de expandir un nodo
            return

        # Si hemos salido del bucle sin encontrar un nodo no visitado, no hay más nodos para explorar
        print("No hay más nodos para explorar.")
        self.model.running = False


#Agentes estaticos
class MuroMetal(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class RocaDestructible(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Salida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

#ensayo implementacion contador de pasos y marcarlos
class Camino(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.visit_number = None  # Inicialmente ninguna casilla ha sido visitada

    def mark_as_visited(self, number):
        """Marcar la casilla como visitada con un número secuencial."""
        if self.visit_number is None:  # Solo marca si no ha sido visitada
            self.visit_number = number

    def step(self):
        pass  # No realiza acciones por sí mismo