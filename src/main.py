import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pygame
from game.game_logic import Game
from ui.screens import GameScreen
from ai.ai_player import AIPlayerWithOllama  # Cambiado de AIPlayerWithGemini a AIPlayerWithOllama

def main():
    """Función principal que inicia el juego."""
    # Inicializar el juego
    game = Game()
    
    # Inicializar la IA con Ollama
    ai_player = AIPlayerWithOllama(model_name="llama3")  # Puedes cambiar a otro modelo que tengas instalado
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