import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pygame
from game.game_logic import Game
from ui.screens import GameScreen
from ai.gemini_player import AIPlayerWithGemini  # Cambiado a Gemini

def main():
    """Función principal que inicia el juego."""
    # Inicializar el juego
    game = Game()
    
    # Inicializar la IA con Gemini
    ai_player = AIPlayerWithGemini()  # Usamos Gemini en lugar de Ollama
    ai_player.initialize_conversation()
    
    # Inicializar la interfaz gráfica
    game_screen = GameScreen(game)
    
    # Ejecutar el juego
    try:
        game_screen.run()
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()