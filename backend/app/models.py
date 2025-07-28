"""
Modelos Pydantic para AgentOS
Centraliza todos los modelos para evitar circular imports
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class PriorityLevel(str, Enum):
    """Niveles de prioridad para tareas"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class OptimizationLevel(str, Enum):
    """Niveles de optimización"""
    MINIMAL = "minimal"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMAL = "maximal"

class UnifiedTaskRequest(BaseModel):
    """Modelo unificado para solicitudes de tareas"""
    query: str = Field(..., description="Consulta o tarea a ejecutar")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto adicional")
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL, description="Prioridad de la tarea")
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.BALANCED, description="Nivel de optimización")
    trackable: bool = Field(default=False, description="Si la tarea debe ser trackeable")

class TaskResponse(BaseModel):
    """Respuesta básica de tarea"""
    result: str
    success: bool
    task_id: Optional[str] = None
    session_id: Optional[str] = None

class SystemStatusResponse(BaseModel):
    """Respuesta de estado del sistema"""
    status: str
    version: str
    components: Dict[str, str]
    uptime: float
    memory_usage: Dict[str, Any]
    active_tasks: int

class CognitiveAgentRequest(BaseModel):
    """Solicitud para agentes cognitivos"""
    query: str = Field(..., description="Consulta para agentes cognitivos")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto adicional")
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL, description="Prioridad")
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.BALANCED, description="Optimización")
    use_cognitive_agents: bool = Field(default=True, description="Usar agentes cognitivos")

class CognitiveAgentResponse(BaseModel):
    """Respuesta de agentes cognitivos"""
    success: bool
    result: str
    cognitive_agents_used: List[str] = Field(default_factory=list, description="Agentes utilizados")
    learning_updated: bool = Field(default=False, description="Si se actualizó el aprendizaje")
    final_synthesis: Optional[str] = Field(default=None, description="Síntesis final")
    execution_time: float = Field(default=0.0, description="Tiempo de ejecución")

class ToolExecutionRequest(BaseModel):
    """Solicitud de ejecución de herramienta"""
    tool_name: str = Field(..., description="Nombre de la herramienta")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos de la herramienta")

class ToolExecutionResponse(BaseModel):
    """Respuesta de ejecución de herramienta"""
    success: bool
    tool_name: str
    result: Any
    execution_time: float
    error_message: Optional[str] = None 