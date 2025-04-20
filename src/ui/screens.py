import pygame
import sys
import os
import math
import time
import random
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import *
from ui.buttons import Button

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("juego_ia.log"),
        logging.StreamHandler()
    ]
)

class Button:
    """Clase para crear botones interactivos."""
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.active = True
        
    def draw(self, screen, font):
        color = self.hover_color if self.hovered else self.color
        if not self.active:
            color = (100, 100, 100)  # Color gris para botones inactivos
            
        pygame.draw.rect(screen, color, self.rect, 0, 10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, 10)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if not self.active:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False
        
    def set_active(self, active):
        self.active = active

class Card:
    """Representación visual de una carta."""
    def __init__(self, x, y, card_data, is_face_up=True, is_ai_card=False):
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.card_data = card_data
        self.selected = False
        self.hovered = False
        self.hover_offset = 0  # Para la animación de levantarse
        self.max_hover_offset = 15  # Cantidad máxima que se eleva la carta
        self.hover_speed = 2  # Velocidad de la animación
        self.color = CARD_COLOR
        self.hover_color = (200, 200, 255)
        self.selected_color = (180, 255, 180)
        self.is_face_up = is_face_up
        self.is_ai_card = is_ai_card
        self.original_y = y  # Guardar la posición Y original para la animación
        self.card_border_radius = 10  # Bordes más redondeados
        self.card_shadow_offset = 3  # Sombra para dar profundidad
        
    def update(self):
        """Actualiza la animación de la carta."""
        if self.hovered and not self.is_ai_card:
            # Aumentar offset hasta max_hover_offset
            self.hover_offset = min(self.hover_offset + self.hover_speed, self.max_hover_offset)
        else:
            # Disminuir offset hasta 0
            self.hover_offset = max(self.hover_offset - self.hover_speed, 0)
            
        # Actualizar posición Y de la carta según el hover_offset
        self.rect.y = self.original_y - self.hover_offset
        
    def draw(self, screen, font):
        # Seleccionar el color basado en el estado de la carta
        if self.selected:
            color = self.selected_color
        elif self.hovered and not self.is_ai_card:
            color = self.hover_color
        else:
            color = self.color
        
        # Dibujar sombra
        shadow_rect = pygame.Rect(
            self.rect.x + self.card_shadow_offset,
            self.rect.y + self.card_shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, (50, 50, 50, 150), shadow_rect, 0, self.card_border_radius)
            
        # Dibujar la carta
        pygame.draw.rect(screen, color, self.rect, 0, self.card_border_radius)
        pygame.draw.rect(screen, BLACK, self.rect, 2, self.card_border_radius)
        
        # Decoraciones adicionales para la carta
        # Dibujar un marco decorativo interior
        inner_rect = pygame.Rect(
            self.rect.x + 8, 
            self.rect.y + 8, 
            self.rect.width - 16, 
            self.rect.height - 16
        )
        pygame.draw.rect(screen, (255, 255, 255, 100), inner_rect, 1, self.card_border_radius-2)
        
        # Si es una carta boca abajo (de la IA)
        if not self.is_face_up:
            # Dibujar un diseño para el dorso más elaborado
            pygame.draw.rect(screen, (80, 80, 150), inner_rect, 0, self.card_border_radius-2)
            
            # Dibujar un patrón de rejilla para el dorso
            for i in range(0, inner_rect.width, 10):
                pygame.draw.line(screen, (60, 60, 120), 
                                (inner_rect.left + i, inner_rect.top), 
                                (inner_rect.left + i, inner_rect.bottom), 1)
                
            for j in range(0, inner_rect.height, 10):
                pygame.draw.line(screen, (60, 60, 120), 
                                (inner_rect.left, inner_rect.top + j), 
                                (inner_rect.right, inner_rect.top + j), 1)
                
            # Logo central para el dorso
            symbol_rect = pygame.Rect(0, 0, 30, 30)
            symbol_rect.center = inner_rect.center
            pygame.draw.rect(screen, (200, 200, 255), symbol_rect, 0, 5)
            pygame.draw.rect(screen, (60, 60, 120), symbol_rect, 2, 5)
            
            return
        
        # Dibujar el contenido según el tipo de carta
        if self.card_data.type == "number":
            # Marco decorativo para el número
            value_bg_rect = pygame.Rect(0, 0, 40, 40)
            value_bg_rect.center = self.rect.center
            pygame.draw.rect(screen, (240, 240, 200), value_bg_rect, 0, 5)
            pygame.draw.rect(screen, (100, 100, 100), value_bg_rect, 1, 5)
            
            # El número en sí
            text_surf = font.render(str(self.card_data.value), True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
            
            # Decoraciones en las esquinas
            mini_text = pygame.font.SysFont(None, 20).render(str(self.card_data.value), True, BLACK)
            screen.blit(mini_text, (self.rect.left + 5, self.rect.top + 5))
            screen.blit(mini_text, (self.rect.right - 15, self.rect.bottom - 15))
        else:
            # Para cartas de habilidad
            # Fondo de título
            title_bg = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, 20)
            pygame.draw.rect(screen, (150, 150, 220), title_bg, 0, 5)
            
            # Nombre de la habilidad con fuente más pequeña
            small_font = pygame.font.SysFont(None, 20)  # Reducir tamaño de fuente para título
            name_surf = small_font.render(self.card_data.name, True, BLACK)
            name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.top + 14))
            screen.blit(name_surf, name_rect)
            
            # Icono de la habilidad según el tipo
            icon_rect = pygame.Rect(0, 0, 30, 30)
            icon_rect.center = (self.rect.centerx, self.rect.centery)
            
            if self.card_data.effect_type == "increase":
                # Dibujar un ícono de flecha hacia arriba
                pygame.draw.rect(screen, (100, 200, 100), icon_rect, 0, 5)
                points = [(icon_rect.centerx, icon_rect.top + 5), 
                          (icon_rect.right - 5, icon_rect.centery + 5),
                          (icon_rect.centerx + 5, icon_rect.centery + 5),
                          (icon_rect.centerx + 5, icon_rect.bottom - 5),
                          (icon_rect.centerx - 5, icon_rect.bottom - 5),
                          (icon_rect.centerx - 5, icon_rect.centery + 5),
                          (icon_rect.left + 5, icon_rect.centery + 5)]
                pygame.draw.polygon(screen, (50, 150, 50), points)
            elif self.card_data.effect_type == "swap":
                # Dibujar un ícono de flechas cruzadas
                pygame.draw.rect(screen, (200, 150, 100), icon_rect, 0, 5)
                pygame.draw.line(screen, (150, 100, 50), 
                               (icon_rect.left + 5, icon_rect.top + 5),
                               (icon_rect.right - 5, icon_rect.bottom - 5), 3)
                pygame.draw.line(screen, (150, 100, 50), 
                               (icon_rect.right - 5, icon_rect.top + 5),
                               (icon_rect.left + 5, icon_rect.bottom - 5), 3)
            elif self.card_data.effect_type == "block":
                # Cambiar a un ícono de salvavidas en lugar de escudo
                pygame.draw.rect(screen, (100, 200, 250), icon_rect, 0, 5)
                
                # Dibujar un salvavidas circular
                pygame.draw.circle(screen, (255, 255, 255), icon_rect.center, 12, 0)
                pygame.draw.circle(screen, (255, 50, 50), icon_rect.center, 12, 3)
                pygame.draw.circle(screen, (255, 255, 255), icon_rect.center, 8, 0)
                pygame.draw.circle(screen, (255, 50, 50), icon_rect.center, 8, 2)
                pygame.draw.circle(screen, (255, 255, 255), icon_rect.center, 4, 0)
            elif self.card_data.effect_type == "double":
                # Dibujar un ícono de x2
                pygame.draw.rect(screen, (100, 150, 200), icon_rect, 0, 5)
                x2_text = pygame.font.SysFont(None, 24).render("x2", True, (50, 100, 150))
                x2_rect = x2_text.get_rect(center=icon_rect.center)
                screen.blit(x2_text, x2_rect)
            
            # Descripción en la parte inferior
            tiny_font = pygame.font.SysFont(None, 16)  # Fuente muy pequeña para descripción
            
            # Asegurarse de que la descripción no sea demasiado larga
            max_chars = 18  # Ajustar según el tamaño de la carta
            description = self.card_data.description
            if len(description) > max_chars:
                description = description[:max_chars-3] + "..."
            
            # Hacer el rectángulo de fondo un poco más ancho y alto para texto más pequeño
            desc_bg = pygame.Rect(self.rect.x + 5, self.rect.bottom - 22, self.rect.width - 10, 17)
            pygame.draw.rect(screen, (240, 240, 200), desc_bg, 0, 4)
            
            desc_surf = tiny_font.render(description, True, BLACK)
            desc_rect = desc_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 14))
            screen.blit(desc_surf, desc_rect)
    
    def check_hover(self, pos):
        if not self.is_ai_card:  # Solo las cartas del jugador pueden tener hover
            self.hovered = self.rect.collidepoint(pos)
            return self.hovered
        return False
        
    def is_clicked(self, pos, event):
        if self.is_ai_card:  # Las cartas de la IA no son clickables
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False
    
class RouletteVisualizer:
    """Visualizador de la ruleta rusa."""
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = 0  # Ángulo actual para animación
        self.rotation_speed = 0  # Velocidad de rotación
        self.spinning = False
        self.spin_start_time = 0
        self.spin_result = None  # None = no resultado, True = muerte, False = supervivencia
        self.probability = 1  # Probabilidad actual
        
    def start_spin(self, probability, result):
        """Inicia la animación de giro."""
        self.spinning = True
        self.spin_start_time = pygame.time.get_ticks()
        self.rotation_speed = 20 + random.random() * 10  # Velocidad aleatoria
        self.probability = probability
        self.spin_result = result
        
    def update(self):
        """Actualiza la animación de la ruleta."""
        if self.spinning:
            elapsed = pygame.time.get_ticks() - self.spin_start_time
            
            # Disminuir la velocidad gradualmente
            if elapsed > 1000:  # Después de 1 segundo, comenzar a frenar
                self.rotation_speed = max(0, self.rotation_speed - 0.2)
                
            # Si casi se detiene, parar completamente
            if self.rotation_speed < 0.5:
                self.rotation_speed = 0
                self.spinning = False
                
            # Actualizar ángulo
            self.angle += self.rotation_speed
            if self.angle >= 360:
                self.angle -= 360
        else:
            # Si no está girando, hacer una animación suave
            self.angle += 0.2
            if self.angle >= 360:
                self.angle -= 360
        
    def draw(self, screen, font):
        """Dibuja la ruleta."""
        # Dibujar círculo exterior
        pygame.draw.circle(screen, (120, 220, 130), (self.x, self.y), self.radius, 0)
        pygame.draw.circle(screen, (200, 200, 200), (self.x, self.y), self.radius, 3)
        
        # Dibujar segmentos según la probabilidad con colores más suaves
        danger_angle = 360 * (self.probability / 100)
        safe_angle = 360 - danger_angle
        
        # Segmento peligroso (rosa/rojo suave)
        if danger_angle > 0:
            pygame.draw.arc(screen, (220, 150, 150), 
                        (self.x - self.radius, self.y - self.radius, 
                            self.radius * 2, self.radius * 2),
                        math.radians(self.angle + safe_angle), 
                        math.radians(self.angle + 360), 
                        self.radius)
        
        # Dibujar divisiones entre segmentos
        for i in range(8):
            angle_rad = math.radians(self.angle + i * 45)
            end_x = self.x + math.cos(angle_rad) * self.radius
            end_y = self.y + math.sin(angle_rad) * self.radius
            pygame.draw.line(screen, (200, 200, 200), 
                            (self.x, self.y), (end_x, end_y), 2)
        
        # Dibujar aguja/indicador
        needle_length = self.radius - 10
        needle_angle = math.radians(270)  # Siempre apunta hacia arriba
        needle_x = self.x + math.cos(needle_angle) * needle_length
        needle_y = self.y + math.sin(needle_angle) * needle_length
        pygame.draw.line(screen, (255, 255, 255), 
                        (self.x, self.y), (needle_x, needle_y), 4)
        
        # Dibujar círculo central
        pygame.draw.circle(screen, (150, 150, 150), (self.x, self.y), 15, 0)
        pygame.draw.circle(screen, (100, 100, 100), (self.x, self.y), 15, 1)
        
        # Mostrar probabilidad en el centro
        prob_text = font.render(f"{int(self.probability)}%", True, (255, 255, 255))
        prob_rect = prob_text.get_rect(center=(self.x, self.y))
        screen.blit(prob_text, prob_rect)
        
        # Mostrar resultado si terminó de girar y hay resultado
        if not self.spinning and self.spin_result is not None:
            if self.spin_result:  # Muerte
                result_text = font.render("¡BANG!", True, (255, 50, 50))
            else:  # Supervivencia
                result_text = font.render("Safe", True, (50, 255, 50))
                
            result_rect = result_text.get_rect(center=(self.x, self.y - self.radius - 30))
            screen.blit(result_text, result_rect)

class PlayerVisualizer:
    """Visualizador del jugador y la IA."""
    def __init__(self, x, y, is_ai=False):
        self.x = x
        self.y = y
        self.is_ai = is_ai
        self.size = 60
        self.color = (100, 100, 255) if is_ai else (255, 200, 100)
        self.alive = True
        self.death_animation_time = 0
        self.death_animation_duration = 1500  # 1.5 segundos
        
    def set_alive(self, alive):
        """Actualiza el estado de vida del jugador y reinicia la animación."""
        if self.alive and not alive:  # Si acaba de morir
            self.death_animation_time = pygame.time.get_ticks()
        self.alive = alive
        
    def draw(self, screen, font):
        """Dibuja al jugador o a la IA."""
        current_time = pygame.time.get_ticks()
        
        # Si está muerto y aún animando
        if not self.alive and current_time - self.death_animation_time < self.death_animation_duration:
            # Calcular progreso de la animación
            progress = (current_time - self.death_animation_time) / self.death_animation_duration
            
            # Dibujar explosión o animación de muerte
            radius = int(self.size * (1 + progress))
            alpha = 255 * (1 - progress)
            
            # Crear una superficie con transparencia
            explosion = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(explosion, (255, 50, 50, alpha), (radius, radius), radius)
            
            # Dibujar ondas expansivas
            for i in range(3):
                wave_progress = progress - 0.2 * i
                if 0 < wave_progress < 1:
                    wave_radius = int(self.size * (1 + wave_progress * 1.5))
                    wave_alpha = 150 * (1 - wave_progress)
                    pygame.draw.circle(explosion, (255, 200, 50, wave_alpha), 
                                     (radius, radius), wave_radius, 3)
            
            screen.blit(explosion, (self.x - radius, self.y - radius))
        
        # Dibujar avatar normal o versión "muerta"
        if self.alive:
            # Dibujar círculo para la cabeza
            pygame.draw.circle(screen, self.color, (self.x, self.y - 15), 25)
            pygame.draw.circle(screen, (50, 50, 50), (self.x, self.y - 15), 25, 2)
            
            # Dibujar ojos
            eye_color = (0, 0, 0)
            if self.is_ai:
                # Ojos robóticos para la IA
                pygame.draw.rect(screen, (255, 50, 50), (self.x - 15, self.y - 25, 10, 5))
                pygame.draw.rect(screen, (255, 50, 50), (self.x + 5, self.y - 25, 10, 5))
            else:
                # Ojos humanos para el jugador
                pygame.draw.circle(screen, eye_color, (self.x - 10, self.y - 20), 5)
                pygame.draw.circle(screen, eye_color, (self.x + 10, self.y - 20), 5)
            
            # Dibujar boca
            if self.is_ai:
                # Boca robótica para la IA
                for i in range(3):
                    pygame.draw.line(screen, (50, 50, 50), 
                                   (self.x - 12, self.y - 5 + i*3), 
                                   (self.x + 12, self.y - 5 + i*3), 2)
            else:
                # Sonrisa para el jugador
                pygame.draw.arc(screen, (50, 50, 50), 
                              (self.x - 15, self.y - 15, 30, 20),
                              math.radians(0), math.radians(180), 2)
                
            # Dibujar cuerpo
            pygame.draw.rect(screen, self.color, 
                           (self.x - 20, self.y + 10, 40, 30))
            pygame.draw.rect(screen, (50, 50, 50), 
                           (self.x - 20, self.y + 10, 40, 30), 2)
        else:
            # Versión "muerta" - una X
            pygame.draw.line(screen, (100, 100, 100), 
                           (self.x - 25, self.y - 25), 
                           (self.x + 25, self.y + 25), 5)
            pygame.draw.line(screen, (100, 100, 100), 
                           (self.x + 25, self.y - 25), 
                           (self.x - 25, self.y + 25), 5)
            
        # Etiqueta
        label = "IA" if self.is_ai else "Jugador"
        label_surf = font.render(label, True, (255, 255, 255))
        label_rect = label_surf.get_rect(center=(self.x, self.y + 50))
        screen.blit(label_surf, label_rect)

class GameScreen:
    """Pantalla principal del juego."""
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 48)
        
        # Estado de la interfaz
        self.player_card_objects = []
        self.ai_card_objects = []
        self.center_cards = []  # Cartas jugadas en el centro
        self.buttons = []
        self.selected_card_index = None
        self.game_message = ""
        
        # Estado del juego
        self.waiting_for_ai = False
        self.waiting_time = 0
        self.turn_result = None
        
        # Inicializar botones
        self.init_buttons()
        
        self.ai_thinking = False
        self.ai_decision_start_time = 0
        
        # Añadir nuevas visualizaciones
        self.roulette_vis = RouletteVisualizer(SCREEN_WIDTH - 120, SCREEN_HEIGHT // 2, 80)
        self.player_vis = PlayerVisualizer(120, SCREEN_HEIGHT - 350)
        self.ai_vis = PlayerVisualizer(120, 250, is_ai=True)
        
        # Para efectos especiales
        self.showing_message_effect = False
        self.message_effect_start_time = 0
        self.message_effect_text = ""
        self.message_effect_color = (255, 255, 255)
        
        # Añadir para manejar el scroll en las instrucciones
        self.instructions_scroll_pos = 0
        self.instructions_max_scroll = 0  # Se calculará dinámicamente
        self.instructions_scroll_speed = 15
        
        # Modificado: Panel de instrucciones se muestra automáticamente al inicio
        self.showing_instructions = True
        self.instructions_button = Button(10, 10, 120, 30, "Instrucciones",
                                  color=(70,70,200), hover_color=(100,100,240), text_color=WHITE)
        self.buttons.append(self.instructions_button)
    
    def show_message_effect(self, text, color=(255, 255, 255)):
        """Muestra un efecto de mensaje grande en pantalla."""
        self.showing_message_effect = True
        self.message_effect_start_time = pygame.time.get_ticks()
        self.message_effect_text = text
        self.message_effect_color = color
        self.buttons.append(self.instructions_button)
        
    def update(self):
        """Actualiza todos los elementos animados."""
        # Actualizar animaciones de cartas
        for card in self.player_card_objects:
            card.update()
            
        # Actualizar ruleta
        self.roulette_vis.update()
        
    def init_buttons(self):
        button_y = SCREEN_HEIGHT - 70  # Posicionarlos más abajo
        button_width = 180
        button_height = 50
        button_spacing = 20
        
        # Calcular las posiciones para que estén centrados y espaciados correctamente
        total_width = (button_width * 3) + (button_spacing * 2)
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Botón para jugar carta
        self.play_button = Button(
            start_x, 
            button_y, 
            button_width, button_height, 
            "Jugar Carta", 
            GREEN, 
            (100, 255, 100)
        )
        
        # Botón para usar la ruleta
        self.roulette_button = Button(
            start_x + button_width + button_spacing, 
            button_y, 
            button_width, button_height, 
            "Usar Ruleta", 
            RED, 
            (255, 100, 100)
        )
        
        # Botón para usar habilidad
        self.skill_button = Button(
            start_x + (button_width + button_spacing) * 2, 
            button_y, 
            button_width, button_height, 
            "Usar Habilidad", 
            BLUE, 
            (100, 100, 255)
        )
        
        # Inicialmente, solo el botón de jugar carta está activo
        self.roulette_button.set_active(False)
        self.skill_button.set_active(False)
        
        self.buttons = [self.play_button, self.roulette_button, self.skill_button]
        
    def update_card_objects(self):
        """Actualiza los objetos de carta basados en el estado actual del juego."""
        self.player_card_objects = []
        self.ai_card_objects = []
        
        # Mostrar cartas del jugador humano
        player_cards = self.game.player.hand
        player_y = SCREEN_HEIGHT - 240
        self.update_player_cards(player_cards, player_y)
        
        # Mostrar cartas del jugador IA (boca abajo)
        ai_cards = self.game.ai_player.hand
        ai_y = 120
        self.update_ai_cards(ai_cards, ai_y)
    
    def update_player_cards(self, cards, y):
        """Actualiza las cartas del jugador."""
        start_x = SCREEN_WIDTH // 2 - ((len(cards) * (CARD_WIDTH + CARD_SPACING)) // 2)
        
        for i, card in enumerate(cards):
            card_obj = Card(start_x + i * (CARD_WIDTH + CARD_SPACING), y, card)
            self.player_card_objects.append(card_obj)
    
    def update_ai_cards(self, cards, y):
        """Actualiza las cartas de la IA (boca abajo)."""
        start_x = SCREEN_WIDTH // 2 - ((len(cards) * (CARD_WIDTH + CARD_SPACING)) // 2)
        
        for i, card in enumerate(cards):
            # Para la IA, creamos cartas boca abajo
            card_obj = Card(start_x + i * (CARD_WIDTH + CARD_SPACING), y, card, 
                            is_face_up=False, is_ai_card=True)
            self.ai_card_objects.append(card_obj)
    
    def update_center_cards(self, player_card=None, ai_card=None):
        """Actualiza las cartas jugadas en el centro."""
        self.center_cards = []
        center_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        
        if player_card:
            player_card_obj = Card(SCREEN_WIDTH // 2 - CARD_WIDTH - 20, center_y, player_card)
            self.center_cards.append(player_card_obj)
            
        if ai_card:
            ai_card_obj = Card(SCREEN_WIDTH // 2 + 20, center_y, ai_card, is_face_up=True)
            self.center_cards.append(ai_card_obj)
    
    def handle_events(self):
        """Maneja los eventos de entrada."""
        
        self.update()
        
        # Si la IA está pensando, no permitir interacción del usuario
        if self.ai_thinking:
            # Solo procesar eventos de cierre del juego
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Mostrar un mensaje de "IA pensando..."
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.ai_decision_start_time) // 1000  # en segundos
            dots = "." * (elapsed_time % 4)  # Animación de puntos
            self.game_message = f"La IA está pensando{dots}"
            
            # Si ha pasado demasiado tiempo, asumir que la IA está atascada
            if elapsed_time > 15:  # 15 segundos de timeout
                self.ai_thinking = False
                self.game_message = "La IA tardó demasiado tiempo. Continúa el juego."
                logging.warning("Timeout en la espera de decisión de la IA")
            
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Si estamos esperando por la IA, ignorar los eventos del jugador
        if self.waiting_for_ai:
            return self.handle_ai_turn()
        
        # Verificar hover en cartas y botones
        for card in self.player_card_objects:
            card.check_hover(mouse_pos)
            
        for button in self.buttons:
            button.check_hover(mouse_pos)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            pos = pygame.mouse.get_pos()
            
            for i, card in enumerate(self.player_card_objects):
                if card.is_clicked(mouse_pos, event):
                    # Deseleccionar todas las cartas
                    for c in self.player_card_objects:
                        c.selected = False
                    # Seleccionar la carta clicada
                    card.selected = True
                    self.selected_card_index = i

            if self.showing_instructions and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:   # rueda arriba
                    self.instructions_scroll_pos = max(
                        0, self.instructions_scroll_pos - self.instructions_scroll_speed
                    )
                elif event.button == 5: # rueda abajo
                    self.instructions_scroll_pos = min(
                        self.instructions_max_scroll,
                        self.instructions_scroll_pos + self.instructions_scroll_speed
                    )

            if self.instructions_button.is_clicked(pos, event):
                self.showing_instructions = True

            if self.showing_instructions and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, 'close_btn') and self.close_btn.collidepoint(pos):
                    self.showing_instructions = False
            
            # Verificar clics en botones
            if self.play_button.is_clicked(mouse_pos, event) and self.play_button.active:
                if self.selected_card_index is not None:
                    # Jugada del jugador humano
                    played_card = self.game.player.hand[self.selected_card_index]
                    if played_card.type == "number":
                        # Iniciar la animación/espera para la jugada de la IA
                        self.waiting_for_ai = True
                        self.waiting_time = pygame.time.get_ticks()
                        
                        # Mostrar la carta jugada por el jugador
                        self.update_center_cards(player_card=played_card)
                        
                        # Jugar la carta pero aún no mostrar el resultado
                        self.turn_result = self.game.play_turn(self.selected_card_index)
                        self.selected_card_index = None
                    else:
                        self.game_message = "Solo puedes jugar cartas numéricas en tu turno"
            
            # Lógica para los demás botones
            if self.roulette_button.is_clicked(mouse_pos, event) and self.roulette_button.active:
                if self.game.current_loser == self.game.player:
                    result = self.game.use_roulette(self.game.player)
                    # Iniciar animación de la ruleta
                    self.roulette_vis.start_spin(self.game.roulette.get_probability(), result)
                    
                    if result:
                        self.game_message = "¡Has perdido en la ruleta!"
                        self.show_message_effect("¡BANG!", (255, 50, 50))
                        self.player_vis.set_alive(False)
                    else:
                        self.game_message = "Has sobrevivido a la ruleta"
                        self.show_message_effect("¡SAFE!", (50, 255, 50))
                        
                    # Desactivar los botones de decisión
                    self.roulette_button.set_active(False)
                    self.skill_button.set_active(False)
                    # Activar el botón de jugar para el siguiente turno (si no ha perdido)
                    if self.game.player.alive:
                        self.play_button.set_active(True)  # Añadir esta línea
                    self.update_card_objects()
                
            if self.skill_button.is_clicked(mouse_pos, event) and self.skill_button.active:
                if self.selected_card_index is not None and self.game.current_loser == self.game.player:
                    played_card = self.game.player.hand[self.selected_card_index]
                    if played_card.type == "skill":
                        # Verificar si ya se usó una habilidad en este turno
                        if self.game.skill_used_this_turn:
                            self.game_message = "Ya se usó una habilidad en este turno. Solo puedes usar la ruleta."
                        else:
                            result = self.game.player.use_skill_card(self.selected_card_index, self.game, self.game.ai_player)
                            if result:
                                self.game_message = f"Usaste la habilidad: {played_card.name}"
                                
                                # Desactivar los botones de decisión
                                self.roulette_button.set_active(False)
                                self.skill_button.set_active(False)
                                # Activar el botón de jugar para el siguiente turno
                                self.play_button.set_active(True)  # Añadir esta línea
                                self.update_card_objects()
                                
                                # Si la habilidad cambia el perdedor a la IA, hacer que responda
                                if self.game.current_loser == self.game.ai_player:
                                    # Desactivar botones hasta que la IA responda
                                    self.play_button.set_active(False)
                                    self.roulette_button.set_active(False)
                                    self.skill_button.set_active(False)
                                    
                                    # La IA solo puede usar la ruleta como respuesta
                                    self.game_message = "La IA perdió el turno tras tu habilidad y está decidiendo..."
                                    self.ai_thinking = True
                                    self.ai_decision_start_time = pygame.time.get_ticks()
                                    
                                    # Forzar a la IA a usar la ruleta
                                    try:
                                        result = self.game.use_roulette(self.game.ai_player)
                                        if result:
                                            self.game_message = "¡La IA perdió en la ruleta tras tu habilidad!"
                                        else:
                                            self.game_message = "La IA sobrevivió a la ruleta tras tu habilidad"
                                        self.ai_thinking = False
                                        self.play_button.set_active(True)  # Activar para siguiente turno
                                    except Exception as e:
                                        logging.error(f"Error en la respuesta de la IA: {e}", exc_info=True)
                                        self.game_message = "La IA tuvo un error y pasa su turno"
                                        self.play_button.set_active(True)
                                        self.ai_thinking = False
                                else:
                                    # No cambió el perdedor o hay empate
                                    self.play_button.set_active(True)
                            else:
                                self.game_message = "No se pudo usar la habilidad"
                        
                        # Desactivar los botones de decisión
                        self.roulette_button.set_active(False)
                        self.skill_button.set_active(False)
                        self.update_card_objects()
                    else:
                        self.game_message = "Selecciona una carta de habilidad"
    
    def update_roulette_display(self):
        """Actualiza la visualización de la ruleta con la probabilidad actual."""
        # Actualizar el valor de probabilidad de la visualizador con el valor actual del juego
        self.roulette_vis.probability = self.game.roulette.get_probability()
                
    def handle_ai_turn(self):
        """Maneja el turno de la IA, incluyendo animaciones y pausas."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.waiting_time
        
        # Esperar 1.5 segundos para mostrar la carta de la IA
        if elapsed_time > 1500 and not self.center_cards[-1].is_ai_card:
            # Mostrar la carta jugada por la IA
            if "ai_card" in self.turn_result:
                self.update_center_cards(
                    player_card=self.center_cards[0].card_data, 
                    ai_card=self.turn_result["ai_card"]
                )
        
        # Esperar 3 segundos para mostrar el resultado
        if elapsed_time > 3000:
            self.waiting_for_ai = False
            
            # Procesar el resultado del turno
            self.handle_turn_result(self.turn_result)
            
            # Actualizar las cartas en pantalla
            self.update_card_objects()
            
            # Verificar si alguien perdió y debe decidir entre ruleta o habilidad
            if hasattr(self.game, 'current_loser'):
                if self.game.current_loser == self.game.player:
                    # Activar botones de decisión para el jugador
                    self.roulette_button.set_active(True)
                    
                    # Solo activar el botón de habilidad si tiene cartas de habilidad
                    has_skill_cards = any(card.type == "skill" for card in self.game.player.hand)
                    self.skill_button.set_active(has_skill_cards)
                    
                    # Desactivar el botón de jugar carta mientras se decide
                    self.play_button.set_active(False)  # Añadir esta línea
                    
                    self.game_message = "Perdiste el turno. ¿Usar habilidad o girar la ruleta?"
                elif self.game.current_loser == self.game.ai_player:
                    # La IA decide automáticamente
                    self.game_message = "La IA perdió el turno y está decidiendo..."
                    self.ai_thinking = True
                    self.ai_decision_start_time = pygame.time.get_ticks()
                    
                    # Aquí implementamos la lógica de decisión de la IA
                    try:
                        logging.info("La IA está tomando una decisión después de perder...")
                        ai_decision = self.game.ai_decision_after_losing()
                        logging.info(f"Decisión de la IA: {ai_decision}")
                        
                        if ai_decision["choice"] == "skill":
                            logging.info(f"La IA usa una habilidad: {ai_decision.get('skill_name', 'desconocida')}")
                            # Verificar si ya se usó una habilidad en este turno
                            if self.game.skill_used_this_turn:
                                # La IA solo puede usar la ruleta
                                result = self.game.use_roulette(self.game.ai_player)
                                if result:
                                    self.game_message = "¡La IA perdió en la ruleta!"
                                else:
                                    self.game_message = "La IA sobrevivió a la ruleta"
                                self.play_button.set_active(True)
                            else:
                                # La IA puede usar una habilidad
                                if ai_decision.get("loser_changed", False) and self.game.current_loser == self.game.player:
                                    # El perdedor cambió, ahora el jugador debe decidir
                                    self.game_message = "La IA usó la habilidad y ahora tú pierdes el turno. Solo puedes usar la ruleta."
                                    self.roulette_button.set_active(True)
                                    self.skill_button.set_active(False)  # Desactivar habilidades
                                    self.play_button.set_active(False)  # Desactivar jugar carta hasta resolver
                                else:
                                    # La IA usó una habilidad pero sigue perdiendo o empate
                                    self.game_message = f"La IA usó la habilidad: {ai_decision['skill_name']}"
                                    self.play_button.set_active(True)  # Activar para siguiente turno
                        else:
                            logging.info(f"La IA decide usar la ruleta con probabilidad: {self.game.roulette.get_probability()}%")
                            result = self.game.use_roulette(self.game.ai_player)
                            logging.info(f"Resultado de la ruleta para la IA: {'muerte' if result else 'sobrevivió'}")
                            # Iniciar animación de la ruleta
                            self.roulette_vis.start_spin(self.game.roulette.get_probability(), result)
                            
                            # Actualizar mensaje según resultado
                            if result:
                                self.game_message = "¡La IA perdió en la ruleta!"
                                self.show_message_effect("¡IA ELIMINADA!", (255, 50, 50))
                                self.ai_vis.set_alive(False)
                            else:
                                self.game_message = "La IA sobrevivió a la ruleta"
                                self.show_message_effect("¡IA SAFE!", (50, 255, 50))
                                
                        self.update_card_objects()
                        
                    except Exception as e:
                        logging.error(f"Error en la decisión de la IA: {e}", exc_info=True)
                        self.game_message = "La IA tuvo un error y pasa su turno"
                        self.play_button.set_active(True)

                    self.ai_thinking = False
        
        # Procesar eventos de salida
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
    def handle_turn_result(self, result):
        """Maneja el resultado de un turno de juego."""
        if result["status"] == "error":
            self.game_message = result["message"]
        elif result["status"] == "win":
            self.game_message = f"¡{result['winner']} ha ganado! Razón: {result['reason']}"
        elif result["status"] == "tie":
            self.game_message = "¡Empate! Ambos jugadores conservan sus cartas."
        elif result["status"] == "continue":
            self.game_message = f"{result['turn_winner']} gana el turno."
    
    def draw(self):
        """Dibuja todos los elementos en la pantalla."""
        # Fondo
        self.screen.fill(BACKGROUND_COLOR)
        
        # Título y mensajes
        title = self.title_font.render(GAME_TITLE, True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Información de la IA
        ai_info = self.font.render(f"Cartas de la IA: {len(self.game.ai_player.hand)}", True, WHITE)
        self.screen.blit(ai_info, (50, 80))
        
        # Probabilidad de la ruleta
        roulette_text = self.font.render(
            f"Probabilidad de la ruleta: {self.game.roulette.get_probability()}%", 
            True, 
            WHITE
        )
        self.screen.blit(roulette_text, (SCREEN_WIDTH - 350, 80))
        
        # Dibujar el tablero de juego mejorado
        board_rect = pygame.Rect(SCREEN_WIDTH // 8, 100, SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 180)  # Cambiar 200 a 180
        pygame.draw.rect(self.screen, (40, 60, 40), board_rect, 0, 15)
        pygame.draw.rect(self.screen, (60, 80, 60), board_rect, 5, 15)
        
        # Dibujar líneas decorativas en el tablero
        for i in range(10):
            y = board_rect.top + i * (board_rect.height // 10)
            pygame.draw.line(self.screen, (50, 70, 50), 
                           (board_rect.left + 20, y), 
                           (board_rect.right - 20, y), 1)
        
        # Dibujar visualizaciones del jugador y la IA
        self.player_vis.draw(self.screen, self.font)
        self.ai_vis.draw(self.screen, self.font)
        
        # Dibujar ruleta
        self.roulette_vis.draw(self.screen, self.font)
        
        # Mensaje del juego
        if self.game_message:
            message = self.font.render(self.game_message, True, WHITE)
            self.screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Dibujar cartas del jugador
        for card in self.player_card_objects:
            card.draw(self.screen, self.font)
        
        # Dibujar cartas de la IA
        for card in self.ai_card_objects:
            card.draw(self.screen, self.font)
        
        # Dibujar cartas en el centro
        for card in self.center_cards:
            card.draw(self.screen, self.font)
        
        # Dibujar etiquetas para las áreas de cartas
        player_label = self.font.render("Tus cartas", True, WHITE)
        self.screen.blit(player_label, (50, SCREEN_HEIGHT - 230))
        
        # Dibujar botones
        for button in self.buttons:
            button.draw(self.screen, self.font)
            
        if self.showing_message_effect:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.message_effect_start_time
            
            if elapsed < 2000:  # Duración de 2 segundos
                # Calcular tamaño y opacidad según el tiempo
                max_size = 72
                min_size = 36
                
                if elapsed < 500:  # Primeros 0.5 segundos - creciendo
                    progress = elapsed / 500
                    size = min_size + (max_size - min_size) * progress
                    alpha = 255 * progress
                elif elapsed < 1500:  # 1 segundo mantenido
                    size = max_size
                    alpha = 255
                else:  # Últimos 0.5 segundos - desvaneciéndose
                    progress = (elapsed - 1500) / 500
                    size = max_size - (max_size - min_size) * progress
                    alpha = 255 * (1 - progress)
                
                # Crear superficie con transparencia
                message_font = pygame.font.SysFont(None, int(size))
                message_surf = message_font.render(self.message_effect_text, True, self.message_effect_color)
                
                # Añadir un efecto de sombra
                shadow_surf = message_font.render(self.message_effect_text, True, (0, 0, 0))
                shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3))
                message_surf.set_alpha(alpha)
                shadow_surf.set_alpha(alpha * 0.7)  # Sombra más transparente
                
                # Mostrar el mensaje
                message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(shadow_surf, shadow_rect)
                self.screen.blit(message_surf, message_rect)
            else:
                self.showing_message_effect = False
        
         # Dibujar botón de instrucciones
        self.instructions_button.draw(self.screen, pygame.font.SysFont(None, 24))

        if self.showing_instructions:
            self.draw_instructions_panel()

        pygame.display.flip()
        
    def draw_instructions_panel(self):
        """Dibuja el panel de instrucciones del juego con capacidad de scroll."""
        # Crear un panel semi-transparente
        panel = pygame.Surface((800, 600), pygame.SRCALPHA)
        panel.fill((30, 30, 50, 230))
        panel_pos = (SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 300)
        
        # Añadir un borde al panel
        pygame.draw.rect(panel, (200, 200, 200, 150), panel.get_rect(), 3, 15)
        
        # Título del panel (fijo, no hace scroll)
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("INSTRUCCIONES DEL JUEGO", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 40))
        panel.blit(title_text, title_rect)
        
        # Separador (fijo, no hace scroll)
        pygame.draw.line(panel, (200, 200, 200, 150), (50, 80), (750, 80), 2)
        
        # Crear una superficie para el contenido scrollable
        content_height = 1200  # Altura estimada del contenido
        content_surface = pygame.Surface((700, content_height), pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 0))  # Transparente
        
        # Instrucciones del juego - contenido extenso
        instructions = [
            "OBJETIVO: Eliminar al oponente o hacer que se quede sin cartas numéricas.",
            "",
            "REGLAS BÁSICAS:",
            "1. Cada jugador tiene cartas numéricas (1-10) y cartas de habilidad.",
            "2. En cada turno, ambos jugadores juegan una carta numérica. El valor más alto gana.",
            "3. El perdedor del turno debe tomar una decisión:",
            "   - Usar una carta de habilidad para cambiar la situación.",
            "   - Arriesgarse a girar la ruleta rusa.",
            "4. La ruleta comienza con 1% de probabilidad de 'muerte' y aumenta un 10% cada turno.",
            "5. El juego termina cuando un jugador 'muere' en la ruleta o se queda sin cartas numéricas.",
            "",
            "CARTAS DE HABILIDAD:",
            "• Aumento: Aumenta tu número en 3 puntos.",
            "• Intercambio: Intercambia tu carta con la del oponente.",
            "• Salvavidas: Te salva automáticamente sin usar la ruleta.",
            "• Duplicar: Duplica el valor de tu carta numérica.",
            "",
            "DINÁMICA DEL JUEGO:",
            "1. Al inicio de la partida, cada jugador recibe una mano de cartas aleatorias.",
            "2. En tu turno, selecciona una carta numérica para jugar contra la IA.",
            "3. El jugador con el valor más alto gana el turno.",
            "4. El perdedor debe decidir entre usar una carta de habilidad o girar la ruleta.",
            "5. Las cartas de habilidad pueden cambiar el resultado del turno o evitar la ruleta.",
            "6. Si eliges girar la ruleta, hay una probabilidad de 'muerte' que aumenta cada turno.",
            "7. El juego continúa hasta que un jugador muere en la ruleta o se queda sin cartas.",
            "",
            "ESTRATEGIA:",
            "• Guarda tus cartas numéricas altas para momentos críticos.",
            "• Las cartas de habilidad son valiosas cuando la probabilidad de la ruleta es alta.",
            "• La IA tomará decisiones basadas en la probabilidad de la ruleta y sus cartas disponibles.",
            "• No te arriesgues demasiado en los primeros turnos, la ruleta se vuelve más peligrosa.",
            "",
            "CONTROLES:",
            "• Haz clic en una carta para seleccionarla.",
            "• Usa los botones en la parte inferior para realizar acciones.",
            "• El botón 'Instrucciones' abre esta ventana de ayuda.",
            "",
            "¡Buena suerte y que gane el mejor estratega!"
        ]
        
        font = pygame.font.SysFont(None, 24)
        # calcular altura total
        y_acc = 0
        for line in instructions:
            surf = font.render(line, True, WHITE)
            y_acc += surf.get_height() + 5
        content_height = y_acc

        # crear superficie de contenido
        content_surface = pygame.Surface((700, content_height), pygame.SRCALPHA)
        y = 0
        for line in instructions:
            surf = font.render(line, True, WHITE)
            content_surface.blit(surf, (0, y))
            y += surf.get_height() + 5

        self.instructions_max_scroll = max(0, content_height - 470)
        self.instructions_scroll_pos = max(0, min(self.instructions_scroll_pos, self.instructions_max_scroll))

        content_rect = pygame.Rect(0, self.instructions_scroll_pos, 700, 470)
        panel.blit(content_surface.subsurface(content_rect), (50, 100))

        if self.instructions_max_scroll > 0:
            track_h = 430
            bar_h = max(50, track_h * (470 / content_height))
            bar_y = 120 + (track_h - bar_h) * (self.instructions_scroll_pos / self.instructions_max_scroll)
            pygame.draw.rect(panel, (80,80,80,150), (750,120,10,track_h), 0, 5)
            pygame.draw.rect(panel, (200,200,200,200), (750, bar_y, 10, bar_h), 0, 5)
            # flechas encima
            if self.instructions_scroll_pos>0:
                pygame.draw.polygon(panel, WHITE, [(755,120),(765,140),(745,140)])
            if self.instructions_scroll_pos<self.instructions_max_scroll:
                pygame.draw.polygon(panel, WHITE, [(755,550),(765,530),(745,530)])

        local_close = pygame.Rect(700, 40, 50, 30)
        pygame.draw.rect(panel, (200,50,50), local_close, 0, 10)
        pygame.draw.rect(panel, WHITE, local_close, 2, 10)
        x_surf = font.render("X", True, WHITE)
        panel.blit(x_surf, x_surf.get_rect(center=local_close.center))
        # mover a coords de pantalla para colisión
        self.close_btn = local_close.move(panel_pos)

        self.screen.blit(panel, panel_pos)
    
    def run(self):
        """Bucle principal del juego."""
        self.game.setup_game()
        self.update_card_objects()
        self.update_roulette_display()
        
        running = True
        while running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update_roulette_display()
            self.draw()
            
            if self.game.is_game_over():
                winner_name = self.game.winner.name if self.game.winner else "Empate"
                self.game_message = f"¡Juego terminado! Ganador: {winner_name}"
                self.show_message_effect("¡Juego Terminado!", (255, 50, 50))
                self.play_button.set_active(False)