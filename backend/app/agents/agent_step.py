from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json


class StepStatus(Enum):
    """Estados de un paso del agente"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_FOR_APPROVAL = "waiting_for_approval"


class StepType(Enum):
    """Tipos de pasos del agente"""
    ANALYSIS = "analysis"
    TOOL_EXECUTION = "tool_execution"
    DECISION = "decision"
    GENERATION = "generation"
    VALIDATION = "validation"
    COORDINATION = "coordination"
    HUMAN_INTERACTION = "human_interaction"


class AgentStep:
    """Representa un paso estructurado en la ejecución de un agente"""
    
    def __init__(
        self,
        step_id: str,
        step_type: StepType,
        name: str,
        description: str,
        agent_name: str,
        input_data: Optional[Dict[str, Any]] = None
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.name = name
        self.description = description
        self.agent_name = agent_name
        self.status = StepStatus.PENDING
        self.input_data = input_data or {}
        self.output_data = {}
        self.error_data = {}
        self.metadata = {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3
        self.execution_time: Optional[float] = None
        self.tool_calls: List[Dict[str, Any]] = []
        self.context_used: List[str] = []
    
    def start(self):
        """Marca el paso como iniciado"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, output_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Marca el paso como completado"""
        self.status = StepStatus.COMPLETED
        self.output_data = output_data
        self.metadata.update(metadata or {})
        self.completed_at = datetime.now()
        self._calculate_execution_time()
    
    def fail(self, error: Exception, context: str = ""):
        """Marca el paso como fallido"""
        self.status = StepStatus.FAILED
        self.error_data = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.completed_at = datetime.now()
        self._calculate_execution_time()
    
    def skip(self, reason: str = ""):
        """Marca el paso como omitido"""
        self.status = StepStatus.SKIPPED
        self.metadata["skip_reason"] = reason
        self.completed_at = datetime.now()
        self._calculate_execution_time()
    
    def wait_for_approval(self, approval_data: Dict[str, Any]):
        """Marca el paso como esperando aprobación"""
        self.status = StepStatus.WAITING_FOR_APPROVAL
        self.metadata["approval_data"] = approval_data
        self.completed_at = datetime.now()
        self._calculate_execution_time()
    
    def retry(self):
        """Incrementa el contador de reintentos"""
        self.retry_count += 1
        self.status = StepStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.execution_time = None
        self.error_data = {}
    
    def can_retry(self) -> bool:
        """Verifica si el paso puede ser reintentado"""
        return self.retry_count < self.max_retries and self.status == StepStatus.FAILED
    
    def add_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Optional[Any] = None):
        """Agrega una llamada a herramienta al paso"""
        tool_call = {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.tool_calls.append(tool_call)
    
    def add_context_used(self, context_key: str):
        """Agrega contexto utilizado al paso"""
        if context_key not in self.context_used:
            self.context_used.append(context_key)
    
    def _calculate_execution_time(self):
        """Calcula el tiempo de ejecución del paso"""
        if self.started_at and self.completed_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el paso a diccionario"""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "name": self.name,
            "description": self.description,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_data": self.error_data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "execution_time": self.execution_time,
            "tool_calls": self.tool_calls,
            "context_used": self.context_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStep':
        """Crea un AgentStep desde un diccionario"""
        step = cls(
            step_id=data["step_id"],
            step_type=StepType(data["step_type"]),
            name=data["name"],
            description=data["description"],
            agent_name=data["agent_name"],
            input_data=data.get("input_data", {})
        )
        
        step.status = StepStatus(data["status"])
        step.output_data = data.get("output_data", {})
        step.error_data = data.get("error_data", {})
        step.metadata = data.get("metadata", {})
        step.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("started_at"):
            step.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            step.completed_at = datetime.fromisoformat(data["completed_at"])
        
        step.retry_count = data.get("retry_count", 0)
        step.max_retries = data.get("max_retries", 3)
        step.execution_time = data.get("execution_time")
        step.tool_calls = data.get("tool_calls", [])
        step.context_used = data.get("context_used", [])
        
        return step
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del paso"""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "step_type": self.step_type.value,
            "execution_time": self.execution_time,
            "retry_count": self.retry_count,
            "tool_calls_count": len(self.tool_calls),
            "context_used_count": len(self.context_used),
            "has_error": bool(self.error_data),
            "has_output": bool(self.output_data)
        }
    
    def __str__(self) -> str:
        return f"AgentStep({self.step_id}: {self.name} - {self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__() 