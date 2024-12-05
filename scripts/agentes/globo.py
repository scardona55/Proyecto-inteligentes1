import random
from mesa import Agent
from scripts.agentes.muro_metal import MuroMetal
from scripts.agentes.roca_destructible import RocaDestructible
from itertools import product



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
    
    @classmethod
    def encontrar_bomberman(cls, mapa):
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Bomberman':
                    return (f, c)
        return None

    @classmethod
    def encontrar_globos(cls, mapa):
        globos = []
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Globo':
                    globos.append((f, c))
        return globos

    @classmethod
    def encontrar_salida(cls, mapa):
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Salida':
                    return (f, c)
        return None

    @classmethod
    def es_movimiento_valido(cls, mapa, pos):
        f, c = pos
        return (0 <= f < len(mapa) and 
                0 <= c < len(mapa[0]) and 
                mapa[f][c] not in ['MuroMetal', 'RocaDestructible', 'Globo'])

    @classmethod
    def generar_movimientos_globos(cls, mapa, pos_globos):
        movimientos_globos_lista = []
        
        for pos_globo in pos_globos:
            movimientos_globo = []
            direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # Izquierda, Arriba, Derecha, Abajo
            
            for df, dc in direcciones:
                nueva_pos = (pos_globo[0] + df, pos_globo[1] + dc)
                if cls.es_movimiento_valido(mapa, nueva_pos):
                    movimientos_globo.append(nueva_pos)
            
            # Si un globo no tiene movimientos válidos, puede quedarse en su posición actual
            if not movimientos_globo:
                movimientos_globo.append(pos_globo)
            
            movimientos_globos_lista.append(movimientos_globo)
        
        return movimientos_globos_lista

    @classmethod
    def generar_combinaciones_movimientos(cls, movimientos_globos):
        combinaciones = list(product(*movimientos_globos)) if movimientos_globos else []
        
        # Filtrar combinaciones donde dos globos intentan moverse a la misma posición
        combinaciones_unicas = [
            combinacion for combinacion in combinaciones 
            if len(combinacion) == len(set(combinacion))
        ]
        
        return combinaciones_unicas

    @classmethod
    def distancia_manhattan(cls, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @classmethod
    def calcular_heuristica(cls, pos_bomberman, pos_globos, pos_salida):
        if pos_salida is None:
            return -float('inf')
        dist_salida = cls.distancia_manhattan(pos_bomberman, pos_salida)
        if pos_bomberman == pos_salida:
            return float('inf')
        if pos_bomberman in pos_globos:
            return -float('inf')
        if not pos_globos:
            return -dist_salida
        dist_min_globo = min(cls.distancia_manhattan(pos_bomberman, globo) for globo in pos_globos)
        FACTOR_SEGURIDAD = 10
        if dist_min_globo <= 2:
            penalizacion = FACTOR_SEGURIDAD * (3 - dist_min_globo)**2
            return -dist_salida - penalizacion
        return -dist_salida

    @classmethod
    def alfa_beta(cls, mapa, profundidad, alfa, beta, es_max):
        pos_bomberman = cls.encontrar_bomberman(mapa)
        pos_globos = cls.encontrar_globos(mapa)
        pos_salida = cls.encontrar_salida(mapa)

            # Debugging: Verificar si Bomberman fue encontrado
        if pos_bomberman is None:
            print("DEBUG: Bomberman no fue encontrado en el mapa_simulado.")
        else:
            print(f"DEBUG: Bomberman encontrado en {pos_bomberman}.")
        if profundidad == 0:
            return cls.calcular_heuristica(pos_bomberman, pos_globos, pos_salida)
        if pos_bomberman == pos_salida:
            return float('inf')
        if pos_bomberman in pos_globos:
            return -float('inf')
        if es_max:
            valor_max = -float('inf')
            movimientos_bomberman = cls.generar_movimientos_bomberman(mapa, pos_bomberman)
            for mov_bomberman in movimientos_bomberman:
                mapa_simulado = [fila[:] for fila in mapa]
                mapa_simulado[pos_bomberman[0]][pos_bomberman[1]] = 'Camino'
                mapa_simulado[mov_bomberman[0]][mov_bomberman[1]] = 'Bomberman'
                if mov_bomberman == pos_salida:
                    valor = float('inf')
                    valor_max = max(valor_max, valor)
                    alfa = max(alfa, valor_max)
                    if beta <= alfa:
                        break
                    continue
                movs_globos = cls.generar_movimientos_globos(mapa_simulado, pos_globos)
                combinaciones_globos = cls.generar_combinaciones_movimientos(movs_globos)
                if not combinaciones_globos:
                    combinaciones_globos = [tuple(pos_globos)]
                for combinacion_globos in combinaciones_globos:
                    mapa_globos_simulado = [fila[:] for fila in mapa_simulado]
                    for pos_orig, pos_dest in zip(pos_globos, combinacion_globos):
                        mapa_globos_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                        mapa_globos_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
                    if mov_bomberman in combinacion_globos:
                        valor = -float('inf')
                    else:
                        valor = cls.alfa_beta(mapa_globos_simulado, profundidad - 1, alfa, beta, False)
                    valor_max = max(valor_max, valor)
                    alfa = max(alfa, valor_max)
                    if beta <= alfa:
                        break
                if beta <= alfa:
                    break
            return valor_max
        else:
            valor_min = float('inf')
            movs_globos = cls.generar_movimientos_globos(mapa, pos_globos)
            combinaciones_globos = cls.generar_combinaciones_movimientos(movs_globos)
            if not combinaciones_globos:
                combinaciones_globos = [tuple(pos_globos)]
            for combinacion_globos in combinaciones_globos:
                mapa_globos_simulado = [fila[:] for fila in mapa]
                for pos_orig, pos_dest in zip(pos_globos, combinacion_globos):
                    mapa_globos_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                    mapa_globos_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
                if pos_bomberman in combinacion_globos:
                    valor = -float('inf')
                else:
                    valor = cls.alfa_beta(mapa_globos_simulado, profundidad - 1, alfa, beta, True)
                valor_min = min(valor_min, valor)
                beta = min(beta, valor_min)
                if beta <= alfa:
                    break
            return valor_min

    @classmethod
    def generar_movimientos_bomberman(cls, mapa, pos_bomberman):
        movimientos = []
        direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        for df, dc in direcciones:
            nueva_pos = (pos_bomberman[0] + df, pos_bomberman[1] + dc)
            if cls.es_movimiento_valido(mapa, nueva_pos):
                movimientos.append(nueva_pos)
        return movimientos

    @classmethod
    def mejores_movimientos_globos(cls, mapa):
        mejores_movimientos = []
        pos_globos = cls.encontrar_globos(mapa)
        pos_bomberman = cls.encontrar_bomberman(mapa)
        pos_salida = cls.encontrar_salida(mapa)
        if pos_bomberman is None or pos_salida is None:
            print("Error: Bomberman o Salida no están en el mapa.")
            return [{'globo_original': pos_globo, 'mejor_movimiento': pos_globo} for pos_globo in pos_globos]
        movimientos_posibles = cls.generar_movimientos_globos(mapa, pos_globos)
        if not movimientos_posibles:
            return [{'globo_original': pos_globo, 'mejor_movimiento': pos_globo} for pos_globo in pos_globos]
        combinaciones_globos = cls.generar_combinaciones_movimientos(movimientos_posibles)
        if not combinaciones_globos:
            combinaciones_globos = [tuple(pos_globos)]
        mejor_valor = float('inf')
        mejor_combinacion = None
        for combinacion in combinaciones_globos:
            mapa_simulado = [fila[:] for fila in mapa]
            for pos_orig, pos_dest in zip(pos_globos, combinacion):
                mapa_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                mapa_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
            valor = cls.alfa_beta(mapa_simulado, 4, float('-inf'), float('inf'), True)
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_combinacion = combinacion
        for pos_globo, mejor_mov in zip(pos_globos, mejor_combinacion):
            mejores_movimientos.append({
                'globo_original': pos_globo,
                'mejor_movimiento': mejor_mov
            })
        return mejores_movimientos

    @classmethod
    def mover_globos(cls, mejores_movimientos, grid, mapa, altura_matriz):
        for movimiento in mejores_movimientos:
            globo_original = movimiento['globo_original']
            mejor_movimiento = movimiento['mejor_movimiento']
            # Mesa usa (x, y), mapa usa (fila, columna) = (y, x)
            agentes_en_celda = grid.get_cell_list_contents((globo_original[1], globo_original[0]))
            globo = next((agente for agente in agentes_en_celda if isinstance(agente, Globo)), None)
            if globo:
                # Aplicar la inversión de coordenadas
                if mejor_movimiento:
                    mejor_mov_adaptado = (
                        mejor_movimiento[1],
                        altura_matriz - 1 - mejor_movimiento[0]
                    )
                else:
                    mejor_mov_adaptado = (
                        globo_original[1],
                        altura_matriz - 1 - globo_original[0]
                    )

                # Verificar si el movimiento es válido (no sobrescribe a Bomberman)
                if mapa[mejor_movimiento[0]][mejor_movimiento[1]] != 'Bomberman':
                    # Mover al globo en el grid de Mesa
                    grid.move_agent(globo, (mejor_mov_adaptado[0], mejor_mov_adaptado[1]))
                    # Actualizar el mapa simulado
                    mapa[globo_original[0]][globo_original[1]] = 'Camino'
                    mapa[mejor_movimiento[0]][mejor_movimiento[1]] = 'Globo'
                    print(f"Globo {globo.unique_id} movido de {globo_original} a {mejor_movimiento}")
                else:
                    print(f"Globo {globo.unique_id} intenta moverse a la posición de Bomberman en {mejor_movimiento}, movimiento cancelado.")
            else:
                print(f"No se encontró el globo en la posición {globo_original}")