"""
Sistema de Base de Datos - AgentOS
Gestión de conexión PostgreSQL y operaciones CRUD
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime

from .models import Base, Conversation, Message, AgentMemory, AgentKnowledge, SystemMetrics, ExecutionState

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de base de datos para AgentOS
    Maneja conexiones, sesiones y operaciones CRUD
    """
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa la conexión a la base de datos"""
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/agentdb")
        
        try:
            # Configurar engine con pool de conexiones
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Cambiar a True para debug SQL
            )
            
            # Crear SessionLocal
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Crear tablas si no existen
            self._create_tables()
            
            logger.info("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas si no existen"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Tablas de base de datos verificadas/creadas")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager para sesiones de base de datos"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error en sesión de BD: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("✅ Conexión a BD exitosa")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a BD: {e}")
            return False
    
    # ===============================
    # OPERACIONES DE CONVERSACIONES
    # ===============================
    
    def create_conversation(self, conversation_id: str, agent_id: str, extra_data: Dict = None) -> bool:
        """Crea una nueva conversación"""
        try:
            with self.get_session() as session:
                conversation = Conversation(
                    id=conversation_id,
                    agent_id=agent_id,
                    extra_data=extra_data or {}
                )
                session.add(conversation)
                session.commit()
                logger.info(f"✅ Conversación creada: {conversation_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error creando conversación {conversation_id}: {e}")
            return False
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   agent_id: str = None, tools_used: List = None) -> int:
        """Añade un mensaje a una conversación"""
        try:
            with self.get_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    agent_id=agent_id,
                    tools_used=tools_used or []
                )
                session.add(message)
                session.commit()
                logger.info(f"✅ Mensaje añadido a conversación {conversation_id}")
                return message.id
        except Exception as e:
            logger.error(f"❌ Error añadiendo mensaje a {conversation_id}: {e}")
            return 0
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene mensajes de una conversación"""
        try:
            with self.get_session() as session:
                messages = session.query(Message)\
                    .filter_by(conversation_id=conversation_id)\
                    .order_by(Message.timestamp.desc())\
                    .limit(limit)\
                    .all()
                
                return [{
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "agent_id": msg.agent_id,
                    "tools_used": msg.tools_used
                } for msg in reversed(messages)]  # Orden cronológico
        except Exception as e:
            logger.error(f"❌ Error obteniendo mensajes de {conversation_id}: {e}")
            return []
    
    # ===============================
    # OPERACIONES DE MEMORIA
    # ===============================
    
    def store_memory(self, agent_id: str, memory_type: str, content: str, 
                    context: str = None, importance_score: int = 5,
                    conversation_id: str = None, tags: List = None) -> int:
        """Almacena memoria de agente"""
        try:
            with self.get_session() as session:
                memory = AgentMemory(
                    agent_id=agent_id,
                    memory_type=memory_type,
                    content=content,
                    context=context,
                    importance_score=importance_score,
                    source_conversation_id=conversation_id,
                    tags=tags or []
                )
                session.add(memory)
                session.commit()
                
                logger.info(f"✅ Memoria almacenada para agente {agent_id}: {memory.id}")
                return memory.id
        except Exception as e:
            logger.error(f"❌ Error almacenando memoria para {agent_id}: {e}")
            return 0
    
    def get_agent_memories(self, agent_id: str, memory_type: str = None, 
                          limit: int = 10) -> List[Dict]:
        """Obtiene memorias de un agente"""
        try:
            with self.get_session() as session:
                query = session.query(AgentMemory).filter_by(agent_id=agent_id)
                
                if memory_type:
                    query = query.filter_by(memory_type=memory_type)
                
                memories = query.order_by(AgentMemory.importance_score.desc())\
                    .limit(limit).all()
                
                return [{
                    "id": mem.id,
                    "memory_type": mem.memory_type,
                    "content": mem.content,
                    "context": mem.context,
                    "importance_score": mem.importance_score,
                    "created_at": mem.created_at.isoformat(),
                    "tags": mem.tags
                } for mem in memories]
        except Exception as e:
            logger.error(f"❌ Error obteniendo memorias de {agent_id}: {e}")
            return []
    
    def update_memory_access(self, memory_id: int) -> bool:
        """Actualiza el timestamp de último acceso de una memoria"""
        try:
            with self.get_session() as session:
                memory = session.query(AgentMemory).filter_by(id=memory_id).first()
                if memory:
                    memory.last_accessed = datetime.utcnow()
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Error actualizando acceso de memoria {memory_id}: {e}")
            return False
    
    # ===============================
    # NUEVO: OPERACIONES DE EXECUTION STATE
    # ===============================
    
    def create_execution_state(self, task_id: str, session_id: str, query: str,
                              user_context: Dict = None, priority: str = "normal",
                              optimization_level: str = "balanced") -> bool:
        """Crea un nuevo estado de ejecución"""
        try:
            with self.get_session() as session:
                execution_state = ExecutionState(
                    task_id=task_id,
                    session_id=session_id,
                    original_query=query,
                    user_context=user_context or {},
                    priority=priority,
                    optimization_level=optimization_level,
                    status='running',
                    current_step=0,
                    total_steps=1
                )
                session.add(execution_state)
                session.commit()
                logger.info(f"✅ Estado de ejecución creado: {task_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error creando estado de ejecución {task_id}: {e}")
            return False
    
    def update_execution_state(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un estado de ejecución"""
        try:
            with self.get_session() as session:
                execution_state = session.query(ExecutionState).filter_by(task_id=task_id).first()
                if execution_state:
                    for key, value in updates.items():
                        if hasattr(execution_state, key):
                            setattr(execution_state, key, value)
                    session.commit()
                    logger.info(f"✅ Estado de ejecución actualizado: {task_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Error actualizando estado de ejecución {task_id}: {e}")
            return False
    
    def get_execution_state(self, task_id: str) -> Optional[Dict]:
        """Obtiene un estado de ejecución"""
        try:
            with self.get_session() as session:
                execution_state = session.query(ExecutionState).filter_by(task_id=task_id).first()
                if execution_state:
                    return {
                        "task_id": execution_state.task_id,
                        "session_id": execution_state.session_id,
                        "current_step": execution_state.current_step,
                        "total_steps": execution_state.total_steps,
                        "status": execution_state.status,
                        "context_window": execution_state.context_window,
                        "agent_states": execution_state.agent_states,
                        "intermediate_results": execution_state.intermediate_results,
                        "tool_executions": execution_state.tool_executions,
                        "original_query": execution_state.original_query,
                        "user_context": execution_state.user_context,
                        "priority": execution_state.priority,
                        "optimization_level": execution_state.optimization_level,
                        "intent_analysis": execution_state.intent_analysis,
                        "task_decomposition": execution_state.task_decomposition,
                        "selected_agents": execution_state.selected_agents,
                        "can_pause": execution_state.can_pause,
                        "can_resume": execution_state.can_resume,
                        "pause_requested": execution_state.pause_requested,
                        "created_at": execution_state.created_at.isoformat(),
                        "updated_at": execution_state.updated_at.isoformat(),
                        "started_at": execution_state.started_at.isoformat() if execution_state.started_at else None,
                        "paused_at": execution_state.paused_at.isoformat() if execution_state.paused_at else None,
                        "completed_at": execution_state.completed_at.isoformat() if execution_state.completed_at else None,
                        "execution_time": execution_state.execution_time,
                        "tokens_used": execution_state.tokens_used,
                        "memory_accessed": execution_state.memory_accessed,
                        "optimization_applied": execution_state.optimization_applied,
                        "error_details": execution_state.error_details,
                        "performance_metrics": execution_state.performance_metrics,
                        "extra_data": execution_state.extra_data
                    }
                return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de ejecución {task_id}: {e}")
            return None
    
    def pause_execution(self, task_id: str) -> bool:
        """Pausa una ejecución"""
        try:
            return self.update_execution_state(task_id, {
                "status": "paused",
                "pause_requested": True,
                "paused_at": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"❌ Error pausando ejecución {task_id}: {e}")
            return False
    
    def resume_execution(self, task_id: str) -> bool:
        """Reanuda una ejecución"""
        try:
            return self.update_execution_state(task_id, {
                "status": "running",
                "pause_requested": False,
                "paused_at": None
            })
        except Exception as e:
            logger.error(f"❌ Error reanudando ejecución {task_id}: {e}")
            return False
    
    def complete_execution(self, task_id: str, final_result: Dict = None) -> bool:
        """Marca una ejecución como completada"""
        try:
            updates = {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "current_step": -1  # Indicador de completado
            }
            if final_result:
                updates["extra_data"] = final_result
            
            return self.update_execution_state(task_id, updates)
        except Exception as e:
            logger.error(f"❌ Error completando ejecución {task_id}: {e}")
            return False
    
    def get_active_executions(self, limit: int = 50) -> List[Dict]:
        """Obtiene ejecuciones activas"""
        try:
            with self.get_session() as session:
                executions = session.query(ExecutionState)\
                    .filter(ExecutionState.status.in_(['running', 'paused']))\
                    .order_by(ExecutionState.created_at.desc())\
                    .limit(limit)\
                    .all()
                
                return [{
                    "task_id": exec.task_id,
                    "session_id": exec.session_id,
                    "status": exec.status,
                    "current_step": exec.current_step,
                    "total_steps": exec.total_steps,
                    "priority": exec.priority,
                    "created_at": exec.created_at.isoformat(),
                    "original_query": exec.original_query[:100] + "..." if len(exec.original_query) > 100 else exec.original_query
                } for exec in executions]
        except Exception as e:
            logger.error(f"❌ Error obteniendo ejecuciones activas: {e}")
            return []
    
    # ===============================
    # OPERACIONES DE CONOCIMIENTO
    # ===============================
    
    def store_knowledge(self, agent_id: str, knowledge_type: str, title: str,
                       content: str, description: str = None, confidence_score: int = 5) -> int:
        """Almacena conocimiento de agente"""
        try:
            with self.get_session() as session:
                knowledge = AgentKnowledge(
                    agent_id=agent_id,
                    knowledge_type=knowledge_type,
                    title=title,
                    description=description,
                    content=content,
                    confidence_score=confidence_score
                )
                session.add(knowledge)
                session.commit()
                
                logger.info(f"✅ Conocimiento almacenado para agente {agent_id}: {knowledge.id}")
                return knowledge.id
        except Exception as e:
            logger.error(f"❌ Error almacenando conocimiento para {agent_id}: {e}")
            return 0
    
    def get_agent_knowledge(self, agent_id: str, knowledge_type: str = None,
                           limit: int = 10) -> List[Dict]:
        """Obtiene conocimiento de un agente"""
        try:
            with self.get_session() as session:
                query = session.query(AgentKnowledge).filter_by(agent_id=agent_id)
                
                if knowledge_type:
                    query = query.filter_by(knowledge_type=knowledge_type)
                
                knowledge_items = query.order_by(AgentKnowledge.confidence_score.desc())\
                    .limit(limit).all()
                
                return [{
                    "id": item.id,
                    "knowledge_type": item.knowledge_type,
                    "title": item.title,
                    "description": item.description,
                    "content": item.content,
                    "confidence_score": item.confidence_score,
                    "usage_count": item.usage_count,
                    "success_rate": item.success_rate,
                    "created_at": item.created_at.isoformat()
                } for item in knowledge_items]
        except Exception as e:
            logger.error(f"❌ Error obteniendo conocimiento de {agent_id}: {e}")
            return []
    
    # ===============================
    # OPERACIONES DE MÉTRICAS
    # ===============================
    
    def store_metric(self, metric_type: str, metric_name: str, metric_value: str,
                    agent_id: str = None, conversation_id: str = None, 
                    task_id: str = None, extra_data: Dict = None) -> int:
        """Almacena una métrica del sistema"""
        try:
            with self.get_session() as session:
                metric = SystemMetrics(
                    metric_type=metric_type,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    task_id=task_id,
                    extra_data=extra_data or {}
                )
                session.add(metric)
                session.commit()
                return metric.id
        except Exception as e:
            logger.error(f"❌ Error almacenando métrica {metric_name}: {e}")
            return 0

# Instancia global del gestor de base de datos
db_manager = DatabaseManager() 
db_manager = DatabaseManager() 