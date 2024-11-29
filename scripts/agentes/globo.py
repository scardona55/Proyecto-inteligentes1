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
        # Movimiento hacia Bomberman
        if self.model.bomberman:
            nueva_pos = self.mover_hacia_bomberman(self.model.bomberman.pos)
            if nueva_pos:
                self.model.grid.move_agent(self, nueva_pos)

        # Verificar colisión con Bomberman
        if self.pos == self.model.bomberman.pos:
            self.inflict_damage()

    def inflict_damage(self):
        """Método para infligir daño a Bomberman."""
        self.model.bomberman.vida -= 1 
        if self.model.bomberman.vida <= 0:
            self.model.bomberman.die()  # Método para manejar la muerte del Bomberman

    def heuristic(self, posicion, objetivo):
        """Función heurística para la distancia al objetivo."""
        return abs(posicion[0] - objetivo[0]) + abs(posicion[1] - objetivo[1])

    def mover_hacia_bomberman(self, bomberman_pos):
        """Decide el mejor movimiento para acercarse a Bomberman."""
        movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        mejor_valor = float("inf")
        mejor_movimiento = None

        for movimiento in movimientos:
            nueva_pos = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])
            if self.model.grid.out_of_bounds(nueva_pos):
                continue

            # Evaluar la heurística solo si la celda no tiene un obstáculo
            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_pos)):
                valor = self.heuristic(nueva_pos, bomberman_pos)
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = nueva_pos

        return mejor_movimiento
