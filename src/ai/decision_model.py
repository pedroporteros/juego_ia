class DecisionModel:
    def __init__(self):
        self.player_hand = []
        self.last_card_played = None

    def update_hand(self, hand):
        self.player_hand = hand

    def update_last_card(self, card):
        self.last_card_played = card

    def make_decision(self):
        # Implementar la lógica de decisión aquí
        if self.last_card_played is None:
            return "Esperar"
        
        # Ejemplo de lógica simple
        if self.last_card_played.value > 5:
            return "Jugar carta"
        else:
            return "Pasar"