import random

class Roulette:
    """Implementa la mecánica de ruleta rusa con probabilidad creciente."""
    
    def __init__(self, initial_probability=1):
        """
        Inicializa la ruleta con una probabilidad dada.
        
        Args:
            initial_probability: Probabilidad inicial de "muerte" en porcentaje
        """
        self.initial_probability = initial_probability
        self.current_probability = initial_probability
        self.increment = 10  # Incremento en cada turno (10%)
    
    def spin(self):
        """
        Simula girar la ruleta y determina si el jugador "muere".
        
        Returns:
            bool: True si el jugador "muere", False en caso contrario
        """
        random_value = random.random() * 100  # Valor entre 0 y 100
        return random_value <= self.current_probability
    
    def increase_probability(self):
        """Aumenta la probabilidad de "muerte" según el incremento establecido."""
        self.current_probability += self.increment
        # Aseguramos que no supere el 100%
        self.current_probability = min(self.current_probability, 100)
    
    def reset(self):
        """Restablece la probabilidad al valor inicial."""
        self.current_probability = self.initial_probability
    
    def get_probability(self):
        """Devuelve la probabilidad actual en porcentaje."""
        return self.current_probability