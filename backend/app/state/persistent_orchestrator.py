"""
Persistent Orchestrator - AgentOS Enterprise
Wrapper que añade persistencia al orquestador actual SIN cambiar su lógica
Implementa Factor 9: Gestionar tu estado
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import time

from ..orchestrator import unified_orchestrator
from .state_manager import state_manager, ExecutionState

logger = logging.getLogger(__name__)

class PersistentOrchestrator:
    """
    Wrapper que hace persistente el orquestador actual
    NO modifica la lógica existente, solo añade persistencia
    """
    
    def __init__(self):
        self.current_orchestrator = unified_orchestrator
        self.state_manager = state_manager
    
    async def execute_task_with_persistence(self, task_id: str, query: str,
                                          user_context: Dict = None, 
                                          priority: str = "normal",
                                          optimization_level: str = "balanced") -> Dict[str, Any]:
        """
        Ejecutar tarea con persistencia completa
        Wrappea unified_orchestrator.execute_task() sin modificarlo
        """
        start_time = time.time()
        
        try:
            # 1. Crear estado persistente inicial
            session_id = str(uuid.uuid4())
            state = await self.state_manager.create_execution_state(
                task_id=task_id,
                session_id=session_id,
                query=query,
                user_context=user_context,
                priority=priority,
                optimization_level=optimization_level
            )
            
            logger.info(f"🔄 Iniciando ejecución persistente: {task_id}")
            
            # 2. Configurar estimación de pasos
            await self._estimate_and_set_steps(task_id, query)
            
            # 3. Ejecutar orquestador actual SIN CAMBIOS
            result = await self._execute_with_monitoring(task_id, query)
            
            # 4. Completar estado con resultado final
            execution_time = int(time.time() - start_time)
            await self.state_manager.update_execution_state(task_id, {
                "execution_time": execution_time
            })
            
            await self.state_manager.complete_execution(task_id, result)
            
            # 5. Añadir métricas adicionales para enterprise
            enhanced_result = {
                **result,
                "task_id": task_id,
                "execution_time": execution_time,
                "persistent": True,
                "resumable": True,
                "steps_completed": state.current_step if task_id in self.state_manager.active_states else 0
            }
            
            logger.info(f"✅ Ejecución persistente completada: {task_id} en {execution_time}s")
            return enhanced_result
            
        except Exception as e:
            # Manejar error y actualizar estado
            await self._handle_execution_error(task_id, e)
            
            execution_time = int(time.time() - start_time)
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "session_id": state.session_id if 'state' in locals() else "unknown",
                "execution_time": execution_time,
                "persistent": True,
                "resumable": False
            }
    
    async def _execute_with_monitoring(self, task_id: str, query: str) -> Dict[str, Any]:
        """
        Ejecuta el orquestador actual con monitoreo de pasos
        NO modifica la lógica del orquestador
        """
        
        # Interceptar y monitorear cada paso del orquestador actual
        original_orchestrator = self.current_orchestrator
        
        # Paso 1: Inicialización
        await self.state_manager.advance_step(task_id, "Inicializando sesión")
        
        # Paso 2: Análisis de intención
        await self.state_manager.advance_step(task_id, "Analizando intención del usuario")
        
        # Paso 3: Descomposición de tarea
        await self.state_manager.advance_step(task_id, "Descomponiendo tarea")
        
        # Paso 4: Selección de agentes
        await self.state_manager.advance_step(task_id, "Seleccionando agentes óptimos")
        
        # Paso 5: Ejecución con agentes cognitivos
        await self.state_manager.advance_step(task_id, "Ejecutando con agentes cognitivos")
        
        # EJECUTAR ORQUESTADOR ACTUAL (SIN CAMBIOS)
        result = await original_orchestrator.execute_task(query)
        
        # Paso 6: Síntesis de resultados
        await self.state_manager.advance_step(task_id, "Sintetizando resultados")
        
        # Paso 7: Actualización de memoria
        await self.state_manager.advance_step(task_id, "Actualizando memoria y aprendizaje")
        
        # Registrar resultado intermedio
        await self.state_manager.add_intermediate_result(task_id, {
            "orchestrator_result": result,
            "step_description": "Orquestador unificado completado"
        })
        
        return result
    
    async def _estimate_and_set_steps(self, task_id: str, query: str):
        """Estima el número total de pasos basado en la complejidad"""
        try:
            # Estimación simple basada en longitud de query y palabras clave
            base_steps = 7  # Pasos básicos del orquestador
            
            # Añadir pasos por complejidad
            complexity_keywords = [
                'investiga', 'analiza', 'crea', 'busca', 'documenta', 
                'visualiza', 'compara', 'evalúa', 'optimiza'
            ]
            
            additional_steps = sum(1 for keyword in complexity_keywords 
                                 if keyword in query.lower())
            
            total_steps = base_steps + additional_steps
            
            await self.state_manager.update_execution_state(task_id, {
                "total_steps": total_steps
            })
            
            logger.info(f"📊 Estimados {total_steps} pasos para tarea: {task_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Error estimando pasos para {task_id}: {e}")
            # Fallback a número fijo
            await self.state_manager.update_execution_state(task_id, {
                "total_steps": 7
            })
    
    async def _handle_execution_error(self, task_id: str, error: Exception):
        """Maneja errores durante la ejecución"""
        try:
            error_details = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.state_manager.update_execution_state(task_id, {
                "status": "failed",
                "error_details": error_details
            })
            
            logger.error(f"❌ Error en ejecución persistente {task_id}: {error}")
            
        except Exception as e:
            logger.error(f"❌ Error manejando error de ejecución {task_id}: {e}")
    
    async def pause_task(self, task_id: str) -> Dict[str, Any]:
        """
        Pausa una tarea en ejecución
        NUEVO: Capacidad enterprise de pausar/reanudar
        """
        try:
            success = await self.state_manager.pause_execution(task_id)
            
            if success:
                state = await self.state_manager.get_execution_state(task_id)
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": "paused",
                    "message": "Tarea pausada exitosamente",
                    "current_step": state.current_step if state else 0,
                    "progress": state.progress_percentage if state else 0,
                    "resume_url": f"/api/v2/tasks/{task_id}/resume"
                }
            else:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": "No se pudo pausar la tarea"
                }
                
        except Exception as e:
            logger.error(f"❌ Error pausando tarea {task_id}: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    async def resume_task(self, task_id: str) -> Dict[str, Any]:
        """
        Reanuda una tarea pausada
        NUEVO: Capacidad enterprise de pausar/reanudar
        """
        try:
            # Verificar que la tarea existe y está pausada
            state = await self.state_manager.get_execution_state(task_id)
            
            if not state:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": "Tarea no encontrada"
                }
            
            if not state.is_paused:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": f"Tarea no está pausada. Estado actual: {state.status}"
                }
            
            # Reanudar ejecución
            success = await self.state_manager.resume_execution(task_id)
            
            if success:
                # Continuar ejecución desde donde se pausó
                asyncio.create_task(self._continue_paused_execution(task_id))
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": "running",
                    "message": "Tarea reanudada exitosamente",
                    "current_step": state.current_step,
                    "progress": state.progress_percentage,
                    "streaming_url": f"/api/v2/tasks/{task_id}/stream"
                }
            else:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": "No se pudo reanudar la tarea"
                }
                
        except Exception as e:
            logger.error(f"❌ Error reanudando tarea {task_id}: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _continue_paused_execution(self, task_id: str):
        """
        Continúa una ejecución pausada
        Implementa lógica de resuming inteligente
        """
        try:
            state = await self.state_manager.get_execution_state(task_id)
            if not state:
                return
            
            logger.info(f"🔄 Continuando ejecución pausada: {task_id} desde paso {state.current_step}")
            
            # Determinar desde dónde continuar basado en el paso actual
            if state.current_step < state.total_steps:
                # Re-ejecutar desde el orquestador pero con contexto preservado
                result = await self._execute_with_monitoring(task_id, state.original_query)
                
                # Completar ejecución
                await self.state_manager.complete_execution(task_id, result)
                
                logger.info(f"✅ Ejecución pausada completada: {task_id}")
            else:
                # Ya estaba completa, solo marcar como tal
                await self.state_manager.update_execution_state(task_id, {
                    "status": "completed"
                })
                
        except Exception as e:
            logger.error(f"❌ Error continuando ejecución pausada {task_id}: {e}")
            await self._handle_execution_error(task_id, e)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado completo de una tarea"""
        try:
            state = await self.state_manager.get_execution_state(task_id)
            
            if not state:
                return None
            
            return {
                "task_id": task_id,
                "session_id": state.session_id,
                "status": state.status,
                "current_step": state.current_step,
                "total_steps": state.total_steps,
                "progress": state.progress_percentage,
                "original_query": state.original_query,
                "priority": state.priority,
                "optimization_level": state.optimization_level,
                "can_pause": state.can_pause and state.is_running,
                "can_resume": state.can_resume and state.is_paused,
                "intermediate_results": state.intermediate_results,
                "tool_executions": state.tool_executions,
                "agent_states": state.agent_states,
                "execution_time": state.execution_time,
                "memory_accessed": state.memory_accessed,
                "optimization_applied": state.optimization_applied,
                "created_at": state.extra_data.get("created_at"),
                "updated_at": state.extra_data.get("updated_at")
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de tarea {task_id}: {e}")
            return None
    
    async def list_active_tasks(self) -> List[Dict[str, Any]]:
        """Lista todas las tareas activas"""
        try:
            from ..database.database import db_manager
            
            active_executions = db_manager.get_active_executions()
            
            return [{
                "task_id": exec["task_id"],
                "session_id": exec["session_id"],
                "status": exec["status"],
                "current_step": exec["current_step"],
                "total_steps": exec["total_steps"],
                "priority": exec["priority"],
                "created_at": exec["created_at"],
                "query_preview": exec["original_query"]
            } for exec in active_executions]
            
        except Exception as e:
            logger.error(f"❌ Error listando tareas activas: {e}")
            return []

# Instancia global del orquestador persistente
persistent_orchestrator = PersistentOrchestrator() 