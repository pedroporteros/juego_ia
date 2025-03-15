import pygame
from config.settings import BLACK

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
        if not self.active:
            color = (150, 150, 150)  # Gris para botones inactivos
        else:
            color = self.hover_color if self.hovered else self.color
            
        pygame.draw.rect(screen, color, self.rect, 0, 10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, 10)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        if not self.active:
            return False
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