"""
MCP Bridge - AgentOS Enterprise
Puente que integra herramientas reales vía MCP con el sistema actual
Implementa Factor 4: Herramientas transparentes
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..mcp.server import mcp_server, execute_mcp_tool
from .real_tools import RealWebSearch, RealDocumentAnalyzer, RealDataVisualizer, RealFileOperations

logger = logging.getLogger(__name__)

class MCPBridge:
    """
    Puente que conecta el sistema actual con herramientas reales vía MCP
    Permite descubrimiento dinámico y ejecución transparente
    """
    
    def __init__(self):
        self.real_tools = {
            "web_search": RealWebSearch(),
            "document_analyzer": RealDocumentAnalyzer(),
            "data_visualizer": RealDataVisualizer(),
            "file_operations": RealFileOperations()
        }
        
        # Registrar herramientas reales en MCP
        self._register_real_tools_in_mcp()
        
        logger.info("🌉 MCP Bridge inicializado - Herramientas reales disponibles")
    
    def _register_real_tools_in_mcp(self):
        """Registra herramientas reales en el servidor MCP"""
        
        # Web Search Tool
        mcp_server.register_tool(
            name="real_web_search",
            description="Búsqueda web real usando DuckDuckGo y scraping",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de búsqueda"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Número máximo de resultados",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            handler=self._real_web_search_handler
        )
        
        # Document Analysis Tool
        mcp_server.register_tool(
            name="real_document_analysis",
            description="Análisis real de documentos (PDF, DOCX, TXT)",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta al archivo a analizar"
                    }
                },
                "required": ["file_path"]
            },
            handler=self._real_document_analysis_handler
        )
        
        # Data Visualization Tool
        mcp_server.register_tool(
            name="real_data_visualization",
            description="Creación de gráficos reales con matplotlib/seaborn",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Datos para visualizar"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "pie", "scatter", "histogram"],
                        "description": "Tipo de gráfico"
                    },
                    "title": {
                        "type": "string",
                        "description": "Título del gráfico"
                    }
                },
                "required": ["data", "chart_type"]
            },
            handler=self._real_data_visualization_handler
        )
        
        # File Operations Tool
        mcp_server.register_tool(
            name="real_file_operations",
            description="Operaciones reales de archivos",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "list"],
                        "description": "Tipo de operación"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Ruta del archivo"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido para escribir (solo para write)"
                    }
                },
                "required": ["operation", "file_path"]
            },
            handler=self._real_file_operations_handler
        )
        
        logger.info(f"✅ {len(self.real_tools)} herramientas reales registradas en MCP")
    
    # Handlers para herramientas reales
    async def _real_web_search_handler(self, args: Dict[str, Any]) -> str:
        """Handler para búsqueda web real"""
        try:
            query = args.get("query", "")
            max_results = args.get("max_results", 5)
            
            web_search = self.real_tools["web_search"]
            result = await web_search.search(query, max_results)
            
            if result["success"]:
                results_text = "\n".join([
                    f"- {r['title']}: {r['snippet'][:100]}..."
                    for r in result["results"][:3]
                ])
                return f"Búsqueda web real completada:\n{results_text}"
            else:
                return "No se encontraron resultados en la búsqueda web"
                
        except Exception as e:
            logger.error(f"❌ Error en búsqueda web real: {e}")
            return f"Error en búsqueda web: {str(e)}"
    
    async def _real_document_analysis_handler(self, args: Dict[str, Any]) -> str:
        """Handler para análisis de documentos real"""
        try:
            file_path = args.get("file_path", "")
            
            doc_analyzer = self.real_tools["document_analyzer"]
            result = await doc_analyzer.analyze_document(file_path)
            
            if result["success"]:
                return f"Análisis de documento completado:\n- Tipo: {result['file_type']}\n- Páginas: {result.get('pages', 'N/A')}\n- Contenido extraído: {result['content'][:200]}..."
            else:
                return f"Error analizando documento: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"❌ Error en análisis de documento: {e}")
            return f"Error en análisis de documento: {str(e)}"
    
    async def _real_data_visualization_handler(self, args: Dict[str, Any]) -> str:
        """Handler para visualización de datos real"""
        try:
            data = args.get("data", {})
            chart_type = args.get("chart_type", "bar")
            title = args.get("title", "Gráfico")
            
            data_viz = self.real_tools["data_visualizer"]
            result = await data_viz.create_chart(data, chart_type)
            
            if result["success"]:
                return f"Gráfico creado exitosamente:\n- Tipo: {chart_type}\n- Título: {title}\n- Archivo: {result['file_path']}"
            else:
                return f"Error creando gráfico: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"❌ Error en visualización de datos: {e}")
            return f"Error en visualización: {str(e)}"
    
    async def _real_file_operations_handler(self, args: Dict[str, Any]) -> str:
        """Handler para operaciones de archivos reales"""
        try:
            operation = args.get("operation", "")
            file_path = args.get("file_path", "")
            content = args.get("content", "")
            
            file_ops = self.real_tools["file_operations"]
            
            if operation == "read":
                result = await file_ops.read_file(file_path)
            elif operation == "write":
                result = await file_ops.write_file(file_path, content)
            elif operation == "list":
                result = await file_ops.list_directory(file_path)
            else:
                return f"Operación no soportada: {operation}"
            
            if result["success"]:
                if operation == "read":
                    return f"Archivo leído: {result['content'][:200]}..."
                elif operation == "write":
                    return f"Archivo escrito exitosamente: {file_path}"
                elif operation == "list":
                    return f"Directorio listado: {len(result['files'])} archivos encontrados"
            else:
                return f"Error en operación de archivo: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error en operación de archivo: {e}")
            return f"Error en operación de archivo: {str(e)}"
    
    # Métodos de integración con el sistema actual
    async def execute_with_real_tools(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta tarea con herramientas reales cuando sea apropiado
        Wrapper que añade herramientas reales al flujo actual
        """
        try:
            # Detectar si la tarea requiere herramientas reales
            tool_requirements = await self._detect_tool_requirements(task)
            
            if not tool_requirements:
                # No requiere herramientas reales, continuar con flujo normal
                return {"requires_real_tools": False, "message": "Continuar con flujo normal"}
            
            # Ejecutar herramientas reales vía MCP
            real_tool_results = []
            for tool_name, tool_args in tool_requirements.items():
                try:
                    result = await execute_mcp_tool(tool_name, tool_args)
                    real_tool_results.append({
                        "tool": tool_name,
                        "result": result.content[0]['text'] if result.content else "No result",
                        "success": not result.isError
                    })
                except Exception as e:
                    logger.error(f"❌ Error ejecutando herramienta real {tool_name}: {e}")
                    real_tool_results.append({
                        "tool": tool_name,
                        "result": f"Error: {str(e)}",
                        "success": False
                    })
            
            return {
                "requires_real_tools": True,
                "real_tool_results": real_tool_results,
                "enhanced_context": {
                    **context,
                    "real_tool_data": real_tool_results
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en execute_with_real_tools: {e}")
            return {"requires_real_tools": False, "error": str(e)}
    
    async def _detect_tool_requirements(self, task: str) -> Dict[str, Dict[str, Any]]:
        """
        Detecta qué herramientas reales requiere una tarea
        Análisis simple basado en palabras clave
        """
        task_lower = task.lower()
        requirements = {}
        
        # Detectar búsqueda web
        web_keywords = ["busca", "investiga", "encuentra", "consulta", "web", "internet", "online"]
        if any(keyword in task_lower for keyword in web_keywords):
            requirements["real_web_search"] = {
                "query": task,
                "max_results": 5
            }
        
        # Detectar análisis de documentos
        doc_keywords = ["analiza", "documento", "pdf", "word", "excel", "archivo"]
        if any(keyword in task_lower for keyword in doc_keywords):
            # Esto requeriría que el usuario proporcione la ruta del archivo
            requirements["real_document_analysis"] = {
                "file_path": "path/to/document"  # Placeholder
            }
        
        # Detectar visualización de datos
        viz_keywords = ["gráfico", "visualiza", "grafica", "chart", "plot", "datos"]
        if any(keyword in task_lower for keyword in viz_keywords):
            requirements["real_data_visualization"] = {
                "data": {"placeholder": "data"},  # Placeholder
                "chart_type": "bar",
                "title": "Gráfico generado"
            }
        
        # Detectar operaciones de archivos
        file_keywords = ["lee", "escribe", "crea", "archivo", "guarda", "lee archivo"]
        if any(keyword in task_lower for keyword in file_keywords):
            requirements["real_file_operations"] = {
                "operation": "read",
                "file_path": "path/to/file"  # Placeholder
            }
        
        return requirements
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Obtiene lista de herramientas disponibles vía MCP"""
        try:
            tools = await mcp_server.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools
            ]
        except Exception as e:
            logger.error(f"❌ Error obteniendo herramientas disponibles: {e}")
            return []

# Instancia global del MCP Bridge
mcp_bridge = MCPBridge() 