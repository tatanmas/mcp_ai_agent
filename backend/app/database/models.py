"""
Modelos de Base de Datos - AgentOS Memoria Persistente
Compatible con sistema actual, migración gradual
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    """
    Tabla de conversaciones persistentes
    Reemplaza el dict in-memory actual
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)  # conversation_id
    agent_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON, default=dict)
    
    # Relación con mensajes
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Índices para búsqueda rápida
    __table_args__ = (
        Index('idx_conversation_agent', 'agent_id'),
        Index('idx_conversation_created', 'created_at'),
        Index('idx_conversation_active', 'is_active'),
    )

class Message(Base):
    """
    Tabla de mensajes individuales
    Reemplaza ChatMessage actual con persistencia
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey('conversations.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' o 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Metadatos adicionales
    agent_id = Column(String)
    tools_used = Column(JSON, default=list)  # Herramientas usadas en este mensaje
    extra_data = Column(JSON, default=dict)
    
    # Relación con conversación
    conversation = relationship("Conversation", back_populates="messages")
    
    # Índices para búsqueda rápida
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_role', 'role'),
        Index('idx_message_agent', 'agent_id'),
    )

class ExecutionState(Base):
    """
    NUEVO: Tabla de estados de ejecución persistentes
    Implementa Factor 9: Gestionar tu estado
    """
    __tablename__ = "execution_states"
    
    task_id = Column(String, primary_key=True)  # UUID único por tarea
    session_id = Column(String, nullable=False)  # Referencia a sesión del orquestador
    
    # Estado de progreso
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=1)
    status = Column(String, default='running')  # 'running', 'paused', 'completed', 'failed'
    
    # Contexto y estado
    context_window = Column(Text)  # Ventana de contexto actual serializada
    agent_states = Column(JSON, default=dict)  # Estado de cada agente
    intermediate_results = Column(JSON, default=list)  # Resultados intermedios
    tool_executions = Column(JSON, default=list)  # Herramientas ejecutadas
    
    # Query y configuración original
    original_query = Column(Text, nullable=False)
    user_context = Column(JSON, default=dict)
    priority = Column(String, default='normal')
    optimization_level = Column(String, default='balanced')
    
    # Análisis y planificación
    intent_analysis = Column(JSON, default=dict)
    task_decomposition = Column(JSON, default=list)
    selected_agents = Column(JSON, default=list)
    
    # Control de ejecución
    can_pause = Column(Boolean, default=True)
    can_resume = Column(Boolean, default=True)
    pause_requested = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    paused_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Métricas
    execution_time = Column(Integer, default=0)  # Segundos
    tokens_used = Column(Integer, default=0)
    memory_accessed = Column(Boolean, default=False)
    optimization_applied = Column(Boolean, default=False)
    
    # Metadatos adicionales
    error_details = Column(JSON, default=dict)
    performance_metrics = Column(JSON, default=dict)
    extra_data = Column(JSON, default=dict)
    
    # Índices para búsqueda optimizada
    __table_args__ = (
        Index('idx_execution_session', 'session_id'),
        Index('idx_execution_status', 'status'),
        Index('idx_execution_created', 'created_at'),
        Index('idx_execution_priority', 'priority'),
        Index('idx_execution_can_pause', 'can_pause'),
    )

class AgentMemory(Base):
    """
    Tabla de memoria de agentes
    Sistema avanzado de memoria persistente
    """
    __tablename__ = "agent_memory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    memory_type = Column(String, nullable=False)  # 'short_term', 'medium_term', 'long_term'
    content = Column(Text, nullable=False)
    context = Column(Text)  # Contexto adicional
    importance_score = Column(Integer, default=1)  # 1-10 para priorización
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Para short_term memory
    
    # Metadatos
    source_conversation_id = Column(String, nullable=True)
    source_message_id = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)  # Para categorización
    extra_data = Column(JSON, default=dict)
    
    # Índices para búsqueda optimizada
    __table_args__ = (
        Index('idx_memory_agent_type', 'agent_id', 'memory_type'),
        Index('idx_memory_importance', 'importance_score'),
        Index('idx_memory_created', 'created_at'),
        Index('idx_memory_accessed', 'last_accessed'),
        Index('idx_memory_expires', 'expires_at'),
    )

class AgentKnowledge(Base):
    """
    Tabla de conocimiento acumulado de agentes
    Para patrones, aprendizajes y insights
    """
    __tablename__ = "agent_knowledge"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    knowledge_type = Column(String, nullable=False)  # 'pattern', 'fact', 'procedure', 'preference'
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    
    # Métricas
    confidence_score = Column(Integer, default=5)  # 1-10
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer, default=100)  # Porcentaje
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Metadatos
    source_interactions = Column(JSON, default=list)  # IDs de conversaciones que generaron este conocimiento
    related_tools = Column(JSON, default=list)  # Herramientas relacionadas
    extra_data = Column(JSON, default=dict)
    
    # Índices
    __table_args__ = (
        Index('idx_knowledge_agent_type', 'agent_id', 'knowledge_type'),
        Index('idx_knowledge_confidence', 'confidence_score'),
        Index('idx_knowledge_usage', 'usage_count'),
        Index('idx_knowledge_title', 'title'),
    )

class SystemMetrics(Base):
    """
    Tabla de métricas del sistema
    Para monitoreo y optimización
    """
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String, nullable=False)  # 'performance', 'usage', 'error', 'optimization'
    metric_name = Column(String, nullable=False)
    metric_value = Column(String, nullable=False)
    
    # Contexto
    agent_id = Column(String, nullable=True)
    conversation_id = Column(String, nullable=True)
    task_id = Column(String, nullable=True)  # Nueva referencia a ExecutionState
    
    # Metadatos
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, default=dict)
    
    # Índices
    __table_args__ = (
        Index('idx_metrics_type', 'metric_type'),
        Index('idx_metrics_name', 'metric_name'),
        Index('idx_metrics_timestamp', 'timestamp'),
        Index('idx_metrics_task', 'task_id'),
    ) 