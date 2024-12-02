from mesa import Agent
import random
from collections import deque
import heapq
from .camino import Camino
from .muro_metal import MuroMetal
from .roca_destructible import RocaDestructible
from .salida import Salida
from .globo import Globo  # Asegúrate de tener la clase Globo definida
from heapq import heappop, heappush

class Bomberman(Agent):
    def __init__(self, unique_id, model,algoritmo='random', vida=1, beam_width = 3):
        super().__init__(unique_id, model)
        self.stack = [] 
        self.visitados = set()
        self.queue = deque()
        self.priorityqueue = []
        self.costos = {}  # Diccionario para almacenar costos acumulados
        self.algoritmo = algoritmo
        self.visit_count = 0  # Contador de pasos
        self.vida = vida  # Nueva propiedad de vida
        self.beam_width = 2
        self.camino = []
        self.listica=[]

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
        elif self.algoritmo == 'alfa-beta':
            self.mejor_movimiento()
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

    def encontrar_globos(self, tablero):
        posiciones_globos = []

        # Recorremos cada fila y cada columna del tablero
        for fila_idx, fila in enumerate(tablero):
            for col_idx, celda in enumerate(fila):
                if celda == 'Globo':
                    posiciones_globos.append((fila_idx, col_idx))

        return posiciones_globos


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
        """Algoritmo de Beam Search modificado con retroceso completo al primer nivel, 
        expansión de los n mejores nodos de menor coste, y búsqueda de nodos no visitados en niveles anteriores.
        Prioridad de movimientos: izquierda, arriba, derecha, abajo."""

        # Inicializar el nodo inicial en la cola de prioridad y la estructura de niveles
        if not self.priorityqueue:
            initial_state = (self.heuristic(self.pos), 0, [self.pos])  # [heuristic_score, idx, path]
            heapq.heappush(self.priorityqueue, initial_state)
            self.level_nodes = [[]]  # Estructura para almacenar nodos por nivel

        while self.priorityqueue:
            # Seleccionar los n mejores nodos de menor coste y expandir cada uno de ellos
            current_level = heapq.nsmallest(self.beam_width, self.priorityqueue)
            self.priorityqueue.clear()  # Limpiar la cola para agregar los nuevos nodos generados
            
            for _, _, path in current_level:  # Modificación para ajustar el desempaquetado a tres valores
                posicion_actual = path[-1]

                # Verificar si Bomberman ha alcanzado la salida
                if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(posicion_actual)):
                    print("¡Bomberman ha llegado a la salida!")
                    self.model.running = False
                    return

                # Agregar la posición actual a la lista de visitados y mover Bomberman a esa posición
                self.visitados.add(posicion_actual)
                self.model.grid.move_agent(self, posicion_actual)
                self.marcar_casilla(posicion_actual)  # Visualizar el movimiento

                # Evaluar interacciones con enemigos en la posición actual
                if self.interaccion_con_globo(posicion_actual):
                    if self.vida <= 0:
                        return

                # Generar hijos (movimientos posibles) y agregar a la cola de prioridad
                movimientos = [(-1,0),(0,1),(1,0),(0,-1)]  # Orden de prioridad: izquierda, arriba, derecha, abajo
                next_level = []
                for idx, movimiento in enumerate(movimientos):
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    # Verificar si la posición es válida y no visitada
                    if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                        continue

                    # Evitar obstáculos
                    contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
                    if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                        continue

                    # Calcular heurística ajustada según la prioridad del movimiento
                    new_path = path + [nueva_posicion]
                    heuristic_score = self.heuristic(nueva_posicion)

                    # Agregar el nuevo nodo hijo a la lista `next_level` con el índice para el orden de desempate
                    heapq.heappush(next_level, (heuristic_score, idx, new_path))

                # Agregar los nodos generados al `priorityqueue` para el próximo ciclo
                for heuristic_score, idx, new_path in next_level:
                    heapq.heappush(self.priorityqueue, (heuristic_score, idx, new_path))

            # Seleccionar nuevamente los n mejores nodos de menor coste para el próximo ciclo
            self.priorityqueue = heapq.nsmallest(self.beam_width, self.priorityqueue)
            self.level_nodes.append(next_level)

            # Si no quedan más nodos en el nivel actual, retroceder y buscar nodos no visitados
            if not self.priorityqueue:
                for level in self.level_nodes:
                    unvisited_nodes = [(score, idx, path) for score, idx, path in level if path[-1] not in self.visitados]
                    if unvisited_nodes:
                        self.priorityqueue = heapq.nsmallest(self.beam_width, unvisited_nodes)
                        break
                else:
                    # Si no hay más nodos no visitados, terminar la búsqueda
                    print("No se ha encontrado la salida y no hay más nodos por visitar.")
                    self.model.running = False
                    return

    
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
        """Algoritmo de Hill Climbing por decisiones, mostrando paso a paso el recorrido de Bomberman, avanzando una casilla por cada llamada."""

        # Inicializamos las estructuras solo una vez
        if not hasattr(self, 'niveles'):
            self.niveles = {}  # Diccionario para almacenar nodos de decisiones en cada nivel
            self.visitados = set()  # Conjunto para guardar posiciones visitadas
            self.cola_prioridad = []  # Cola de prioridad para almacenar nodos ordenados por heurística
            self.nivel_inicial = 0  # Nivel inicial con los hijos del nodo de inicio
            heapq.heappush(self.cola_prioridad, (self.heuristic(self.pos), 0, self.pos))  # Añadimos la posición inicial
            self.niveles[self.nivel_inicial] = []  # Lista de decisiones del primer nivel

        # Si la cola de prioridad está vacía, significa que ya no hay más nodos para explorar
        if not self.cola_prioridad:
            print("No hay más nodos por visitar. Terminando búsqueda.")
            self.model.running = False
            return

        # Obtenemos el nodo de menor costo de la cola de prioridad
        _, _, nodo_actual = heapq.heappop(self.cola_prioridad)

        # Si el nodo actual ya fue visitado, continuamos al siguiente paso
        if nodo_actual in self.visitados:
            return

        # Marcamos el nodo actual como visitado y lo expandimos
        self.visitados.add(nodo_actual)
        self.marcar_casilla(nodo_actual)
        self.model.grid.move_agent(self, nodo_actual)  # Mueve visualmente a Bomberman
        self.pos = nodo_actual  # Actualizamos la posición de Bomberman

        print(f"Expandiendo nodo en posición {nodo_actual}")

        # Verificamos si Bomberman ha encontrado la salida
        if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(nodo_actual)):
            print("¡Bomberman ha llegado a la salida!")
            self.model.running = False
            return

        # Genera las posiciones adyacentes (hijos del nodo actual)
        movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Orden de prioridad: izquierda, arriba, derecha, abajo
        hijos = []
        for indice, movimiento in enumerate(movimientos):
            nueva_posicion = (nodo_actual[0] + movimiento[0], nodo_actual[1] + movimiento[1])

            # Validamos si la posición es válida, no visitada y sin obstáculos
            if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                continue
            contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
            if any(isinstance(agente, (MuroMetal, RocaDestructible)) for agente in contenido_celda):
                continue

            # Calculamos la heurística y añadimos el nodo a la lista de hijos y a la cola de prioridad
            heuristic_score = self.heuristic(nueva_posicion)
            hijos.append((heuristic_score, indice, nueva_posicion))  # Añadimos el índice de movimiento como criterio de desempate
            heapq.heappush(self.cola_prioridad, (heuristic_score, indice, nueva_posicion))

        # Si hay hijos, añadimos este conjunto al siguiente nivel
        if hijos:
            hijos.sort(key=lambda x: (x[0], x[1]))  # Ordenamos hijos por costo heurístico y luego por orden de movimiento
            self.niveles[self.nivel_inicial + 1] = hijos  # Guardamos los hijos en el siguiente nivel de decisión
            self.nivel_inicial += 1  # Pasamos al siguiente nivel
        else:
            # Si es un nodo hoja, intentamos regresar al primer nivel y explorar en secuencia cada nivel
            for nivel in range(len(self.niveles)):
                if nivel in self.niveles and self.niveles[nivel]:  # Si hay nodos no visitados en el nivel
                    nodos_no_visitados = [nodo for nodo in self.niveles[nivel] if nodo[2] not in self.visitados]
                    if nodos_no_visitados:
                        # Ordenamos los nodos no visitados por heurística y prioridad
                        nodos_no_visitados.sort(key=lambda x: (x[0], x[1]))
                        for _, _, siguiente_posicion in nodos_no_visitados:
                            if siguiente_posicion not in self.visitados:
                                heapq.heappush(self.cola_prioridad, (self.heuristic(siguiente_posicion), 0, siguiente_posicion))
                                print(f"Retrocediendo a la decisión del nivel {nivel}, nodo {siguiente_posicion}")
                        break
            else:
                # Si ya no hay nodos en ningún nivel
                print("No hay más nodos por visitar. Terminando búsqueda.")
                self.model.running = False
                return

    def Aestrella(self,mapa):
        mapa=self.encontrar_globos(mapa)
        print(mapa)
        # Inicialización de variables si es la primera vez que se llama al método
        if not hasattr(self, 'initialized') or not self.initialized:
            self.came_from = {}     # Diccionario para reconstruir el camino
            self.g_score = {}       # Costo actual desde el inicio hasta cada nodo
            self.f_score = {}       # Costo estimado total hasta la meta
            self.open_set = []      # Lista de nodos por explorar (usada como cola de prioridad)
            self.listica = []       # Lista auxiliar para registrar los nodos visitados
            
            # Inicializar valores para la posición inicial solo una vez
            start = self.pos
            self.g_score[start] = 0
            self.f_score[start] = self.heuristic(start)
            heapq.heappush(self.open_set, (self.f_score[start], 0, start))
            heapq.heappush(self.listica, (self.f_score[start], start))
            
            self.initialized = True  # Marcar que la inicialización está completa

        # Verificar si todavía hay nodos por expandir en open_set
        if self.open_set:
            # Expandir el nodo con el menor f_score
            current = heapq.heappop(self.open_set)[2]

            # Si el nodo actual es la salida, terminamos
            if current == self.model.salida_pos:
                print("¡Bomberman ha llegado a la salida!")
                print(f"Esta es la listica: {self.listica}")
                for listota in self.listica:
                    contador = 0
                    lista_mortal = []
                    for listota2 in self.listica:
                        if listota2[0] == listota[0]:
                            contador += 1
                            lista_mortal.append(listota2[1])
                    print(f"Valor: {listota[0]}, veces: {contador}, lista: {lista_mortal}")
                self.model.running = False
                return

            # Animación solo cuando se expande el nodo `current`
            if current != self.pos:
                self.model.grid.move_agent(self, current)
                self.marcar_casilla(current)

                # Verificar interacción con globo
                if self.interaccion_con_globo(current):
                    if self.vida <= 0:
                        return

            # Definir los movimientos en el orden de preferencia (izquierda, arriba, derecha, abajo)
            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for idx, movimiento in enumerate(movimientos):
                nueva_posicion = (current[0] + movimiento[0], current[1] + movimiento[1])

                # Verificar si la nueva posición es válida (dentro de los límites del mapa)
                if self.model.grid.out_of_bounds(nueva_posicion):
                    continue

                # Verificar si hay obstáculos
                if any(isinstance(agente, (MuroMetal, RocaDestructible)) 
                    for agente in self.model.grid.get_cell_list_contents(nueva_posicion)):
                    continue

                # Calcular el g_score tentativo
                tentative_g_score = self.g_score[current] + 1  # Suponemos un costo de movimiento de 10

                # Si encontramos un mejor camino hacia nueva_posicion
                if nueva_posicion not in self.g_score or tentative_g_score < self.g_score[nueva_posicion]:
                    # Actualizar el camino y los scores
                    self.came_from[nueva_posicion] = current
                    self.g_score[nueva_posicion] = tentative_g_score
                    self.f_score[nueva_posicion] = tentative_g_score + self.heuristic(nueva_posicion)

                    # Agregar a open_set si no está ya
                    if not any(pos == nueva_posicion for score, idx, pos in self.open_set):
                        # Al agregar a `open_set`, se utiliza una tupla (f_score, idx, nueva_posicion)
                        # donde `idx` asegura que se prioricen los movimientos en el orden deseado
                        heapq.heappush(self.open_set, (self.f_score[nueva_posicion], idx, nueva_posicion))
                        heapq.heappush(self.listica, (self.f_score[nueva_posicion], nueva_posicion))

        # Si `open_set` está vacío y no encontramos la salida
        else:
            print("No se encontró un camino hacia la salida")
            self.model.running = False

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
    
    def mejor_movimiento(self, mapa):
        mejor_valor = float('-inf')
        mejor_mov = None
        
        pos_bomberman = self.encontrar_bomberman(mapa)
        movimientos_posibles = self.generar_movimientos_bomberman(mapa, pos_bomberman)
        
        # Si no hay movimientos posibles, quedarse en la posición actual
        if not movimientos_posibles:
            return pos_bomberman
        
        for movimiento in movimientos_posibles:
            # Simular movimiento
            nuevo_mapa = [fila[:] for fila in mapa]
            nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Camino'
            nuevo_mapa[movimiento[0]][movimiento[1]] = 'Bomberman'
            
            valor = self.alfa_beta(nuevo_mapa, 4, float('-inf'), float('inf'), False)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_mov = movimiento
        print(f"la mejor pos bomb es: {mejor_mov}")
        self.model.grid.move_agent(self, mejor_mov)
        self.marcar_casilla(mejor_mov)
        
        return mejor_mov if mejor_mov is not None else pos_bomberman