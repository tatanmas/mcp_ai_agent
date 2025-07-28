"""
Cognitive Multi-Agent Coordinator - AgentOS
Coordinador que gestiona agentes cognitivos especializados
Integración de MemoryOS + MIRIX + SciBORG + Test-Time Learning + MCP
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .specialized_agents import create_specialized_agent, CognitiveAgent
from .cognitive_mcp_bridge import cognitive_mcp_bridge

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Roles de agentes según papers AaaS-AN y MARCO"""
    COORDINATOR = "coordinator"      # Orquesta tareas y delega
    SPECIALIST = "specialist"        # Dominio específico
    VALIDATOR = "validator"          # Valida resultados
    EXECUTOR = "executor"            # Ejecuta acciones
    SYNTHESIZER = "synthesizer"      # Combina resultados

class TaskComplexity(Enum):
    """Niveles de complejidad según G-Memory"""
    SIMPLE = "simple"           # Un agente puede resolverlo
    MODERATE = "moderate"       # 2-3 agentes colaborando
    COMPLEX = "complex"         # 3+ agentes con dependencias
    EXPERT = "expert"           # Requiere especialización profunda

@dataclass
class AgentMessage:
    """Mensaje entre agentes (AutoGen pattern)"""
    id: str
    sender_id: str
    receiver_id: str
    content: str
    message_type: str  # request, response, delegation, validation
    context: Dict[str, Any]
    timestamp: datetime
    task_id: str

@dataclass 
class SubTask:
    """Subtarea en descomposición (MARCO pattern)"""
    id: str
    description: str
    assigned_agent: str
    dependencies: List[str]
    status: str  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    priority: int = 5
    estimated_duration: int = 60  # segundos

@dataclass
class CoordinationContext:
    """Contexto de coordinación (G-Memory hierarchy)"""
    task_id: str
    main_task: str
    complexity: TaskComplexity
    participating_agents: List[str]
    conversation_history: List[AgentMessage]
    shared_memory: Dict[str, Any]
    workflow_state: Dict[str, Any]

class CognitiveCoordinator:
    """
    Coordinador de Agentes Cognitivos Especializados
    Gestiona agentes con cerebros diferenciados y razonamiento especializado
    """
    
    def __init__(self):
        # Crear agentes cognitivos especializados
        self.cognitive_agents: Dict[str, CognitiveAgent] = {
            "researcher": create_specialized_agent("researcher"),
            "coder": create_specialized_agent("coder"),
            "coordinator": create_specialized_agent("coordinator")
        }
        
        self.active_tasks: Dict[str, CoordinationContext] = {}
        
        logger.info("🧠 CognitiveCoordinator inicializado con 3 agentes cognitivos especializados")
    
    async def coordinate_with_cognitive_agents(self, task: str, user_context: Dict = None) -> Dict[str, Any]:
        """
        Coordinación usando agentes cognitivos especializados
        Cada agente aplica su razonamiento especializado
        """
        try:
            task_id = str(uuid.uuid4())
            
            # 1. Análisis cognitivo de complejidad
            complexity = await self._cognitive_complexity_analysis(task)
            
            # 2. Selección de agentes cognitivos
            selected_agents = await self._select_cognitive_agents(task, complexity)
            
            # 3. Ejecución con razonamiento especializado
            cognitive_results = await self._execute_cognitive_reasoning(
                task_id, task, selected_agents, user_context or {}
            )
            
            # 4. Síntesis cognitiva avanzada
            final_synthesis = await self._cognitive_synthesis(task_id, task, cognitive_results)
            
            # 5. Aprendizaje colectivo (Test-Time Learning)
            await self._collective_learning_update(task, cognitive_results, final_synthesis)
            
            return {
                "task_id": task_id,
                "original_task": task,
                "complexity": complexity.value,
                "cognitive_agents_used": list(selected_agents.keys()),
                "cognitive_reasoning_applied": True,
                "specialized_insights": cognitive_results,
                "final_synthesis": final_synthesis,
                "learning_updated": True,
                "coordination_success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error en coordinación cognitiva: {e}")
            return {
                "task_id": task_id if 'task_id' in locals() else "unknown",
                "error": str(e),
                "coordination_success": False,
                "cognitive_agents_available": list(self.cognitive_agents.keys())
            }
    
    async def _cognitive_complexity_analysis(self, task: str) -> TaskComplexity:
        """Análisis de complejidad usando razonamiento cognitivo"""
        try:
            # Usar agente coordinator para análisis de complejidad especializado
            coordinator_agent = self.cognitive_agents["coordinator"]
            
            analysis_result = await coordinator_agent.specialized_reasoning(
                task=f"Analyze complexity of: {task}",
                context={"analysis_type": "complexity_assessment"}
            )
            
            # Extraer nivel de complejidad del análisis cognitivo
            domain_insights = analysis_result.get("domain_insights", {})
            complexity_level = domain_insights.get("coordination_priorities", ["moderate"])
            
            # Mapear a TaskComplexity
            if any("high" in priority.lower() for priority in complexity_level):
                return TaskComplexity.COMPLEX
            elif any("moderate" in priority.lower() for priority in complexity_level):
                return TaskComplexity.MODERATE
            else:
                return TaskComplexity.SIMPLE
                
        except Exception as e:
            logger.warning(f"Error en análisis cognitivo de complejidad: {e}")
            return TaskComplexity.MODERATE
    
    async def _select_cognitive_agents(self, task: str, complexity: TaskComplexity) -> Dict[str, CognitiveAgent]:
        """Selección inteligente de agentes cognitivos según especialización"""
        selected_agents = {}
        task_lower = task.lower()
        
        # Selección basada en especialización cognitiva
        if any(word in task_lower for word in ["research", "analyze", "study", "investigate", "trends"]):
            selected_agents["researcher"] = self.cognitive_agents["researcher"]
        
        if any(word in task_lower for word in ["implement", "code", "develop", "program", "build", "create"]):
            selected_agents["coder"] = self.cognitive_agents["coder"]
        
        # Coordinator para síntesis si múltiples agentes o tarea compleja
        if len(selected_agents) > 1 or complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            selected_agents["coordinator"] = self.cognitive_agents["coordinator"]
        
        # Si no se seleccionó ningún agente específico, usar coordinator
        if not selected_agents:
            selected_agents["coordinator"] = self.cognitive_agents["coordinator"]
        
        logger.info(f"🎯 Agentes cognitivos seleccionados: {list(selected_agents.keys())}")
        return selected_agents
    
    async def _execute_cognitive_reasoning(self, task_id: str, task: str, 
                                         selected_agents: Dict[str, CognitiveAgent], 
                                         context: Dict) -> Dict[str, Any]:
        """Ejecutar razonamiento especializado en paralelo con herramientas MCP"""
        try:
            reasoning_tasks = []
            
            # Preparar contexto enriquecido para cada agente
            for agent_id, agent in selected_agents.items():
                agent_context = {
                    **context,
                    "task_id": task_id,
                    "agent_specialization": agent.specialization,
                    "other_agents": [aid for aid in selected_agents.keys() if aid != agent_id],
                    "coordination_mode": "cognitive_collaboration",
                    "mcp_tools_available": True  # Indicar que hay herramientas MCP disponibles
                }
                
                reasoning_task = agent.specialized_reasoning(task, agent_context)
                reasoning_tasks.append((agent_id, reasoning_task))
            
            # Ejecutar razonamiento especializado en paralelo
            results = {}
            for agent_id, reasoning_task in reasoning_tasks:
                try:
                    result = await reasoning_task
                    results[agent_id] = result
                    logger.info(f"✅ Razonamiento cognitivo completado - {agent_id}")
                except Exception as e:
                    logger.error(f"❌ Error en razonamiento cognitivo {agent_id}: {e}")
                    results[agent_id] = {
                        "success": False,
                        "error": str(e),
                        "agent_id": agent_id
                    }
            
            # Ejecutar herramientas MCP si es necesario
            mcp_results = await self._execute_mcp_tools_for_task(task, list(selected_agents.keys()))
            if mcp_results.get("success", False):
                # Integrar resultados MCP en el contexto de cada agente
                for agent_id in results:
                    if results[agent_id].get("success", True):
                        results[agent_id]["mcp_tool_results"] = mcp_results.get("results", {}).get(agent_id, [])
                        results[agent_id]["enhanced_with_mcp"] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error en ejecución cognitiva: {e}")
            return {}
    
    async def _execute_mcp_tools_for_task(self, task: str, agent_ids: List[str]) -> Dict[str, Any]:
        """Ejecutar herramientas MCP para la tarea"""
        try:
            # Usar el bridge MCP para ejecutar herramientas coordinadas
            mcp_results = await cognitive_mcp_bridge.execute_coordinated_tools(task, agent_ids)
            
            if mcp_results.get("success", False):
                logger.info(f"🔧 Herramientas MCP ejecutadas: {mcp_results.get('tools_executed', 0)} herramientas")
            else:
                logger.warning(f"⚠️ No se ejecutaron herramientas MCP: {mcp_results.get('error', 'Unknown error')}")
            
            return mcp_results
            
        except Exception as e:
            logger.error(f"Error ejecutando herramientas MCP: {e}")
            return {"success": False, "error": str(e)}
    
    async def _cognitive_synthesis(self, task_id: str, task: str, cognitive_results: Dict[str, Any]) -> Dict[str, Any]:
        """Síntesis cognitiva avanzada de resultados especializados"""
        try:
            # Si hay agente coordinator, usar su capacidad de síntesis
            if "coordinator" in cognitive_results:
                coordinator_result = cognitive_results["coordinator"]
                base_synthesis = coordinator_result.get("domain_insights", {})
            else:
                base_synthesis = {}
            
            # Extraer insights especializados de cada agente
            specialized_insights = {}
            confidence_scores = []
            
            for agent_id, result in cognitive_results.items():
                if result.get("success", True):  # Default True for backward compatibility
                    agent_insights = result.get("domain_insights", {})
                    confidence = result.get("confidence", 0.7)
                    
                    specialized_insights[agent_id] = {
                        "specialization": result.get("specialization", agent_id),
                        "insights": agent_insights,
                        "confidence": confidence,
                        "reasoning_mode": result.get("reasoning_mode", "analytical")
                    }
                    confidence_scores.append(confidence)
            
            # Calcular síntesis general
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            synthesis = {
                "task": task,
                "cognitive_synthesis_type": "multi_agent_specialized_reasoning",
                "agents_contributed": list(specialized_insights.keys()),
                "specialized_insights": specialized_insights,
                "overall_confidence": overall_confidence,
                "synthesis_quality": "high" if overall_confidence > 0.8 else "moderate",
                "cognitive_patterns_identified": self._identify_cognitive_patterns(cognitive_results),
                "recommendations": self._generate_synthesis_recommendations(specialized_insights),
                "next_steps": self._suggest_next_steps(task, specialized_insights),
                "learning_opportunities": self._identify_learning_opportunities(cognitive_results)
            }
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error en síntesis cognitiva: {e}")
            return {
                "error": str(e),
                "partial_results": cognitive_results,
                "synthesis_status": "failed"
            }
    
    def _identify_cognitive_patterns(self, cognitive_results: Dict) -> List[str]:
        """Identificar patrones cognitivos en los resultados"""
        patterns = []
        
        # Analizar patrones de razonamiento
        reasoning_modes = [result.get("reasoning_mode") for result in cognitive_results.values()]
        unique_modes = set(filter(None, reasoning_modes))
        
        if len(unique_modes) > 1:
            patterns.append("multi_modal_reasoning")
        
        # Analizar niveles de confianza
        confidences = [result.get("confidence", 0) for result in cognitive_results.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        if avg_confidence > 0.9:
            patterns.append("high_confidence_consensus")
        elif avg_confidence < 0.6:
            patterns.append("uncertainty_requiring_exploration")
        
        # Analizar especialización
        specializations = [result.get("specialization") for result in cognitive_results.values()]
        if len(set(filter(None, specializations))) > 1:
            patterns.append("cross_domain_collaboration")
        
        return patterns
    
    def _generate_synthesis_recommendations(self, specialized_insights: Dict) -> List[str]:
        """Generar recomendaciones basadas en insights especializados"""
        recommendations = []
        
        # Recomendaciones por tipo de agente
        for agent_id, insights in specialized_insights.items():
            agent_insights = insights.get("insights", {})
            
            if agent_id == "researcher" and "research_strategy" in agent_insights:
                recommendations.append(f"Research: {agent_insights['research_strategy']}")
            
            elif agent_id == "coder" and "implementation_strategy" in agent_insights:
                recommendations.append(f"Development: {agent_insights['implementation_strategy']}")
            
            elif agent_id == "coordinator" and "orchestration_plan" in agent_insights:
                recommendations.append(f"Coordination: {agent_insights['orchestration_plan']}")
        
        return recommendations
    
    def _suggest_next_steps(self, task: str, specialized_insights: Dict) -> List[str]:
        """Sugerir próximos pasos basados en análisis cognitivo"""
        next_steps = []
        
        # Basado en agentes involucrados
        agents_involved = list(specialized_insights.keys())
        
        if "researcher" in agents_involved:
            next_steps.append("Conduct detailed research and validation")
        
        if "coder" in agents_involved:
            next_steps.append("Proceed with technical implementation")
        
        if "coordinator" in agents_involved:
            next_steps.append("Synthesize results and plan next phase")
        
        if len(agents_involved) > 1:
            next_steps.append("Coordinate cross-functional collaboration")
        
        return next_steps
    
    def _identify_learning_opportunities(self, cognitive_results: Dict) -> List[str]:
        """Identificar oportunidades de aprendizaje para los agentes"""
        opportunities = []
        
        for agent_id, result in cognitive_results.items():
            confidence = result.get("confidence", 0.7)
            
            if confidence < 0.6:
                opportunities.append(f"{agent_id}: Improve domain knowledge and reasoning patterns")
            elif confidence > 0.9:
                opportunities.append(f"{agent_id}: Share successful patterns with other agents")
        
        return opportunities
    
    async def _collective_learning_update(self, task: str, cognitive_results: Dict, synthesis: Dict):
        """Actualizar aprendizaje colectivo de todos los agentes (Test-Time Learning)"""
        try:
            # Compartir insights entre agentes para aprendizaje cruzado
            for agent_id, agent in self.cognitive_agents.items():
                if agent_id in cognitive_results:
                    # El agente aprende de su propia experiencia (ya implementado en specialized_reasoning)
                    continue
                else:
                    # Aprendizaje cruzado: agentes aprenden de las experiencias de otros
                    await self._cross_agent_learning(agent, task, cognitive_results, synthesis)
            
            logger.info("🧠 Aprendizaje colectivo actualizado para todos los agentes cognitivos")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje colectivo: {e}")
    
    async def _cross_agent_learning(self, agent: CognitiveAgent, task: str, 
                                  cognitive_results: Dict, synthesis: Dict):
        """Aprendizaje cruzado entre agentes cognitivos"""
        try:
            # Extraer insights relevantes de otros agentes
            cross_learning_insights = []
            
            for other_agent_id, result in cognitive_results.items():
                if other_agent_id != agent.agent_id and result.get("success", True):
                    insights = result.get("domain_insights", {})
                    cross_learning_insights.append({
                        "source_agent": other_agent_id,
                        "insights": insights,
                        "confidence": result.get("confidence", 0.7)
                    })
            
            # Almacenar en memoria como aprendizaje cruzado
            if cross_learning_insights:
                cross_learning_memory = {
                    "task_context": task,
                    "learning_type": "cross_agent_collaboration",
                    "insights_from_peers": cross_learning_insights,
                    "synthesis_quality": synthesis.get("synthesis_quality", "moderate"),
                    "learned_at": datetime.utcnow().isoformat()
                }
                
                # Actualizar memoria del agente con aprendizaje cruzado
                agent.learning_system["experiences"].append(cross_learning_memory)
                
        except Exception as e:
            logger.error(f"Error en aprendizaje cruzado para {agent.agent_id}: {e}")
    
    def get_cognitive_agents_status(self) -> Dict[str, Any]:
        """Status de todos los agentes cognitivos"""
        status = {}
        
        for agent_id, agent in self.cognitive_agents.items():
            status[agent_id] = agent.get_cognitive_status()
        
        # Obtener estado del bridge MCP
        mcp_bridge_status = cognitive_mcp_bridge.get_bridge_status()
        
        return {
            "cognitive_agents": status,
            "total_agents": len(self.cognitive_agents),
            "active_tasks": len(self.active_tasks),
            "cognitive_coordination": "enabled",
            "specialized_reasoning": "operational",
            "collective_learning": "active",
            "mcp_integration": {
                "status": "active",
                "available_tools": mcp_bridge_status.get("available_tools", 0),
                "tool_categories": mcp_bridge_status.get("tool_categories", {}),
                "agent_tool_usage": mcp_bridge_status.get("agent_tool_usage", {})
            }
        }

# Instancia global del coordinador cognitivo
cognitive_coordinator = CognitiveCoordinator() 