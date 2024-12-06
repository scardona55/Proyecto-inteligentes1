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
from .bomba import Bomba
import heapq
from itertools import product


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
        self.priorityqueue = []  # Usado para Beam Search
        self.beam_width = 2
        self.camino = []
        self.listica=[]
        self.bombs = []  # Lista de bombas colocadas
        self.bomb_placed = False  # Indica si se colocó una bomba
        self.podados=0
        
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
        """Beam Search con colocación de bombas y destrucción de rocas destructibles."""
        if not self.priorityqueue:
            # Inicializar el nodo inicial
            initial_state = (self.heuristic(self.pos), [self.pos])
            heapq.heappush(self.priorityqueue, initial_state)

        if self.priorityqueue:
            _, path = heapq.heappop(self.priorityqueue)
            posicion_actual = path[-1]

            # Mover Bomberman a la posición actual
            self.model.grid.move_agent(self, posicion_actual)
            self.visitados.add(posicion_actual)
            self.marcar_casilla(posicion_actual)

            # Verificar si Bomberman llegó a la salida
            if any(isinstance(agente, Salida) for agente in self.model.grid.get_cell_list_contents(posicion_actual)):
                print("¡Bomberman ha llegado a la salida!")
                self.model.running = False
                return

            # Detectar contenido de celdas adyacentes
            movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for dx, dy in movimientos:
                nueva_posicion = (posicion_actual[0] + dx, posicion_actual[1] + dy)
                if self.model.grid.out_of_bounds(nueva_posicion) or nueva_posicion in self.visitados:
                    continue

                contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
                if any(isinstance(agente, RocaDestructible) for agente in contenido_celda):
                    if not self.bomb_placed:
                        self.colocar_bomba(posicion_actual)
                        self.bomb_placed = True
                        print(f"Bomba colocada en {posicion_actual}. Apuntando a {nueva_posicion}.")
                        return

                if any(isinstance(agente, MuroMetal) for agente in contenido_celda):
                    continue

                # Agregar nuevas posiciones a explorar
                nuevo_camino = path + [nueva_posicion]
                heuristic_score = self.heuristic(nueva_posicion)
                heapq.heappush(self.priorityqueue, (heuristic_score, nuevo_camino))

            # Mantener los n mejores nodos en la cola
            self.priorityqueue = heapq.nsmallest(self.beam_width, self.priorityqueue)

        if not self.priorityqueue:
            print("No se encontró una salida. Fin del juego.")
            self.model.running = False


    def destruir_roca(self, posicion):
        """Destruye una roca destructible en la posición indicada."""
        contenido_celda = self.model.grid.get_cell_list_contents(posicion)
        roca = next((agente for agente in contenido_celda if isinstance(agente, RocaDestructible)), None)
        if roca:
            self.model.grid.remove_agent(roca)
            print(f"Roca destruida en {posicion}.")

    def find_safe_positions(self):
        """Encuentra posiciones seguras alejadas de bombas."""
        movimientos = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        safe_positions = []
        for dx, dy in movimientos:
            nueva_posicion = (self.pos[0] + dx, self.pos[1] + dy)
            if self.model.grid.out_of_bounds(nueva_posicion):
                continue

            contenido_celda = self.model.grid.get_cell_list_contents(nueva_posicion)
            if not any(isinstance(agente, Bomba) for agente in contenido_celda):
                safe_positions.append(nueva_posicion)

        return safe_positions

    def heuristic(self, posicion):
        """Función heurística para estimar la distancia a la salida."""
        salida_pos = self.model.salida_pos
        return abs(posicion[0] - salida_pos[0]) + abs(posicion[1] - salida_pos[1])
    
    def colocar_bomba(self, posicion):
        """Coloca una bomba en la posición actual."""
        bomba = Bomba(self.model.next_id(), self.model, posicion)
        self.model.grid.place_agent(bomba, posicion)
        self.bombs.append(bomba)
        self.model.schedule.add(bomba)
        self.bomb_placed = True
    

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
        """
        Recorre la matriz `mapa` y retorna la posición (f, c) donde se encuentra 'Bomberman' o 'BombermanSalida'.
        Si no lo encuentra, retorna None.
        """
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] in ['Bomberman', 'BombermanSalida']:
                    return (f, c)
        return None  # Retorna None en lugar de una cadena

    def encontrar_globos(self, mapa):
        """
        Retorna una lista con las posiciones (f, c) de todas las casillas donde hay 'Globo'.
        """
        globos = []
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] == 'Globo':
                    globos.append((f, c))
        return globos

    def encontrar_salida(self, mapa):
        """
        Retorna la posición (f, c) donde se encuentra 'Salida' o 'BombermanSalida'.
        Si no se encuentra, retorna None.
        """
        for f in range(len(mapa)):
            for c in range(len(mapa[0])):
                if mapa[f][c] in ['Salida', 'BombermanSalida']:
                    return (f, c)
        return None  # Retorna None en lugar de una cadena

    def es_movimiento_valido(self, mapa, pos):
        """
        Verifica si un movimiento es válido, es decir:
        - La posición (f, c) está dentro de los límites del mapa.
        - La casilla no es 'MuroMetal' ni 'RocaDestructible'.
        
        Retorna True si es válido, False en caso contrario.
        """
        f, c = pos
        return (0 <= f < len(mapa) and 
                0 <= c < len(mapa[0]) and 
                mapa[f][c] not in ['MuroMetal', 'RocaDestructible'])

    def generar_movimientos_bomberman(self, mapa, pos_actual):
        """
        Genera todos los movimientos válidos que Bomberman puede realizar desde `pos_actual`.
        El orden de exploración es: izquierda, arriba, derecha, abajo.
        
        Direcciones:
        - Izquierda: (0, -1)
        - Arriba:    (-1, 0)
        - Derecha:   (0, 1)
        - Abajo:     (1, 0)
        """
        direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        movimientos_validos = []
        
        for df, dc in direcciones:
            nueva_pos = (pos_actual[0] + df, pos_actual[1] + dc)
            if self.es_movimiento_valido(mapa, nueva_pos):
                movimientos_validos.append(nueva_pos)
        
        return movimientos_validos

    def generar_movimientos_globos(self, mapa, pos_globos):
        """
        Genera todas las combinaciones posibles de movimientos para TODOS los globos.
        Cada globo puede moverse a una posición válida en las direcciones: izquierda, 
        arriba, derecha, o abajo. Si no hay movimientos válidos para un globo, se genera 
        un mensaje indicando que no se encontraron movimientos válidos, y ese globo queda excluido.

        Se generan todas las combinaciones de movimientos (producto cartesiano),
        y se filtran aquellas donde dos globos intenten ocupar la misma posición.
        
        Además, se evita que los globos se muevan a la posición de 'Bomberman' o 'Salida'.
        
        Retorna una lista de tuplas, donde cada tupla representa una combinación
        completa de movimiento, siendo cada elemento de la tupla la posición final
        de un globo. Si no es posible mover un globo, no se incluye en las combinaciones.
        """
        direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        movimientos_globos_por_globo = []

        # Encontrar la posición de Bomberman para evitar que los globos se muevan a esa posición
        pos_bomberman = self.encontrar_bomberman(mapa)
        pos_salida = self.encontrar_salida(mapa)
        
        # Para cada globo, generar sus movimientos posibles
        for pos_globo in pos_globos:
            movimientos_globo = []
            for df, dc in direcciones:
                nueva_pos = (pos_globo[0] + df, pos_globo[1] + dc)
                # Agregar movimiento si es válido y no es la posición de Bomberman ni la Salida
                if self.es_movimiento_valido(mapa, nueva_pos) and nueva_pos != pos_bomberman and nueva_pos != pos_salida:
                    movimientos_globo.append(nueva_pos)
            
            # Si un globo no tiene movimientos válidos, imprimir mensaje y excluirlo
            if not movimientos_globo:
                print(f"Para el globo en la posición {pos_globo} no se encontraron movimientos válidos.")
                continue  # Excluye este globo de la lista de combinaciones
            
            movimientos_globos_por_globo.append(movimientos_globo)
        
        # Generar todas las combinaciones con product
        combinaciones = list(product(*movimientos_globos_por_globo)) if movimientos_globos_por_globo else []

        # Filtrar combinaciones donde haya solapamiento de globos (dos globos en la misma posición)
        combinaciones_unicas = [
            combinacion for combinacion in combinaciones
            if len(combinacion) == len(set(combinacion))  # Asegura que todas las posiciones son únicas
        ]

        return combinaciones_unicas

    def distancia_manhattan(self, pos1, pos2):
        """
        Calcula la distancia Manhattan entre dos posiciones pos1 y pos2.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def calcular_heuristica(self, pos_bomberman, pos_globos, pos_salida):
        """
        Heurística que devuelve valores mayores cuanto más cerca está Bomberman de la salida.
        Además, penaliza si hay globos muy cerca (≤ 2 casillas).

        - Cuanto más cerca a la salida, mayor la heurística.
        - Si hay globos a 2 o menos casillas, se resta una penalización.
        """
        # Asegurar que pos_globos sea una lista
        if pos_globos is None:
            pos_globos = []
        elif isinstance(pos_globos, tuple):
            pos_globos = [pos_globos]
        
        # Verificar que la salida esté presente
        if pos_salida is None:
            print("Error en calcular_heuristica: No se encuentra la salida en el mapa.")
            return float('-inf')  # O manejarlo según tu lógica de juego
        
        dist_salida = self.distancia_manhattan(pos_bomberman, pos_salida)
        
        # Base de la heurística:
        # Iniciamos con un valor alto (ej: 1000) y restamos la distancia a la salida.
        # Así, mientras menor sea la distancia, mayor la heurística.
        heur = 1000 - dist_salida
        
        # Penalizar si hay globos a cierta distancia
        for globo in pos_globos:
            dist_globo = self.distancia_manhattan(pos_bomberman, globo)
            if dist_globo == 0:
                heur -= 1000  # Colisión fatal
            elif dist_globo == 1:
                heur -= 500  # Muy peligroso
            elif dist_globo == 2:
                heur -= 200  # Peligroso
        
        return heur

    def alfa_beta(self, mapa, profundidad, alfa, beta, es_max):
        """
        Implementación del algoritmo alfa-beta para tomar la mejor decisión.
        
        - `mapa`: estado actual del juego (matriz con strings que indican lo que hay en cada casilla).
        - `profundidad`: la profundidad actual del árbol de búsqueda.
        - `alfa`, `beta`: valores del algoritmo alfa-beta.
        - `es_max`: booleano que indica si el turno actual es de Bomberman (max) o de los globos (min).
        
        El algoritmo:
        1. Identifica el estado actual (posiciones de Bomberman, globos, salida).
        2. Comprueba si es un estado terminal:
           - Bomberman muere (-inf).
           - Bomberman llega a la salida (+inf).
           - Si profundidad = 0, retorna la heurística.
        3. Si es el turno de Bomberman (max):
           - Genera todos los movimientos de Bomberman, simula cada uno, y llama a alfa-beta con min.
        4. Si es el turno de los globos (min):
           - Genera todas las combinaciones de movimientos para los globos, simula cada una, y llama a alfa-beta con max.
        5. Retorna el mejor valor (max o min según corresponda).
        """
        
        # Encontrar posiciones
        pos_bomberman = self.encontrar_bomberman(mapa)
        pos_globos = self.encontrar_globos(mapa)
        pos_salida = self.encontrar_salida(mapa)
        
        # Verificar si Bomberman y la salida fueron encontrados
        if pos_bomberman is None:
            print("Error en alfa_beta: Bomberman no se encuentra en el mapa.")
            return float('-inf')  # Considerar esto como una colisión fatal
        
        if pos_salida is None:
            print("Error en alfa_beta: No se encuentra la salida en el mapa.")
            return float('-inf')  # Podría considerarse también una condición de fallo
        
        # Comprobar estados terminales
        # Bomberman muere si un globo está en la misma posición
        for pos_globo in pos_globos:
            if pos_bomberman == pos_globo:
                print(f"Bomberman choca con un globo en {pos_globo}.")
                return float('-inf')
        
        # Bomberman llega a la salida
        if pos_bomberman == pos_salida:
            print(f"Bomberman ha llegado a la salida en {pos_salida}.")
            return float('inf')
        
        # Profundidad agotada, retorna heurística
        if profundidad == 0:
            return self.calcular_heuristica(pos_bomberman, pos_globos, pos_salida)
        
        if es_max:
            # Turno de Bomberman (maximiza)
            valor_max = float('-inf')
            movimientos_bomberman = self.generar_movimientos_bomberman(mapa, pos_bomberman)
            
            # Si no hay movimientos posibles, se queda en el mismo lugar
            if not movimientos_bomberman:
                movimientos_bomberman = [pos_bomberman]
            
            for mov_bomberman in movimientos_bomberman:
                # Simular el movimiento de Bomberman
                nuevo_mapa = [fila[:] for fila in mapa]
                
                # Restaurar 'Salida' si Bomberman se mueve desde 'Salida' o 'BombermanSalida'
                if pos_bomberman == pos_salida or mapa[pos_bomberman[0]][pos_bomberman[1]] == 'BombermanSalida':
                    nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Salida'
                else:
                    nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Camino'
                
                # Mover a la nueva posición
                if mov_bomberman == pos_salida:
                    nuevo_mapa[mov_bomberman[0]][mov_bomberman[1]] = 'BombermanSalida'
                else:
                    nuevo_mapa[mov_bomberman[0]][mov_bomberman[1]] = 'Bomberman'
                
                print(f"Bomberman se mueve a {mov_bomberman}")
                print("Mapa después del movimiento de Bomberman:")
                for fila in nuevo_mapa:
                    print(fila)
                
                # Llamar a alfa-beta para el siguiente turno (min)
                valor = self.alfa_beta(nuevo_mapa, profundidad - 1, alfa, beta, False)
                
                # Actualizar valor_max y alfa
                if valor > valor_max:
                    valor_max = valor
                alfa = max(alfa, valor_max)
                
                # Poda alfa-beta
                if beta <= alfa:
                    self.podados += 1
                    print("Se realiza una poda alfa-beta en el turno de Bomberman.")
                    break
            
            return valor_max
        
        else:
            # Turno de los globos (minimiza)
            valor_min = float('inf')
            movs_globos = self.generar_movimientos_globos(mapa, pos_globos)
            
            # Si no hay movimientos, los globos se quedan en el mismo lugar
            if not movs_globos:
                movs_globos = [pos_globos]
            
            for combinacion_mov_globos in movs_globos:
                # Simular todos los movimientos de globos
                mapa_simulado = [fila[:] for fila in mapa]
                
                for (pos_orig, pos_dest) in zip(pos_globos, combinacion_mov_globos):
                    # Liberar la posición original del globo
                    if mapa_simulado[pos_orig[0]][pos_orig[1]] == 'GloboSalida':
                        mapa_simulado[pos_orig[0]][pos_orig[1]] = 'Salida'
                    else:
                        mapa_simulado[pos_orig[0]][pos_orig[1]] = 'Camino'
                    
                    # Mover el globo
                    mapa_simulado[pos_dest[0]][pos_dest[1]] = 'Globo'
                
                print(f"Globos se mueven a {combinacion_mov_globos}")
                print("Mapa después del movimiento de los globos:")
                for fila in mapa_simulado:
                    print(fila)
                
                # Llamar a alfa-beta con el siguiente turno (max)
                valor = self.alfa_beta(mapa_simulado, profundidad - 1, alfa, beta, True)
                
                # Actualizar valor_min y beta
                if valor < valor_min:
                    valor_min = valor
                beta = min(beta, valor_min)
                
                # Poda alfa-beta
                if beta <= alfa:
                    self.podados += 1
                    print("Se realiza una poda alfa-beta en el turno de los globos.")
                    break
            
            return valor_min

    def mejor_movimiento(self, mapa):
        """
        Función que determina el mejor movimiento inicial de Bomberman utilizando
        el algoritmo alfa-beta.
        
        Retorna la mejor posición a la que debería moverse Bomberman.
        """
        print(f"mapaoriginal{mapa}")
        profundidad = 5  # Niveles de profundidad
        pos_bomberman = self.encontrar_bomberman(mapa)
        pos_salida = self.encontrar_salida(mapa)
        
        # Verificar si Bomberman y la salida fueron encontrados
        if pos_bomberman is None:
            print("Error: Bomberman no se encuentra en el mapa.")
            return None  # O manejarlo según tu lógica de juego
        
        if pos_salida is None:
            print("Error: No se encuentra la salida en el mapa.")
            return None  # O manejarlo según tu lógica de juego
        
        movimientos_posibles = self.generar_movimientos_bomberman(mapa, pos_bomberman)
        
        # Si no hay movimientos posibles, Bomberman se queda en su lugar
        if not movimientos_posibles:
            return pos_bomberman
        
        mejor_valor = float('-inf')
        mejor_mov = None
        
        for movimiento in movimientos_posibles:
            # Simular el movimiento de Bomberman
            nuevo_mapa = [fila[:] for fila in mapa]
            
            # Restaurar 'Salida' si Bomberman se mueve desde 'Salida' o 'BombermanSalida'
            if pos_bomberman == pos_salida or mapa[pos_bomberman[0]][pos_bomberman[1]] == 'BombermanSalida':
                nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Salida'
            else:
                nuevo_mapa[pos_bomberman[0]][pos_bomberman[1]] = 'Camino'
            
            # Mover a la nueva posición
            if movimiento == pos_salida:
                nuevo_mapa[movimiento[0]][movimiento[1]] = 'BombermanSalida'
            else:
                nuevo_mapa[movimiento[0]][movimiento[1]] = 'Bomberman'
            
            # Llamar a alfa-beta para evaluar este movimiento
            # Aquí pasamos es_max = False porque sigue el turno de los globos (min)
            valor = self.alfa_beta(nuevo_mapa, profundidad - 1, float('-inf'), float('inf'), False)
            
            # **Corrección Clave: Priorizar Movimientos que Llevan a la Salida**
            if valor == float('inf'):
                # Si el movimiento lleva a la salida, seleccionarlo inmediatamente
                mejor_mov = movimiento
                mejor_valor = valor
                break  # No es necesario evaluar otros movimientos
            
            # **Seleccionar el movimiento con el valor heurístico más alto si no es una victoria inmediata**
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_mov = movimiento

        # **Después de evaluar todos los movimientos, realizar el movimiento seleccionado**
        if mejor_mov:
            # Intercambiar x e y, e invertir y para adaptarse al modelo
            altura_matriz = len(mapa)
            mejor_mov_adaptado = (mejor_mov[1], altura_matriz - 1 - mejor_mov[0]) if mejor_mov else pos_bomberman

            # **Código de Animación: Mover al agente y marcar la casilla**
            self.model.grid.move_agent(self, mejor_mov_adaptado)
            self.marcar_casilla(mejor_mov_adaptado) 
            
            # Imprimir información de depuración
            print(f"La mejor posición de Bomberman es: {mejor_mov}, la cantidad de nodos podados: {self.podados}")
        
        # Retorna la mejor posición para Bomberman
        return mejor_mov if mejor_mov is not None else pos_bomberman