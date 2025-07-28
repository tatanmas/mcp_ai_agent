"""
State Manager - AgentOS Enterprise
Implementa Factor 9: Gestionar tu estado
Permite pausar/reanudar tareas sin perder contexto
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List
from datetime import datetime
import uuid

from ..database.database import db_manager

logger = logging.getLogger(__name__)

class ExecutionState:
    """Clase para representar el estado de ejecución en memoria"""
    
    def __init__(self, task_id: str, session_id: str, query: str, **kwargs):
        self.task_id = task_id
        self.session_id = session_id
        self.original_query = query
        
        # Estado de progreso
        self.current_step = kwargs.get('current_step', 0)
        self.total_steps = kwargs.get('total_steps', 1)
        self.status = kwargs.get('status', 'running')
        
        # Contexto y datos
        self.context_window = kwargs.get('context_window', '')
        self.agent_states = kwargs.get('agent_states', {})
        self.intermediate_results = kwargs.get('intermediate_results', [])
        self.tool_executions = kwargs.get('tool_executions', [])
        
        # Configuración
        self.user_context = kwargs.get('user_context', {})
        self.priority = kwargs.get('priority', 'normal')
        self.optimization_level = kwargs.get('optimization_level', 'balanced')
        
        # Análisis y planificación
        self.intent_analysis = kwargs.get('intent_analysis', {})
        self.task_decomposition = kwargs.get('task_decomposition', [])
        self.selected_agents = kwargs.get('selected_agents', [])
        
        # Control
        self.can_pause = kwargs.get('can_pause', True)
        self.can_resume = kwargs.get('can_resume', True)
        self.pause_requested = kwargs.get('pause_requested', False)
        
        # Métricas
        self.execution_time = kwargs.get('execution_time', 0)
        self.tokens_used = kwargs.get('tokens_used', 0)
        self.memory_accessed = kwargs.get('memory_accessed', False)
        self.optimization_applied = kwargs.get('optimization_applied', False)
        
        # Metadatos
        self.error_details = kwargs.get('error_details', {})
        self.performance_metrics = kwargs.get('performance_metrics', {})
        self.extra_data = kwargs.get('extra_data', {})
    
    @property
    def is_complete(self) -> bool:
        """Verifica si la ejecución está completa"""
        return self.status in ['completed', 'failed']
    
    @property
    def is_paused(self) -> bool:
        """Verifica si la ejecución está pausada"""
        return self.status == 'paused'
    
    @property
    def is_running(self) -> bool:
        """Verifica si la ejecución está corriendo"""
        return self.status == 'running'
    
    @property
    def progress_percentage(self) -> float:
        """Calcula el porcentaje de progreso"""
        if self.total_steps <= 0:
            return 0.0
        return min(100.0, (self.current_step / self.total_steps) * 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario para persistencia"""
        return {
            'task_id': self.task_id,
            'session_id': self.session_id,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'status': self.status,
            'context_window': self.context_window,
            'agent_states': self.agent_states,
            'intermediate_results': self.intermediate_results,
            'tool_executions': self.tool_executions,
            'original_query': self.original_query,
            'user_context': self.user_context,
            'priority': self.priority,
            'optimization_level': self.optimization_level,
            'intent_analysis': self.intent_analysis,
            'task_decomposition': self.task_decomposition,
            'selected_agents': self.selected_agents,
            'can_pause': self.can_pause,
            'can_resume': self.can_resume,
            'pause_requested': self.pause_requested,
            'execution_time': self.execution_time,
            'tokens_used': self.tokens_used,
            'memory_accessed': self.memory_accessed,
            'optimization_applied': self.optimization_applied,
            'error_details': self.error_details,
            'performance_metrics': self.performance_metrics,
            'extra_data': self.extra_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionState':
        """Crea un ExecutionState desde un diccionario"""
        task_id = data.pop('task_id')
        session_id = data.pop('session_id')
        query = data.pop('original_query')
        return cls(task_id, session_id, query, **data)

class StateManager:
    """
    Gestor de estado persistente para AgentOS Enterprise
    Implementa los 12 factores de agentes IA
    """
    
    def __init__(self):
        self.active_states: Dict[str, ExecutionState] = {}
        self.update_listeners: Dict[str, List[asyncio.Queue]] = {}
    
    async def create_execution_state(self, task_id: str, session_id: str, query: str,
                                   user_context: Dict = None, priority: str = "normal",
                                   optimization_level: str = "balanced") -> ExecutionState:
        """Crea un nuevo estado de ejecución"""
        try:
            # Crear en base de datos
            success = db_manager.create_execution_state(
                task_id=task_id,
                session_id=session_id,
                query=query,
                user_context=user_context,
                priority=priority,
                optimization_level=optimization_level
            )
            
            if not success:
                raise Exception(f"No se pudo crear estado en BD para {task_id}")
            
            # Crear en memoria
            state = ExecutionState(
                task_id=task_id,
                session_id=session_id,
                query=query,
                user_context=user_context or {},
                priority=priority,
                optimization_level=optimization_level
            )
            
            self.active_states[task_id] = state
            self.update_listeners[task_id] = []
            
            logger.info(f"✅ Estado de ejecución creado: {task_id}")
            
            # Notificar creación
            await self._notify_update(task_id, {
                "type": "state_created",
                "task_id": task_id,
                "status": "running",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error creando estado de ejecución {task_id}: {e}")
            raise
    
    async def get_execution_state(self, task_id: str) -> Optional[ExecutionState]:
        """Obtiene un estado de ejecución (memoria o BD)"""
        try:
            # Intentar primero desde memoria
            if task_id in self.active_states:
                return self.active_states[task_id]
            
            # Si no está en memoria, cargar desde BD
            state_data = db_manager.get_execution_state(task_id)
            if state_data:
                state = ExecutionState.from_dict(state_data)
                self.active_states[task_id] = state
                self.update_listeners[task_id] = []
                return state
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de ejecución {task_id}: {e}")
            return None
    
    async def update_execution_state(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un estado de ejecución"""
        try:
            # Actualizar en memoria
            if task_id in self.active_states:
                state = self.active_states[task_id]
                for key, value in updates.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
            
            # Actualizar en BD
            success = db_manager.update_execution_state(task_id, updates)
            
            if success:
                # Notificar actualización
                await self._notify_update(task_id, {
                    "type": "state_updated",
                    "task_id": task_id,
                    "updates": updates,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado de ejecución {task_id}: {e}")
            return False
    
    async def pause_execution(self, task_id: str) -> bool:
        """Pausa una ejecución"""
        try:
            success = db_manager.pause_execution(task_id)
            
            if success and task_id in self.active_states:
                state = self.active_states[task_id]
                state.status = "paused"
                state.pause_requested = True
                
                await self._notify_update(task_id, {
                    "type": "execution_paused",
                    "task_id": task_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error pausando ejecución {task_id}: {e}")
            return False
    
    async def resume_execution(self, task_id: str) -> bool:
        """Reanuda una ejecución"""
        try:
            success = db_manager.resume_execution(task_id)
            
            if success and task_id in self.active_states:
                state = self.active_states[task_id]
                state.status = "running"
                state.pause_requested = False
                
                await self._notify_update(task_id, {
                    "type": "execution_resumed",
                    "task_id": task_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error reanudando ejecución {task_id}: {e}")
            return False
    
    async def complete_execution(self, task_id: str, final_result: Dict = None) -> bool:
        """Marca una ejecución como completada"""
        try:
            success = db_manager.complete_execution(task_id, final_result)
            
            if success and task_id in self.active_states:
                state = self.active_states[task_id]
                state.status = "completed"
                
                await self._notify_update(task_id, {
                    "type": "execution_completed",
                    "task_id": task_id,
                    "final_result": final_result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Limpiar de memoria activa después de un tiempo
                asyncio.create_task(self._cleanup_completed_state(task_id))
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error completando ejecución {task_id}: {e}")
            return False
    
    async def add_intermediate_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Añade un resultado intermedio"""
        try:
            if task_id in self.active_states:
                state = self.active_states[task_id]
                state.intermediate_results.append({
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "step": state.current_step
                })
                
                # Actualizar en BD
                await self.update_execution_state(task_id, {
                    "intermediate_results": state.intermediate_results
                })
                
                # Notificar resultado intermedio
                await self._notify_update(task_id, {
                    "type": "intermediate_result",
                    "task_id": task_id,
                    "result": result,
                    "step": state.current_step,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo resultado intermedio {task_id}: {e}")
            return False
    
    async def add_tool_execution(self, task_id: str, tool_name: str, 
                               parameters: Dict, result: Dict) -> bool:
        """Registra la ejecución de una herramienta"""
        try:
            if task_id in self.active_states:
                state = self.active_states[task_id]
                tool_execution = {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "step": state.current_step
                }
                
                state.tool_executions.append(tool_execution)
                
                # Actualizar en BD
                await self.update_execution_state(task_id, {
                    "tool_executions": state.tool_executions
                })
                
                # Notificar ejecución de herramienta
                await self._notify_update(task_id, {
                    "type": "tool_executed",
                    "task_id": task_id,
                    "tool_execution": tool_execution,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error registrando ejecución de herramienta {task_id}: {e}")
            return False
    
    async def advance_step(self, task_id: str, description: str = None) -> bool:
        """Avanza al siguiente paso de ejecución"""
        try:
            if task_id in self.active_states:
                state = self.active_states[task_id]
                state.current_step += 1
                
                await self.update_execution_state(task_id, {
                    "current_step": state.current_step
                })
                
                # Notificar avance de paso
                await self._notify_update(task_id, {
                    "type": "step_advanced",
                    "task_id": task_id,
                    "current_step": state.current_step,
                    "total_steps": state.total_steps,
                    "progress": state.progress_percentage,
                    "description": description,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error avanzando paso {task_id}: {e}")
            return False
    
    async def stream_updates(self, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream de actualizaciones en tiempo real para una tarea"""
        if task_id not in self.update_listeners:
            self.update_listeners[task_id] = []
        
        queue = asyncio.Queue()
        self.update_listeners[task_id].append(queue)
        
        try:
            while True:
                update = await queue.get()
                if update is None:  # Señal de terminación
                    break
                yield update
        finally:
            if queue in self.update_listeners.get(task_id, []):
                self.update_listeners[task_id].remove(queue)
    
    async def _notify_update(self, task_id: str, update: Dict[str, Any]):
        """Notifica actualizaciones a todos los listeners"""
        if task_id in self.update_listeners:
            for queue in self.update_listeners[task_id]:
                try:
                    await queue.put(update)
                except Exception as e:
                    logger.warning(f"Error notificando update para {task_id}: {e}")
    
    async def _cleanup_completed_state(self, task_id: str, delay: int = 300):
        """Limpia estados completados después de un delay"""
        await asyncio.sleep(delay)  # 5 minutos por defecto
        
        if task_id in self.active_states:
            state = self.active_states[task_id]
            if state.is_complete:
                del self.active_states[task_id]
                
                # Terminar listeners
                if task_id in self.update_listeners:
                    for queue in self.update_listeners[task_id]:
                        await queue.put(None)  # Señal de terminación
                    del self.update_listeners[task_id]
                
                logger.info(f"🧹 Estado completado limpiado de memoria: {task_id}")

# Instancia global del state manager
state_manager = StateManager() 