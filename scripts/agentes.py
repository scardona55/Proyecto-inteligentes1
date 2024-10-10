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
        self.visit_count = 0  # Contador de pasos

    def seleccionar_algoritmo(self):
        if self.algoritmo == 'random':
            self.step2()
        elif self.algoritmo == 'profundidad':
            self.step()
        elif self.algoritmo == 'amplitud':
            self.step3()
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