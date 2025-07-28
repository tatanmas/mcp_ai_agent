"""
Orquestador Central - Cerebro del Sistema Unificado AgentOS
Implementa la arquitectura de Meta-Agente con orquestación inteligente
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import google.generativeai as genai
import os

# Importar módulos especializados
from app.agents.cognitive_coordinator import cognitive_coordinator
from app.memory.vector_memory import vector_memory
from app.optimization.adaptive_graph_pruning import adaptive_graph_pruning
from app.mcp.server import mcp_server, get_mcp_tools, execute_mcp_tool
from app.tools.real_tools import REAL_TOOLS_REGISTRY
from app.tools.mcp_bridge import mcp_bridge
from app.tasks.complex_tasks import complex_task_manager

logger = logging.getLogger(__name__)

class UnifiedOrchestrator:
    """
    Orquestador Central - Meta-Agente que coordina todos los sistemas
    """
    
    def __init__(self):
        self.session_id = None
        self.current_task = None
        self.agent_pool = {}
        self.memory_context = {}
        self.optimization_state = {}
        
        # Configurar Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            logger.error("GEMINI_API_KEY no configurada")
            self.model = None
    
    async def initialize_session(self, user_query: str) -> str:
        """Inicializar sesión y generar plan de ejecución"""
        self.session_id = str(uuid.uuid4())
        logger.info(f"🚀 Iniciando sesión {self.session_id}")
        
        # Analizar intención del usuario
        intent_analysis = await self._analyze_user_intent(user_query)
        
        # Descomponer tarea
        task_decomposition = await self._decompose_task(user_query, intent_analysis)
        
        # Seleccionar agentes óptimos
        agent_selection = await self._select_optimal_agents(task_decomposition)
        
        # Crear plan de ejecución
        execution_plan = {
            "session_id": self.session_id,
            "intent": intent_analysis,
            "decomposition": task_decomposition,
            "agents": agent_selection,
            "created_at": datetime.now().isoformat()
        }
        
        self.current_task = execution_plan
        return self.session_id
    
    async def _analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """Analizar la intención del usuario usando LLM"""
        if not self.model:
            return {"intent": "general", "confidence": 0.5}
        
        prompt = f"""
        Analiza la siguiente consulta del usuario y determina:
        1. Tipo de tarea (investigación, análisis, creación, optimización, etc.)
        2. Complejidad (baja, media, alta)
        3. Herramientas necesarias (web_search, document_analysis, data_visualization, etc.)
        4. Agentes cognitivos requeridos
        5. Patrón de coordinación recomendado (AutoGen, MIRIX, G-Memory, etc.)
        
        Consulta: {query}
        
        Responde en formato JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error analizando intención: {e}")
            return {"intent": "general", "confidence": 0.5}
    
    async def _decompose_task(self, query: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Descomponer tarea en sub-tareas usando Chain-of-Thought"""
        if not self.model:
            return [{"task": query, "type": "general"}]
        
        prompt = f"""
        Descompón la siguiente tarea en sub-tareas específicas usando Chain-of-Thought:
        
        Tarea principal: {query}
        Análisis de intención: {json.dumps(intent, indent=2)}
        
        Para cada sub-tarea especifica:
        1. Descripción clara
        2. Tipo de operación
        3. Herramientas necesarias
        4. Dependencias con otras sub-tareas
        5. Criterios de éxito
        
        Responde en formato JSON con array de sub-tareas.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error descomponiendo tarea: {e}")
            return [{"task": query, "type": "general"}]
    
    async def _select_optimal_agents(self, decomposition: List[Dict[str, Any]]) -> List[str]:
        """Seleccionar agentes óptimos usando AGP"""
        try:
            # Usar AGP para optimización de agentes
            optimization_result = await adaptive_graph_pruning.optimize_agent_selection(
                tasks=decomposition,
                available_agents=cognitive_coordinator.get_available_agents()
            )
            
            return optimization_result.get("selected_agents", [])
        except Exception as e:
            logger.error(f"Error seleccionando agentes: {e}")
            return ["cognitive_coordinator"]
    
    async def execute_task(self, user_query: str) -> Dict[str, Any]:
        """Ejecutar tarea completa usando orquestación inteligente"""
        try:
            # 1. Inicializar sesión
            session_id = await self.initialize_session(user_query)
            
            # 2. Recuperar contexto de memoria
            memory_context = await self._retrieve_memory_context(user_query)
            
            # 3. Ejecutar sub-tareas con agentes cognitivos
            results = await self._execute_subtasks_with_agents()
            
            # 4. Sintetizar resultados
            final_result = await self._synthesize_results(results)
            
            # 5. Actualizar memoria y aprender
            await self._update_memory_and_learn(user_query, final_result)
            
            return {
                "success": True,
                "session_id": session_id,
                "result": final_result,
                "agents_used": self.current_task.get("agents", []),
                "memory_accessed": bool(memory_context),
                "optimization_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando tarea: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
    
    async def _retrieve_memory_context(self, query: str) -> Dict[str, Any]:
        """Recuperar contexto relevante de memoria (MIRIX-inspired)"""
        try:
            # Active Retrieval - generar tópico de conversación
            topic = await self._generate_conversation_topic(query)
            
            # Buscar en memoria vectorial
            memory_results = await vector_memory.search_memories(
                agent_id="unified_orchestrator",
                query=topic,
                limit=5
            )
            
            self.memory_context = {
                "topic": topic,
                "relevant_memories": memory_results,
                "retrieved_at": datetime.now().isoformat()
            }
            
            return self.memory_context
            
        except Exception as e:
            logger.error(f"Error recuperando memoria: {e}")
            return {}
    
    async def _generate_conversation_topic(self, query: str) -> str:
        """Generar tópico de conversación para Active Retrieval"""
        if not self.model:
            return query
        
        prompt = f"""
        Genera un tópico de conversación conciso (2-3 palabras) para la siguiente consulta:
        Consulta: {query}
        
        El tópico debe ser útil para recuperar información relevante de memoria.
        Responde solo el tópico, sin explicaciones.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generando tópico: {e}")
            return query
    
    async def _execute_subtasks_with_agents(self) -> List[Dict[str, Any]]:
        """Ejecutar sub-tareas con agentes cognitivos especializados"""
        results = []
        decomposition = self.current_task.get("decomposition", [])
        
        for i, subtask in enumerate(decomposition):
            try:
                logger.info(f"🔄 Ejecutando sub-tarea {i+1}/{len(decomposition)}: {subtask.get('task', '')}")
                
                # Seleccionar agente para esta sub-tarea
                agent_id = await self._select_agent_for_subtask(subtask)
                
                # ===============================
                # INTEGRACIÓN MCP BRIDGE (NUEVO)
                # ===============================
                
                # Verificar si la sub-tarea requiere herramientas reales
                subtask_context = {
                    "subtask_info": subtask,
                    "memory_context": self.memory_context,
                    "session_id": self.session_id
                }
                
                real_tools_result = await mcp_bridge.execute_with_real_tools(
                    task=subtask.get("task", ""),
                    context=subtask_context
                )
                
                # Si requiere herramientas reales, usar contexto mejorado
                if real_tools_result.get("requires_real_tools", False):
                    logger.info(f"🔧 Usando herramientas reales para sub-tarea {i+1}")
                    subtask_context = real_tools_result.get("enhanced_context", subtask_context)
                    
                    # Añadir resultados de herramientas reales al contexto
                    subtask_context["real_tool_results"] = real_tools_result.get("real_tool_results", [])
                
                # Ejecutar con agente cognitivo (con o sin herramientas reales)
                result = await cognitive_coordinator.coordinate_with_cognitive_agents(
                    task=subtask.get("task", ""),
                    user_context=subtask_context
                )
                
                # Añadir información de herramientas reales al resultado
                if real_tools_result.get("requires_real_tools", False):
                    result["real_tools_used"] = real_tools_result.get("real_tool_results", [])
                    result["enhanced_with_real_tools"] = True
                else:
                    result["enhanced_with_real_tools"] = False
                
                results.append({
                    "subtask_id": i,
                    "agent_id": agent_id,
                    "result": result,
                    "success": True,
                    "real_tools_enhanced": real_tools_result.get("requires_real_tools", False)
                })
                
            except Exception as e:
                logger.error(f"Error en sub-tarea {i+1}: {e}")
                results.append({
                    "subtask_id": i,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def _select_agent_for_subtask(self, subtask: Dict[str, Any]) -> str:
        """Seleccionar agente específico para una sub-tarea"""
        task_type = subtask.get("type", "general")
        
        # Mapeo de tipos de tarea a agentes especializados
        agent_mapping = {
            "research": "research_agent",
            "analysis": "analysis_agent", 
            "creation": "creation_agent",
            "optimization": "optimization_agent",
            "coordination": "coordination_agent"
        }
        
        return agent_mapping.get(task_type, "cognitive_coordinator")
    
    async def _synthesize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sintetizar resultados de sub-tareas en respuesta coherente"""
        if not self.model:
            return {"synthesis": "Resultados procesados", "subtasks": len(results)}
        
        # Preparar contexto para síntesis
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            return {"error": "No se completaron sub-tareas exitosamente"}
        
        prompt = f"""
        Sintetiza los siguientes resultados de sub-tareas en una respuesta coherente:
        
        Sub-tareas completadas: {len(successful_results)}
        
        Resultados:
        {json.dumps(successful_results, indent=2)}
        
        Genera una respuesta que:
        1. Integre todos los hallazgos relevantes
        2. Sea coherente y bien estructurada
        3. Incluya insights y conclusiones
        4. Sea útil para el usuario
        
        Responde en formato JSON con campos: summary, insights, recommendations, data_sources
        """
        
        try:
            response = self.model.generate_content(prompt)
            synthesis = json.loads(response.text)
            
            return {
                "synthesis": synthesis,
                "subtasks_processed": len(successful_results),
                "total_subtasks": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error sintetizando resultados: {e}")
            return {
                "synthesis": "Resultados procesados exitosamente",
                "subtasks_processed": len(successful_results),
                "total_subtasks": len(results)
            }
    
    async def _update_memory_and_learn(self, original_query: str, final_result: Dict[str, Any]):
        """Actualizar memoria y aprender de la ejecución"""
        try:
            # Almacenar experiencia en memoria
            await vector_memory.store_memory(
                agent_id="unified_orchestrator",
                memory_type="episodic",
                content=f"Query: {original_query} | Result: {json.dumps(final_result)}",
                context=f"Session: {self.session_id}",
                importance_score=7
            )
            
            # Actualizar optimización con feedback
            await adaptive_graph_pruning.update_optimization_metrics(
                session_id=self.session_id,
                success=final_result.get("success", False),
                agents_used=self.current_task.get("agents", []),
                performance_metrics={
                    "subtasks_completed": final_result.get("subtasks_processed", 0),
                    "total_subtasks": final_result.get("total_subtasks", 0)
                }
            )
            
            logger.info(f"✅ Memoria y optimización actualizadas para sesión {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando memoria y optimización: {e}")

# Instancia global del orquestador
orchestrator = UnifiedOrchestrator()
unified_orchestrator = orchestrator  # Alias para compatibilidad 