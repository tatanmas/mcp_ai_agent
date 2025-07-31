from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid
from enum import Enum


class ExecutionStatus(Enum):
    """Estados de ejecución del agente"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING_FOR_APPROVAL = "waiting_for_approval"


class AgentState:
    """Estado de un agente individual"""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.current_step = 0
        self.total_steps = 0
        self.retry_count = 0
        self.max_retries = 3
        self.status = ExecutionStatus.IDLE
        self.last_activity = datetime.now()
        self.context_data = {}
        self.output_data = {}


class StateManager:
    """Gestiona el estado de ejecución y negocio de los agentes"""
    
    def __init__(self):
        self.conversation_id: Optional[str] = None
        self.execution_state: Dict[str, Any] = {}
        self.business_state: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.agent_states: Dict[str, AgentState] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def start_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Inicia una nueva conversación"""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        self.conversation_id = conversation_id
        self.execution_state = {
            "status": ExecutionStatus.IDLE.value,
            "current_workflow": None,
            "current_step": 0,
            "total_steps": 0,
            "started_at": datetime.now().isoformat()
        }
        self.business_state = {
            "user_input": {},
            "pending_approvals": [],
            "completed_tasks": [],
            "errors": []
        }
        self.conversation_history = []
        self.agent_states = {}
        self.updated_at = datetime.now()
        
        return conversation_id
    
    def add_agent_state(self, agent_name: str) -> AgentState:
        """Agrega estado para un agente específico"""
        agent_state = AgentState(agent_name)
        self.agent_states[agent_name] = agent_state
        return agent_state
    
    def get_agent_state(self, agent_name: str) -> Optional[AgentState]:
        """Obtiene el estado de un agente específico"""
        return self.agent_states.get(agent_name)
    
    def update_execution_state(self, **kwargs):
        """Actualiza el estado de ejecución"""
        self.execution_state.update(kwargs)
        self.execution_state["updated_at"] = datetime.now().isoformat()
        self.updated_at = datetime.now()
    
    def update_business_state(self, **kwargs):
        """Actualiza el estado de negocio"""
        self.business_state.update(kwargs)
        self.updated_at = datetime.now()
    
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Agrega mensaje al historial de conversación"""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
    
    def can_pause(self) -> bool:
        """Verifica si la conversación puede ser pausada"""
        current_status = self.execution_state.get("status")
        return current_status in [ExecutionStatus.RUNNING.value, ExecutionStatus.WAITING_FOR_APPROVAL.value]
    
    def can_resume(self) -> bool:
        """Verifica si la conversación puede ser reanudada"""
        current_status = self.execution_state.get("status")
        return current_status == ExecutionStatus.PAUSED.value
    
    def pause_conversation(self, reason: str = "User requested pause"):
        """Pausa la conversación"""
        if self.can_pause():
            self.update_execution_state(
                status=ExecutionStatus.PAUSED.value,
                pause_reason=reason,
                paused_at=datetime.now().isoformat()
            )
            return True
        return False
    
    def resume_conversation(self):
        """Reanuda la conversación"""
        if self.can_resume():
            self.update_execution_state(
                status=ExecutionStatus.RUNNING.value,
                resumed_at=datetime.now().isoformat()
            )
            return True
        return False
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del estado actual"""
        return {
            "conversation_id": self.conversation_id,
            "execution_state": self.execution_state,
            "business_state": {
                "pending_approvals_count": len(self.business_state.get("pending_approvals", [])),
                "completed_tasks_count": len(self.business_state.get("completed_tasks", [])),
                "errors_count": len(self.business_state.get("errors", []))
            },
            "conversation_history_count": len(self.conversation_history),
            "agent_states_count": len(self.agent_states),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario para persistencia"""
        return {
            "conversation_id": self.conversation_id,
            "execution_state": self.execution_state,
            "business_state": self.business_state,
            "conversation_history": self.conversation_history,
            "agent_states": {
                name: {
                    "agent_name": state.agent_name,
                    "current_step": state.current_step,
                    "total_steps": state.total_steps,
                    "retry_count": state.retry_count,
                    "status": state.status.value,
                    "last_activity": state.last_activity.isoformat(),
                    "context_data": state.context_data,
                    "output_data": state.output_data
                }
                for name, state in self.agent_states.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateManager':
        """Crea un StateManager desde un diccionario"""
        state_manager = cls()
        state_manager.conversation_id = data.get("conversation_id")
        state_manager.execution_state = data.get("execution_state", {})
        state_manager.business_state = data.get("business_state", {})
        state_manager.conversation_history = data.get("conversation_history", [])
        
        # Reconstruir agent states
        for name, state_data in data.get("agent_states", {}).items():
            agent_state = AgentState(state_data["agent_name"])
            agent_state.current_step = state_data.get("current_step", 0)
            agent_state.total_steps = state_data.get("total_steps", 0)
            agent_state.retry_count = state_data.get("retry_count", 0)
            agent_state.status = ExecutionStatus(state_data.get("status", "idle"))
            agent_state.last_activity = datetime.fromisoformat(state_data.get("last_activity"))
            agent_state.context_data = state_data.get("context_data", {})
            agent_state.output_data = state_data.get("output_data", {})
            state_manager.agent_states[name] = agent_state
        
        state_manager.created_at = datetime.fromisoformat(data.get("created_at"))
        state_manager.updated_at = datetime.fromisoformat(data.get("updated_at"))
        
        return state_manager 