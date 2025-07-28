"""
Cognitive Agent Architecture - AgentOS
Implementación basada en papers MemoryOS, MIRIX, SciBORG, Test-Time Learning
Arquitectura cognitiva diferenciada por especialización
"""

import asyncio
import logging
import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

from ..memory.vector_memory import vector_memory
from ..database.database import db_manager

logger = logging.getLogger(__name__)

def safe_json_serialize(obj):
    """Serialización JSON segura que maneja numpy arrays"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    else:
        return obj

class ReasoningMode(Enum):
    """Modos de razonamiento especializados según SciBORG"""
    ANALYTICAL = "analytical"           # Para researcher
    TECHNICAL = "technical"             # Para coder  
    COORDINATIVE = "coordinative"       # Para coordinator
    CREATIVE = "creative"               # Para future agents
    LOGICAL = "logical"                 # Para future agents

class MemoryType(Enum):
    """Tipos de memoria según MIRIX"""
    CORE = "core"                       # Identidad y personalidad
    EPISODIC = "episodic"               # Experiencias específicas
    SEMANTIC = "semantic"               # Conocimiento conceptual
    PROCEDURAL = "procedural"           # Cómo hacer cosas
    WORKING = "working"                 # Memoria de trabajo actual
    RESOURCE = "resource"               # Herramientas y referencias

@dataclass
class CognitiveState:
    """Estado cognitivo actual del agente (MemoryOS working memory)"""
    current_task: Optional[str] = None
    reasoning_mode: ReasoningMode = ReasoningMode.ANALYTICAL
    active_memories: List[Dict] = None
    context_window: List[Dict] = None
    confidence_level: float = 0.7
    specialization_focus: str = ""
    learning_buffer: List[Dict] = None

    def __post_init__(self):
        if self.active_memories is None:
            self.active_memories = []
        if self.context_window is None:
            self.context_window = []
        if self.learning_buffer is None:
            self.learning_buffer = []

@dataclass
class PersonalityProfile:
    """Perfil de personalidad computacional (MIRIX Core Memory)"""
    agent_id: str
    role_identity: str
    behavioral_traits: List[str]
    communication_style: str
    decision_making_approach: str
    expertise_confidence: float
    collaboration_preference: str
    learning_style: str
    problem_solving_approach: str

class CognitiveAgent:
    """
    Agente Cognitivo Base con Arquitectura Especializada
    Implementa MemoryOS + MIRIX + SciBORG patterns
    """
    
    def __init__(self, agent_id: str, specialization: str, personality: PersonalityProfile):
        self.agent_id = agent_id
        self.specialization = specialization
        self.personality = personality
        
        # Estado cognitivo (MemoryOS working memory)
        self.cognitive_state = CognitiveState(
            specialization_focus=specialization,
            reasoning_mode=self._get_default_reasoning_mode()
        )
        
        # Sistemas de memoria especializados (MIRIX)
        self.memory_systems = {
            MemoryType.CORE: {},           # Identidad y personalidad
            MemoryType.EPISODIC: [],       # Experiencias de tareas
            MemoryType.SEMANTIC: {},       # Conocimiento del dominio
            MemoryType.PROCEDURAL: {},     # Procedimientos especializados
            MemoryType.WORKING: [],        # Contexto actual
            MemoryType.RESOURCE: {}        # Herramientas y referencias
        }
        
        # Inicializar memoria core con personalidad
        self._initialize_core_memory()
        
        # Sistema de aprendizaje (Test-Time Learning)
        self.learning_system = {
            "experiences": [],
            "feedback_patterns": {},
            "performance_metrics": {},
            "adaptation_rules": {}
        }
        
        logger.info(f"🧠 CognitiveAgent {agent_id} inicializado - Especialización: {specialization}")
    
    def _get_default_reasoning_mode(self) -> ReasoningMode:
        """Modo de razonamiento por defecto según especialización"""
        reasoning_map = {
            "research": ReasoningMode.ANALYTICAL,
            "coding": ReasoningMode.TECHNICAL,
            "coordination": ReasoningMode.COORDINATIVE,
            "analysis": ReasoningMode.ANALYTICAL,
            "development": ReasoningMode.TECHNICAL
        }
        return reasoning_map.get(self.specialization, ReasoningMode.ANALYTICAL)
    
    def _initialize_core_memory(self):
        """Inicializar memoria core con identidad del agente (MIRIX)"""
        self.memory_systems[MemoryType.CORE] = {
            "identity": {
                "agent_id": self.agent_id,
                "role": self.personality.role_identity,
                "specialization": self.specialization,
                "created_at": datetime.utcnow().isoformat()
            },
            "personality": {
                "traits": self.personality.behavioral_traits,
                "communication_style": self.personality.communication_style,
                "decision_approach": self.personality.decision_making_approach,
                "collaboration_style": self.personality.collaboration_preference
            },
            "capabilities": {
                "reasoning_modes": [self._get_default_reasoning_mode().value],
                "expertise_areas": [self.specialization],
                "confidence_level": self.personality.expertise_confidence
            }
        }
    
    async def specialized_reasoning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sistema de razonamiento especializado por dominio (SciBORG)
        Cada especialización tiene su propio patrón de razonamiento
        """
        try:
            # Activar contexto cognitivo
            self.cognitive_state.current_task = task
            self.cognitive_state.context_window = [context]
            
            # Recuperar memoria relevante especializada
            relevant_memories = await self._retrieve_specialized_memories(task)
            self.cognitive_state.active_memories = relevant_memories
            
            # Aplicar razonamiento específico por especialización
            reasoning_result = await self._apply_domain_reasoning(task, context, relevant_memories)
            
            # Actualizar memoria episódica con experiencia
            await self._store_episodic_memory(task, context, reasoning_result)
            
            # Aplicar aprendizaje continuo (Test-Time Learning)
            await self._apply_test_time_learning(task, reasoning_result)
            
            return reasoning_result
            
        except Exception as e:
            logger.error(f"❌ Error en razonamiento especializado {self.agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "specialization": self.specialization
            }
    
    async def _retrieve_specialized_memories(self, task: str) -> Dict[str, Any]:
        """Recuperación de memoria especializada por dominio"""
        try:
            # Búsqueda semántica en memoria vectorial
            semantic_memories = vector_memory.semantic_search(
                agent_id=self.agent_id,
                query=task,
                limit=5,
                min_score=0.3
            )
            
            # Memoria semántica especializada
            domain_keywords = self._extract_domain_keywords(task)
            semantic_knowledge = []
            for keyword in domain_keywords:
                if keyword in self.memory_systems[MemoryType.SEMANTIC]:
                    semantic_knowledge.append(self.memory_systems[MemoryType.SEMANTIC][keyword])
            
            # Memoria procedimental relevante
            procedural_memories = []
            for proc_name, procedure in self.memory_systems[MemoryType.PROCEDURAL].items():
                if any(keyword in proc_name.lower() for keyword in domain_keywords):
                    procedural_memories.append(procedure)
            
            return {
                "semantic_search": semantic_memories,
                "domain_knowledge": semantic_knowledge,
                "procedures": procedural_memories,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recuperando memorias especializadas: {e}")
            return {
                "semantic_search": [],
                "domain_knowledge": [],
                "procedures": [],
                "retrieved_at": datetime.utcnow().isoformat()
            }
    
    def _extract_domain_keywords(self, task: str) -> List[str]:
        """Extracción de palabras clave específicas del dominio"""
        # Keywords por especialización
        domain_maps = {
            "research": ["analyze", "study", "investigate", "data", "trends", "findings", "research"],
            "coding": ["implement", "code", "develop", "algorithm", "function", "programming", "software"],
            "coordination": ["coordinate", "manage", "organize", "synthesize", "combine", "workflow"]
        }
        
        base_keywords = domain_maps.get(self.specialization, [])
        task_words = [word.lower().strip('.,!?') for word in task.split()]
        
        return list(set(base_keywords + [word for word in task_words if len(word) > 3]))
    
    async def _apply_domain_reasoning(self, task: str, context: Dict, memories: Dict) -> Dict[str, Any]:
        """
        Aplicar razonamiento específico del dominio
        AQUÍ ES DONDE CADA AGENTE SE DIFERENCIA COGNITIVAMENTE
        """
        reasoning_mode = self.cognitive_state.reasoning_mode
        
        # Template base que será especializado por cada subclase
        reasoning_result = {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "reasoning_mode": reasoning_mode.value,
            "task_analysis": await self._analyze_task_domain_specific(task),
            "memory_integration": memories,
            "domain_insights": await self._generate_domain_insights(task, context),
            "confidence": self.cognitive_state.confidence_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return reasoning_result
    
    async def _analyze_task_domain_specific(self, task: str) -> Dict[str, Any]:
        """Análisis de tarea específico por dominio - será sobrescrito por subclases"""
        return {
            "task": task,
            "complexity": "moderate",
            "domain_relevance": "high",
            "approach": "specialized_reasoning"
        }
    
    async def _generate_domain_insights(self, task: str, context: Dict) -> Dict[str, Any]:
        """Generación de insights específicos del dominio - será sobrescrito por subclases"""
        return {
            "insights": f"Domain-specific analysis for {self.specialization}",
            "recommendations": ["Apply specialized knowledge", "Use domain tools"],
            "next_steps": ["Continue with specialized approach"]
        }
    
    async def _store_episodic_memory(self, task: str, context: Dict, result: Dict):
        """Almacenar experiencia en memoria episódica (MIRIX)"""
        try:
            episode = {
                "id": str(uuid.uuid4()),
                "task": task,
                "context": context,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "performance_score": result.get("confidence", 0.7),
                "lessons_learned": []
            }
            
            self.memory_systems[MemoryType.EPISODIC].append(episode)
            
            # Almacenar también en BD persistente
            safe_episode = safe_json_serialize(episode)
            memory_id = db_manager.store_memory(
                agent_id=self.agent_id,
                memory_type="episodic",
                content=f"Completed task: {task}",
                context=json.dumps({"episode": safe_episode}),
                importance_score=8,
                tags=["episodic", self.specialization, "experience"]
            )
            
            # Indexar en memoria vectorial
            if memory_id:
                vector_memory.add_memory_to_vector_store(
                    agent_id=self.agent_id,
                    memory_id=memory_id,
                    content=f"Experience: {task}",
                    memory_type="episodic",
                    importance_score=8,
                    tags=["episodic", self.specialization]
                )
            
        except Exception as e:
            import traceback
            logger.error(f"Error almacenando memoria episódica: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    async def _apply_test_time_learning(self, task: str, result: Dict):
        """Aplicar aprendizaje en tiempo de test (Test-Time Learning)"""
        try:
            # Extraer patrones de la experiencia
            performance = result.get("confidence", 0.7)
            
            # Actualizar métricas de performance
            if task not in self.learning_system["performance_metrics"]:
                self.learning_system["performance_metrics"][task] = []
            
            self.learning_system["performance_metrics"][task].append({
                "performance": performance,
                "timestamp": datetime.utcnow().isoformat(),
                "context": result.get("domain_insights", {})
            })
            
            # Detectar patrones de mejora/degradación
            if len(self.learning_system["performance_metrics"][task]) > 1:
                trend = self._detect_performance_trend(task)
                if trend["improving"]:
                    # Reforzar estrategias exitosas
                    await self._reinforce_successful_patterns(task, result)
                elif trend["degrading"]:
                    # Adaptar estrategias
                    await self._adapt_strategies(task, result)
            
            # Actualizar memoria semántica con nuevos conceptos
            await self._update_semantic_memory(task, result)
            
        except Exception as e:
            logger.error(f"Error en test-time learning: {e}")
    
    def _detect_performance_trend(self, task: str) -> Dict[str, bool]:
        """Detectar tendencias de performance para aprendizaje"""
        metrics = self.learning_system["performance_metrics"][task]
        if len(metrics) < 2:
            return {"improving": False, "degrading": False}
        
        recent_avg = np.mean([m["performance"] for m in metrics[-3:]])
        older_avg = np.mean([m["performance"] for m in metrics[:-3]]) if len(metrics) > 3 else metrics[0]["performance"]
        
        improvement_threshold = 0.1
        
        return {
            "improving": recent_avg > older_avg + improvement_threshold,
            "degrading": recent_avg < older_avg - improvement_threshold
        }
    
    async def _reinforce_successful_patterns(self, task: str, result: Dict):
        """Reforzar patrones exitosos en memoria procedimental"""
        try:
            successful_pattern = {
                "task_type": task,
                "successful_approach": result.get("domain_insights", {}),
                "confidence_achieved": result.get("confidence", 0.7),
                "reinforcement_count": 1,
                "last_success": datetime.utcnow().isoformat()
            }
            
            pattern_key = f"success_pattern_{hash(task) % 1000}"
            if pattern_key in self.memory_systems[MemoryType.PROCEDURAL]:
                self.memory_systems[MemoryType.PROCEDURAL][pattern_key]["reinforcement_count"] += 1
            else:
                self.memory_systems[MemoryType.PROCEDURAL][pattern_key] = successful_pattern
                
        except Exception as e:
            logger.error(f"Error reforzando patrones exitosos: {e}")
    
    async def _adapt_strategies(self, task: str, result: Dict):
        """Adaptar estrategias cuando performance degrada"""
        # Implementar lógica de adaptación específica por agente
        adaptation = {
            "task": task,
            "previous_approach": result.get("domain_insights", {}),
            "adaptation_needed": True,
            "suggested_changes": ["adjust_reasoning_mode", "seek_additional_context"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.learning_system["adaptation_rules"][task] = adaptation
    
    async def _update_semantic_memory(self, task: str, result: Dict):
        """Actualizar memoria semántica con nuevos conceptos (MIRIX)"""
        try:
            # Extraer conceptos nuevos del resultado
            insights = result.get("domain_insights", {})
            new_concepts = insights.get("insights", "")
            
            if new_concepts and isinstance(new_concepts, str):
                concepts = [concept.strip() for concept in new_concepts.split(",")]
                
                for concept in concepts:
                    if concept and len(concept) > 3:
                        if concept not in self.memory_systems[MemoryType.SEMANTIC]:
                            self.memory_systems[MemoryType.SEMANTIC][concept] = {
                                "definition": f"Concept learned from {task}",
                                "related_tasks": [task],
                                "confidence": result.get("confidence", 0.7),
                                "learned_at": datetime.utcnow().isoformat()
                            }
                        else:
                            # Actualizar concepto existente
                            self.memory_systems[MemoryType.SEMANTIC][concept]["related_tasks"].append(task)
                            
        except Exception as e:
            logger.error(f"Error actualizando memoria semántica: {e}")
    
    def get_cognitive_status(self) -> Dict[str, Any]:
        """Status cognitivo completo del agente"""
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "cognitive_state": {
                "current_task": self.cognitive_state.current_task,
                "reasoning_mode": self.cognitive_state.reasoning_mode.value,
                "confidence": self.cognitive_state.confidence_level,
                "active_memories_count": len(self.cognitive_state.active_memories)
            },
            "memory_systems": {
                "core_identity": bool(self.memory_systems[MemoryType.CORE]),
                "episodic_experiences": len(self.memory_systems[MemoryType.EPISODIC]),
                "semantic_concepts": len(self.memory_systems[MemoryType.SEMANTIC]),
                "procedural_patterns": len(self.memory_systems[MemoryType.PROCEDURAL])
            },
            "learning_progress": {
                "tasks_experienced": len(self.learning_system["performance_metrics"]),
                "adaptation_rules": len(self.learning_system["adaptation_rules"]),
                "total_experiences": len(self.learning_system["experiences"])
            },
            "personality": {
                "role_identity": self.personality.role_identity,
                "communication_style": self.personality.communication_style,
                "expertise_confidence": self.personality.expertise_confidence
            }
        } 