from decouple import config
from openai import OpenAI
from typing import Generator, List, Dict, Any

# Constantes
DEEPSEEK_API_KEY = config("DEEPSEEK_API_KEY", default=None)
DEEPSEEK_MODEL = "deepseek-chat"

class AIClient:
    """Clase para manejar las interacciones con la API de DeepSeek."""
    
    @staticmethod
    def get_client() -> OpenAI:
        """Crea una nueva instancia del cliente OpenAI."""
        return OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
        )

    @staticmethod
    def create_completion(messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Crea una nueva completion usando el modelo DeepSeek."""
        client = AIClient.get_client()
        completion = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        return completion

def get_llm_response(messages: List[Dict[str, Any]]) -> str:
    """Obtiene la respuesta del modelo de lenguaje."""
    completion = AIClient.create_completion(messages)
    answer = ""
    
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            answer += chunk.choices[0].delta.content
    
    return answer