from mesa import Agent
import random

class Bomberman(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self): 
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  #arriba, abajo, izquierda, derecha
        posibles_movimientos = []

        # Verificar si puedo mover
        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            # Verificar limite del mapa
            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            contenido_celda = self.model.grid.get_cell_list_contents([nueva_posicion])
            if any(isinstance(obj, (MuroMetal, RocaDestructible)) for obj in contenido_celda):
                continue

            # Agregar el movimiento a la lista de movimientos válidos
            posibles_movimientos.append(movimiento)

        # Mov valido, se escoge uno al azar 
        if posibles_movimientos:
            movimiento = random.choice(posibles_movimientos)
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])
            self.model.grid.move_agent(self, nueva_posicion)



#Agentes estaticos
class MuroMetal(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class RocaDestructible(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
