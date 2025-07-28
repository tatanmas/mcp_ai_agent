"""
Cognitive MCP Bridge - AgentOS
Bridge que permite a los agentes cognitivos usar herramientas MCP
Migra agentes de sistema legacy a MCP estándar
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..mcp.server import mcp_server, execute_mcp_tool


logger = logging.getLogger(__name__)

class CognitiveMCPBridge:
    """
    Bridge que conecta agentes cognitivos con herramientas MCP
    Permite que los agentes usen herramientas reales vía MCP
    """
    
    def __init__(self):
        self.available_tools = {}
        self.tool_usage_stats = {}
        
        # Inicializar bridge
        self._initialize_bridge()
        
        logger.info("🧠 Cognitive MCP Bridge inicializado")
    
    def _initialize_bridge(self):
        """Inicializar bridge con herramientas MCP disponibles"""
        try:
            # Obtener herramientas disponibles del MCP server
            asyncio.create_task(self._load_available_tools())
            
        except Exception as e:
            logger.error(f"Error inicializando Cognitive MCP Bridge: {e}")
    
    async def _load_available_tools(self):
        """Cargar herramientas disponibles del MCP server"""
        try:
            tools = await mcp_server.list_tools()
            
            for tool in tools:
                self.available_tools[tool.name] = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                    "category": self._categorize_tool(tool.name)
                }
            
            logger.info(f"✅ {len(self.available_tools)} herramientas MCP cargadas para agentes cognitivos")
            
        except Exception as e:
            logger.error(f"Error cargando herramientas MCP: {e}")
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorizar herramienta para agentes cognitivos"""
        if "web" in tool_name or "search" in tool_name:
            return "research"
        elif "document" in tool_name or "pdf" in tool_name or "excel" in tool_name:
            return "analysis"
        elif "chart" in tool_name or "visual" in tool_name or "statistical" in tool_name:
            return "visualization"
        elif "file" in tool_name or "read" in tool_name or "write" in tool_name:
            return "file_operations"
        elif "calculator" in tool_name:
            return "computation"
        else:
            return "general"
    
    async def execute_tool_for_agent(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar herramienta MCP para un agente cognitivo específico
        """
        try:
            if tool_name not in self.available_tools:
                return {
                    "success": False,
                    "error": f"Herramienta '{tool_name}' no disponible",
                    "agent_id": agent_id
                }
            
            # Ejecutar herramienta vía MCP
            result = await execute_mcp_tool(tool_name, arguments)
            
            # Actualizar estadísticas de uso
            self._update_tool_usage_stats(agent_id, tool_name, result.isError)
            
            return {
                "success": not result.isError,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "result": result.content[0]['text'] if result.content else "No result",
                "is_error": result.isError,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {tool_name} para agente {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "tool_name": tool_name
            }
    
    def _update_tool_usage_stats(self, agent_id: str, tool_name: str, is_error: bool):
        """Actualizar estadísticas de uso de herramientas"""
        if agent_id not in self.tool_usage_stats:
            self.tool_usage_stats[agent_id] = {}
        
        if tool_name not in self.tool_usage_stats[agent_id]:
            self.tool_usage_stats[agent_id][tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "last_used": None
            }
        
        stats = self.tool_usage_stats[agent_id][tool_name]
        stats["total_calls"] += 1
        stats["last_used"] = datetime.utcnow().isoformat()
        
        if is_error:
            stats["failed_calls"] += 1
        else:
            stats["successful_calls"] += 1
    
    async def get_tools_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Obtener herramientas recomendadas para un agente específico"""
        try:
            agent_specialization = self._get_agent_specialization(agent_id)
            
            # Filtrar herramientas por especialización del agente
            recommended_tools = []
            
            for tool_name, tool_info in self.available_tools.items():
                if self._is_tool_suitable_for_agent(tool_name, agent_specialization):
                    recommended_tools.append({
                        **tool_info,
                        "suitability_score": self._calculate_suitability_score(tool_name, agent_specialization)
                    })
            
            # Ordenar por score de adecuación
            recommended_tools.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            return recommended_tools
            
        except Exception as e:
            logger.error(f"Error obteniendo herramientas para agente {agent_id}: {e}")
            return []
    
    def _get_agent_specialization(self, agent_id: str) -> str:
        """Obtener especialización de un agente"""
        specializations = {
            "researcher": "research",
            "coder": "development", 
            "coordinator": "coordination"
        }
        return specializations.get(agent_id, "general")
    
    def _is_tool_suitable_for_agent(self, tool_name: str, agent_specialization: str) -> bool:
        """Determinar si una herramienta es adecuada para un agente"""
        tool_category = self._categorize_tool(tool_name)
        
        suitability_mapping = {
            "research": ["research", "analysis", "general"],
            "development": ["file_operations", "computation", "general"],
            "coordination": ["visualization", "analysis", "general"]
        }
        
        suitable_categories = suitability_mapping.get(agent_specialization, ["general"])
        return tool_category in suitable_categories
    
    def _calculate_suitability_score(self, tool_name: str, agent_specialization: str) -> float:
        """Calcular score de adecuación de herramienta para agente"""
        tool_category = self._categorize_tool(tool_name)
        
        # Scores de adecuación por especialización
        scores = {
            "research": {
                "research": 1.0,
                "analysis": 0.8,
                "visualization": 0.6,
                "file_operations": 0.4,
                "computation": 0.3,
                "general": 0.5
            },
            "development": {
                "file_operations": 1.0,
                "computation": 0.9,
                "analysis": 0.7,
                "visualization": 0.5,
                "research": 0.3,
                "general": 0.5
            },
            "coordination": {
                "visualization": 1.0,
                "analysis": 0.8,
                "research": 0.6,
                "file_operations": 0.4,
                "computation": 0.3,
                "general": 0.5
            }
        }
        
        return scores.get(agent_specialization, {}).get(tool_category, 0.5)
    
    async def execute_coordinated_tools(self, task: str, agent_ids: List[str]) -> Dict[str, Any]:
        """
        Ejecutar herramientas coordinadas para múltiples agentes
        """
        try:
            # Analizar tarea para determinar herramientas necesarias
            required_tools = await self._analyze_task_for_tools(task)
            
            # Asignar herramientas a agentes
            agent_assignments = self._assign_tools_to_agents(required_tools, agent_ids)
            
            # Ejecutar herramientas en paralelo
            results = {}
            for agent_id, tool_assignments in agent_assignments.items():
                agent_results = []
                for tool_name, arguments in tool_assignments.items():
                    result = await self.execute_tool_for_agent(agent_id, tool_name, arguments)
                    agent_results.append(result)
                results[agent_id] = agent_results
            
            return {
                "success": True,
                "task": task,
                "agents_involved": agent_ids,
                "tools_executed": len([r for agent_results in results.values() for r in agent_results]),
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en ejecución coordinada de herramientas: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    async def _analyze_task_for_tools(self, task: str) -> List[Dict[str, Any]]:
        """Analizar tarea para determinar herramientas necesarias"""
        task_lower = task.lower()
        required_tools = []
        
        # Detectar necesidades de búsqueda web
        web_keywords = ["busca", "investiga", "encuentra", "consulta", "web", "internet"]
        if any(keyword in task_lower for keyword in web_keywords):
            required_tools.append({
                "tool_name": "real_web_search",
                "arguments": {"query": task, "max_results": 5},
                "priority": "high"
            })
        
        # Detectar necesidades de análisis de documentos
        doc_keywords = ["analiza", "documento", "pdf", "word", "excel", "archivo"]
        if any(keyword in task_lower for keyword in doc_keywords):
            required_tools.append({
                "tool_name": "real_analyze_document",
                "arguments": {"file_path": "path/to/document"},
                "priority": "medium"
            })
        
        # Detectar necesidades de visualización
        viz_keywords = ["gráfico", "visualiza", "grafica", "chart", "plot", "datos"]
        if any(keyword in task_lower for keyword in viz_keywords):
            required_tools.append({
                "tool_name": "real_create_chart",
                "arguments": {"data": {"placeholder": "data"}, "chart_type": "bar"},
                "priority": "medium"
            })
        
        # Detectar necesidades de operaciones de archivos
        file_keywords = ["lee", "escribe", "crea", "archivo", "guarda"]
        if any(keyword in task_lower for keyword in file_keywords):
            required_tools.append({
                "tool_name": "real_read_file",
                "arguments": {"file_path": "path/to/file"},
                "priority": "low"
            })
        
        return required_tools
    
    def _assign_tools_to_agents(self, required_tools: List[Dict[str, Any]], agent_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Asignar herramientas a agentes según especialización"""
        assignments = {agent_id: {} for agent_id in agent_ids}
        
        for tool_info in required_tools:
            tool_name = tool_info["tool_name"]
            arguments = tool_info["arguments"]
            
            # Encontrar agente más adecuado para la herramienta
            best_agent = self._find_best_agent_for_tool(tool_name, agent_ids)
            
            if best_agent:
                assignments[best_agent][tool_name] = arguments
        
        return assignments
    
    def _find_best_agent_for_tool(self, tool_name: str, agent_ids: List[str]) -> Optional[str]:
        """Encontrar el agente más adecuado para una herramienta"""
        best_agent = None
        best_score = 0
        
        for agent_id in agent_ids:
            specialization = self._get_agent_specialization(agent_id)
            score = self._calculate_suitability_score(tool_name, specialization)
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Obtener estado del bridge"""
        return {
            "available_tools": len(self.available_tools),
            "tool_categories": {
                category: len([t for t in self.available_tools.values() if t["category"] == category])
                for category in set(t["category"] for t in self.available_tools.values())
            },
            "agent_tool_usage": self.tool_usage_stats,
            "bridge_status": "operational"
        }

# Instancia global del bridge cognitivo MCP
cognitive_mcp_bridge = CognitiveMCPBridge() 