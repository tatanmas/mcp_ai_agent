"""
Conflict Resolution System - AgentOS
Sistema de resolución inteligente de conflictos en memoria multi-agente
Basado en MemoryAgentBench CR (Conflict Resolution) competency
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import difflib
import numpy as np

from ..agents.cognitive_agent import CognitiveAgent, MemoryType
from ..memory.vector_memory import vector_memory
from ..database.database import db_manager

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Tipos de conflictos identificados"""
    FACTUAL_CONTRADICTION = "factual_contradiction"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  
    SOURCE_DISCREPANCY = "source_discrepancy"
    CONFIDENCE_MISMATCH = "confidence_mismatch"
    CONTEXTUAL_AMBIGUITY = "contextual_ambiguity"

class ConflictSeverity(Enum):
    """Severidad del conflicto"""
    LOW = "low"           # Diferencias menores
    MEDIUM = "medium"     # Inconsistencias significativas
    HIGH = "high"         # Contradicciones directas
    CRITICAL = "critical" # Conflictos que impiden funcionamiento

class ResolutionStrategy(Enum):
    """Estrategias de resolución"""
    SOURCE_PRIORITY = "source_priority"       # Priorizar por fuente confiable
    TEMPORAL_LATEST = "temporal_latest"       # Usar información más reciente
    CONFIDENCE_WEIGHTED = "confidence_weighted" # Pesar por niveles de confianza
    CONTEXT_SPECIFIC = "context_specific"     # Resolver por contexto específico
    HUMAN_REVIEW = "human_review"            # Requerir revisión humana

@dataclass
class ConflictInstance:
    """Instancia de conflicto detectada"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    affected_agents: List[str]
    conflicting_memories: List[Dict[str, Any]]
    conflict_description: str
    confidence_scores: List[float]
    detection_timestamp: str
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolved: bool = False
    resolution_result: Optional[Dict[str, Any]] = None

@dataclass
class ResolutionResult:
    """Resultado de resolución de conflicto"""
    conflict_id: str
    strategy_used: ResolutionStrategy
    resolved_memory: Dict[str, Any]
    confidence_score: float
    affected_agents_updated: List[str]
    resolution_reasoning: str
    success: bool

class ConflictResolutionSystem:
    """
    Sistema de Resolución de Conflictos Multi-Agente
    Implementa MemoryAgentBench CR competency para robustez cognitiva
    """
    
    def __init__(self):
        self.active_conflicts: Dict[str, ConflictInstance] = {}
        self.resolved_conflicts: List[ConflictInstance] = []
        self.resolution_history: List[ResolutionResult] = []
        
        # Configuración de resolución
        self.confidence_threshold = 0.7
        self.similarity_threshold = 0.85
        self.max_conflicts_per_agent = 10
        
        # Estadísticas
        self.conflicts_detected = 0
        self.conflicts_resolved = 0
        self.resolution_success_rate = 0.0
        
        logger.info("🔧 ConflictResolutionSystem inicializado")
    
    async def detect_memory_conflicts(self, 
                                    agent_id: str,
                                    new_memory: Dict[str, Any],
                                    memory_type: MemoryType) -> List[ConflictInstance]:
        """
        Detectar conflictos entre nueva memoria y memoria existente
        Implementa detection logic según MemoryAgentBench
        """
        try:
            conflicts = []
            
            # 1. Búsqueda semántica de memorias similares
            similar_memories = await self._find_similar_memories(agent_id, new_memory, memory_type)
            
            # 2. Análisis de conflictos por tipo
            for similar_memory in similar_memories:
                conflict_types = await self._analyze_conflict_types(new_memory, similar_memory)
                
                for conflict_type in conflict_types:
                    conflict = await self._create_conflict_instance(
                        agent_id, new_memory, similar_memory, conflict_type
                    )
                    
                    if conflict:
                        conflicts.append(conflict)
                        self.active_conflicts[conflict.conflict_id] = conflict
                        self.conflicts_detected += 1
            
            if conflicts:
                logger.info(f"🔍 Detectados {len(conflicts)} conflictos para agente {agent_id}")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"❌ Error detectando conflictos: {e}")
            return []
    
    async def _find_similar_memories(self, 
                                   agent_id: str,
                                   new_memory: Dict[str, Any],
                                   memory_type: MemoryType) -> List[Dict[str, Any]]:
        """Encontrar memorias similares para comparación"""
        
        # Extraer contenido textual de la nueva memoria
        content = self._extract_memory_content(new_memory)
        if not content:
            return []
        
        # Búsqueda semántica en memoria vectorial
        vector_results = vector_memory.semantic_search(
            agent_id=agent_id,
            query=content,
            limit=10,
            min_score=self.similarity_threshold
        )
        
        # Búsqueda en base de datos persistente
        # Convertir MemoryType a string si es necesario
        if hasattr(memory_type, 'value'):
            memory_type_str = memory_type.value
        else:
            memory_type_str = str(memory_type)
            
        db_memories = await db_manager.recall_memory(
            agent_id=agent_id,
            memory_type=memory_type_str,
            limit=20
        )
        
        # Combinar y filtrar resultados
        all_memories = vector_results + [mem for mem in db_memories if mem not in vector_results]
        
        # Filtrar por similitud textual adicional
        similar_memories = []
        for memory in all_memories:
            memory_content = self._extract_memory_content(memory)
            if memory_content and self._calculate_text_similarity(content, memory_content) > 0.7:
                similar_memories.append(memory)
        
        return similar_memories[:5]  # Top 5 más similares
    
    def _extract_memory_content(self, memory: Dict[str, Any]) -> str:
        """Extraer contenido textual de una memoria"""
        
        # Diferentes formas de extraer contenido según estructura
        content_fields = ["content", "description", "insights", "findings", "result"]
        
        for field in content_fields:
            if field in memory and memory[field]:
                if isinstance(memory[field], str):
                    return memory[field]
                elif isinstance(memory[field], dict):
                    return json.dumps(memory[field])
        
        # Fallback: convertir toda la memoria a string
        return json.dumps(memory)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud textual entre dos textos"""
        
        # Usar difflib para similitud de secuencias
        similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return similarity
    
    async def _analyze_conflict_types(self, 
                                    new_memory: Dict[str, Any],
                                    existing_memory: Dict[str, Any]) -> List[ConflictType]:
        """Analizar tipos de conflictos entre memorias"""
        
        conflicts = []
        
        # 1. Contradicciones factuales
        if await self._detect_factual_contradiction(new_memory, existing_memory):
            conflicts.append(ConflictType.FACTUAL_CONTRADICTION)
        
        # 2. Inconsistencias temporales
        if await self._detect_temporal_inconsistency(new_memory, existing_memory):
            conflicts.append(ConflictType.TEMPORAL_INCONSISTENCY)
        
        # 3. Discrepancias de fuente
        if await self._detect_source_discrepancy(new_memory, existing_memory):
            conflicts.append(ConflictType.SOURCE_DISCREPANCY)
        
        # 4. Desajustes de confianza
        if await self._detect_confidence_mismatch(new_memory, existing_memory):
            conflicts.append(ConflictType.CONFIDENCE_MISMATCH)
        
        # 5. Ambigüedad contextual
        if await self._detect_contextual_ambiguity(new_memory, existing_memory):
            conflicts.append(ConflictType.CONTEXTUAL_AMBIGUITY)
        
        return conflicts
    
    async def _detect_factual_contradiction(self, new_mem: Dict, existing_mem: Dict) -> bool:
        """Detectar contradicciones factuales directas"""
        
        # Keywords que indican negación/contradicción
        contradiction_indicators = [
            ("true", "false"), ("yes", "no"), ("increase", "decrease"),
            ("positive", "negative"), ("success", "failure"), ("correct", "incorrect")
        ]
        
        new_content = self._extract_memory_content(new_mem).lower()
        existing_content = self._extract_memory_content(existing_mem).lower()
        
        for pos_term, neg_term in contradiction_indicators:
            if ((pos_term in new_content and neg_term in existing_content) or
                (neg_term in new_content and pos_term in existing_content)):
                return True
        
        return False
    
    async def _detect_temporal_inconsistency(self, new_mem: Dict, existing_mem: Dict) -> bool:
        """Detectar inconsistencias temporales"""
        
        # Extraer timestamps si están disponibles
        new_timestamp = new_mem.get("timestamp", new_mem.get("created_at"))
        existing_timestamp = existing_mem.get("timestamp", existing_mem.get("created_at"))
        
        if new_timestamp and existing_timestamp:
            try:
                new_time = datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))
                existing_time = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))
                
                # Si la memoria nueva es más antigua pero contradice la existente
                if new_time < existing_time:
                    # Verificar si hay contradicción factual
                    return await self._detect_factual_contradiction(new_mem, existing_mem)
                    
            except Exception:
                pass
        
        return False
    
    async def _detect_source_discrepancy(self, new_mem: Dict, existing_mem: Dict) -> bool:
        """Detectar discrepancias de fuente"""
        
        new_source = new_mem.get("source", new_mem.get("agent_id"))
        existing_source = existing_mem.get("source", existing_mem.get("agent_id"))
        
        # Verificar confiabilidad de fuentes
        if new_source and existing_source and new_source != existing_source:
            new_confidence = new_mem.get("confidence", new_mem.get("importance_score", 0.5))
            existing_confidence = existing_mem.get("confidence", existing_mem.get("importance_score", 0.5))
            
            # Discrepancia si hay diferencia significativa en confianza
            if abs(new_confidence - existing_confidence) > 0.3:
                return True
        
        return False
    
    async def _detect_confidence_mismatch(self, new_mem: Dict, existing_mem: Dict) -> bool:
        """Detectar desajustes en niveles de confianza"""
        
        new_conf = new_mem.get("confidence", new_mem.get("importance_score", 0.5))
        existing_conf = existing_mem.get("confidence", existing_mem.get("importance_score", 0.5))
        
        # Mismatch si contenido similar pero confianza muy diferente
        content_similarity = self._calculate_text_similarity(
            self._extract_memory_content(new_mem),
            self._extract_memory_content(existing_mem)
        )
        
        if content_similarity > 0.8 and abs(new_conf - existing_conf) > 0.4:
            return True
        
        return False
    
    async def _detect_contextual_ambiguity(self, new_mem: Dict, existing_mem: Dict) -> bool:
        """Detectar ambigüedad contextual"""
        
        # Verificar si los contextos son diferentes pero el contenido similar
        new_context = new_mem.get("context", {})
        existing_context = existing_mem.get("context", {})
        
        if new_context and existing_context:
            context_similarity = self._calculate_dict_similarity(new_context, existing_context)
            content_similarity = self._calculate_text_similarity(
                self._extract_memory_content(new_mem),
                self._extract_memory_content(existing_mem)
            )
            
            # Ambigüedad si contenido similar pero contextos diferentes
            if content_similarity > 0.8 and context_similarity < 0.5:
                return True
        
        return False
    
    def _calculate_dict_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """Calcular similitud entre diccionarios"""
        
        if not dict1 or not dict2:
            return 0.0
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        if not all_keys:
            return 1.0
        
        matching_keys = set(dict1.keys()) & set(dict2.keys())
        matching_values = sum(1 for key in matching_keys if dict1[key] == dict2[key])
        
        similarity = (len(matching_keys) + matching_values) / (len(all_keys) * 2)
        return similarity
    
    async def _create_conflict_instance(self,
                                      agent_id: str,
                                      new_memory: Dict[str, Any],
                                      existing_memory: Dict[str, Any],
                                      conflict_type: ConflictType) -> Optional[ConflictInstance]:
        """Crear instancia de conflicto detectado"""
        
        try:
            conflict_id = f"conflict_{agent_id}_{len(self.active_conflicts)}_{datetime.utcnow().strftime('%H%M%S')}"
            
            # Determinar severidad
            severity = await self._assess_conflict_severity(new_memory, existing_memory, conflict_type)
            
            # Extraer scores de confianza
            new_conf = new_memory.get("confidence", new_memory.get("importance_score", 0.5))
            existing_conf = existing_memory.get("confidence", existing_memory.get("importance_score", 0.5))
            
            # Crear descripción del conflicto
            description = await self._generate_conflict_description(
                new_memory, existing_memory, conflict_type
            )
            
            conflict = ConflictInstance(
                conflict_id=conflict_id,
                conflict_type=conflict_type,
                severity=severity,
                affected_agents=[agent_id],
                conflicting_memories=[new_memory, existing_memory],
                conflict_description=description,
                confidence_scores=[new_conf, existing_conf],
                detection_timestamp=datetime.utcnow().isoformat()
            )
            
            return conflict
            
        except Exception as e:
            logger.error(f"❌ Error creando instancia de conflicto: {e}")
            return None
    
    async def _assess_conflict_severity(self,
                                      new_memory: Dict[str, Any],
                                      existing_memory: Dict[str, Any],
                                      conflict_type: ConflictType) -> ConflictSeverity:
        """Evaluar severidad del conflicto"""
        
        # Calcular diferencia en confianza
        new_conf = new_memory.get("confidence", 0.5)
        existing_conf = existing_memory.get("confidence", 0.5)
        conf_diff = abs(new_conf - existing_conf)
        
        # Calcular similitud de contenido
        content_similarity = self._calculate_text_similarity(
            self._extract_memory_content(new_memory),
            self._extract_memory_content(existing_memory)
        )
        
        # Reglas de severidad por tipo de conflicto
        if conflict_type == ConflictType.FACTUAL_CONTRADICTION:
            if content_similarity > 0.9 and conf_diff < 0.2:
                return ConflictSeverity.CRITICAL
            elif content_similarity > 0.7:
                return ConflictSeverity.HIGH
            else:
                return ConflictSeverity.MEDIUM
                
        elif conflict_type == ConflictType.TEMPORAL_INCONSISTENCY:
            return ConflictSeverity.HIGH if conf_diff > 0.3 else ConflictSeverity.MEDIUM
            
        elif conflict_type == ConflictType.CONFIDENCE_MISMATCH:
            return ConflictSeverity.MEDIUM if conf_diff > 0.5 else ConflictSeverity.LOW
            
        else:
            return ConflictSeverity.LOW
    
    async def _generate_conflict_description(self,
                                           new_memory: Dict[str, Any],
                                           existing_memory: Dict[str, Any],
                                           conflict_type: ConflictType) -> str:
        """Generar descripción legible del conflicto"""
        
        new_content = self._extract_memory_content(new_memory)[:100]
        existing_content = self._extract_memory_content(existing_memory)[:100]
        
        descriptions = {
            ConflictType.FACTUAL_CONTRADICTION: f"Contradicción factual: '{new_content}' vs '{existing_content}'",
            ConflictType.TEMPORAL_INCONSISTENCY: f"Inconsistencia temporal entre memorias similares",
            ConflictType.SOURCE_DISCREPANCY: f"Discrepancia entre fuentes de información",
            ConflictType.CONFIDENCE_MISMATCH: f"Desajuste en niveles de confianza para contenido similar",
            ConflictType.CONTEXTUAL_AMBIGUITY: f"Ambigüedad contextual en información similar"
        }
        
        return descriptions.get(conflict_type, "Conflicto detectado entre memorias")
    
    async def resolve_conflict(self, conflict_id: str) -> ResolutionResult:
        """
        Resolver conflicto específico usando estrategia apropiada
        Implementa resolution strategies según MemoryAgentBench
        """
        try:
            if conflict_id not in self.active_conflicts:
                raise ValueError(f"Conflicto {conflict_id} no encontrado")
            
            conflict = self.active_conflicts[conflict_id]
            
            # 1. Seleccionar estrategia de resolución
            strategy = await self._select_resolution_strategy(conflict)
            
            # 2. Aplicar estrategia
            resolution_result = await self._apply_resolution_strategy(conflict, strategy)
            
            # 3. Actualizar memoria de agentes afectados
            if resolution_result.success:
                await self._update_agent_memories(conflict, resolution_result)
                
                # Marcar conflicto como resuelto
                conflict.resolved = True
                conflict.resolution_strategy = strategy
                conflict.resolution_result = resolution_result.__dict__
                
                # Mover a resueltos
                self.resolved_conflicts.append(conflict)
                del self.active_conflicts[conflict_id]
                self.conflicts_resolved += 1
            
            # 4. Actualizar estadísticas
            self._update_resolution_stats()
            
            self.resolution_history.append(resolution_result)
            
            logger.info(f"🔧 Conflicto {conflict_id} resuelto usando {strategy.value}")
            
            return resolution_result
            
        except Exception as e:
            logger.error(f"❌ Error resolviendo conflicto {conflict_id}: {e}")
            return ResolutionResult(
                conflict_id=conflict_id,
                strategy_used=ResolutionStrategy.HUMAN_REVIEW,
                resolved_memory={},
                confidence_score=0.0,
                affected_agents_updated=[],
                resolution_reasoning=f"Error en resolución: {str(e)}",
                success=False
            )
    
    async def _select_resolution_strategy(self, conflict: ConflictInstance) -> ResolutionStrategy:
        """Seleccionar estrategia óptima de resolución"""
        
        # Estrategias por tipo de conflicto y severidad
        if conflict.severity == ConflictSeverity.CRITICAL:
            return ResolutionStrategy.HUMAN_REVIEW
        
        if conflict.conflict_type == ConflictType.FACTUAL_CONTRADICTION:
            return ResolutionStrategy.CONFIDENCE_WEIGHTED
        elif conflict.conflict_type == ConflictType.TEMPORAL_INCONSISTENCY:
            return ResolutionStrategy.TEMPORAL_LATEST
        elif conflict.conflict_type == ConflictType.SOURCE_DISCREPANCY:
            return ResolutionStrategy.SOURCE_PRIORITY
        elif conflict.conflict_type == ConflictType.CONFIDENCE_MISMATCH:
            return ResolutionStrategy.CONFIDENCE_WEIGHTED
        else:
            return ResolutionStrategy.CONTEXT_SPECIFIC
    
    async def _apply_resolution_strategy(self, 
                                       conflict: ConflictInstance,
                                       strategy: ResolutionStrategy) -> ResolutionResult:
        """Aplicar estrategia de resolución específica"""
        
        memories = conflict.conflicting_memories
        confidences = conflict.confidence_scores
        
        if strategy == ResolutionStrategy.CONFIDENCE_WEIGHTED:
            # Resolver basado en pesos de confianza
            resolved_memory, confidence, reasoning = await self._resolve_by_confidence(memories, confidences)
            
        elif strategy == ResolutionStrategy.TEMPORAL_LATEST:
            # Usar la información más reciente
            resolved_memory, confidence, reasoning = await self._resolve_by_temporal(memories)
            
        elif strategy == ResolutionStrategy.SOURCE_PRIORITY:
            # Resolver por prioridad de fuente
            resolved_memory, confidence, reasoning = await self._resolve_by_source(memories)
            
        elif strategy == ResolutionStrategy.CONTEXT_SPECIFIC:
            # Resolver por contexto específico
            resolved_memory, confidence, reasoning = await self._resolve_by_context(memories)
            
        else:
            # Human review required
            return ResolutionResult(
                conflict_id=conflict.conflict_id,
                strategy_used=strategy,
                resolved_memory={},
                confidence_score=0.0,
                affected_agents_updated=[],
                resolution_reasoning="Requiere revisión humana",
                success=False
            )
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            strategy_used=strategy,
            resolved_memory=resolved_memory,
            confidence_score=confidence,
            affected_agents_updated=conflict.affected_agents,
            resolution_reasoning=reasoning,
            success=True
        )
    
    async def _resolve_by_confidence(self, memories: List[Dict], confidences: List[float]) -> Tuple[Dict, float, str]:
        """Resolver usando pesos de confianza"""
        
        # Seleccionar memoria con mayor confianza
        max_conf_idx = np.argmax(confidences)
        resolved_memory = memories[max_conf_idx].copy()
        
        # Calcular nueva confianza ponderada
        total_weight = sum(confidences)
        weighted_confidence = max(confidences) if total_weight == 0 else max(confidences)
        
        reasoning = f"Resuelto por confianza máxima: {weighted_confidence:.2f}"
        
        return resolved_memory, weighted_confidence, reasoning
    
    async def _resolve_by_temporal(self, memories: List[Dict]) -> Tuple[Dict, float, str]:
        """Resolver usando información más reciente"""
        
        # Encontrar memoria más reciente
        latest_memory = memories[0]
        latest_timestamp = memories[0].get("timestamp", "1970-01-01T00:00:00")
        
        for memory in memories[1:]:
            memory_timestamp = memory.get("timestamp", "1970-01-01T00:00:00")
            if memory_timestamp > latest_timestamp:
                latest_memory = memory
                latest_timestamp = memory_timestamp
        
        confidence = latest_memory.get("confidence", 0.7)
        reasoning = f"Resuelto por información más reciente: {latest_timestamp}"
        
        return latest_memory, confidence, reasoning
    
    async def _resolve_by_source(self, memories: List[Dict]) -> Tuple[Dict, float, str]:
        """Resolver por prioridad de fuente"""
        
        # Prioridad de fuentes (esto se puede configurar)
        source_priority = {
            "researcher": 0.9,
            "coder": 0.8,
            "coordinator": 0.7,
            "external_api": 0.6,
            "default": 0.5
        }
        
        best_memory = memories[0]
        best_priority = 0.0
        
        for memory in memories:
            source = memory.get("source", memory.get("agent_id", "default"))
            priority = source_priority.get(source, 0.5)
            
            if priority > best_priority:
                best_memory = memory
                best_priority = priority
        
        confidence = best_memory.get("confidence", best_priority)
        reasoning = f"Resuelto por prioridad de fuente: {best_priority:.2f}"
        
        return best_memory, confidence, reasoning
    
    async def _resolve_by_context(self, memories: List[Dict]) -> Tuple[Dict, float, str]:
        """Resolver por contexto específico"""
        
        # Seleccionar memoria con contexto más rico/específico
        best_memory = memories[0]
        best_context_score = 0.0
        
        for memory in memories:
            context = memory.get("context", {})
            # Score basado en cantidad y especificidad del contexto
            context_score = len(context) * 0.1 + sum(1 for v in context.values() if v) * 0.2
            
            if context_score > best_context_score:
                best_memory = memory
                best_context_score = context_score
        
        confidence = best_memory.get("confidence", 0.6)
        reasoning = f"Resuelto por especificidad de contexto: {best_context_score:.2f}"
        
        return best_memory, confidence, reasoning
    
    async def _update_agent_memories(self, conflict: ConflictInstance, resolution: ResolutionResult):
        """Actualizar memorias de agentes afectados con resolución"""
        
        for agent_id in conflict.affected_agents:
            try:
                # Almacenar memoria resuelta
                db_manager.store_memory(
                    agent_id=agent_id,
                    memory_type="resolved_conflict",
                    content=f"Resolved conflict: {conflict.conflict_description}",
                    context=json.dumps({
                        "conflict_id": conflict.conflict_id,
                        "resolution_strategy": resolution.strategy_used.value,
                        "resolved_memory": resolution.resolved_memory,
                        "confidence": resolution.confidence_score
                    }),
                    importance_score=8,
                    tags=["conflict_resolution", "memory_update", conflict.conflict_type.value]
                )
                
                # Indexar en memoria vectorial
                vector_memory.add_memory_to_vector_store(
                    agent_id=agent_id,
                    memory_id=len(self.resolution_history),
                    content=f"Conflict resolved: {resolution.resolution_reasoning}",
                    memory_type="conflict_resolution",
                    importance_score=8,
                    tags=["resolved_conflict", agent_id]
                )
                
            except Exception as e:
                logger.error(f"❌ Error actualizando memoria de agente {agent_id}: {e}")
    
    def _update_resolution_stats(self):
        """Actualizar estadísticas de resolución"""
        
        if self.conflicts_detected > 0:
            self.resolution_success_rate = self.conflicts_resolved / self.conflicts_detected
    
    def get_conflict_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de resolución de conflictos"""
        
        return {
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "active_conflicts": len(self.active_conflicts),
            "resolution_success_rate": self.resolution_success_rate,
            "conflict_types_detected": {
                ctype.value: sum(1 for c in self.resolved_conflicts if c.conflict_type == ctype)
                for ctype in ConflictType
            },
            "resolution_strategies_used": {
                strategy.value: sum(1 for r in self.resolution_history if r.strategy_used == strategy)
                for strategy in ResolutionStrategy
            },
            "average_resolution_confidence": np.mean([r.confidence_score for r in self.resolution_history]) if self.resolution_history else 0.0,
            "system_status": "active"
        }

# Instancia global del sistema de resolución de conflictos
conflict_resolution = ConflictResolutionSystem() 