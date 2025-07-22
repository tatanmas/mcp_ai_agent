from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from typing import List, Optional
import asyncio
import json
import logging

# Importar MCP Server
from app.mcp.server import mcp_server, execute_legacy_tool_via_mcp, get_mcp_tools, execute_mcp_tool

# Importar Sistema de Base de Datos
from app.database.database import db_manager

# Importar Sistema de Memoria Vectorial (Avance 2.5)
from app.memory.vector_memory import vector_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentOS API",
    description="Sistema Avanzado de Agentes IA - Backend MVP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Más permisivo para testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API with error handling
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY no está configurada!")
        raise ValueError("GEMINI_API_KEY es requerida")
    
    genai.configure(api_key=api_key)
    logger.info("✅ Gemini API configurada correctamente")
except Exception as e:
    logger.error(f"❌ Error configurando Gemini API: {e}")

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = "default"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_id: str
    conversation_id: str
    memory_used: bool = False

class Agent(BaseModel):
    id: str
    name: str
    description: str
    personality: str
    tools: List[str]
    memory_type: str

# In-memory storage (simple MVP)
conversations = {}
agents = {
    "default": Agent(
        id="default",
        name="Asistente General",
        description="Un agente inteligente con acceso a herramientas básicas",
        personality="Amigable, útil y preciso. Siempre busca resolver problemas de manera eficiente y usa herramientas cuando es necesario.",
        tools=["web_search", "calculator", "memory"],
        memory_type="enhanced"
    ),
    "researcher": Agent(
        id="researcher",
        name="Investigador IA",
        description="Especialista en investigación y análisis de información",
        personality="Analítico, meticuloso y orientado a los datos. Proporciona información detallada y verificada. Siempre busca fuentes confiables.",
        tools=["web_search", "pdf_analysis", "data_visualization", "memory"],
        memory_type="long_term"
    ),
    "coder": Agent(
        id="coder",
        name="Desarrollador IA",
        description="Experto en programación y desarrollo de software",
        personality="Técnico, preciso y orientado a las mejores prácticas. Genera código limpio, eficiente y bien documentado.",
        tools=["code_execution", "github_search", "documentation", "memory"],
        memory_type="technical"
    )
}

# Simple tool functions
async def web_search_tool(query: str) -> str:
    """Simula una búsqueda web inteligente"""
    logger.info(f"🔍 Búsqueda web: {query}")
    # En el futuro aquí iría SerpAPI o similar
    return f"Resultados de búsqueda para '{query}': He encontrado información relevante sobre {query}. Los datos más recientes indican tendencias positivas y múltiples fuentes confirman la importancia del tema."

async def calculator_tool(expression: str) -> str:
    """Calculadora segura"""
    logger.info(f"🧮 Calculando: {expression}")
    try:
        # Evaluación más segura - solo permite operaciones básicas
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Resultado: {result}"
        else:
            return "Error: Solo se permiten operaciones matemáticas básicas"
    except Exception as e:
        logger.error(f"Error en cálculo: {e}")
        return f"Error en el cálculo: {str(e)}"

async def memory_tool(action: str, data: str = None) -> str:
    """Sistema de memoria simple pero funcional"""
    logger.info(f"🧠 Memoria {action}: {data[:50] if data else 'N/A'}...")
    if action == "store":
        return f"✅ Información almacenada en memoria: {data[:100]}..."
    elif action == "recall":
        return "📝 Recuperando de memoria: Información contextual relevante de conversaciones anteriores"
    return "❌ Acción de memoria no reconocida"

async def pdf_analysis_tool(document: str) -> str:
    """Simula análisis de documentos PDF"""
    logger.info(f"📄 Analizando documento: {document}")
    return f"Análisis completado del documento '{document}': Documento procesado, extraídos puntos clave y resumen generado."

async def code_execution_tool(code: str) -> str:
    """Simula ejecución de código"""
    logger.info(f"💻 Ejecutando código: {code[:50]}...")
    return f"Código ejecutado exitosamente. Resultado: [simulado] - El código proporcionado ha sido analizado y ejecutado en un entorno seguro."

# Tool registry expandido
tools_registry = {
    "web_search": web_search_tool,
    "calculator": calculator_tool,
    "memory": memory_tool,
    "pdf_analysis": pdf_analysis_tool,
    "data_visualization": lambda data: f"📊 Gráfico generado para: {data}",
    "code_execution": code_execution_tool,
    "github_search": lambda query: f"🐙 Búsqueda en GitHub: {query} - Repositorios relevantes encontrados",
    "documentation": lambda topic: f"📚 Documentación de {topic}: Guías y ejemplos disponibles"
}

async def execute_tool(tool_name: str, **kwargs) -> str:
    """Ejecuta una herramienta específica con mejor manejo de errores"""
    try:
        if tool_name in tools_registry:
            tool_func = tools_registry[tool_name]
            if asyncio.iscoroutinefunction(tool_func):
                return await tool_func(**kwargs)
            else:
                return tool_func(**kwargs)
        return f"❌ Herramienta '{tool_name}' no encontrada"
    except Exception as e:
        logger.error(f"Error ejecutando herramienta {tool_name}: {e}")
        return f"❌ Error ejecutando {tool_name}: {str(e)}"

async def generate_response_with_gemini(message: str, agent: Agent, conversation_history: List[ChatMessage]) -> str:
    """Genera respuesta usando Gemini con mejor prompt engineering"""
    
    # Construir prompt optimizado
    system_prompt = f"""Eres {agent.name}: {agent.description}

Personalidad: {agent.personality}

Herramientas disponibles: {', '.join(agent.tools)}

INSTRUCCIONES IMPORTANTES:
- Mantén tu personalidad única y consistente
- Si necesitas usar herramientas, usa el formato: [TOOL:nombre_herramienta:parámetros]
- Para cálculos matemáticos, SIEMPRE usa [TOOL:calculator:expresión]
- Para búsquedas de información, usa [TOOL:web_search:consulta]
- Para recordar información, usa [TOOL:memory:store:información] o [TOOL:memory:recall:]
- Sé específico, útil y mantén el contexto de conversaciones anteriores
- Responde en español de manera natural y conversacional
"""
    
    # Construir historial de conversación
    history_context = ""
    if conversation_history:
        recent_messages = conversation_history[-6:]  # Últimos 6 mensajes
        history_context = "\n".join([f"{msg.role}: {msg.content}" for msg in recent_messages])
    
    full_prompt = f"{system_prompt}\n\nHistorial reciente:\n{history_context}\n\nUsuario: {message}\n\n{agent.name}:"
    
    try:
        # Usar Gemini con configuración optimizada
        model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
                top_p=0.8,
                top_k=40
            )
        )
        
        response = model.generate_content(full_prompt)
        
        if response.text:
            logger.info(f"✅ Respuesta generada por Gemini para agente {agent.id}")
            return response.text
        else:
            logger.warning("⚠️ Gemini devolvió respuesta vacía")
            return "Lo siento, no pude generar una respuesta en este momento. ¿Podrías reformular tu pregunta?"
            
    except Exception as e:
        logger.error(f"❌ Error con Gemini: {e}")
        # Fallback response
        return f"Como {agent.name}, entiendo tu consulta '{message}'. Aunque tengo limitaciones técnicas temporales, puedo ayudarte con información general y usar mis herramientas cuando sea necesario."

async def process_tools_in_response(response: str, agent: Agent) -> str:
    """Procesa y ejecuta herramientas con mejor parsing y manejo de errores"""
    
    if "[TOOL:" not in response:
        return response
    
    # Parsing más robusto de herramientas
    import re
    tool_pattern = r'\[TOOL:([^:]+):([^\]]*)\]'
    tools_found = re.findall(tool_pattern, response)
    
    logger.info(f"🔧 Encontradas {len(tools_found)} herramientas para ejecutar")
    
    for tool_name, params in tools_found:
        if tool_name in agent.tools:
            try:
                logger.info(f"⚙️ Ejecutando {tool_name} con parámetros: {params}")
                
                # Parsing más inteligente de parámetros
                if tool_name == "web_search":
                    tool_result = await execute_tool(tool_name, query=params)
                elif tool_name == "calculator":
                    tool_result = await execute_tool(tool_name, expression=params)
                elif tool_name == "memory":
                    if ":" in params:
                        action, data = params.split(":", 1)
                        tool_result = await execute_tool(tool_name, action=action, data=data)
                    else:
                        tool_result = await execute_tool(tool_name, action=params)
                elif tool_name in ["pdf_analysis", "code_execution", "github_search", "documentation"]:
                    # Herramientas que toman un parámetro genérico
                    if tool_name == "pdf_analysis":
                        tool_result = await execute_tool(tool_name, document=params)
                    elif tool_name == "code_execution":
                        tool_result = await execute_tool(tool_name, code=params)
                    else:
                        tool_result = await execute_tool(tool_name, query=params)
                else:
                    tool_result = await execute_tool(tool_name, data=params)
                
                # Reemplazar la llamada de herramienta con el resultado
                tool_call = f"[TOOL:{tool_name}:{params}]"
                tool_output = f"\n\n🔧 **Uso de {tool_name}:** {tool_result}\n"
                response = response.replace(tool_call, tool_output)
                
            except Exception as e:
                logger.error(f"❌ Error ejecutando {tool_name}: {e}")
                tool_call = f"[TOOL:{tool_name}:{params}]"
                error_output = f"\n\n❌ **Error en {tool_name}:** {str(e)}\n"
                response = response.replace(tool_call, error_output)
        else:
            logger.warning(f"⚠️ Herramienta {tool_name} no disponible para agente {agent.id}")
    
    return response

# API Routes
@app.get("/")
async def root():
    return {
        "message": "AgentOS Backend API está funcionando!", 
        "version": "1.0.0",
        "status": "active",
        "agents_available": len(agents)
    }

@app.get("/health")
async def health_check():
    # Verificar conectividad con Gemini
    gemini_status = "OK"
    try:
        # Test básico de Gemini
        test_model = genai.GenerativeModel('gemini-1.5-pro')
        # No hacer llamada real, solo verificar que esté configurado
        if os.getenv("GEMINI_API_KEY"):
            gemini_status = "configured"
        else:
            gemini_status = "not_configured"
    except Exception as e:
        gemini_status = f"error: {str(e)}"
    
    # Verificar conexión a base de datos
    db_status = "connected" if db_manager.test_connection() else "disconnected"
    
    return {
        "status": "healthy", 
        "timestamp": "2025-01-22",
        "services": {
            "api": "running",
            "gemini": gemini_status,
            "agents": len(agents),
            "mcp_server": "running",
            "mcp_tools": len(mcp_server.tools),
            "database": db_status,
            "memory_system": "persistent",
            "vector_memory": "enabled",
            "embedding_model": vector_memory.model_name
        }
    }

@app.get("/api/v1/agents")
async def get_agents():
    """Obtiene lista de agentes disponibles"""
    logger.info("📋 Solicitando lista de agentes")
    return {"agents": list(agents.values())}

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Obtiene información de un agente específico"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    logger.info(f"🤖 Solicitando información del agente: {agent_id}")
    return {"agent": agents[agent_id]}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Endpoint principal para chatear con agentes"""
    
    logger.info(f"💬 Nueva consulta para agente {request.agent_id}: {request.message[:50]}...")
    
    # Validar agente
    if request.agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    
    agent = agents[request.agent_id]
    
    # Generar conversation_id si no existe
    conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
    
    # Inicializar conversación si no existe
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Agregar mensaje del usuario al historial
    user_message = ChatMessage(role="user", content=request.message)
    conversations[conversation_id].append(user_message)
    
    try:
        # Generar respuesta con Gemini
        ai_response = await generate_response_with_gemini(
            request.message, 
            agent, 
            conversations[conversation_id]
        )
        
        # Procesar herramientas en la respuesta
        final_response = await process_tools_in_response(ai_response, agent)
        
        # Agregar respuesta del agente al historial
        agent_message = ChatMessage(role="assistant", content=final_response)
        conversations[conversation_id].append(agent_message)
        
        # Limitar historial (últimos 30 mensajes)
        if len(conversations[conversation_id]) > 30:
            conversations[conversation_id] = conversations[conversation_id][-30:]
        
        logger.info(f"✅ Respuesta generada exitosamente para {conversation_id}")
        
        return ChatResponse(
            response=final_response,
            agent_id=request.agent_id,
            conversation_id=conversation_id,
            memory_used=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error procesando solicitud: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando solicitud: {str(e)}")

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Obtiene el historial de una conversación"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id],
        "message_count": len(conversations[conversation_id])
    }

# ===============================
# NUEVOS ENDPOINTS MCP ESTÁNDAR
# ===============================

@app.get("/mcp/info")
async def get_mcp_server_info():
    """Información del servidor MCP estándar"""
    return mcp_server.get_server_info()

@app.get("/mcp/tools")
async def list_mcp_tools():
    """Lista herramientas en formato MCP estándar"""
    tools = await get_mcp_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools
        ]
    }

class MCPToolRequest(BaseModel):
    name: str
    arguments: dict

@app.post("/mcp/tools/execute")
async def execute_mcp_tool_endpoint(request: MCPToolRequest):
    """Ejecuta herramienta usando protocolo MCP estándar"""
    try:
        result = await execute_mcp_tool(request.name, request.arguments)
        return {
            "result": result.content,
            "isError": result.isError,
            "timestamp": "2025-01-22"
        }
    except Exception as e:
        logger.error(f"❌ Error ejecutando herramienta MCP {request.name}: {e}")
        return {
            "result": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
            "timestamp": "2025-01-22"
        }

# Endpoint para comparar legacy vs MCP
@app.post("/api/v1/tools/compare")
async def compare_tool_execution(request: MCPToolRequest):
    """Compara ejecución legacy vs MCP para testing"""
    try:
        # Ejecución MCP
        mcp_result = await execute_mcp_tool(request.name, request.arguments)
        
        # Ejecución Legacy (para comparación)
        if request.name == "calculator":
            legacy_params = request.arguments.get("expression", "")
        elif request.name == "web_search":
            legacy_params = request.arguments.get("query", "")
        elif request.name == "memory":
            action = request.arguments.get("action", "")
            data = request.arguments.get("data", "")
            legacy_params = f"{action}:{data}" if data else action
        else:
            legacy_params = str(request.arguments)
        
        legacy_result = await execute_legacy_tool_via_mcp(request.name, legacy_params)
        
        return {
            "tool": request.name,
            "arguments": request.arguments,
            "mcp_result": mcp_result.content[0]["text"],
            "legacy_result": legacy_result,
            "results_match": mcp_result.content[0]["text"] == legacy_result,
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en comparación: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===============================
# NUEVOS ENDPOINTS MEMORIA PERSISTENTE - AVANCE 2
# ===============================

@app.get("/api/v1/memory/stats")
async def get_memory_system_stats():
    """Estadísticas generales del sistema de memoria"""
    system_stats = db_manager.get_system_stats()
    return {
        "system": system_stats,
        "memory_system": "persistent",
        "database_status": system_stats.get("database_status", "unknown")
    }

class MemoryStoreRequest(BaseModel):
    agent_id: str
    memory_type: str = "medium_term"  # short_term, medium_term, long_term
    content: str
    context: str = None
    importance_score: int = 5  # 1-10
    tags: List[str] = []

@app.post("/api/v1/memory/store")
async def store_agent_memory(request: MemoryStoreRequest):
    """Almacena memoria de agente en base de datos persistente"""
    try:
        memory_id = db_manager.store_memory(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            content=request.content,
            context=request.context,
            importance_score=request.importance_score,
            tags=request.tags
        )
        
        if memory_id > 0:
            return {
                "success": True,
                "memory_id": memory_id,
                "message": f"Memoria almacenada para agente {request.agent_id}",
                "timestamp": "2025-01-22"
            }
        else:
            raise HTTPException(status_code=500, detail="Error almacenando memoria")
            
    except Exception as e:
        logger.error(f"❌ Error en endpoint store_memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

class MemoryRecallRequest(BaseModel):
    agent_id: str
    memory_type: str = None
    search_term: str = None
    limit: int = 10

@app.post("/api/v1/memory/recall")
async def recall_agent_memory(request: MemoryRecallRequest):
    """Recupera memoria de agente desde base de datos"""
    try:
        memories = db_manager.recall_memory(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            search_term=request.search_term,
            limit=request.limit
        )
        
        return {
            "success": True,
            "agent_id": request.agent_id,
            "memories": memories,
            "count": len(memories),
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en endpoint recall_memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/v1/memory/stats/{agent_id}")
async def get_agent_memory_stats(agent_id: str):
    """Estadísticas de memoria de un agente específico"""
    try:
        stats = db_manager.get_memory_stats(agent_id)
        return {
            "agent_id": agent_id,
            "memory_stats": stats,
            "timestamp": "2025-01-22"
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo stats de memoria para {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para migrar conversación actual a BD (testing)
@app.post("/api/v1/migrate/conversation/{conversation_id}")
async def migrate_conversation_to_db(conversation_id: str):
    """Migra una conversación in-memory a base de datos persistente"""
    try:
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversación no encontrada en memoria")
        
        messages = conversations[conversation_id]
        if not messages:
            raise HTTPException(status_code=400, detail="Conversación vacía")
        
        # Determinar agent_id del primer mensaje del asistente
        agent_id = "default"
        for msg in messages:
            if hasattr(msg, 'role') and msg.role == "assistant":
                agent_id = getattr(msg, 'agent_id', "default")
                break
        
        # Crear conversación en BD
        success = db_manager.create_conversation(conversation_id, agent_id)
        if not success:
            raise HTTPException(status_code=500, detail="Error creando conversación en BD")
        
        # Migrar mensajes
        migrated_count = 0
        for message in messages:
            success = db_manager.add_message(
                conversation_id=conversation_id,
                role=message.role,
                content=message.content,
                agent_id=agent_id
            )
            if success:
                migrated_count += 1
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages_migrated": migrated_count,
            "agent_id": agent_id,
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error migrando conversación {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para probar memoria persistente vs in-memory
@app.post("/api/v1/memory/compare")
async def compare_memory_systems(request: MemoryRecallRequest):
    """Compara memoria persistente vs in-memory para testing"""
    try:
        # Memoria persistente
        persistent_memories = db_manager.recall_memory(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            search_term=request.search_term,
            limit=request.limit
        )
        
        # Memoria in-memory (actual)
        in_memory_count = len(conversations)
        in_memory_messages = 0
        for conv_messages in conversations.values():
            in_memory_messages += len(conv_messages)
        
        return {
            "comparison": {
                "persistent_memory": {
                    "memories_count": len(persistent_memories),
                    "system": "postgresql",
                    "searchable": True,
                    "survives_restart": True
                },
                "in_memory": {
                    "conversations": in_memory_count,
                    "total_messages": in_memory_messages,
                    "system": "python_dict",
                    "searchable": False,
                    "survives_restart": False
                }
            },
            "recommendation": "Use persistent memory for production",
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error comparando sistemas de memoria: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===============================
# NUEVOS ENDPOINTS MEMORIA VECTORIAL - AVANCE 2.5
# ===============================

class SemanticSearchRequest(BaseModel):
    agent_id: str
    query: str
    limit: int = 10
    memory_type: str = None
    min_score: float = 0.3

@app.post("/api/v1/memory/semantic-search")
async def semantic_search_endpoint(request: SemanticSearchRequest):
    """Búsqueda semántica usando embeddings vectoriales"""
    try:
        results = vector_memory.semantic_search(
            agent_id=request.agent_id,
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type,
            min_score=request.min_score
        )
        
        return {
            "success": True,
            "query": request.query,
            "agent_id": request.agent_id,
            "results": results,
            "count": len(results),
            "search_type": "semantic",
            "embedding_model": vector_memory.model_name,
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda semántica: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/v1/memory/hybrid-search")
async def hybrid_search_endpoint(request: SemanticSearchRequest):
    """Búsqueda híbrida: semántica + tradicional (implementando G-Memory approach)"""
    try:
        results = vector_memory.hybrid_search(
            agent_id=request.agent_id,
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type
        )
        
        # Separar estadísticas por tipo de búsqueda
        semantic_count = len([r for r in results if r.get('search_type') == 'semantic'])
        traditional_count = len([r for r in results if r.get('search_type') == 'traditional'])
        
        return {
            "success": True,
            "query": request.query,
            "agent_id": request.agent_id,
            "results": results,
            "count": len(results),
            "search_type": "hybrid",
            "breakdown": {
                "semantic_results": semantic_count,
                "traditional_results": traditional_count
            },
            "embedding_model": vector_memory.model_name,
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda híbrida: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/v1/memory/migrate-to-vectors/{agent_id}")
async def migrate_memories_to_vectors(agent_id: str):
    """Migra memorias existentes al sistema vectorial (SciBORG RAG indexing)"""
    try:
        migrated_count = vector_memory.migrate_existing_memories(agent_id)
        
        if migrated_count > 0:
            return {
                "success": True,
                "agent_id": agent_id,
                "migrated_memories": migrated_count,
                "message": f"✅ {migrated_count} memorias migradas a sistema vectorial",
                "embedding_model": vector_memory.model_name,
                "timestamp": "2025-01-22"
            }
        else:
            return {
                "success": False,
                "agent_id": agent_id,
                "migrated_memories": 0,
                "message": "No se encontraron memorias para migrar o error en migración",
                "timestamp": "2025-01-22"
            }
            
    except Exception as e:
        logger.error(f"❌ Error migrando memorias a vectores: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/v1/memory/vector-stats/{agent_id}")
async def get_vector_memory_stats(agent_id: str):
    """Estadísticas del sistema de memoria vectorial"""
    try:
        vector_stats = vector_memory.get_vector_stats(agent_id)
        traditional_stats = db_manager.get_memory_stats(agent_id)
        
        return {
            "agent_id": agent_id,
            "vector_memory": vector_stats,
            "traditional_memory": traditional_stats,
            "comparison": {
                "vectors_indexed": vector_stats.get('total_vectors', 0),
                "traditional_memories": traditional_stats.get('total_memories', 0),
                "embedding_coverage": f"{(vector_stats.get('total_vectors', 0) / max(traditional_stats.get('total_memories', 1), 1) * 100):.1f}%"
            },
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo stats vectoriales: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Modificar endpoint de store para auto-indexar en vectores
@app.post("/api/v1/memory/store-enhanced")
async def store_agent_memory_enhanced(request: MemoryStoreRequest):
    """Almacena memoria con auto-indexación vectorial"""
    try:
        # Almacenar en BD tradicional
        memory_id = db_manager.store_memory(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            content=request.content,
            context=request.context,
            importance_score=request.importance_score,
            tags=request.tags
        )
        
        if memory_id > 0:
            # Auto-indexar en sistema vectorial
            vector_success = vector_memory.add_memory_to_vector_store(
                agent_id=request.agent_id,
                memory_id=memory_id,
                content=request.content,
                memory_type=request.memory_type,
                importance_score=request.importance_score,
                tags=request.tags
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "message": f"Memoria almacenada para agente {request.agent_id}",
                "vector_indexed": vector_success,
                "enhanced_storage": True,
                "timestamp": "2025-01-22"
            }
        else:
            raise HTTPException(status_code=500, detail="Error almacenando memoria")
            
    except Exception as e:
        logger.error(f"❌ Error en store enhanced: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Test endpoint para comparar tipos de búsqueda
@app.post("/api/v1/memory/search-comparison")
async def compare_search_methods(request: SemanticSearchRequest):
    """Compara diferentes métodos de búsqueda (traditional vs semantic vs hybrid)"""
    try:
        # Búsqueda tradicional
        traditional_results = db_manager.recall_memory(
            agent_id=request.agent_id,
            memory_type=request.memory_type,
            search_term=request.query,
            limit=request.limit
        )
        
        # Búsqueda semántica
        semantic_results = vector_memory.semantic_search(
            agent_id=request.agent_id,
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type,
            min_score=request.min_score
        )
        
        # Búsqueda híbrida
        hybrid_results = vector_memory.hybrid_search(
            agent_id=request.agent_id,
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type
        )
        
        return {
            "query": request.query,
            "agent_id": request.agent_id,
            "comparison": {
                "traditional": {
                    "count": len(traditional_results),
                    "results": traditional_results,
                    "method": "SQL ILIKE"
                },
                "semantic": {
                    "count": len(semantic_results),
                    "results": semantic_results,
                    "method": f"FAISS + {vector_memory.model_name}"
                },
                "hybrid": {
                    "count": len(hybrid_results),
                    "results": hybrid_results,
                    "method": "Combined SQL + Vector"
                }
            },
            "recommendation": "hybrid" if len(hybrid_results) >= len(semantic_results) else "semantic",
            "timestamp": "2025-01-22"
        }
        
    except Exception as e:
        logger.error(f"❌ Error comparando métodos de búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 