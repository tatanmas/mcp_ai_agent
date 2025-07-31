from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from app.core.llm import LLMClient
from app.state.state_manager import StateManager
from app.agents.agent_step import AgentStep, StepType, StepStatus


class EnhancedBaseAgent:
    """Agente base mejorado con los 12 factores de los agentes de IA"""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        max_context_tokens: int = 4000,
        max_retries: int = 3
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.max_context_tokens = max_context_tokens
        self.max_retries = max_retries
        
        # Componentes principales
        self.llm_client = LLMClient()
        self.state_manager = StateManager()
        
        # Estado de ejecución
        self.current_step: Optional[AgentStep] = None
        self.step_history: List[AgentStep] = []
        self.is_running = False
    
    async def execute_step(
        self,
        step_type: StepType,
        step_name: str,
        step_description: str,
        input_data: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> AgentStep:
        """Ejecuta un paso del agente con control de flujo estructurado"""
        
        # Crear paso
        step = AgentStep(
            step_id=str(uuid.uuid4()),
            step_type=step_type,
            name=step_name,
            description=step_description,
            agent_name=self.name,
            input_data=input_data or {}
        )
        
        self.current_step = step
        self.step_history.append(step)
        
        try:
            # Iniciar paso
            step.start()
            self.is_running = True
            
            # Construir contexto para el LLM
            context = self._build_context_window(input_data or {})
            step.add_context_used("main_context")
            
            # Ejecutar LLM con contexto optimizado
            response = await self._execute_llm_with_context(context, step)
            
            # Procesar respuesta
            output_data = self._parse_llm_response(response, step)
            
            # Completar paso
            step.complete(output_data, {"context_tokens": len(context)})
            
            # Actualizar estado
            self._update_state_after_step(step, conversation_id)
            
            return step
            
        except Exception as e:
            # Manejar error
            step.fail(e, f"Error en paso: {step_name}")
            
            # Reintentar si es posible
            if step.can_retry():
                step.retry()
                return await self.execute_step(step_type, step_name, step_description, input_data, conversation_id)
            
            raise e
        
        finally:
            self.is_running = False
            self.current_step = None
    
    def _build_context_window(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Construye la ventana de contexto optimizada"""
        
        context = []
        
        # Construir el prompt del sistema combinado
        system_parts = [self.system_prompt]
        
        # Si hay contexto específico de pregunta, agregarlo al sistema
        if "question_context" in input_data:
            system_parts.append(f"CONTEXTO ESPECÍFICO PARA LA PREGUNTA:\n{input_data['question_context']}")
        
        # Combinar todos los mensajes de sistema en uno solo
        combined_system = "\n\n".join(system_parts)
        context.append({
            "role": "system",
            "content": combined_system,
            "metadata": {"type": "system_prompt"},
            "priority": 1
        })
        
        # Agregar la pregunta específica
        if "question" in input_data:
            question_text = input_data["question"].get("question_text", "")
            context.append({
                "role": "user",
                "content": f"PREGUNTA: {question_text}",
                "metadata": {"type": "question"},
                "priority": 1
            })
        else:
            # Fallback: agregar datos de entrada al contexto
            if input_data:
                context.append({
                    "role": "user",
                    "content": str(input_data),
                    "metadata": {"type": "input_data"},
                    "priority": 1
                })
        
        return context
    
    async def _execute_llm_with_context(self, context: List[Dict[str, Any]], step: AgentStep) -> str:
        """Ejecuta el LLM con el contexto optimizado"""
        
        # Verificar límites de contexto
        total_tokens = sum(len(msg.get("content", "")) // 3 for msg in context)
        if total_tokens > self.max_context_tokens * 0.98:
            # Crear resumen si es necesario
            summary = self._summarize_context(context)
            context = [
                {
                    "role": "system",
                    "content": f"Resumen del contexto anterior: {summary}",
                    "metadata": {"type": "context_summary"},
                    "priority": 1
                }
            ]
        
        # Ejecutar LLM
        response = await self.llm_client.generate_response(context)
        
        # Registrar en el paso
        step.add_tool_call("llm_generation", {"context_length": len(context)}, response)
        
        return response
    
    def _summarize_context(self, context: List[Dict[str, Any]]) -> str:
        """Crea un resumen del contexto para reducir tokens"""
        if len(context) <= 3:
            return "Contexto actual es corto, no necesita resumen."
        
        # Tomar los mensajes más importantes
        important_messages = [msg for msg in context if msg.get("priority", 2) == 1]
        
        if not important_messages:
            # Si no hay mensajes importantes, tomar los últimos 2 mensajes
            important_messages = context[-2:] if len(context) >= 2 else context
        
        summary_parts = []
        for msg in important_messages:
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_parts.append(f"{role}: {content}")
        
        return f"Resumen del contexto: {' | '.join(summary_parts)}"
    
    def _parse_llm_response(self, response: str, step: AgentStep) -> Dict[str, Any]:
        """Parsea la respuesta del LLM"""
        
        # Intentar parsear JSON si es posible
        try:
            import json
            parsed_response = json.loads(response)
            return {
                "type": "structured",
                "content": parsed_response,
                "raw_response": response
            }
        except json.JSONDecodeError:
            # Respuesta de texto plano
            return {
                "type": "text",
                "content": response,
                "raw_response": response
            }
    
    def _update_state_after_step(self, step: AgentStep, conversation_id: Optional[str]):
        """Actualiza el estado después de completar un paso"""
        
        if conversation_id:
            self.state_manager.conversation_id = conversation_id
        
        # Actualizar estado de ejecución
        self.state_manager.update_execution_state(
            current_step=step.step_id,
            last_step_type=step.step_type.value,
            last_step_name=step.name
        )
        
        # Agregar al historial
        self.state_manager.add_to_history(
            role="agent",
            content=f"Paso completado: {step.name}",
            metadata={
                "step_id": step.step_id,
                "step_type": step.step_type.value,
                "execution_time": step.execution_time,
                "status": step.status.value
            }
        )
    
    def can_pause(self) -> bool:
        """Verifica si el agente puede ser pausado"""
        return self.is_running and self.current_step is not None
    
    def pause_execution(self, reason: str = "User requested pause") -> bool:
        """Pausa la ejecución del agente"""
        if self.can_pause():
            self.state_manager.pause_conversation(reason)
            return True
        return False
    
    def resume_execution(self) -> bool:
        """Reanuda la ejecución del agente"""
        return self.state_manager.resume_conversation()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la ejecución del agente"""
        return {
            "agent_name": self.name,
            "is_running": self.is_running,
            "current_step": self.current_step.get_summary() if self.current_step else None,
            "total_steps": len(self.step_history),
            "completed_steps": len([s for s in self.step_history if s.status == StepStatus.COMPLETED]),
            "failed_steps": len([s for s in self.step_history if s.status == StepStatus.FAILED]),
            "state_summary": self.state_manager.get_state_summary()
        }
    
    def get_agent_info(self) -> Dict[str, str]:
        """Retorna información del agente"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "max_context_tokens": str(self.max_context_tokens),
            "max_retries": str(self.max_retries)
        }
    
    def reset(self):
        """Reinicia el estado del agente"""
        self.step_history = []
        self.current_step = None
        self.is_running = False
        self.state_manager = StateManager()
    
    def save_state(self, conversation_id: str):
        """Guarda el estado del agente"""
        # Aquí se implementaría la persistencia a PostgreSQL
        # Por ahora solo actualizamos el conversation_id
        self.state_manager.conversation_id = conversation_id
    
    def load_state(self, conversation_id: str):
        """Carga el estado del agente"""
        # Aquí se implementaría la carga desde PostgreSQL
        # Por ahora solo actualizamos el conversation_id
        self.state_manager.conversation_id = conversation_id 