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
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_type = Column(String, nullable=False)  # 'performance', 'usage', 'error', 'tool_execution'
    agent_id = Column(String, nullable=True)
    
    # Métricas
    metric_name = Column(String, nullable=False)
    metric_value = Column(String, nullable=False)
    extra_data = Column(JSON, default=dict)
    
    # Índices
    __table_args__ = (
        Index('idx_metrics_timestamp', 'timestamp'),
        Index('idx_metrics_type', 'metric_type'),
        Index('idx_metrics_agent', 'agent_id'),
        Index('idx_metrics_name', 'metric_name'),
    ) 