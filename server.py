from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from scripts.modelo import MiModelo
from scripts.agentes import Bomberman, MuroMetal, RocaDestructible, Salida

#Visualizacion de los agentes
def agent_portrayal(agent):
    portrayal = {}
    if isinstance(agent, Bomberman):
        portrayal["Shape"] = "imagenes/bomba.jpeg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, MuroMetal):
        portrayal["Shape"] = "imagenes/muro_metal.jpg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, RocaDestructible):
        portrayal["Shape"] = "imagenes/roca.jpg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, Salida):
        portrayal["Shape"] = "imagenes/pasto.jpg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    return portrayal


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

server = ModularServer(MiModelo,
                       [grid],
                       "Simulación de Bomberman",
                       {"ancho": 10, "alto": 10})

server.port = 8521

server.launch()
