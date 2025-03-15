import requests
import json
import os
import sys
import logging
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import OLLAMA_URL

# Configurar logging
log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"ai_player_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # También mostrar en consola
    ]
)

class AIPlayerWithOllama:
    """Implementa un jugador de IA que usa Ollama para tomar decisiones."""
    
    def __init__(self, model_name="llama3"):
        # Configurar la URL de Ollama
        self.base_url = OLLAMA_URL
        self.model = model_name
        logging.info(f"Inicializando AIPlayerWithOllama usando modelo: {model_name}")
        logging.info(f"URL de Ollama: {self.base_url}")
        
        # Sistema de memoria para el contexto del juego
        self.game_memory = []
        
    def initialize_conversation(self):
        """Inicializa la conversación con la IA explicándole el juego."""
        system_prompt = """
        Eres una IA que juega un juego de cartas llamado "Ruleta Rusa con Cartas". Las reglas son:
        1. Tienes cartas numéricas (1-10) y cartas de habilidad.
        2. En cada turno, ambos jugadores juegan una carta numérica. El número más alto gana.
        3. Si pierdes, puedes usar una carta de habilidad o arriesgarte con una ruleta rusa.
        4. Las habilidades incluyen: aumentar tu número, intercambiar cartas, o bloquear efectos.
        5. La ruleta empieza con 1% de probabilidad de "muerte" y aumenta 10% cada turno.
        6. El juego termina cuando un jugador "muere" en la ruleta o se acaban las cartas numéricas.
        
        Tu objetivo es ganar el juego tomando decisiones estratégicas sobre qué cartas jugar y cuándo arriesgarte.
        """
        
        self.game_memory.append({"role": "system", "content": system_prompt})
        logging.info("Conversación inicializada con sistema de reglas")
    
    def make_decision(self, game_state):
        """
        Solicita a la IA local una decisión basada en el estado actual del juego.
        
        Args:
            game_state: Diccionario con el estado actual del juego
            
        Returns:
            dict: Decisión tomada por la IA
        """
        # Convertir el estado del juego a un formato legible para la IA
        state_description = self._format_game_state(game_state)
        logging.info("Estado del juego formateado para la IA:")
        logging.info(state_description)
        
        # Añadir el estado a la memoria
        self.game_memory.append({"role": "user", "content": state_description})
        
        # Crear el prompt para la IA
        prompt = f"""
        Basado en el estado actual del juego:
        {state_description}
        
        Por favor, toma una decisión estratégica:
        1. ¿Qué carta numérica deberías jugar? Elige la mejor opción.
        2. Si pierdes este turno, ¿deberías usar una carta de habilidad o arriesgarte con la ruleta?
        
        Responde con un formato JSON como este:
        {{
            "card_to_play": indice_de_la_carta,
            "if_lose_choice": "skill" o "roulette",
            "skill_card_index": índice_de_la_carta_de_habilidad (si elegiste skill),
            "reasoning": "breve explicación de tu decisión"
        }}
        """
        
        messages = [{"role": "system", "content": self.game_memory[0]["content"]}]
        messages.append({"role": "user", "content": prompt})
        
        logging.info("Enviando prompt a Ollama...")
        
        try:
            # Hacer la solicitud a Ollama
            response_text = self._call_ollama(messages)
            
            # Añadir la respuesta a la memoria
            self.game_memory.append({"role": "model", "content": response_text})
            
            # Registrar la respuesta completa
            logging.info("Respuesta completa de Ollama:")
            logging.info(response_text)
            
            # Extraer el JSON de la respuesta
            json_str = self._extract_json(response_text)
            logging.info(f"JSON extraído: {json_str}")
            
            if json_str:
                decision = json.loads(json_str)
                logging.info(f"Decisión parseada exitosamente: {decision}")
            else:
                # Si no hay JSON, crearemos uno por defecto
                decision = {
                    "card_to_play": 0,  # Primera carta
                    "if_lose_choice": "roulette",
                    "skill_card_index": None,
                    "reasoning": "Decisión por defecto debido a un error en la salida"
                }
                logging.warning("No se pudo extraer JSON, usando decisión por defecto")
            
            return decision
            
        except Exception as e:
            logging.error(f"Error al comunicarse con Ollama: {e}", exc_info=True)
            # Devolver una decisión por defecto en caso de error
            return {
                "card_to_play": 0,  # Primera carta
                "if_lose_choice": "roulette",
                "skill_card_index": None,
                "reasoning": "Error en la comunicación con la IA"
            }
    
    def _call_ollama(self, messages):
        """Realiza una llamada a la API de Ollama."""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        logging.info(f"Enviando solicitud a {url}")
        logging.info(f"Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(url, json=payload)
            logging.info(f"Respuesta recibida - Status: {response.status_code}")
            
            if response.status_code == 200:
                logging.info("Solicitud exitosa")
                response_data = response.json()
                return response_data["message"]["content"]
            else:
                error_msg = f"Error en la llamada a Ollama: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar a Ollama. Asegúrate de que el servidor esté en ejecución."
            logging.critical(error_msg)
            raise Exception(error_msg)
    
    def _extract_json(self, text):
        """Extrae JSON de la respuesta de texto."""
        logging.info("Intentando extraer JSON de la respuesta...")
        
        # Buscamos el primer { y el último }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and start < end:
            json_str = text[start:end+1]
            try:
                # Verificar que es un JSON válido
                json.loads(json_str)
                logging.info("JSON encontrado en formato directo")
                return json_str
            except json.JSONDecodeError as e:
                logging.warning(f"JSON inválido encontrado: {e}")
        
        # Si no pudimos encontrar un JSON válido, intentamos con ```json ... ```
        import re
        json_blocks = re.findall(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
        if json_blocks:
            try:
                # Verificar que el primer bloque es un JSON válido
                json.loads(json_blocks[0])
                logging.info("JSON encontrado en bloque de código")
                return json_blocks[0]
            except json.JSONDecodeError as e:
                logging.warning(f"JSON inválido encontrado en bloque de código: {e}")
        
        logging.warning("No se encontró ningún JSON válido en la respuesta")
        return None
    
    def _format_game_state(self, game_state):
        """Formatea el estado del juego para la IA."""
        hand = game_state["hand"]
        hand_description = "Tus cartas son:\n"
        
        # Añade información sobre las cartas numéricas y de habilidad por separado
        number_cards = []
        skill_cards = []
        
        for i, card in enumerate(hand):
            if card.type == "number":
                number_cards.append(f"{i}: Carta Numérica {card.value}")
            else:
                skill_cards.append(f"{i}: Habilidad '{card.name}' - {card.description}")
        
        hand_description += "\nCartas numéricas:\n"
        hand_description += "\n".join(number_cards) if number_cards else "No tienes cartas numéricas"
        
        hand_description += "\n\nCartas de habilidad:\n"
        hand_description += "\n".join(skill_cards) if skill_cards else "No tienes cartas de habilidad"
        
        return f"""
        {hand_description}
        
        Última carta jugada por el oponente: {game_state.get('opponent_last_card', 'Ninguna')}
        Probabilidad actual de la ruleta: {game_state.get('roulette_probability', 1)}%
        Turno actual: {game_state.get('turn_count', 0)}
        """
        
    def _call_ollama(self, messages, timeout=10):
        """Realiza una llamada a la API de Ollama con timeout."""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        logging.info(f"Enviando solicitud a {url}")
        logging.info(f"Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            logging.info(f"Respuesta recibida - Status: {response.status_code}")
            
            if response.status_code == 200:
                logging.info("Solicitud exitosa")
                response_data = response.json()
                return response_data["message"]["content"]
            else:
                error_msg = f"Error en la llamada a Ollama: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = f"Timeout en la solicitud a Ollama después de {timeout} segundos"
            logging.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar a Ollama. Asegúrate de que el servidor esté en ejecución."
            logging.critical(error_msg)
            raise Exception(error_msg)