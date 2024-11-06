from mesa import Agent
from .camino import Camino
from .muro_metal import MuroMetal
from .roca_destructible import RocaDestructible
from .salida import Salida
from .globo import Globo
from .bomberman import Bomberman

class Bomba(Agent):
    def __init__(self, unique_id, model, poder_destruccion=1):
        super().__init__(unique_id, model)
        self.poder_destruccion = poder_destruccion
        self.explotada = False
    
    def detonar(self):
        """Método para detonar la bomba y afectar los elementos en rango"""
        if self.explotada:
            return  # Si ya explotó, no hace nada
        
        posiciones_afectadas = self.calcular_posiciones_afectadas()
        for posicion in posiciones_afectadas:
            contenido_celda = self.model.grid.get_cell_list_contents(posicion)
            
            for agente in contenido_celda:
                # Interacción con una roca destructible
                if isinstance(agente, RocaDestructible):
                    self.model.grid.remove_agent(agente)
                    print(f"Roca en {posicion} destruida por la bomba.")
                
                # Interacción con Bomberman
                if isinstance(agente, Bomberman):
                    agente.vida -= 1
                    print(f"Bomberman en {posicion} fue alcanzado y pierde una vida. Vida restante: {agente.vida}")
                    if agente.vida <= 0:
                        print("¡Bomberman ha sido derrotado!")
                        self.model.running = False

        # Marca la bomba como explotada
        self.explotada = True

    def calcular_posiciones_afectadas(self):
        """Calcula las posiciones afectadas en las direcciones cardinales según el poder de destrucción."""
        posiciones_afectadas = []
        x, y = self.pos

        # Añadir posiciones en cada dirección cardinal según el poder de destrucción
        for i in range(1, self.poder_destruccion + 1):
            posiciones_afectadas.append((x + i, y))   # Abajo
            posiciones_afectadas.append((x - i, y))   # Arriba
            posiciones_afectadas.append((x, y + i))   # Derecha
            posiciones_afectadas.append((x, y - i))   # Izquierda
        
        # Filtra posiciones fuera del tablero
        posiciones_afectadas = [pos for pos in posiciones_afectadas if not self.model.grid.out_of_bounds(pos)]
        return posiciones_afectadas
