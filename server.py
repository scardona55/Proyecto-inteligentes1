from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from scripts.modelo import MiModelo
from scripts.agentes import Bomberman, MuroMetal, RocaDestructible, Salida, Camino
from scripts.lecturaArc import cargar_archivo, validar_mapa

# Visualización de los agentes
def agent_portrayal(agent):
    portrayal = {}
    if isinstance(agent, Bomberman):
        portrayal["Shape"] = "imagenes/personaje.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 3
    elif isinstance(agent, MuroMetal):
        portrayal["Shape"] = "imagenes/muro_metal2.jpeg"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif isinstance(agent, RocaDestructible):
        portrayal["Shape"] = "imagenes/muro_roca.jpg"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif isinstance(agent, Salida):
        portrayal["Shape"] = "imagenes/salida.jpeg"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1
    elif isinstance(agent, Camino):
        portrayal["Shape"] = "imagenes/pasto.jpg"
        portrayal["scale"] = 1
        portrayal["Layer"] = 0

    return portrayal

# Cargar archivo del mapa
ruta_archivo = cargar_archivo()

mapa = None

# Verificar si el archivo es válido
if ruta_archivo:
    mapa = validar_mapa(ruta_archivo)  # Obtener el mapa como lista de listas
    if mapa is None:  # Si el mapa es inválido
        print("No se pudo cargar un mapa válido. Usando mapa por defecto.")
        mapa = None
else:
    mapa = None  # Si no se carga archivo, se usará la generación aleatoria en el modelo

altoM = 4
anchoM = 7

# Seleccionar el algoritmo a usar ('random', 'profundidad', 'amplitud')
algoritmo = 'profundidad'

grid = CanvasGrid(agent_portrayal, anchoM, altoM, 500, 500)

server = ModularServer(MiModelo,
                       [grid],
                       "Simulación de Bomberman",
                       {"mapa": mapa, "ancho": anchoM, "alto": altoM, "algoritmo": algoritmo})

server.port = 8521
server.launch()