from mesa import Agent, Model
import random
from collections import deque


class Bomberman(Agent):
    def __init__(self, unique_id, model, algoritmo='random'):
        super().__init__(unique_id, model)
        self.stack = [] 
        self.visitados = set()
        self.queue = deque()  
        self.algoritmo = algoritmo
        self.visit_count = 0


        def seleccionar_algoritmo(self):
            # Llama al método correspondiente según el algoritmo seleccionado
            if self.algoritmo == 'random':
                self.step2()  # Llama al método de movimientos aleatorios
            elif self.algoritmo == 'profundidad':
                self.step()  # Llama al método de búsqueda en profundidad
            elif self.algoritmo == 'amplitud':
                self.step3()  # Llama al método de búsqueda en amplitud
            else:
                raise ValueError("Algoritmo no válido. Elija 'random', 'profundidad' o 'amplitud'.")



    def step2(self):
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        random.shuffle(movimientos)

        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            # Verificar si hay un agente en la nueva posición
            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)

                for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                    if isinstance(agente, Salida):
                        print("¡Bomberman ha llegado a la salida!")
                        self.model.running = False
                break

    def step(self): #profundidad
        # 1. Añadir la posición inicial a la pila solo si no ha sido visitada
        if self.pos not in self.visitados:
            self.stack.append(self.pos)
            self.visitados.add(self.pos)

        # 2. Expandir la posición actual si la pila no está vacía
        if self.stack:
            posicion_actual = self.stack[-1]  # Obtiene el último elemento de la pila sin eliminarlo
            movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            hay_hijos = False  # Bandera para verificar si hay movimientos válidos

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                # Evitar posiciones ya visitadas
                if nueva_posicion not in self.visitados:
                    # Verificar si hay un agente bloqueando el movimiento
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        # Mover el agente a la nueva posición
                        self.model.grid.move_agent(self, nueva_posicion)
                        # Añadir la nueva posición a la pila para futuras exploraciones
                        self.stack.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)
                        hay_hijos = True  # Hay al menos un movimiento válido

                        # Verificar si es la salida
                        for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                            if isinstance(agente, Salida):
                                print("¡Bomberman ha llegado a la salida!")
                                self.model.running = False
                        break

            # Si no hay movimientos válidos (hijos) restantes, eliminar la posición de la pila
            if not hay_hijos:
                self.stack.pop()
                # Retroceder a la posición anterior si la pila no está vacía
                if self.stack:
                    posicion_anterior = self.stack[-1]  # La nueva posición actual será la anterior en la pila
                    self.model.grid.move_agent(self, posicion_anterior)  # Mueve al agente a la posición anterior

    def step3(self):  # Breadth-First Search
        # 1. Añadir la posición inicial a la cola solo si no ha sido visitada
        if self.pos not in self.visitados:
            self.queue.append(self.pos)
            self.visitados.add(self.pos)

        # 2. Expandir la posición actual si la cola no está vacía
        if self.queue:
            posicion_actual = self.queue[0]  # Obtiene el primer elemento de la cola sin eliminarlo todavía

            movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]

            for movimiento in movimientos:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                # Evitar posiciones ya visitadas
                if nueva_posicion not in self.visitados:
                    # Verificar si hay un agente bloqueando el movimiento
                    if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                        # Mover el agente a la nueva posición
                        self.model.grid.move_agent(self, nueva_posicion)
                        # Añadir la nueva posición a la cola para futuras exploraciones
                        self.queue.append(nueva_posicion)
                        self.visitados.add(nueva_posicion)

                        # Verificar si es la salida
                        for agente in self.model.grid.get_cell_list_contents(nueva_posicion):
                            if isinstance(agente, Salida):
                                print("¡Bomberman ha llegado a la salida!")
                                self.model.running = False

            # 3. Eliminar la posición actual de la cola después de la expansión
            self.queue.popleft()


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