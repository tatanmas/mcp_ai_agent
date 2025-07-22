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

from .models import Base, Conversation, Message, AgentMemory, AgentKnowledge, SystemMetrics

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
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Obtiene una conversación por ID"""
        try:
            with self.get_session() as session:
                conversation = session.query(Conversation).filter_by(id=conversation_id).first()
                if conversation:
                    return {
                        "id": conversation.id,
                        "agent_id": conversation.agent_id,
                        "created_at": conversation.created_at.isoformat(),
                        "updated_at": conversation.updated_at.isoformat(),
                        "is_active": conversation.is_active,
                        "extra_data": conversation.extra_data,
                        "message_count": len(conversation.messages)
                    }
                return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversación {conversation_id}: {e}")
            return None
    
    def add_message(self, conversation_id: str, role: str, content: str, agent_id: str = None, tools_used: List = None) -> bool:
        """Agrega un mensaje a una conversación"""
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
                
                # Actualizar timestamp de conversación
                conversation = session.query(Conversation).filter_by(id=conversation_id).first()
                if conversation:
                    conversation.updated_at = message.timestamp
                
                session.commit()
                logger.info(f"✅ Mensaje agregado a {conversation_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error agregando mensaje a {conversation_id}: {e}")
            return False
    
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
    
    def recall_memory(self, agent_id: str, memory_type: str = None, 
                     search_term: str = None, limit: int = 10) -> List[Dict]:
        """Recupera memoria de agente"""
        try:
            with self.get_session() as session:
                query = session.query(AgentMemory).filter_by(agent_id=agent_id)
                
                if memory_type:
                    query = query.filter_by(memory_type=memory_type)
                
                if search_term:
                    query = query.filter(AgentMemory.content.ilike(f"%{search_term}%"))
                
                memories = query.order_by(AgentMemory.importance_score.desc(), 
                                        AgentMemory.last_accessed.desc())\
                               .limit(limit)\
                               .all()
                
                # Actualizar last_accessed
                for memory in memories:
                    memory.last_accessed = memory.created_at  # Simplificado para MVP
                session.commit()
                
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
            logger.error(f"❌ Error recuperando memoria de {agent_id}: {e}")
            return []
    
    def get_memory_stats(self, agent_id: str) -> Dict:
        """Obtiene estadísticas de memoria de un agente"""
        try:
            with self.get_session() as session:
                total = session.query(AgentMemory).filter_by(agent_id=agent_id).count()
                short_term = session.query(AgentMemory)\
                    .filter_by(agent_id=agent_id, memory_type="short_term").count()
                medium_term = session.query(AgentMemory)\
                    .filter_by(agent_id=agent_id, memory_type="medium_term").count()
                long_term = session.query(AgentMemory)\
                    .filter_by(agent_id=agent_id, memory_type="long_term").count()
                
                return {
                    "total_memories": total,
                    "short_term": short_term,
                    "medium_term": medium_term,
                    "long_term": long_term
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats de memoria para {agent_id}: {e}")
            return {"total_memories": 0, "short_term": 0, "medium_term": 0, "long_term": 0}
    
    # ===============================
    # OPERACIONES DE MÉTRICAS
    # ===============================
    
    def log_metric(self, metric_type: str, metric_name: str, metric_value: str, 
                  agent_id: str = None, extra_data: Dict = None) -> bool:
        """Registra una métrica del sistema"""
        try:
            with self.get_session() as session:
                metric = SystemMetrics(
                    metric_type=metric_type,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    agent_id=agent_id,
                    extra_data=extra_data or {}
                )
                session.add(metric)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Error registrando métrica {metric_name}: {e}")
            return False
    
    def get_system_stats(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        try:
            with self.get_session() as session:
                total_conversations = session.query(Conversation).count()
                active_conversations = session.query(Conversation).filter_by(is_active=True).count()
                total_messages = session.query(Message).count()
                total_memories = session.query(AgentMemory).count()
                
                return {
                    "total_conversations": total_conversations,
                    "active_conversations": active_conversations,
                    "total_messages": total_messages,
                    "total_memories": total_memories,
                    "database_status": "connected"
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats del sistema: {e}")
            return {"database_status": "error"}

# Instancia global del gestor de base de datos
db_manager = DatabaseManager() 