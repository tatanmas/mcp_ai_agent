"""
Adaptive Graph Pruning (AGP) - AgentOS
Optimización dinámica de topologías de comunicación multi-agente
Basado en research paper: AGP para mejora de eficiencia y rendimiento
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import networkx as nx
from datetime import datetime

from ..agents.cognitive_agent import CognitiveAgent
from ..agents.cognitive_coordinator import TaskComplexity

logger = logging.getLogger(__name__)

class TopologyType(Enum):
    """Tipos de topología de comunicación"""
    FULLY_CONNECTED = "fully_connected"
    HIERARCHICAL = "hierarchical"
    STAR = "star"
    CHAIN = "chain"
    CUSTOM_OPTIMIZED = "custom_optimized"

class PruningStrategy(Enum):
    """Estrategias de poda según AGP"""
    HARD_PRUNING = "hard_pruning"      # Reduce número de agentes
    SOFT_PRUNING = "soft_pruning"      # Optimiza conexiones
    HYBRID_PRUNING = "hybrid_pruning"  # Combinación de ambas

@dataclass
class AgentTopology:
    """Topología optimizada de agentes"""
    agent_ids: List[str]
    communication_matrix: np.ndarray
    topology_type: TopologyType
    efficiency_score: float
    token_cost_reduction: float
    pruning_applied: PruningStrategy
    optimization_metadata: Dict[str, Any]

@dataclass
class CommunicationEdge:
    """Arista de comunicación entre agentes"""
    source_agent: str
    target_agent: str
    weight: float
    communication_type: str
    necessity_score: float

class AdaptiveGraphPruning:
    """
    Sistema de Optimización de Topología Multi-Agente
    Implementa AGP para construcción dinámica de topologías optimizadas
    """
    
    def __init__(self):
        self.topology_history: List[AgentTopology] = []
        self.efficiency_metrics: Dict[str, List[float]] = {}
        self.pruning_patterns: Dict[str, Any] = {}
        
        # Parámetros de optimización AGP
        self.efficiency_threshold = 0.8
        self.token_reduction_target = 0.7  # 70% reducción target (paper reports 90%+)
        self.max_agents_per_task = 5
        
        logger.info("🌐 AdaptiveGraphPruning inicializado")
    
    async def optimize_agent_topology(self, 
                                    task: str,
                                    task_complexity: TaskComplexity,
                                    available_agents: Dict[str, CognitiveAgent],
                                    previous_performance: Optional[Dict] = None) -> AgentTopology:
        """
        Optimización principal de topología AGP
        Implementa hard-pruning y soft-pruning para máxima eficiencia
        """
        try:
            # 1. Análisis de requerimientos de tarea
            task_requirements = await self._analyze_task_requirements(task, task_complexity)
            
            # 2. Hard Pruning: Selección óptima de agentes
            optimal_agents = await self._hard_pruning_agent_selection(
                task_requirements, available_agents, previous_performance
            )
            
            # 3. Soft Pruning: Optimización de conexiones
            optimized_topology = await self._soft_pruning_topology_optimization(
                optimal_agents, task_requirements
            )
            
            # 4. Validación de eficiencia
            efficiency_metrics = await self._calculate_efficiency_metrics(optimized_topology)
            
            # 5. Almacenar para aprendizaje futuro
            await self._store_topology_performance(optimized_topology, task, efficiency_metrics)
            
            logger.info(f"🌐 Topología AGP optimizada: {len(optimal_agents)} agentes, "
                       f"eficiencia: {efficiency_metrics['efficiency_score']:.2f}")
            
            return optimized_topology
            
        except Exception as e:
            logger.error(f"❌ Error en optimización AGP: {e}")
            # Fallback a topología básica
            return await self._create_fallback_topology(list(available_agents.keys())[:3])
    
    async def _analyze_task_requirements(self, task: str, complexity: TaskComplexity) -> Dict[str, Any]:
        """Análisis de requerimientos de tarea para optimización"""
        
        # Detectar dominios requeridos
        required_domains = []
        task_lower = task.lower()
        
        domain_keywords = {
            "research": ["research", "analyze", "study", "investigate", "trends", "data"],
            "coding": ["implement", "code", "develop", "program", "build", "architecture"],
            "coordination": ["coordinate", "manage", "synthesize", "combine", "organize"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                required_domains.append(domain)
        
        # Estimar intensidad de comunicación
        communication_intensity = self._estimate_communication_intensity(task, complexity)
        
        # Calcular factores de optimización
        optimization_factors = {
            "required_domains": required_domains,
            "communication_intensity": communication_intensity,
            "complexity_level": complexity.value,
            "parallel_potential": len(required_domains) > 1,
            "coordination_overhead": communication_intensity * len(required_domains)
        }
        
        return optimization_factors
    
    def _estimate_communication_intensity(self, task: str, complexity: TaskComplexity) -> float:
        """Estimar intensidad de comunicación requerida"""
        
        # Keywords que indican alta comunicación
        high_comm_keywords = [
            "coordinate", "integrate", "combine", "synthesize", "collaborate",
            "multiple", "various", "different", "phases", "steps"
        ]
        
        comm_indicators = sum(1 for keyword in high_comm_keywords if keyword in task.lower())
        
        # Base intensity por complejidad
        complexity_base = {
            TaskComplexity.SIMPLE: 0.2,
            TaskComplexity.MODERATE: 0.5,
            TaskComplexity.COMPLEX: 0.8,
            TaskComplexity.EXPERT: 1.0
        }
        
        base_intensity = complexity_base.get(complexity, 0.5)
        keyword_boost = min(comm_indicators * 0.15, 0.4)
        
        return min(base_intensity + keyword_boost, 1.0)
    
    async def _hard_pruning_agent_selection(self, 
                                          task_requirements: Dict[str, Any],
                                          available_agents: Dict[str, CognitiveAgent],
                                          previous_performance: Optional[Dict] = None) -> Dict[str, CognitiveAgent]:
        """Hard Pruning: Selección óptima de agentes (reduce número)"""
        
        required_domains = task_requirements["required_domains"]
        complexity_level = task_requirements["complexity_level"]
        
        # Mapeo dominio -> agente
        domain_agent_map = {
            "research": "researcher",
            "coding": "coder", 
            "coordination": "coordinator"
        }
        
        # Selección inicial basada en dominios
        selected_agents = {}
        for domain in required_domains:
            agent_id = domain_agent_map.get(domain)
            if agent_id and agent_id in available_agents:
                selected_agents[agent_id] = available_agents[agent_id]
        
        # Agregar coordinator si múltiples agentes
        if len(selected_agents) > 1 and "coordinator" not in selected_agents:
            if "coordinator" in available_agents:
                selected_agents["coordinator"] = available_agents["coordinator"]
        
        # Si no hay agentes específicos, usar coordinator por defecto
        if not selected_agents and "coordinator" in available_agents:
            selected_agents["coordinator"] = available_agents["coordinator"]
        
        # Aplicar límite máximo de agentes
        if len(selected_agents) > self.max_agents_per_task:
            # Priorizar por performance previa si disponible
            if previous_performance:
                agent_scores = {
                    aid: previous_performance.get(aid, {}).get("efficiency", 0.5)
                    for aid in selected_agents.keys()
                }
                sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
                selected_agents = {
                    aid: selected_agents[aid] 
                    for aid, _ in sorted_agents[:self.max_agents_per_task]
                }
            else:
                # Mantener los primeros agentes
                agent_ids = list(selected_agents.keys())[:self.max_agents_per_task]
                selected_agents = {aid: selected_agents[aid] for aid in agent_ids}
        
        logger.info(f"🎯 Hard Pruning: {len(available_agents)} → {len(selected_agents)} agentes")
        return selected_agents
    
    async def _soft_pruning_topology_optimization(self, 
                                                selected_agents: Dict[str, CognitiveAgent],
                                                task_requirements: Dict[str, Any]) -> AgentTopology:
        """Soft Pruning: Optimización de conexiones (optimiza comunicación)"""
        
        agent_ids = list(selected_agents.keys())
        n_agents = len(agent_ids)
        
        if n_agents == 1:
            # Un solo agente: sin comunicación
            comm_matrix = np.zeros((1, 1))
            topology_type = TopologyType.STAR
        elif n_agents == 2:
            # Dos agentes: comunicación directa
            comm_matrix = np.array([[0, 1], [1, 0]])
            topology_type = TopologyType.CHAIN
        else:
            # Múltiples agentes: optimizar según intensidad de comunicación
            comm_intensity = task_requirements["communication_intensity"]
            
            if comm_intensity > 0.7:
                # Alta comunicación: topología más conectada
                comm_matrix = await self._create_optimized_topology(agent_ids, "high_comm")
                topology_type = TopologyType.FULLY_CONNECTED
            elif comm_intensity > 0.4:
                # Comunicación media: topología jerárquica
                comm_matrix = await self._create_optimized_topology(agent_ids, "medium_comm")
                topology_type = TopologyType.HIERARCHICAL
            else:
                # Baja comunicación: topología estrella (via coordinator)
                comm_matrix = await self._create_optimized_topology(agent_ids, "low_comm")
                topology_type = TopologyType.STAR
        
        # Calcular métricas de eficiencia
        efficiency_score = await self._calculate_topology_efficiency(comm_matrix, task_requirements)
        token_reduction = await self._estimate_token_reduction(comm_matrix, n_agents)
        
        # Crear topología optimizada
        optimized_topology = AgentTopology(
            agent_ids=agent_ids,
            communication_matrix=comm_matrix,
            topology_type=topology_type,
            efficiency_score=efficiency_score,
            token_cost_reduction=token_reduction,
            pruning_applied=PruningStrategy.HYBRID_PRUNING,
            optimization_metadata={
                "task_requirements": task_requirements,
                "optimization_timestamp": datetime.utcnow().isoformat(),
                "agp_version": "1.0"
            }
        )
        
        logger.info(f"🌐 Soft Pruning: Topología {topology_type.value}, "
                   f"eficiencia {efficiency_score:.2f}, reducción tokens {token_reduction:.1%}")
        
        return optimized_topology
    
    async def _create_optimized_topology(self, agent_ids: List[str], communication_mode: str) -> np.ndarray:
        """Crear matriz de comunicación optimizada"""
        
        n = len(agent_ids)
        matrix = np.zeros((n, n))
        
        # Encontrar índice del coordinator si existe
        coord_idx = None
        for i, agent_id in enumerate(agent_ids):
            if agent_id == "coordinator":
                coord_idx = i
                break
        
        if communication_mode == "high_comm":
            # Topología completamente conectada (con pesos optimizados)
            for i in range(n):
                for j in range(i + 1, n):
                    matrix[i][j] = matrix[j][i] = 0.8  # Comunicación bidireccional
        
        elif communication_mode == "medium_comm":
            # Topología jerárquica (coordinator como hub principal)
            if coord_idx is not None:
                for i in range(n):
                    if i != coord_idx:
                        matrix[coord_idx][i] = matrix[i][coord_idx] = 0.9
                # Conexiones directas limitadas entre especialistas
                for i in range(n):
                    for j in range(i + 1, n):
                        if i != coord_idx and j != coord_idx:
                            matrix[i][j] = matrix[j][i] = 0.3
            else:
                # Sin coordinator: chain topology
                for i in range(n - 1):
                    matrix[i][i + 1] = matrix[i + 1][i] = 0.8
        
        elif communication_mode == "low_comm":
            # Topología estrella (solo via coordinator)
            if coord_idx is not None:
                for i in range(n):
                    if i != coord_idx:
                        matrix[coord_idx][i] = matrix[i][coord_idx] = 0.7
            else:
                # Sin coordinator: minimal chain
                for i in range(n - 1):
                    matrix[i][i + 1] = matrix[i + 1][i] = 0.5
        
        return matrix
    
    async def _calculate_topology_efficiency(self, comm_matrix: np.ndarray, 
                                           task_requirements: Dict[str, Any]) -> float:
        """Calcular eficiencia de la topología"""
        
        n_agents = comm_matrix.shape[0]
        
        if n_agents == 1:
            return 1.0  # Máxima eficiencia para un agente
        
        # Calcular conectividad
        connectivity = np.sum(comm_matrix > 0) / (n_agents * (n_agents - 1))
        
        # Calcular overhead de comunicación
        total_communication = np.sum(comm_matrix)
        comm_overhead = total_communication / (n_agents * 2)  # Normalizar
        
        # Factores de eficiencia
        required_intensity = task_requirements.get("communication_intensity", 0.5)
        
        # Eficiencia = balance entre conectividad necesaria y overhead
        connectivity_match = 1.0 - abs(connectivity - required_intensity)
        overhead_penalty = max(0, 1.0 - comm_overhead)
        
        efficiency = (connectivity_match * 0.6) + (overhead_penalty * 0.4)
        
        return max(0.1, min(1.0, efficiency))
    
    async def _estimate_token_reduction(self, comm_matrix: np.ndarray, n_agents: int) -> float:
        """Estimar reducción de tokens vs topología completa"""
        
        if n_agents <= 1:
            return 0.0
        
        # Tokens en topología completa (baseline)
        full_topology_tokens = n_agents * (n_agents - 1) * 100  # Estimación
        
        # Tokens en topología actual
        actual_connections = np.sum(comm_matrix > 0)
        actual_tokens = actual_connections * 100  # Estimación
        
        # Calcular reducción
        if full_topology_tokens > 0:
            reduction = (full_topology_tokens - actual_tokens) / full_topology_tokens
            return max(0.0, min(0.95, reduction))  # Cap at 95% reduction
        
        return 0.0
    
    async def _calculate_efficiency_metrics(self, topology: AgentTopology) -> Dict[str, float]:
        """Calcular métricas completas de eficiencia"""
        
        return {
            "efficiency_score": topology.efficiency_score,
            "token_reduction": topology.token_cost_reduction,
            "connectivity_ratio": np.sum(topology.communication_matrix > 0) / max(1, topology.communication_matrix.size),
            "agent_utilization": len(topology.agent_ids) / self.max_agents_per_task,
            "topology_complexity": np.std(topology.communication_matrix)
        }
    
    async def _store_topology_performance(self, topology: AgentTopology, 
                                        task: str, metrics: Dict[str, float]):
        """Almacenar performance para aprendizaje futuro"""
        
        self.topology_history.append(topology)
        
        # Mantener solo las últimas 100 topologías
        if len(self.topology_history) > 100:
            self.topology_history.pop(0)
        
        # Actualizar métricas de eficiencia
        for metric_name, value in metrics.items():
            if metric_name not in self.efficiency_metrics:
                self.efficiency_metrics[metric_name] = []
            self.efficiency_metrics[metric_name].append(value)
            
            # Mantener solo las últimas 50 métricas
            if len(self.efficiency_metrics[metric_name]) > 50:
                self.efficiency_metrics[metric_name].pop(0)
    
    async def _create_fallback_topology(self, agent_ids: List[str]) -> AgentTopology:
        """Crear topología de fallback en caso de error"""
        
        n = len(agent_ids)
        comm_matrix = np.eye(n)  # Solo comunicación consigo mismos
        
        return AgentTopology(
            agent_ids=agent_ids,
            communication_matrix=comm_matrix,
            topology_type=TopologyType.STAR,
            efficiency_score=0.5,
            token_cost_reduction=0.0,
            pruning_applied=PruningStrategy.HARD_PRUNING,
            optimization_metadata={
                "fallback": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de optimización AGP"""
        return {
            "total_optimizations": len(self.topology_history),
            "average_efficiency": np.mean([t.efficiency_score for t in self.topology_history]) if self.topology_history else 0.0,
            "average_token_reduction": np.mean([t.token_cost_reduction for t in self.topology_history]) if self.topology_history else 0.0,
            "pruning_patterns": self.pruning_patterns,
            "efficiency_metrics": {k: np.mean(v) for k, v in self.efficiency_metrics.items() if v}
        }
    
    # ===============================
    # MÉTODO DE COMPATIBILIDAD (NUEVO)
    # ===============================
    
    async def optimize_agent_selection(self, task: str, available_agents: List[str], 
                                     task_complexity: str = "medium") -> List[str]:
        """
        Método de compatibilidad para selección de agentes
        Wrapper que simplifica la optimización AGP para el orquestador
        """
        try:
            # Convertir task_complexity a enum
            complexity_map = {
                "low": TaskComplexity.LOW,
                "medium": TaskComplexity.MEDIUM,
                "high": TaskComplexity.HIGH
            }
            complexity = complexity_map.get(task_complexity, TaskComplexity.MEDIUM)
            
            # Crear diccionario de agentes disponibles (simulado)
            agents_dict = {}
            for agent_id in available_agents:
                # Crear agente simulado para compatibilidad
                agents_dict[agent_id] = type('Agent', (), {
                    'agent_id': agent_id,
                    'capabilities': ['general'],
                    'performance_score': 0.8
                })()
            
            # Ejecutar optimización AGP
            topology = await self.optimize_agent_topology(
                task=task,
                task_complexity=complexity,
                available_agents=agents_dict
            )
            
            # Retornar lista de agentes seleccionados
            selected_agents = topology.agent_ids[:self.max_agents_per_task]
            
            logger.info(f"🎯 AGP seleccionó {len(selected_agents)} agentes: {selected_agents}")
            return selected_agents
            
        except Exception as e:
            logger.error(f"❌ Error en optimize_agent_selection: {e}")
            # Fallback: retornar primer agente disponible
            return available_agents[:1] if available_agents else []

# Instancia global de AGP
adaptive_graph_pruning = AdaptiveGraphPruning() 