from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import random

# Agente básico que se mueve en la cuadrícula
class MiAgente(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def step(self):
        # Movimiento aleatorio
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        movimiento = random.choice(movimientos)
        self.model.grid.move_agent(self, movimiento)

# Modelo que contiene varios agentes
class MiModelo(Model):
    def __init__(self, N, ancho, alto):
        super().__init__()  # Llamada explícita al constructor de la clase Model
        self.num_agentes = N
        self.grid = MultiGrid(ancho, alto, True)
        self.schedule = RandomActivation(self)

        # Crear y ubicar los agentes
        for i in range(self.num_agentes):
            agente = MiAgente(i, self)
            self.schedule.add(agente)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agente, (x, y))

    def step(self):
        # Avanzar un paso para todos los agentes
        self.schedule.step()

# Función para visualizar los agentes
def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "red",
        "Filled": "true",
        "r": 0.5,
        "Layer": 1  # Añadir capa (Layer) para evitar el error
    }
    return portrayal

# Configuración de la cuadrícula para la visualización
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Crear el servidor con controles
server = ModularServer(MiModelo,
                       [grid],  # Eliminamos el chart
                       "Simulación de Agentes",
                       {"N": 10, "ancho": 10, "alto": 10})

# Establecer el puerto donde se alojará la simulación
server.port = 8521

# Iniciar el servidor
server.launch()
