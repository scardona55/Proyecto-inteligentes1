from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import random

# Agente que representa una casilla en la cuadrícula
class StaticCellAgent(Agent):
    """Agente que representa una casilla estática en la cuadrícula."""
    
    def __init__(self, unique_id, model, color):
        super().__init__(unique_id, model)
        self.color = color  # Color de la casilla
        self.visit_number = None  # Inicialmente ninguna casilla ha sido visitada

    def mark_as_visited(self, number):
        """Marcar la casilla como visitada con un número secuencial."""
        if self.visit_number is None:  # Solo marca si no ha sido visitada
            self.visit_number = number

    def step(self):
        pass  # No realiza acciones

# Agente que representa a Bomberman
class BombermanAgent(Agent):
    """Agente que representa a Bomberman."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.visit_count = 0  # Contador de visitas

    def step(self):
        # Obtener la posición actual de Bomberman
        x, y = self.pos
        
        # Marcar la casilla actual como visitada
        current_cell = [agent for agent in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(agent, StaticCellAgent)][0]
        if current_cell.visit_number is None:  # Solo incrementa si la casilla no ha sido visitada antes
            self.visit_count += 1
            current_cell.mark_as_visited(self.visit_count)

        # Elegir una dirección aleatoria: arriba, abajo, izquierda, derecha
        direction = random.choice(["up", "down", "left", "right"])

        # Calcular la nueva posición basándose en la dirección elegida
        if direction == "up":
            new_pos = (x, y - 1)
        elif direction == "down":
            new_pos = (x, y + 1)
        elif direction == "left":
            new_pos = (x - 1, y)
        elif direction == "right":
            new_pos = (x + 1, y)

        # Comprobar que la nueva posición está dentro de los límites de la cuadrícula
        if self.model.grid.out_of_bounds(new_pos):
            return  # No hacer nada si está fuera de los límites

        # Mover Bomberman a la nueva posición
        self.model.grid.move_agent(self, new_pos)

# Agente que representa un muro
class WallAgent(Agent):
    """Agente que representa un muro de metal."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  # No realiza acciones

# Modelo de la cuadrícula
class MyModel(Model):
    """Modelo que contiene la cuadrícula y los agentes."""
    
    def __init__(self, width, height):
        super().__init__()
        self.grid = MultiGrid(width, height, True)  # Cuadrícula toroidal
        self.schedule = RandomActivation(self)

        # Crear agentes de fondo (casillas)
        for x in range(width):
            for y in range(height):
                color = "lightblue"  # Color de fondo de cada casilla
                static_cell_agent = StaticCellAgent((x, y), self, color)
                self.schedule.add(static_cell_agent)
                self.grid.place_agent(static_cell_agent, (x, y))

        # Crear el agente Bomberman y colocar en una posición
        bomberman = BombermanAgent("Bomberman", self)
        self.schedule.add(bomberman)
        self.grid.place_agent(bomberman, (1, 1))  # Colocando en (1,1) como ejemplo

        # Crear un muro de metal y colocar en una posición
        wall = WallAgent("Wall", self)
        self.schedule.add(wall)
        self.grid.place_agent(wall, (3, 3))  # Colocando en (3,3) como ejemplo

    def step(self):
        self.schedule.step()

# Función de retrato general para todos los agentes
def portrayal(agent):
    if isinstance(agent, StaticCellAgent):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Color": agent.color,
            "Layer": 0,  # Capa de fondo
            "w": 1,
            "h": 1
        }
        if agent.visit_number is not None:
            portrayal["text"] = str(agent.visit_number)  # Mostrar el número de visita
            portrayal["text_color"] = "black"
        return portrayal
    elif isinstance(agent, BombermanAgent):
        return {
            "Shape": "circle",
            "Filled": "true",
            "Color": "red",  # Color de Bomberman
            "Layer": 1,  # Capa de Bomberman
            "r": 0.5,  # Radio del círculo
        }
    elif isinstance(agent, WallAgent):
        return {
            "Shape": "rect",
            "Filled": "true",
            "Color": "grey",  # Color del muro
            "Layer": 1,  # Capa del muro
            "w": 1,
            "h": 1
        }
    return None  # No devuelve nada para agentes no manejados

# Parámetros de la cuadrícula
width = 10  # Ancho de la cuadrícula
height = 10  # Alto de la cuadrícula

# Crear la visualización
grid = CanvasGrid(portrayal, width, height, 500, 500)

# Crear y lanzar el servidor, pasando los parámetros necesarios (width y height)
server = ModularServer(
    MyModel,
    [grid],
    "Modelo con Agentes Estáticos y Dinámicos",
    {"width": width, "height": height}  # Se pasan los parámetros al modelo
)
server.port = 8521  # Cambia el puerto si es necesario
server.launch()
