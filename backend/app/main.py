"""
AgentOS Main Application - FastAPI Server
Sistema de agentes cognitivos hiper-inteligentes con MCP
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from typing import Dict, Any, Optional

# Importar modelos centralizados
from .models import (
    UnifiedTaskRequest, SystemStatusResponse,
    CognitiveAgentRequest, CognitiveAgentResponse,
    ToolExecutionRequest, ToolExecutionResponse
)

# Importar módulos de API
from .api import register_v1_endpoints, register_v2_endpoints

# Importar componentes del sistema
from .orchestrator import orchestrator
from .agents.cognitive_coordinator import cognitive_coordinator
from .tools.mcp_real_tools_bridge import mcp_real_tools_bridge

logger = logging.getLogger(__name__)

# ===============================
# CONFIGURACIÓN DE FASTAPI
# ===============================

app = FastAPI(
    title="AgentOS - Sistema de Agentes Cognitivos",
    description="Sistema de agentes hiper-inteligentes con MCP y herramientas reales",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# REGISTRO DE ENDPOINTS
# ===============================

# Registrar endpoints V1 (básicos)
register_v1_endpoints(app)

# Registrar endpoints V2 (enterprise)
register_v2_endpoints(app)

# ===============================
# ENDPOINTS PRINCIPALES
# ===============================

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "AgentOS - Sistema de Agentes Cognitivos Hiper-Inteligentes",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Cognitive Agents (Researcher, Coder, Coordinator)",
            "MCP Server Integration",
            "Real Tools Bridge",
            "Enterprise Task Tracking",
            "Real-time Streaming",
            "Memory Systems",
            "Test-Time Learning"
        ],
        "endpoints": {
            "v1": "/api/v1/*",
            "v2": "/api/v2/*",
            "docs": "/docs",
            "status": "/status"
        }
    }

@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Estado completo del sistema"""
    try:
        # Obtener estado de agentes cognitivos
        cognitive_status = cognitive_coordinator.get_cognitive_agents_status()
        
        # Obtener herramientas MCP disponibles
        mcp_tools = await mcp_real_tools_bridge.get_available_real_tools()
        
        return SystemStatusResponse(
            status="operational",
            version="2.0.0",
            components={
                "orchestrator": "active",
                "cognitive_coordinator": "operational",
                "mcp_server": "connected",
                "real_tools_bridge": "active",
                "memory_systems": "operational"
            },
            cognitive_agents=cognitive_status,
            mcp_tools={
                "total_tools": len(mcp_tools),
                "categories": {
                    "web_search": len([t for t in mcp_tools if t["category"] == "web_search"]),
                    "document_analysis": len([t for t in mcp_tools if t["category"] == "document_analysis"]),
                    "data_visualization": len([t for t in mcp_tools if t["category"] == "data_visualization"]),
                    "file_operations": len([t for t in mcp_tools if t["category"] == "file_operations"])
                },
                "tools": mcp_tools
            }
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cognitive/execute")
async def execute_with_cognitive_agents(request: CognitiveAgentRequest):
    """
    Ejecutar tarea con agentes cognitivos especializados
    Usa el cognitive_coordinator para razonamiento especializado
    """
    try:
        logger.info(f"🧠 Ejecutando con agentes cognitivos: {request.query}")
        
        result = await cognitive_coordinator.coordinate_with_cognitive_agents(
            task=request.query,
            user_context=request.context or {}
        )
        
        return {
            "success": result.get("coordination_success", False),
            "task_id": result.get("task_id"),
            "cognitive_agents_used": result.get("cognitive_agents_used", []),
            "specialized_insights": result.get("specialized_insights", {}),
            "final_synthesis": result.get("final_synthesis", {}),
            "learning_updated": result.get("learning_updated", False),
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error en ejecución cognitiva: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cognitive/agents")
async def get_cognitive_agents():
    """Obtener información de agentes cognitivos"""
    try:
        status = cognitive_coordinator.get_cognitive_agents_status()
        
        return {
            "cognitive_agents": status,
            "total_agents": len(cognitive_coordinator.cognitive_agents),
            "specializations": {
                "researcher": "Research & Analysis",
                "coder": "Development & Implementation", 
                "coordinator": "Orchestration & Synthesis"
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo agentes cognitivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools/real")
async def get_real_tools():
    """Obtener herramientas reales disponibles vía MCP"""
    try:
        tools = await mcp_real_tools_bridge.get_available_real_tools()
        
        return {
            "real_tools": tools,
            "total_tools": len(tools),
            "categories": {
                "web_search": len([t for t in tools if t["category"] == "web_search"]),
                "document_analysis": len([t for t in tools if t["category"] == "document_analysis"]),
                "data_visualization": len([t for t in tools if t["category"] == "data_visualization"]),
                "file_operations": len([t for t in tools if t["category"] == "file_operations"])
            },
            "mcp_integration": "active"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo herramientas reales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# EVENTOS DE INICIALIZACIÓN
# ===============================

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🚀 AgentOS iniciando...")
    
    # Inicializar componentes
    try:
        # Verificar que el cognitive_coordinator esté operativo
        cognitive_status = cognitive_coordinator.get_cognitive_agents_status()
        logger.info(f"✅ Cognitive Coordinator: {len(cognitive_status['cognitive_agents'])} agentes activos")
        
        # Verificar herramientas MCP
        mcp_tools = await mcp_real_tools_bridge.get_available_real_tools()
        logger.info(f"✅ MCP Real Tools Bridge: {len(mcp_tools)} herramientas registradas")
        
        logger.info("🎉 AgentOS iniciado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("🛑 AgentOS cerrando...")
    
    # Limpiar recursos
    try:
        # Cerrar conexiones y limpiar memoria
        logger.info("🧹 Limpiando recursos...")
        
    except Exception as e:
        logger.error(f"Error en cierre: {e}")

# ===============================
# MANEJO DE ERRORES
# ===============================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return {
        "error": "Error interno del servidor",
        "detail": str(exc),
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)