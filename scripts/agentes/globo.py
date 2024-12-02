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

            # Verificar si la nueva posición contiene un MuroMetal o una RocaDestructible
            if not any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                self.model.grid.move_agent(self, nueva_posicion)
                
                # Verificar interacción con Bomberman (colisión)
                if self.pos == self.model.bomberman.pos:
                    self.inflict_damage()
                
                break
    
    def mejores_movimientos_globos(self, mapa):
        mejores_movimientos = []
        
        pos_globos = self.encontrar_globos(mapa)
        
        # Generar movimientos posibles para TODOS los globos
        movimientos_posibles = self.generar_movimientos_globos(mapa, pos_globos)
        
        # Si no hay movimientos posibles para ningún globo
        if not movimientos_posibles:
            return [{'globo_original': pos_globo, 'mejor_movimiento': pos_globo} for pos_globo in pos_globos]
        
        for i, pos_globo in enumerate(pos_globos):
            mejor_valor = float('inf')
            mejor_mov = None
            
            # Generar movimientos para este conjunto de movimientos posibles
            for movimientos in movimientos_posibles:
                # Verificar que exista un movimiento para este globo
                if i < len(movimientos):
                    movimiento = movimientos[i]
                    
                    # Simular movimiento
                    nuevo_mapa = [fila[:] for fila in mapa]
                    nuevo_mapa[pos_globo[0]][pos_globo[1]] = 'Camino'
                    nuevo_mapa[movimiento[0]][movimiento[1]] = 'Globo'
                    
                    # Calcular valor usando alfa-beta
                    valor = self.alfa_beta(nuevo_mapa, 4, float('-inf'), float('inf'), True)
                    
                    if valor < mejor_valor:
                        mejor_valor = valor
                        mejor_mov = movimiento
            
            # Agregar resultado a la lista de mejores movimientos
            mejores_movimientos.append({
                'globo_original': pos_globo,
                'mejor_movimiento': mejor_mov if mejor_mov is not None else pos_globo
            })
        print(f"globitos{mejores_movimientos}")
        return mejores_movimientos
    
    def encontrar_bomberman(self, mapa):
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Bomberman':
                    return (f, c)
        return (0, 0)  # Posición por defecto si no se encuentra
    
    def encontrar_globos(self, mapa):
        globos = []
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Globo':
                    globos.append((f, c))
        return globos
    
    def encontrar_salida(self, mapa):
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Salida':
                    return (f, c)
        return (len(mapa)-1, len(mapa[0])-1)  # Posición por defecto si no se encuentra
    
    def es_movimiento_valido(self, mapa, pos):
        f, c = pos
        return (0 <= f < len(mapa) and 
                0 <= c < len(mapa[0]) and 
                mapa[f][c] not in ['MuroMetal', 'RocaDestructible'])
    
    def generar_movimientos_bomberman(self, mapa, pos_actual):
        direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # Izq, Arriba, Der, Abajo
        movimientos_validos = []
        
        for df, dc in direcciones:
            nueva_pos = (pos_actual[0] + df, pos_actual[1] + dc)
            if self.es_movimiento_valido(mapa, nueva_pos):
                movimientos_validos.append(nueva_pos)
        
        return movimientos_validos
    
    def generar_movimientos_globos(self, mapa, pos_globos):
        movimientos_globos_lista = []
        
        for pos_globo in pos_globos:
            movimientos_globo = []
            direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # Izq, Arriba, Der, Abajo
            
            for df, dc in direcciones:
                nueva_pos = (pos_globo[0] + df, pos_globo[1] + dc)
                if (self.es_movimiento_valido(mapa, nueva_pos) and 
                    nueva_pos not in pos_globos):
                    movimientos_globo.append(nueva_pos)
            
            movimientos_globos_lista.append(movimientos_globo)
        
        return self.generar_combinaciones_movimientos(movimientos_globos_lista)
    
    def generar_combinaciones_movimientos(self, movimientos_globos):
        from itertools import product
        return list(product(*movimientos_globos)) if movimientos_globos else []
    
    def distancia_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def calcular_heuristica(self, pos_bomberman, pos_globos, pos_salida):
        if pos_globos is None:
            pos_globos = []
        
        dist_salida = self.distancia_manhattan(pos_bomberman, pos_salida)
        
        # Si no hay globos, solo nos importa la distancia a la salida
        if not pos_globos:
            return -dist_salida  # Minimizar distancia a la salida
        
        dist_globos = min(
            self.distancia_manhattan(pos_bomberman, pos_globo) 
            for pos_globo in pos_globos
        )
        return dist_salida - dist_globos
    
    def alfa_beta(self, mapa, profundidad, alfa, beta, es_max):
        # Copiar el mapa para no modificar el original
        nuevo_mapa = [fila[:] for fila in mapa]
        
        # Encontrar posiciones actuales
        pos_bomberman = self.encontrar_bomberman(mapa)
        pos_globos = self.encontrar_globos(mapa)
        pos_salida = self.encontrar_salida(mapa)
        
        # Condiciones de terminación
        if profundidad == 0:
            return self.calcular_heuristica(pos_bomberman, pos_globos, pos_salida)
        
        # Verificar estado terminal
        if (pos_bomberman in pos_globos or 
            pos_bomberman == pos_salida):
            return float('inf') if pos_bomberman == pos_salida else float('-inf')
        
        if es_max:  # Turno de Bomberman (maximizar)
            valor_max = float('-inf')
            movimientos_bomberman = self.generar_movimientos_bomberman(mapa, pos_bomberman)
            
            for mov_bomberman in movimientos_bomberman:
                # Simular movimiento de Bomberman
                nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Camino'
                nuevo_mapa[mov_bomberman[0]][mov_bomberman[1]] = 'Bomberman'
                
                # Generar movimientos de globos
                movs_globos = self.generar_movimientos_globos(nuevo_mapa, pos_globos)
                
                # Si no hay movimientos de globos, seguir con el actual
                if not movs_globos:
                    movs_globos = [pos_globos]
                
                for movs_globo in movs_globos:
                    # Simular movimiento de globos
                    mapa_simulado = [fila[:] for fila in nuevo_mapa]
                    for (pos_orig, pos_dest) in zip(pos_globos, movs_globo):
                        mapa_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                        mapa_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
                    
                    valor = self.alfa_beta(
                        mapa_simulado, 
                        profundidad - 1, 
                        alfa, 
                        beta, 
                        False
                    )
                    
                    valor_max = max(valor_max, valor)
                    alfa = max(alfa, valor_max)
                    
                    if beta <= alfa:
                        break
                
                if beta <= alfa:
                    break
            
            return valor_max
        
        else:  # Turno de Globos (minimizar)
            valor_min = float('inf')
            movs_globos = self.generar_movimientos_globos(mapa, pos_globos)
            
            # Si no hay movimientos de globos, seguir con el actual
            if not movs_globos:
                movs_globos = [pos_globos]
            
            for movs_globo in movs_globos:
                # Simular movimiento de globos
                mapa_simulado = [fila[:] for fila in mapa]
                for (pos_orig, pos_dest) in zip(pos_globos, movs_globo):
                    mapa_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                    mapa_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
                
                valor = self.alfa_beta(
                    mapa_simulado, 
                    profundidad - 1, 
                    alfa, 
                    beta, 
                    True
                )
                
                valor_min = min(valor_min, valor)
                beta = min(beta, valor_min)
                
                if beta <= alfa:
                    break
            
            return valor_min