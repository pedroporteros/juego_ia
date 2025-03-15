class Card:
    """Clase base para todas las cartas del juego."""
    def __init__(self, id):
        self.id = id

class NumberCard(Card):
    """Carta numérica con un valor del 1 al 10."""
    def __init__(self, id, value):
        super().__init__(id)
        self.value = value
        self.type = "number"
    
    def __str__(self):
        return f"Carta Numérica: {self.value}"

class SkillCard(Card):
    """Carta de habilidad con diferentes efectos."""
    def __init__(self, id, name, description, effect_type):
        super().__init__(id)
        self.name = name
        self.description = description
        self.effect_type = effect_type  # "increase", "swap", "block", etc.
        self.type = "skill"
    
    def use(self, game_state, player, target=None):
        """Aplica el efecto de la habilidad según su tipo."""
        if self.effect_type == "increase":
            return self._increase_effect(game_state, player)
        elif self.effect_type == "swap":
            return self._swap_effect(game_state, player, target)
        elif self.effect_type == "block":
            return self._block_effect(game_state, player, target)
        elif self.effect_type == "double":
            return self._double_effect(game_state, player)
        # Otros efectos pueden ser añadidos aquí
        return False
    
    def _increase_effect(self, game_state, player):
        """Incrementa el valor de la carta numérica jugada en 3."""
        if player.played_card and player.played_card.type == "number":
            # Guardar el valor original para el mensaje
            valor_original = player.played_card.value
            
            # Aplicar el aumento
            player.played_card.value += 3
            
            # Determinar el oponente
            opponent = game_state.ai_player if player == game_state.player else game_state.player
            
            # Mostrar mensaje informativo
            game_state.game_message = f"{player.name} aumentó su carta de {valor_original} a {player.played_card.value}"
            
            # Recalcular ganador
            if player.played_card.value > opponent.played_card.value:
                game_state.current_loser = opponent
                game_state.game_message += f" y ahora gana el turno"
            elif opponent.played_card.value > player.played_card.value:
                game_state.current_loser = player
                game_state.game_message += f" pero sigue perdiendo el turno"
            else:
                game_state.current_loser = None
                game_state.game_message += f" y ahora hay empate"
                
            return True
        return False
    
    def _swap_effect(self, game_state, player, target):
        """Intercambia la carta con la del adversario."""
        if player.played_card and target.played_card:
            player.played_card, target.played_card = target.played_card, player.played_card
            # Recalcular ganador
            if player == game_state.player:
                opponent = game_state.ai_player
            else:
                opponent = game_state.player
                
            if player.played_card.value > opponent.played_card.value:
                game_state.current_loser = opponent
                game_state.game_message = f"{player.name} gana el turno tras el intercambio."
            elif opponent.played_card.value > player.played_card.value:
                game_state.current_loser = player
                game_state.game_message = f"{opponent.name} gana el turno tras el intercambio."
            return True
        return False
    
    def _block_effect(self, game_state, player, target):
        """Bloquea el efecto de la carta del oponente."""
        # Verificar si el jugador que usa la carta es quien está perdiendo
        if game_state.current_loser == player:
            # Cambiar el estado para que nadie pierda en este turno
            game_state.current_loser = None
            # Actualizar el mensaje de juego
            game_state.game_message = f"¡{player.name} ha usado un salvavidas y se salva automáticamente!"
            # Indicar que el turno debe terminar (ya no es necesario usar la ruleta)
            game_state.turn_completed = True
            return True
        else:
            # Si el jugador no está perdiendo, aún puede usar la carta para anular el turno
            game_state.current_loser = None
            game_state.game_message = f"{player.name} ha usado un salvavidas y ha bloqueado el turno."
            return True
        
    def _double_effect(self, game_state, player):
        """Duplica el valor de tu carta numérica."""
        if player.played_card and player.played_card.type == "number":
            player.played_card.value *= 2
            # Recalcular ganador
            if player == game_state.player:
                opponent = game_state.ai_player
            else:
                opponent = game_state.player
                
            if player.played_card.value > opponent.played_card.value:
                game_state.current_loser = opponent
                game_state.game_message = f"{player.name} gana el turno tras duplicar su carta."
            elif opponent.played_card.value > player.played_card.value:
                game_state.current_loser = player
                game_state.game_message = f"{opponent.name} gana el turno a pesar de la duplicación."
            return True
        return False
    
    def __str__(self):
        return f"Habilidad: {self.name} - {self.description}"