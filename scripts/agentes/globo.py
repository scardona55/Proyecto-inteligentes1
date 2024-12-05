import random
from mesa import Agent
from scripts.agentes.muro_metal import MuroMetal
from scripts.agentes.roca_destructible import RocaDestructible
from itertools import product
from .camino import Camino

class Globo(Agent):
    """Clase que representa un enemigo Globo."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health = 1  # Puede tener más atributos, como salud o daño.

    def stepsito(self):
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

    def marcar_casilla(self, posicion):
        """Marca la casilla en la que está Bomberman con el número de paso."""
        agentes_en_casilla = self.model.grid.get_cell_list_contents(posicion)
        for agente in agentes_en_casilla:
            if isinstance(agente, Camino):
                self.visit_count += 1
                agente.mark_as_visited(self.visit_count)
                break

    def mover_hacia_bomberman(self, bomberman_pos):
        """Decide el mejor movimiento para acercarse a Bomberman."""
        movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        mejor_valor = float("inf")
        mejor_movimiento = None

        for movimiento in movimientos:
            nueva_pos = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])
            if self.model.grid.out_of_bounds(nueva_pos):
                continue

            # Verificar si la nueva posición contiene un MuroMetal o una RocaDestructible
            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)
                
                # Verificar interacción con Bomberman (colisión)
                if self.pos == self.model.bomberman.pos:
                    self.inflict_damage()
                
                break
    
    def encontrar_bomberman(self, mapa):
        """Encuentra la posición de Bomberman en el mapa."""
        for f, fila in enumerate(mapa):
            for c, celda in enumerate(fila):
                if celda == 'Bomberman':
                    return (f, c)
        return None  # Retorna None si no se encuentra

    def es_movimiento_valido(self, mapa, pos):
        """Verifica si una posición es válida para moverse (sin obstáculos)."""
        f, c = pos
        return (0 <= f < len(mapa)) and (0 <= c < len(mapa[0])) and (mapa[f][c] not in ['MuroMetal', 'RocaDestructible'])

    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def generar_movimientos_globo(self, mapa, pos_globo, pos_bomberman, posiciones_ocupadas):
        """Genera movimientos válidos para un solo globo, priorizando aquellos que acercan al globo a Bomberman."""
        movimientos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Arriba, Abajo, Izquierda, Derecha

        # Explora todas las direcciones posibles
        for df, dc in direcciones:
            nueva_pos = (pos_globo[0] + df, pos_globo[1] + dc)
            if self.es_movimiento_valido(mapa, nueva_pos):
                # Evita moverse a una posición ya ocupada por otro globo en esta iteración
                if nueva_pos not in posiciones_ocupadas:
                    # Verifica si el movimiento reduce la distancia a Bomberman
                    if self.distancia_manhattan(nueva_pos, pos_bomberman) < self.distancia_manhattan(pos_globo, pos_bomberman):
                        movimientos.append(nueva_pos)

        # Si no hay movimientos que acerquen, permite que se quede en su posición
        if not movimientos:
            movimientos.append(pos_globo)

        return movimientos

    def mejor_movimiento(self, mapa):
        """
        Determina y aplica el mejor movimiento para este globo hacia Bomberman.
        Imprime la posición inicial y la posición final del movimiento.
        """
        pos_bomberman = self.encontrar_bomberman(mapa)
        if pos_bomberman is None:
            print("Bomberman no encontrado en el mapa.")
            return  # Retorna sin hacer nada si no se encuentra Bomberman

        pos_globo = self.pos  # Posición actual del globo

        # Genera posibles movimientos, evitando posiciones ocupadas por otros globos
        posiciones_ocupadas = [g.pos for g in self.model.schedule.agents if isinstance(g, Globo) and g != self]
        movimientos_posibles = self.generar_movimientos_globo(mapa, pos_globo, pos_bomberman, posiciones_ocupadas)

        # Selecciona el primer movimiento válido (puedes cambiar la estrategia si lo deseas)
        if movimientos_posibles:
            nueva_pos = movimientos_posibles[0]  # Puedes implementar lógica más sofisticada
            if nueva_pos != pos_globo:
                # Mover al globo en la grilla
                self.model.grid.move_agent(self, nueva_pos)
                print(f"Globo movido de {pos_globo} a {nueva_pos}")
            else:
                print(f"Globo en {pos_globo} no se mueve")
        else:
            print(f"Globo en {pos_globo} no se mueve")