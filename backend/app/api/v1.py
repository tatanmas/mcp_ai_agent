"""
API V1 - AgentOS Basic
Endpoints básicos del sistema original
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from typing import Dict, Any, Optional

from ..models import UnifiedTaskRequest, TaskResponse
from ..orchestrator import orchestrator

logger = logging.getLogger(__name__)



def register_v1_endpoints(app: FastAPI):
    """Registra endpoints V1 básicos"""
    
    @app.post("/api/v1/execute", response_model=TaskResponse)
    async def execute_task(request: UnifiedTaskRequest):
        """Endpoint básico de ejecución de tareas"""
        try:
            result = await orchestrator.execute_task(request.query)
            
            return TaskResponse(
                result=str(result.get("result", "Tarea completada")),
                success=True,
                task_id=result.get("task_id")
            )
            
        except Exception as e:
            logger.error(f"Error ejecutando tarea: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/health")
    async def health_check():
        """Health check básico"""
        return {"status": "healthy", "version": "v1"} 