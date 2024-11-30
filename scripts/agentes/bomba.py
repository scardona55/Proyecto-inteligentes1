from mesa import Agent
from .roca_destructible import RocaDestructible

class Bomba(Agent):
    # Constante para definir el rango de explosión
    RANGO_EXPLOSION = 1  # Puedes ajustar el rango según sea necesario

    def __init__(self, unique_id, model, pos, tiempo_explosion=3):
        """
        Constructor de la bomba.

        Args:
            unique_id (int): Identificador único del agente.
            model (Model): Instancia del modelo.
            pos (tuple): Posición inicial de la bomba.
            tiempo_explosion (int): Tiempo en pasos antes de explotar.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.tiempo_explosion = tiempo_explosion

    def step(self):
        """
        Lógica del paso de la bomba.
        Reduce el temporizador y detona cuando llega a 0.
        """
        self.tiempo_explosion -= 1
        if self.tiempo_explosion <= 0:
            self.explotar()

    def explotar(self):
        """
        Lógica de explosión de la bomba.
        Destruye los objetos afectados dentro del rango de explosión.
        """
        x, y = self.pos
        # Direcciones para explorar en cruz desde la posición actual
        direcciones = [
            (0, 1),   # Arriba
            (0, -1),  # Abajo
            (1, 0),   # Derecha
            (-1, 0)   # Izquierda
        ]

        # Destruir objetos en cada dirección hasta el rango especificado
        for dx, dy in direcciones:
            for r in range(1, self.RANGO_EXPLOSION + 1):
                nueva_pos = (x + r * dx, y + r * dy)

                # Verificar que la posición no esté fuera de los límites
                if not self.model.grid.out_of_bounds(nueva_pos):
                    contenido = self.model.grid.get_cell_list_contents(nueva_pos)
                    for obj in contenido:
                        if isinstance(obj, RocaDestructible):
                            self.model.grid.remove_agent(obj)
                            self.model.schedule.remove(obj)

        # Explosión también afecta la celda donde está la bomba
        contenido_central = self.model.grid.get_cell_list_contents(self.pos)
        for obj in contenido_central:
            if isinstance(obj, RocaDestructible):
                self.model.grid.remove_agent(obj)
                self.model.schedule.remove(obj)

        # Finalmente, elimina la bomba del modelo
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)
