import random
from .card import NumberCard, SkillCard
from .roulette import Roulette
import logging

class Player:
    """Representa a un jugador en el juego."""
    
    def __init__(self, name):
        self.name = name
        self.hand = []  # Cartas en mano
        self.played_card = None  # Carta jugada en el turno actual
        self.alive = True
    
    def play_number_card(self, card_index):
        """
        Juega una carta numérica de la mano.
        
        Args:
            card_index: Índice de la carta en la mano
            
        Returns:
            Card: La carta jugada
        """
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.type == "number":
                self.played_card = card
                self.hand.pop(card_index)
                return card
            else:
                return None
        return None
    
    def use_skill_card(self, card_index, game_state, target=None):
        """
        Usa una carta de habilidad.
        
        Args:
            card_index: Índice de la carta en la mano
            game_state: Estado actual del juego
            target: Objetivo de la habilidad (si aplica)
            
        Returns:
            bool: True si la habilidad se usó correctamente
        """
        if 0 <= card_index < len(self.hand):
            card = self.hand[card_index]
            if card.type == "skill":
                # Verificar si ya se usó una habilidad en este turno
                if game_state.skill_used_this_turn:
                    game_state.game_message = "Ya se usó una habilidad en este turno. Solo puedes usar la ruleta."
                    return False
                    
                result = card.use(game_state, self, target)
                if result:
                    game_state.skill_used_this_turn = True  # Marcar que se usó una habilidad
                    self.hand.pop(card_index)
                return result
        return False

class Game:
    """Controla la lógica del juego de cartas con ruleta rusa."""
    
    def __init__(self, player_name="Jugador", ai_name="IA"):
        self.player = Player(player_name)
        self.ai_player = Player(ai_name)
        self.roulette = Roulette(initial_probability=1)
        self.turn_count = 0
        self.current_player = None
        self.winner = None
        self.game_over = False
        self.current_loser = None
        self.skill_used_this_turn = False
    
    def setup_game(self):
        """Configura el juego, reparte las cartas iniciales."""
        # Generar y repartir cartas numéricas y de habilidad
        number_cards = self._generate_number_cards()
        skill_cards = self._generate_skill_cards()
        
        # Barajar las cartas
        random.shuffle(number_cards)
        random.shuffle(skill_cards)
        
        # Repartir 5 cartas numéricas y 4 de habilidad a cada jugador
        player_number_cards = number_cards[:7]
        player_skill_cards = skill_cards[:4]
        self.player.hand = player_number_cards + player_skill_cards
        
        ai_number_cards = number_cards[7:14]  
        ai_skill_cards = skill_cards[4:8]
        self.ai_player.hand = ai_number_cards + ai_skill_cards
        
        # El jugador humano comienza
        self.current_player = self.player
    
    def _generate_number_cards(self):
        """Genera las cartas numéricas para el juego."""
        cards = []
        card_id = 0
        
        # Crear 2 copias de cada valor numérico (1-10)
        for value in range(1, 11):
            for _ in range(2):  # Dos copias de cada valor
                cards.append(NumberCard(card_id, value))
                card_id += 1
                
        return cards
    
    def _generate_skill_cards(self):
        """Genera las cartas de habilidad para el juego."""
        skills = [
            {"name": "Aumento", "desc": "Aumenta tu número en 3", "effect": "increase"},
            {"name": "Intercambio", "desc": "Intercambia tu carta con la del oponente", "effect": "swap"},
            {"name": "Salvavidas", "desc": "Te salva automáticamente sin usar la ruleta", "effect": "block"},
            {"name": "Duplicar", "desc": "Duplica el valor de tu carta", "effect": "double"},
        ]
        
        cards = []
        id_counter = 100  # IDs para cartas de habilidad comienzan en 100
        
        for skill in skills:
            # Crear dos copias de cada habilidad
            for _ in range(2):
                cards.append(SkillCard(
                    id_counter, 
                    skill["name"], 
                    skill["desc"], 
                    skill["effect"]
                ))
                id_counter += 1
        
        return cards
    
    def play_turn(self, player_card_index):
        """
        Juega un turno completo.
        
        Args:
            player_card_index: Índice de la carta que el jugador quiere jugar
            
        Returns:
            dict: Información sobre el resultado del turno
        """
        
        # Reiniciamos el indicador al inicio de cada turno
        self.skill_used_this_turn = False
        
        # Jugar carta del jugador humano
        player_card = self.player.play_number_card(player_card_index)
        if not player_card:
            return {"status": "error", "message": "Carta inválida"}
        
        # IA juega una carta (selecciona una carta numérica aleatoria)
        ai_number_cards = [i for i, card in enumerate(self.ai_player.hand) 
                           if card.type == "number"]
        
        if not ai_number_cards:
            return {"status": "win", "winner": self.player.name, "reason": "IA sin cartas numéricas"}
        
        # La IA escoge una carta numérica aleatoria (más adelante implementaremos la integración con Gemini)
        ai_card_index = random.choice(ai_number_cards)
        ai_card = self.ai_player.play_number_card(ai_card_index)
        
        # Determinar ganador del turno
        turn_winner = None
        if player_card.value > ai_card.value:
            turn_winner = self.player
            self.current_loser = self.ai_player
        elif ai_card.value > player_card.value:
            turn_winner = self.ai_player
            self.current_loser = self.player
        else:
            # Empate, nadie pierde
            self.current_loser = None
            return {
                "status": "tie", 
                "player_card": player_card,
                "ai_card": ai_card
            }
        
        # Incrementar el contador de turnos y la probabilidad de la ruleta
        self.turn_count += 1
        self.roulette.increase_probability()
        
        return {
            "status": "continue",
            "turn_winner": turn_winner.name,
            "player_card": player_card,
            "ai_card": ai_card,
            "roulette_probability": self.roulette.get_probability()
        }
    
    def use_roulette(self, player):
        """
        El jugador dado gira la ruleta.
        
        Args:
            player: El jugador que gira la ruleta
            
        Returns:
            bool: True si el jugador "muere"
        """
        result = self.roulette.spin()
        if result:
            player.alive = False
            self.game_over = True
            self.winner = self.player if player == self.ai_player else self.ai_player
        return result
    
    def ai_decision_after_losing(self):
        """
        La IA decide si usar una carta de habilidad o girar la ruleta.
        
        Returns:
            dict: Información sobre la decisión tomada
        """
        logging.info("Solicitando decisión a la IA después de perder")
        
        # Si estamos usando una IA externa (que no está implementada aquí),
        # podríamos prepararle un estado de juego simplificado
        game_state = {
            "hand": self.ai_player.hand,
            "opponent_last_card": self.player.played_card.value if self.player.played_card else None,
            "roulette_probability": self.roulette.get_probability(),
            "turn_count": self.turn_count,
            "skill_used": self.skill_used_this_turn
        }
        
        logging.info(f"Estado del juego preparado para la IA: {game_state}")
        
        # Versión simple que no depende de la IA externa
        # Buscar cartas de habilidad disponibles
        ai_skill_cards = [i for i, card in enumerate(self.ai_player.hand) 
                        if card.type == "skill"]
        
        logging.info(f"Cartas de habilidad disponibles: {ai_skill_cards}")
        logging.info(f"Probabilidad actual de la ruleta: {self.roulette.get_probability()}%")
        
        # Decisión simple basada en la probabilidad de la ruleta
        # Si la probabilidad es alta, preferimos usar una habilidad (si hay disponible)
        if ai_skill_cards and not self.skill_used_this_turn and self.roulette.get_probability() > 20:
            # Usar una carta de habilidad aleatoria
            skill_index = random.choice(ai_skill_cards)
            skill_card = self.ai_player.hand[skill_index]
            
            logging.info(f"La IA decide usar la habilidad {skill_card.name} (índice {skill_index})")
            
            # Guardar el perdedor original para verificar si cambia
            original_loser = self.current_loser
            
            # Usar la habilidad
            result = self.ai_player.use_skill_card(skill_index, self, self.player)
            
            # Verificar si el perdedor cambió
            loser_changed = original_loser != self.current_loser
            
            logging.info(f"Resultado de usar la habilidad: {result}, cambio de perdedor: {loser_changed}")
            
            return {
                "choice": "skill",
                "skill_name": skill_card.name,
                "success": result,
                "loser_changed": loser_changed
            }
        else:
            # Girar la ruleta
            logging.info("La IA decide usar la ruleta")
            result = self.use_roulette(self.ai_player)
            logging.info(f"Resultado de la ruleta: {'muerte' if result else 'supervivencia'}")
            
            return {
                "choice": "roulette",
                "died": result
            }
    
    def is_game_over(self):
        """Comprueba si el juego ha terminado."""
        # El juego termina si alguien muere en la ruleta
        if not self.player.alive or not self.ai_player.alive:
            return True
            
        # O si se acaban las cartas numéricas de algún jugador
        player_has_number_cards = any(card.type == "number" for card in self.player.hand)
        ai_has_number_cards = any(card.type == "number" for card in self.ai_player.hand)
        
        if not player_has_number_cards:
            self.game_over = True
            self.winner = self.ai_player
            return True
            
        if not ai_has_number_cards:
            self.game_over = True
            self.winner = self.player
            return True
            
        return self.game_over