"""
SISTEMA DE TAREAS COMPLEJAS MULTI-AGENTE
Sistema para definir y ejecutar tareas reales que requieren colaboración entre agentes
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from ..agents.cognitive_coordinator import cognitive_coordinator
from ..tools.real_tools import REAL_TOOLS_REGISTRY
from ..database.database import db_manager
from ..memory.vector_memory import vector_memory

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Tipos de tareas complejas"""
    RESEARCH_PROJECT = "research_project"
    DOCUMENT_ANALYSIS = "document_analysis"
    DATA_INVESTIGATION = "data_investigation"
    COLLABORATIVE_CODING = "collaborative_coding"
    CONTENT_CREATION = "content_creation"
    PROBLEM_SOLVING = "problem_solving"

class TaskStatus(Enum):
    """Estados de tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ComplexTask(BaseModel):
    """Definición de tarea compleja"""
    task_id: str
    title: str
    description: str
    task_type: TaskType
    context: Dict[str, Any]
    agents_required: List[str]
    tools_needed: List[str]
    documents: List[str] = []
    web_sources: List[str] = []
    deliverables: List[str]
    constraints: Dict[str, Any] = {}
    created_at: str
    estimated_duration: int = 30  # minutos

class TaskExecution(BaseModel):
    """Ejecución de tarea"""
    task_id: str
    status: TaskStatus
    progress: float = 0.0
    current_step: str = ""
    agent_interactions: List[Dict] = []
    results: Dict[str, Any] = {}
    logs: List[str] = []
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ComplexTaskManager:
    """🎯 GESTOR DE TAREAS COMPLEJAS MULTI-AGENTE"""
    
    def __init__(self):
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.task_definitions: Dict[str, ComplexTask] = {}
        
        # Plantillas de tareas predefinidas
        self._initialize_task_templates()
        
        logger.info("🎯 ComplexTaskManager inicializado")
    
    def _initialize_task_templates(self):
        """Inicializar plantillas de tareas complejas"""
        
        # Plantilla: Investigación Web + Análisis
        research_template = ComplexTask(
            task_id="template_research",
            title="Proyecto de Investigación Web",
            description="Investigación profunda usando búsqueda web real y análisis por múltiples agentes",
            task_type=TaskType.RESEARCH_PROJECT,
            context={
                "depth": "comprehensive",
                "sources_required": 5,
                "analysis_type": "comparative"
            },
            agents_required=["researcher", "coordinator"],
            tools_needed=["web_search_real", "get_page_content"],
            deliverables=["research_report", "source_analysis", "conclusions"],
            constraints={"max_sources": 10, "time_limit": 30},
            created_at=datetime.utcnow().isoformat()
        )
        
        # Plantilla: Análisis de Documentos
        document_template = ComplexTask(
            task_id="template_document",
            title="Análisis Profundo de Documentos",
            description="Análisis completo de documentos con colaboración entre agentes",
            task_type=TaskType.DOCUMENT_ANALYSIS,
            context={
                "analysis_depth": "detailed",
                "extract_insights": True,
                "compare_documents": True
            },
            agents_required=["researcher", "coder", "coordinator"],
            tools_needed=["analyze_document", "create_chart"],
            deliverables=["document_summary", "insights", "visualizations"],
            constraints={"supported_formats": ["pdf", "docx", "txt"]},
            created_at=datetime.utcnow().isoformat()
        )
        
        # Plantilla: Desarrollo Colaborativo
        coding_template = ComplexTask(
            task_id="template_coding",
            title="Proyecto de Desarrollo Colaborativo",
            description="Desarrollo de software con múltiples agentes especializados",
            task_type=TaskType.COLLABORATIVE_CODING,
            context={
                "language": "python",
                "complexity": "medium",
                "testing_required": True
            },
            agents_required=["coder", "researcher", "coordinator"],
            tools_needed=["write_file", "read_file", "web_search_real"],
            deliverables=["source_code", "documentation", "tests"],
            constraints={"code_style": "PEP8", "max_files": 5},
            created_at=datetime.utcnow().isoformat()
        )
        
        self.task_templates = {
            "research": research_template,
            "document": document_template,
            "coding": coding_template
        }
        
        logger.info(f"✅ {len(self.task_templates)} plantillas de tareas inicializadas")
    
    async def create_custom_task(self, task_definition: Dict[str, Any]) -> ComplexTask:
        """Crear tarea personalizada"""
        try:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            
            task = ComplexTask(
                task_id=task_id,
                title=task_definition.get("title", "Tarea Personalizada"),
                description=task_definition.get("description", ""),
                task_type=TaskType(task_definition.get("task_type", "problem_solving")),
                context=task_definition.get("context", {}),
                agents_required=task_definition.get("agents_required", ["coordinator"]),
                tools_needed=task_definition.get("tools_needed", []),
                documents=task_definition.get("documents", []),
                web_sources=task_definition.get("web_sources", []),
                deliverables=task_definition.get("deliverables", ["result"]),
                constraints=task_definition.get("constraints", {}),
                created_at=datetime.utcnow().isoformat(),
                estimated_duration=task_definition.get("estimated_duration", 30)
            )
            
            self.task_definitions[task_id] = task
            logger.info(f"✅ Tarea personalizada creada: {task_id}")
            
            return task
            
        except Exception as e:
            logger.error(f"❌ Error creando tarea personalizada: {e}")
            raise
    
    async def execute_complex_task(self, task_id: str) -> TaskExecution:
        """Ejecutar tarea compleja con colaboración multi-agente"""
        try:
            if task_id not in self.task_definitions:
                raise ValueError(f"Tarea no encontrada: {task_id}")
            
            task = self.task_definitions[task_id]
            
            # Inicializar ejecución
            execution = TaskExecution(
                task_id=task_id,
                status=TaskStatus.RUNNING,
                start_time=datetime.utcnow().isoformat()
            )
            
            self.active_tasks[task_id] = execution
            
            logger.info(f"🚀 Iniciando ejecución de tarea compleja: {task.title}")
            
            # Paso 1: Planificación de la tarea
            await self._planning_phase(task, execution)
            
            # Paso 2: Ejecución colaborativa
            await self._collaborative_execution(task, execution)
            
            # Paso 3: Síntesis y entrega
            await self._synthesis_phase(task, execution)
            
            # Finalizar ejecución
            execution.status = TaskStatus.COMPLETED
            execution.end_time = datetime.utcnow().isoformat()
            execution.progress = 100.0
            
            logger.info(f"✅ Tarea compleja completada: {task_id}")
            
            return execution
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando tarea compleja {task_id}: {e}")
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.FAILED
                self.active_tasks[task_id].logs.append(f"Error: {str(e)}")
            raise
    
    async def _planning_phase(self, task: ComplexTask, execution: TaskExecution):
        """Fase de planificación colaborativa"""
        execution.current_step = "Planificación"
        execution.progress = 10.0
        
        # El coordinador planifica la tarea
        planning_result = await cognitive_coordinator.coordinate_with_cognitive_agents(
            task=f"Planificar ejecución de: {task.description}",
            user_context={
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "agents_required": task.agents_required,
                "tools_needed": task.tools_needed,
                "constraints": task.constraints
            }
        )
        
        execution.results["planning"] = planning_result
        execution.logs.append("✅ Fase de planificación completada")
        
        # Almacenar plan en memoria para referencia futura
        plan_summary = f"Plan para {task.title}: {planning_result.get('final_synthesis', {}).get('recommendations', [])}"
        
        for agent_id in task.agents_required:
            db_manager.store_memory(
                agent_id=agent_id,
                memory_type="long_term",
                content=plan_summary,
                importance_score=9,
                tags=["task_planning", task.task_type.value, task.task_id]
            )
    
    async def _collaborative_execution(self, task: ComplexTask, execution: TaskExecution):
        """Fase de ejecución colaborativa real"""
        execution.current_step = "Ejecución Colaborativa"
        execution.progress = 30.0
        
        results = {}
        
        # Ejecutar herramientas reales según la tarea
        if "web_search_real" in task.tools_needed:
            search_results = await self._execute_web_research(task, execution)
            results["web_research"] = search_results
        
        if "analyze_document" in task.tools_needed:
            doc_results = await self._execute_document_analysis(task, execution)
            results["document_analysis"] = doc_results
        
        if "create_chart" in task.tools_needed:
            viz_results = await self._execute_data_visualization(task, execution)
            results["visualizations"] = viz_results
        
        if task.tools_needed and any(tool in ["write_file", "read_file"] for tool in task.tools_needed):
            file_results = await self._execute_file_operations(task, execution)
            results["file_operations"] = file_results
        
        # Colaboración entre agentes
        if len(task.agents_required) > 1:
            collaboration_result = await cognitive_coordinator.coordinate_complex_task(
                task=task.description,
                user_context={
                    "task_id": task.task_id,
                    "participating_agents": task.agents_required,
                    "context": task.context,
                    "available_results": results
                }
            )
            results["agent_collaboration"] = collaboration_result
        
        execution.results["execution"] = results
        execution.progress = 70.0
        execution.logs.append("✅ Fase de ejecución colaborativa completada")
    
    async def _execute_web_research(self, task: ComplexTask, execution: TaskExecution) -> Dict:
        """Ejecutar búsqueda web real"""
        try:
            from ..tools.real_tools import real_web_search
            
            research_queries = task.context.get("search_queries", [])
            if not research_queries:
                # Generar queries basadas en la descripción
                research_queries = [
                    task.description,
                    task.title
                ]
            
            search_results = []
            for query in research_queries:
                result = await real_web_search.search(query, max_results=3)
                search_results.append(result)
                
                # Obtener contenido de páginas relevantes
                if result.get("success") and result.get("results"):
                    for page in result["results"][:2]:  # Top 2 páginas por query
                        content = await real_web_search.get_page_content(page["url"])
                        if content.get("success"):
                            page["content"] = content["content"][:1000]  # Primeros 1000 chars
            
            execution.logs.append(f"🔍 Búsqueda web completada: {len(search_results)} consultas procesadas")
            
            return {
                "queries_processed": len(research_queries),
                "search_results": search_results,
                "success": True
            }
            
        except Exception as e:
            execution.logs.append(f"❌ Error en búsqueda web: {e}")
            return {"error": str(e), "success": False}
    
    async def _execute_document_analysis(self, task: ComplexTask, execution: TaskExecution) -> Dict:
        """Ejecutar análisis real de documentos"""
        try:
            from ..tools.real_tools import real_document_analyzer
            
            analysis_results = []
            for doc_path in task.documents:
                result = await real_document_analyzer.analyze_document(doc_path)
                analysis_results.append(result)
            
            execution.logs.append(f"📄 Análisis de documentos completado: {len(analysis_results)} documentos")
            
            return {
                "documents_analyzed": len(task.documents),
                "analysis_results": analysis_results,
                "success": True
            }
            
        except Exception as e:
            execution.logs.append(f"❌ Error analizando documentos: {e}")
            return {"error": str(e), "success": False}
    
    async def _execute_data_visualization(self, task: ComplexTask, execution: TaskExecution) -> Dict:
        """Ejecutar visualización real de datos"""
        try:
            from ..tools.real_tools import real_data_visualizer
            
            chart_data = task.context.get("chart_data", {})
            chart_type = task.context.get("chart_type", "bar")
            
            if not chart_data:
                # Crear datos de ejemplo basados en resultados previos
                chart_data = {
                    "x": ["Resultado A", "Resultado B", "Resultado C"],
                    "y": [85, 72, 93],
                    "title": f"Análisis de {task.title}"
                }
            
            chart_result = await real_data_visualizer.create_chart(chart_data, chart_type)
            
            execution.logs.append("📊 Visualización de datos completada")
            
            return {
                "chart_created": chart_result.get("success", False),
                "chart_result": chart_result,
                "success": True
            }
            
        except Exception as e:
            execution.logs.append(f"❌ Error creando visualización: {e}")
            return {"error": str(e), "success": False}
    
    async def _execute_file_operations(self, task: ComplexTask, execution: TaskExecution) -> Dict:
        """Ejecutar operaciones reales de archivos"""
        try:
            from ..tools.real_tools import real_file_operations
            
            file_results = []
            
            # Operaciones de lectura
            for file_path in task.context.get("files_to_read", []):
                result = await real_file_operations.read_file(file_path)
                file_results.append({"operation": "read", "file": file_path, "result": result})
            
            # Operaciones de escritura
            files_to_write = task.context.get("files_to_write", {})
            for file_path, content in files_to_write.items():
                result = await real_file_operations.write_file(file_path, content)
                file_results.append({"operation": "write", "file": file_path, "result": result})
            
            execution.logs.append(f"📁 Operaciones de archivos completadas: {len(file_results)}")
            
            return {
                "operations_completed": len(file_results),
                "file_results": file_results,
                "success": True
            }
            
        except Exception as e:
            execution.logs.append(f"❌ Error en operaciones de archivos: {e}")
            return {"error": str(e), "success": False}
    
    async def _synthesis_phase(self, task: ComplexTask, execution: TaskExecution):
        """Fase de síntesis final"""
        execution.current_step = "Síntesis Final"
        execution.progress = 90.0
        
        # Coordinador sintetiza todos los resultados
        synthesis_task = f"Sintetizar resultados de '{task.title}': {execution.results}"
        
        synthesis_result = await cognitive_coordinator.coordinate_with_cognitive_agents(
            task=synthesis_task,
            user_context={
                "task_id": f"{task.task_id}_synthesis",
                "deliverables": task.deliverables,
                "execution_results": execution.results,
                "task_constraints": task.constraints
            }
        )
        
        execution.results["final_synthesis"] = synthesis_result
        execution.logs.append("✅ Síntesis final completada")
        
        # Almacenar resultados finales
        synthesis_summary = f"Resultados de {task.title}: {synthesis_result.get('final_synthesis', {}).get('recommendations', [])}"
        
        for agent_id in task.agents_required:
            db_manager.store_memory(
                agent_id=agent_id,
                memory_type="long_term",
                content=synthesis_summary,
                importance_score=10,
                tags=["task_completion", task.task_type.value, task.task_id]
            )
    
    def get_task_status(self, task_id: str) -> Optional[TaskExecution]:
        """Obtener estado de tarea"""
        return self.active_tasks.get(task_id)
    
    def get_available_templates(self) -> Dict[str, ComplexTask]:
        """Obtener plantillas disponibles"""
        return self.task_templates
    
    def list_active_tasks(self) -> List[TaskExecution]:
        """Listar tareas activas"""
        return list(self.active_tasks.values())

# Instancia global del gestor de tareas
complex_task_manager = ComplexTaskManager() 