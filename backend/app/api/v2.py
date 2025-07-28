"""
API V2 Enterprise - AgentOS
Endpoints enterprise que añaden funcionalidad SIN tocar V1
Implementa visualización en tiempo real, pausar/reanudar, y tracking
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..state.persistent_orchestrator import persistent_orchestrator
from ..state.state_manager import state_manager
from ..main import UnifiedTaskRequest  # Reutilizar modelo existente

logger = logging.getLogger(__name__)

# ===============================
# MODELOS PYDANTIC V2
# ===============================

class TaskCreateRequest(BaseModel):
    """Solicitud para crear tarea trackeable"""
    query: str
    context: Optional[Dict[str, Any]] = {}
    priority: Optional[str] = "normal"  # low, normal, high
    optimization_level: Optional[str] = "balanced"  # minimal, balanced, aggressive
    trackable: Optional[bool] = True  # Nueva opción enterprise

class TaskCreateResponse(BaseModel):
    """Respuesta de creación de tarea"""
    task_id: str
    status: str
    message: str
    tracking_url: str
    pause_url: str
    estimated_time: int  # segundos
    created_at: str

class TaskStatusResponse(BaseModel):
    """Estado detallado de tarea"""
    task_id: str
    session_id: str
    status: str
    current_step: int
    total_steps: int
    progress: float
    original_query: str
    priority: str
    optimization_level: str
    can_pause: bool
    can_resume: bool
    intermediate_results: List[Dict[str, Any]]
    tool_executions: List[Dict[str, Any]]
    execution_time: int
    memory_accessed: bool
    optimization_applied: bool
    created_at: Optional[str]
    updated_at: Optional[str]

class TaskControlResponse(BaseModel):
    """Respuesta de control de tarea (pause/resume)"""
    success: bool
    task_id: str
    status: str
    message: str
    current_step: Optional[int] = None
    progress: Optional[float] = None
    action_url: Optional[str] = None

class ActiveTasksSummary(BaseModel):
    """Resumen de tareas activas"""
    total_active: int
    running: int
    paused: int
    failed: int
    tasks: List[Dict[str, Any]]

# ===============================
# FUNCIONES DE ENDPOINTS V2
# ===============================

def register_v2_endpoints(app: FastAPI):
    """Registra los endpoints V2 enterprise en la app existente"""
    
    @app.post("/api/v2/tasks/start", response_model=TaskCreateResponse)
    async def start_trackable_task(request: TaskCreateRequest):
        """
        NUEVO: Crear tarea con tracking completo
        Versión enterprise del endpoint /api/v1/execute
        """
        try:
            task_id = str(uuid.uuid4())
            
            logger.info(f"🚀 Iniciando tarea trackeable V2: {task_id}")
            
            # Ejecutar en background con persistencia
            asyncio.create_task(
                persistent_orchestrator.execute_task_with_persistence(
                    task_id=task_id,
                    query=request.query,
                    user_context=request.context,
                    priority=request.priority,
                    optimization_level=request.optimization_level
                )
            )
            
            # Estimar tiempo basado en complejidad
            estimated_time = _estimate_execution_time(request.query)
            
            return TaskCreateResponse(
                task_id=task_id,
                status="started",
                message="Tarea iniciada con tracking completo",
                tracking_url=f"/api/v2/tasks/{task_id}/stream",
                pause_url=f"/api/v2/tasks/{task_id}/pause",
                estimated_time=estimated_time,
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Error iniciando tarea trackeable: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/tasks/{task_id}", response_model=TaskStatusResponse)
    async def get_task_status(task_id: str):
        """
        NUEVO: Estado detallado de tarea con métricas enterprise
        """
        try:
            task_status = await persistent_orchestrator.get_task_status(task_id)
            
            if not task_status:
                raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
            return TaskStatusResponse(**task_status)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de tarea {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/tasks/{task_id}/stream")
    async def stream_task_progress(task_id: str):
        """
        NUEVO: Stream en tiempo real de progreso de tarea
        Server-Sent Events para visualización live
        """
        try:
            # Verificar que la tarea existe
            task_status = await persistent_orchestrator.get_task_status(task_id)
            if not task_status:
                raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
            async def event_stream():
                """Generador de eventos SSE"""
                try:
                    # Enviar estado inicial
                    initial_data = {
                        'type': 'initial_status',
                        'task_id': task_id,
                        'status': task_status['status'],
                        'current_step': task_status['current_step'],
                        'total_steps': task_status['total_steps'],
                        'progress': task_status['progress'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(initial_data)}\n\n"
                    
                    # Stream de actualizaciones
                    async for update in state_manager.stream_updates(task_id):
                        yield f"data: {json.dumps(update)}\n\n"
                        
                except Exception as e:
                    logger.error(f"Error en stream para {task_id}: {e}")
                    error_data = {
                        'type': 'error',
                        'message': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error en stream de tarea {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v2/tasks/{task_id}/pause", response_model=TaskControlResponse)
    async def pause_task(task_id: str):
        """
        NUEVO: Pausar tarea en ejecución
        Capacidad enterprise de control granular
        """
        try:
            result = await persistent_orchestrator.pause_task(task_id)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return TaskControlResponse(
                success=True,
                task_id=task_id,
                status="paused",
                message=result["message"],
                current_step=result.get("current_step"),
                progress=result.get("progress"),
                action_url=result.get("resume_url")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error pausando tarea {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v2/tasks/{task_id}/resume", response_model=TaskControlResponse)
    async def resume_task(task_id: str):
        """
        NUEVO: Reanudar tarea pausada
        Capacidad enterprise de resuming inteligente
        """
        try:
            result = await persistent_orchestrator.resume_task(task_id)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return TaskControlResponse(
                success=True,
                task_id=task_id,
                status="running",
                message=result["message"],
                current_step=result.get("current_step"),
                progress=result.get("progress"),
                action_url=result.get("streaming_url")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error reanudando tarea {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/tasks", response_model=ActiveTasksSummary)
    async def list_active_tasks():
        """
        NUEVO: Lista todas las tareas activas con métricas
        Dashboard enterprise de monitoreo
        """
        try:
            active_tasks = await persistent_orchestrator.list_active_tasks()
            
            # Calcular métricas
            total_active = len(active_tasks)
            running = len([t for t in active_tasks if t["status"] == "running"])
            paused = len([t for t in active_tasks if t["status"] == "paused"])
            failed = len([t for t in active_tasks if t["status"] == "failed"])
            
            return ActiveTasksSummary(
                total_active=total_active,
                running=running,
                paused=paused,
                failed=failed,
                tasks=active_tasks
            )
            
        except Exception as e:
            logger.error(f"❌ Error listando tareas activas: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/tasks/{task_id}/results")
    async def get_task_results(task_id: str):
        """
        NUEVO: Obtener resultados detallados incluyendo intermedios
        Visualización completa de la ejecución
        """
        try:
            task_status = await persistent_orchestrator.get_task_status(task_id)
            
            if not task_status:
                raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
            return {
                "task_id": task_id,
                "status": task_status["status"],
                "final_result": task_status.get("extra_data", {}),
                "intermediate_results": task_status["intermediate_results"],
                "tool_executions": task_status["tool_executions"],
                "execution_timeline": _build_execution_timeline(task_status),
                "performance_metrics": {
                    "execution_time": task_status["execution_time"],
                    "steps_completed": task_status["current_step"],
                    "total_steps": task_status["total_steps"],
                    "efficiency": task_status["current_step"] / max(task_status["total_steps"], 1) * 100
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo resultados de tarea {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/system/metrics")
    async def get_system_metrics():
        """Obtener métricas del sistema enterprise"""
        try:
            # Obtener métricas del state manager
            active_tasks = await state_manager.get_active_executions()
            
            # Calcular métricas de performance
            total_tasks = len(active_tasks)
            running_tasks = len([t for t in active_tasks if t.status == 'running'])
            paused_tasks = len([t for t in active_tasks if t.status == 'paused'])
            failed_tasks = len([t for t in active_tasks if t.status == 'failed'])
            
            # Calcular tiempo promedio de ejecución
            completed_tasks = [t for t in active_tasks if t.status == 'completed']
            avg_execution_time = sum(t.execution_time for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0.0
            
            # Calcular tasa de éxito
            success_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 100.0
            
            # Calcular throughput (tareas por minuto)
            throughput = len(completed_tasks) / (avg_execution_time / 60) if avg_execution_time > 0 else 0.0
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "active_tasks": {
                    "total": total_tasks,
                    "running": running_tasks,
                    "paused": paused_tasks,
                    "failed": failed_tasks
                },
                "performance": {
                    "average_execution_time": round(avg_execution_time, 2),
                    "success_rate": round(success_rate, 2),
                    "throughput": round(throughput, 2)
                },
                "health": {
                    "database": "connected",
                    "orchestrator": "operational",
                    "state_manager": "active",
                    "streaming": "available"
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas del sistema: {e}")
            raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

    @app.get("/api/v2/tools/available")
    async def get_available_tools():
        """Obtener lista de herramientas disponibles vía MCP"""
        try:
            from ..tools.mcp_bridge import mcp_bridge
            
            tools = await mcp_bridge.get_available_tools()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_tools": len(tools),
                "tools": tools,
                "mcp_server_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo herramientas disponibles: {e}")
            raise HTTPException(status_code=500, detail=f"Error obteniendo herramientas: {str(e)}")

    @app.post("/api/v2/tools/execute")
    async def execute_tool(tool_request: Dict[str, Any]):
        """Ejecutar una herramienta específica vía MCP"""
        try:
            from ..tools.mcp_bridge import mcp_bridge
            from ..mcp.server import execute_mcp_tool
            
            tool_name = tool_request.get("tool_name")
            arguments = tool_request.get("arguments", {})
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="tool_name es requerido")
            
            # Ejecutar herramienta vía MCP
            result = await execute_mcp_tool(tool_name, arguments)
            
            return {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result.content[0]['text'] if result.content else "No result",
                "success": not result.isError,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta: {e}")
            raise HTTPException(status_code=500, detail=f"Error ejecutando herramienta: {str(e)}")

# ===============================
# FUNCIONES AUXILIARES
# ===============================

def _estimate_execution_time(query: str) -> int:
    """Estima tiempo de ejecución basado en complejidad de query"""
    base_time = 30  # 30 segundos base
    
    complexity_keywords = [
        'investiga', 'analiza', 'crea', 'busca', 'documenta', 
        'visualiza', 'compara', 'evalúa', 'optimiza', 'desarrolla'
    ]
    
    additional_time = sum(10 for keyword in complexity_keywords 
                         if keyword in query.lower())
    
    return base_time + additional_time

def _build_execution_timeline(task_status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Construye timeline de ejecución"""
    timeline = []
    
    # Añadir resultados intermedios a timeline
    for result in task_status.get("intermediate_results", []):
        timeline.append({
            "type": "intermediate_result",
            "timestamp": result.get("timestamp"),
            "step": result.get("step"),
            "description": result.get("result", {}).get("step_description", "Resultado intermedio")
        })
    
    # Añadir ejecuciones de herramientas
    for tool_exec in task_status.get("tool_executions", []):
        timeline.append({
            "type": "tool_execution",
            "timestamp": tool_exec.get("timestamp"),
            "step": tool_exec.get("step"),
            "description": f"Ejecutada herramienta: {tool_exec.get('tool_name')}"
        })
    
    # Ordenar por timestamp
    timeline.sort(key=lambda x: x.get("timestamp", ""))
    
    return timeline 