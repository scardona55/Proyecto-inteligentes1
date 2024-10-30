import random
from mesa import Agent
from scripts.agentes.muro_metal import MuroMetal
from scripts.agentes.roca_destructible import RocaDestructible

class Globo(Agent):
    """Clase que representa un enemigo Globo."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health = 1  # Puede tener más atributos, como salud o daño.

    def step(self):
        """Define el comportamiento del Globo en cada paso del modelo."""
        self.mover_aleatorio()  # Llama al movimiento aleatorio en cada paso

        # Verificar colisión con Bomberman
        if self.pos == self.model.bomberman.pos:  # Asumiendo que model tiene una referencia al Bomberman
            self.inflict_damage()

    def inflict_damage(self):
        """Método para infligir daño a Bomberman."""
        self.model.bomberman.vida -= 1  # Suponiendo que Bomberman tiene un atributo de salud
        if self.model.bomberman.vida <= 0:
            self.model.bomberman.die()  # Método para manejar la muerte del Bomberman

    def mover_aleatorio(self):
        movimientos = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        random.shuffle(movimientos)

        for movimiento in movimientos:
            nueva_posicion = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

            # Verificar si la nueva posición está fuera de los límites del grid
            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            # Verificar si la nueva posición contiene un MuroMetal o una RocaDestructible
            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)
                
                # Verificar interacción con Bomberman (colisión)
                if self.pos == self.model.bomberman.pos:
                    self.inflict_damage()
                
                break
