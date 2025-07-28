"""
MCP Real Tools Bridge - AgentOS Enterprise
Integración óptima de herramientas reales con MCP Server
Migra real_tools.py a formato MCP estándar
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..mcp.server import mcp_server, MCPToolCall, MCPToolResult
from .real_tools import (
    RealWebSearch, RealDocumentAnalyzer, 
    RealDataVisualizer, RealFileOperations
)

logger = logging.getLogger(__name__)

class MCPRealToolsBridge:
    """
    Bridge que integra herramientas reales directamente con MCP
    Migra real_tools.py a formato MCP estándar para interoperabilidad
    """
    
    def __init__(self):
        # Instanciar herramientas reales
        self.real_tools = {
            "web_search": RealWebSearch(),
            "document_analyzer": RealDocumentAnalyzer(),
            "data_visualizer": RealDataVisualizer(),
            "file_operations": RealFileOperations()
        }
        
        # Registrar todas las herramientas reales en MCP
        self._register_all_real_tools()
        
        logger.info("🔧 MCP Real Tools Bridge inicializado - Herramientas reales integradas")
    
    def _register_all_real_tools(self):
        """Registra todas las herramientas reales en formato MCP estándar"""
        
        # 1. Web Search Tools
        self._register_web_search_tools()
        
        # 2. Document Analysis Tools
        self._register_document_analysis_tools()
        
        # 3. Data Visualization Tools
        self._register_data_visualization_tools()
        
        # 4. File Operation Tools
        self._register_file_operation_tools()
        
        logger.info(f"✅ {len(self.real_tools)} categorías de herramientas reales registradas en MCP")
    
    def _register_web_search_tools(self):
        """Registra herramientas de búsqueda web"""
        
        # Búsqueda web básica
        mcp_server.register_tool(
            name="real_web_search",
            description="Búsqueda web real usando DuckDuckGo con scraping inteligente",
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
            handler=self._handle_web_search
        )
        
        # Obtener contenido de página
        mcp_server.register_tool(
            name="real_get_page_content",
            description="Obtener contenido real de una página web específica",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL de la página a obtener"
                    }
                },
                "required": ["url"]
            },
            handler=self._handle_get_page_content
        )
    
    def _register_document_analysis_tools(self):
        """Registra herramientas de análisis de documentos"""
        
        # Análisis general de documentos
        mcp_server.register_tool(
            name="real_analyze_document",
            description="Análisis real de documentos (PDF, DOCX, XLSX, TXT)",
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
            handler=self._handle_analyze_document
        )
        
        # Análisis específico por tipo
        mcp_server.register_tool(
            name="real_analyze_pdf",
            description="Análisis específico de archivos PDF",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta al archivo PDF"
                    }
                },
                "required": ["file_path"]
            },
            handler=self._handle_analyze_pdf
        )
        
        mcp_server.register_tool(
            name="real_analyze_excel",
            description="Análisis específico de archivos Excel",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta al archivo Excel"
                    }
                },
                "required": ["file_path"]
            },
            handler=self._handle_analyze_excel
        )
    
    def _register_data_visualization_tools(self):
        """Registra herramientas de visualización de datos"""
        
        # Creación de gráficos
        mcp_server.register_tool(
            name="real_create_chart",
            description="Crear gráficos reales con matplotlib/seaborn",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Datos para visualizar (formato: {'x': [...], 'y': [...]})"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "pie", "histogram"],
                        "description": "Tipo de gráfico"
                    },
                    "title": {
                        "type": "string",
                        "description": "Título del gráfico"
                    },
                    "xlabel": {
                        "type": "string",
                        "description": "Etiqueta del eje X"
                    },
                    "ylabel": {
                        "type": "string",
                        "description": "Etiqueta del eje Y"
                    }
                },
                "required": ["data", "chart_type"]
            },
            handler=self._handle_create_chart
        )
        
        # Análisis estadístico
        mcp_server.register_tool(
            name="real_statistical_analysis",
            description="Análisis estadístico de datos",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array de datos numéricos"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["descriptive", "correlation", "distribution"],
                        "description": "Tipo de análisis"
                    }
                },
                "required": ["data"]
            },
            handler=self._handle_statistical_analysis
        )
    
    def _register_file_operation_tools(self):
        """Registra herramientas de operaciones de archivos"""
        
        # Leer archivo
        mcp_server.register_tool(
            name="real_read_file",
            description="Leer contenido de un archivo",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta al archivo"
                    }
                },
                "required": ["file_path"]
            },
            handler=self._handle_read_file
        )
        
        # Escribir archivo
        mcp_server.register_tool(
            name="real_write_file",
            description="Escribir contenido a un archivo",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Ruta del archivo"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido a escribir"
                    }
                },
                "required": ["file_path", "content"]
            },
            handler=self._handle_write_file
        )
        
        # Listar directorio
        mcp_server.register_tool(
            name="real_list_directory",
            description="Listar contenido de un directorio",
            input_schema={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Ruta del directorio"
                    }
                },
                "required": ["dir_path"]
            },
            handler=self._handle_list_directory
        )
    
    # Handlers para herramientas reales
    async def _handle_web_search(self, args: Dict[str, Any]) -> str:
        """Handler para búsqueda web real"""
        try:
            query = args.get("query", "")
            max_results = args.get("max_results", 5)
            
            result = await self.real_tools["web_search"].search(query, max_results)
            
            if result["success"]:
                results_text = "\n".join([
                    f"• {r['title']}\n  {r['snippet'][:150]}...\n  URL: {r['url']}"
                    for r in result["results"][:3]
                ])
                return f"🔍 Búsqueda web completada para '{query}':\n\n{results_text}"
            else:
                return f"❌ No se encontraron resultados para '{query}'"
                
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            return f"❌ Error en búsqueda web: {str(e)}"
    
    async def _handle_get_page_content(self, args: Dict[str, Any]) -> str:
        """Handler para obtener contenido de página"""
        try:
            url = args.get("url", "")
            
            result = await self.real_tools["web_search"].get_page_content(url)
            
            if result["success"]:
                return f"📄 Contenido de {url}:\n\n{result['content'][:500]}..."
            else:
                return f"❌ Error obteniendo contenido: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error obteniendo contenido: {e}")
            return f"❌ Error obteniendo contenido: {str(e)}"
    
    async def _handle_analyze_document(self, args: Dict[str, Any]) -> str:
        """Handler para análisis general de documentos"""
        try:
            file_path = args.get("file_path", "")
            
            result = await self.real_tools["document_analyzer"].analyze_document(file_path)
            
            if result["success"]:
                stats = result.get("statistics", {})
                return f"📄 Análisis de documento completado:\n" \
                       f"• Tipo: {result['file_type']}\n" \
                       f"• Páginas: {result.get('pages', 'N/A')}\n" \
                       f"• Caracteres: {stats.get('total_characters', 'N/A')}\n" \
                       f"• Palabras: {stats.get('total_words', 'N/A')}\n" \
                       f"• Contenido: {result['content'][:200]}..."
            else:
                return f"❌ Error analizando documento: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error analizando documento: {e}")
            return f"❌ Error analizando documento: {str(e)}"
    
    async def _handle_analyze_pdf(self, args: Dict[str, Any]) -> str:
        """Handler específico para PDFs"""
        try:
            file_path = args.get("file_path", "")
            
            result = await self.real_tools["document_analyzer"]._analyze_pdf(file_path)
            
            if result["success"]:
                stats = result.get("statistics", {})
                return f"📄 Análisis PDF completado:\n" \
                       f"• Páginas: {result['pages']}\n" \
                       f"• Caracteres: {stats.get('total_characters', 'N/A')}\n" \
                       f"• Palabras: {stats.get('total_words', 'N/A')}\n" \
                       f"• Contenido: {result['content'][:300]}..."
            else:
                return f"❌ Error analizando PDF: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error analizando PDF: {e}")
            return f"❌ Error analizando PDF: {str(e)}"
    
    async def _handle_analyze_excel(self, args: Dict[str, Any]) -> str:
        """Handler específico para Excel"""
        try:
            file_path = args.get("file_path", "")
            
            result = await self.real_tools["document_analyzer"]._analyze_excel(file_path)
            
            if result["success"]:
                sheets_info = []
                for sheet_name, sheet_data in result["sheet_data"].items():
                    sheets_info.append(f"• {sheet_name}: {sheet_data['rows']} filas, {sheet_data['columns']} columnas")
                
                return f"📊 Análisis Excel completado:\n" \
                       f"• Hojas: {result['total_sheets']}\n" \
                       f"• Detalles:\n" + "\n".join(sheets_info)
            else:
                return f"❌ Error analizando Excel: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error analizando Excel: {e}")
            return f"❌ Error analizando Excel: {str(e)}"
    
    async def _handle_create_chart(self, args: Dict[str, Any]) -> str:
        """Handler para crear gráficos"""
        try:
            data = args.get("data", {})
            chart_type = args.get("chart_type", "bar")
            title = args.get("title", "Gráfico")
            
            result = await self.real_tools["data_visualizer"].create_chart(data, chart_type)
            
            if result["success"]:
                return f"📊 Gráfico creado exitosamente:\n" \
                       f"• Tipo: {chart_type}\n" \
                       f"• Título: {title}\n" \
                       f"• Archivo: {result['file_path']}\n" \
                       f"• ID: {result['chart_id']}"
            else:
                return f"❌ Error creando gráfico: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error creando gráfico: {e}")
            return f"❌ Error creando gráfico: {str(e)}"
    
    async def _handle_statistical_analysis(self, args: Dict[str, Any]) -> str:
        """Handler para análisis estadístico"""
        try:
            data = args.get("data", [])
            analysis_type = args.get("analysis_type", "descriptive")
            
            if not data:
                return "❌ No se proporcionaron datos para análisis"
            
            # Análisis descriptivo básico
            import numpy as np
            
            data_array = np.array(data)
            stats = {
                "count": len(data_array),
                "mean": float(np.mean(data_array)),
                "std": float(np.std(data_array)),
                "min": float(np.min(data_array)),
                "max": float(np.max(data_array)),
                "median": float(np.median(data_array))
            }
            
            return f"📈 Análisis estadístico ({analysis_type}):\n" \
                   f"• Cantidad: {stats['count']}\n" \
                   f"• Media: {stats['mean']:.2f}\n" \
                   f"• Desv. Est.: {stats['std']:.2f}\n" \
                   f"• Mínimo: {stats['min']:.2f}\n" \
                   f"• Máximo: {stats['max']:.2f}\n" \
                   f"• Mediana: {stats['median']:.2f}"
                
        except Exception as e:
            logger.error(f"Error en análisis estadístico: {e}")
            return f"❌ Error en análisis estadístico: {str(e)}"
    
    async def _handle_read_file(self, args: Dict[str, Any]) -> str:
        """Handler para leer archivo"""
        try:
            file_path = args.get("file_path", "")
            
            result = await self.real_tools["file_operations"].read_file(file_path)
            
            if result["success"]:
                return f"📖 Archivo leído exitosamente:\n" \
                       f"• Tamaño: {result['size']} caracteres\n" \
                       f"• Contenido: {result['content'][:300]}..."
            else:
                return f"❌ Error leyendo archivo: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error leyendo archivo: {e}")
            return f"❌ Error leyendo archivo: {str(e)}"
    
    async def _handle_write_file(self, args: Dict[str, Any]) -> str:
        """Handler para escribir archivo"""
        try:
            file_path = args.get("file_path", "")
            content = args.get("content", "")
            
            result = await self.real_tools["file_operations"].write_file(file_path, content)
            
            if result["success"]:
                return f"✍️ Archivo escrito exitosamente:\n" \
                       f"• Ruta: {file_path}\n" \
                       f"• Bytes escritos: {result['bytes_written']}"
            else:
                return f"❌ Error escribiendo archivo: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error escribiendo archivo: {e}")
            return f"❌ Error escribiendo archivo: {str(e)}"
    
    async def _handle_list_directory(self, args: Dict[str, Any]) -> str:
        """Handler para listar directorio"""
        try:
            dir_path = args.get("dir_path", "")
            
            result = await self.real_tools["file_operations"].list_directory(dir_path)
            
            if result["success"]:
                items_info = []
                for item in result["items"][:10]:  # Mostrar solo primeros 10
                    item_type = "📁" if item["type"] == "directory" else "📄"
                    size_info = f" ({item['size']} bytes)" if item["size"] else ""
                    items_info.append(f"{item_type} {item['name']}{size_info}")
                
                return f"📂 Directorio listado: {dir_path}\n" \
                       f"• Total items: {result['total_items']}\n" \
                       f"• Contenido:\n" + "\n".join(items_info)
            else:
                return f"❌ Error listando directorio: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error listando directorio: {e}")
            return f"❌ Error listando directorio: {str(e)}"
    
    async def get_available_real_tools(self) -> List[Dict[str, Any]]:
        """Obtiene lista de herramientas reales disponibles vía MCP"""
        try:
            tools = await mcp_server.list_tools()
            real_tools = [tool for tool in tools if tool.name.startswith("real_")]
            
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                    "category": self._get_tool_category(tool.name)
                }
                for tool in real_tools
            ]
        except Exception as e:
            logger.error(f"Error obteniendo herramientas reales: {e}")
            return []
    
    def _get_tool_category(self, tool_name: str) -> str:
        """Determina la categoría de una herramienta"""
        if "web" in tool_name:
            return "web_search"
        elif "document" in tool_name or "pdf" in tool_name or "excel" in tool_name:
            return "document_analysis"
        elif "chart" in tool_name or "statistical" in tool_name:
            return "data_visualization"
        elif "file" in tool_name or "read" in tool_name or "write" in tool_name or "list" in tool_name:
            return "file_operations"
        else:
            return "general"

# Instancia global del bridge de herramientas reales
mcp_real_tools_bridge = MCPRealToolsBridge() 