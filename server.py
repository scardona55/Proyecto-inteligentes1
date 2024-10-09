from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from scripts.modelo import MiModelo
from scripts.agentes import Bomberman, MuroMetal, RocaDestructible, Salida
from scripts.lecturaArc import cargar_archivo, validar_mapa

# Visualización de los agentes
def agent_portrayal(agent):
    portrayal = {}
    if isinstance(agent, Bomberman):
        portrayal["Shape"] = "imagenes/personaje.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, MuroMetal):
        portrayal["Shape"] = "imagenes/muro_metal2.jpeg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, RocaDestructible):
        portrayal["Shape"] = "imagenes/muro_roca.jpg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif isinstance(agent, Salida):
        portrayal["Shape"] = "imagenes/salida.jpeg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    return portrayal

# Cargar el archivo y obtener la ruta
ruta_archivo = cargar_archivo()  # Permitir al usuario seleccionar un archivo

# Inicializar mapa
mapa = None

# Verificar si el archivo es válido
if ruta_archivo:
    mapa = validar_mapa(ruta_archivo)  # Obtener el mapa como lista de listas
    if mapa is None:  # Si el mapa es inválido
        print("No se pudo cargar un mapa válido. Usando mapa por defecto.")
        mapa = None  # Indicamos que no hay mapa cargado para que el modelo lo genere aleatoriamente
else:
    mapa = None  # Si no se carga archivo, se usará la generación aleatoria en el modelo

# Crear el CanvasGrid con imagen de fondo
altoM = 4
anchoM = 7
grid = CanvasGrid(agent_portrayal, anchoM, altoM)  # Cambiado a dimensiones dinámicas

server = ModularServer(MiModelo,
                       [grid],
                       "Simulación de Bomberman",
                       {"mapa": mapa, "ancho": anchoM, "alto": altoM})

server.port = 8521
server.launch()
