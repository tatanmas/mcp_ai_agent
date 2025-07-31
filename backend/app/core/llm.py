from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from typing import List, Dict, Any


class LLMClient:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.default_llm_model,
            google_api_key=settings.google_api_key,
            temperature=0.7,
            max_output_tokens=2048,
            convert_system_message_to_human=True
        )
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Genera una respuesta usando LangChain con Gemini"""
        try:
            # Convertir mensajes al formato de LangChain
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            # Validar que hay mensajes para procesar
            if not langchain_messages:
                return "Error: No hay mensajes para procesar"
            
            # Si solo hay mensajes de sistema, agregar un mensaje de usuario por defecto
            system_messages = [msg for msg in langchain_messages if isinstance(msg, SystemMessage)]
            user_messages = [msg for msg in langchain_messages if isinstance(msg, HumanMessage)]
            
            if system_messages and not user_messages:
                langchain_messages.append(HumanMessage(content="Por favor, procesa la información proporcionada."))
            
            # Generar respuesta
            response = await self.llm.ainvoke(langchain_messages)
            return response.content
            
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    async def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analiza una tarea para determinar qué agente especializado necesita"""
        messages = [
            {
                "role": "system",
                "content": """Eres un analizador de tareas. Analiza la consulta y determina qué tipo de especialista necesita.

Tipos de especialistas disponibles:
- "tech": Para preguntas sobre tecnología, desarrollo, programación, arquitectura de software, APIs, bases de datos, DevOps, etc.
- "business": Para preguntas sobre estrategia de negocios, marketing, ventas, pricing, modelos de negocio, análisis de mercado, etc.
- "analysis": Para preguntas sobre análisis de datos, estadísticas, métricas, reportes, visualización de datos, etc.

Responde ÚNICAMENTE en formato JSON:
{
    "specialist_type": "tech|business|analysis",
    "confidence": 0.0-1.0,
    "reasoning": "explicación detallada"
}"""
            },
            {
                "role": "user",
                "content": f"Analiza esta tarea: {task}"
            }
        ]
        
        try:
            response = await self.generate_response(messages)
            
            # Intentar parsear JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                if all(key in result for key in ["specialist_type", "confidence", "reasoning"]):
                    return result
            
            # Fallback
            return {
                "specialist_type": "tech",
                "confidence": 0.5,
                "reasoning": f"No se pudo analizar automáticamente: {response[:100]}..."
            }
            
        except Exception as e:
            return {
                "specialist_type": "tech",
                "confidence": 0.3,
                "reasoning": f"Error en análisis: {str(e)}"
            } 