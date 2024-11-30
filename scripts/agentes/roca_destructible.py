from mesa import Agent

class RocaDestructible(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_destructible = True  # Indica que puede ser destruida
        self.is_active = True        # Estado activo de la roca

    def destroy(self):
        """Elimina la roca del modelo."""
        if self.is_active:  # Solo destruye si está activa
            self.is_active = False
            self.model.grid.remove_agent(self)
            print(f"Roca {self.unique_id} destruida.")
