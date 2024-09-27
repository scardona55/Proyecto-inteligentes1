from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from scripts.modelo import MiModelo  # Importar el modelo
from scripts.agentes import Bomberman, MuroMetal, RocaDestructible  # Importar los agentes

# Función para visualizar los agentes
def agent_portrayal(agent):
    if isinstance(agent, Bomberman):
        portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "r": 0.8, "Layer": 1}
    elif isinstance(agent, MuroMetal):
        portrayal = {"Shape": "rect", "Color": "gray", "Filled": "true", "w": 1, "h": 1, "Layer": 2}
    elif isinstance(agent, RocaDestructible):
        portrayal = {"Shape": "rect", "Color": "brown", "Filled": "true", "w": 1, "h": 1, "Layer": 2}
    return portrayal

# Configuración de la cuadrícula para la visualización
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

# Crear el servidor con controles
server = ModularServer(MiModelo,
                       [grid],
                       "Simulación de Bomberman",
                       {"ancho": 10, "alto": 10})

# Establecer el puerto donde se alojará la simulación
server.port = 8521

# Iniciar el servidor
server.launch()
