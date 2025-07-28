"""
Sistema de Memoria Vectorial Avanzada - AgentOS
Implementación basada en papers SciBORG, MemoryOS y G-Memory
Embeddings semánticos + FAISS + RAG
"""

import os
import numpy as np
import faiss
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from ..database.database import db_manager

logger = logging.getLogger(__name__)

class VectorMemorySystem:
    """
    Sistema de memoria vectorial avanzada
    Implementación inspirada en SciBORG RAG + MemoryOS hierarchy
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", vector_dim: int = 384):
        self.model_name = model_name
        self.vector_dim = vector_dim
        self.embedder = None
        self.vector_stores = {}  # Almacenes por agente
        self.index_files = {}   # Archivos de índices FAISS
        
        self._initialize_embedder()
        logger.info(f"🧠 VectorMemorySystem inicializado con {model_name}")
    
    def _initialize_embedder(self):
        """Inicializa el modelo de embeddings"""
        try:
            if SentenceTransformer is None:
                logger.warning("⚠️ sentence-transformers no disponible, usando embeddings simulados")
                return
                
            self.embedder = SentenceTransformer(self.model_name)
            logger.info(f"✅ Modelo de embeddings {self.model_name} cargado")
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo de embeddings: {e}")
            self.embedder = None
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Genera embedding para un texto"""
        if self.embedder is None:
            # Embedding simulado para testing
            np.random.seed(hash(text) % 2**32)
            return np.random.rand(self.vector_dim).astype('float32')
        
        try:
            embedding = self.embedder.encode([text])[0]
            return embedding.astype('float32')
        except Exception as e:
            logger.error(f"❌ Error generando embedding: {e}")
            # Fallback: embedding simulado
            np.random.seed(hash(text) % 2**32)
            return np.random.rand(self.vector_dim).astype('float32')
    
    def _get_agent_index(self, agent_id: str) -> faiss.IndexFlatIP:
        """Obtiene o crea índice FAISS para un agente"""
        if agent_id not in self.vector_stores:
            # Crear nuevo índice FAISS (Inner Product para similitud coseno)
            index = faiss.IndexFlatIP(self.vector_dim)
            self.vector_stores[agent_id] = {
                'index': index,
                'metadata': [],  # Lista de metadatos correspondientes
                'memory_ids': []  # IDs de memoria en BD
            }
            logger.info(f"🆕 Nuevo índice vectorial creado para agente {agent_id}")
        
        return self.vector_stores[agent_id]
    
    def add_memory_to_vector_store(self, agent_id: str, memory_id: int, content: str, 
                                  memory_type: str, importance_score: int, tags: List[str]) -> bool:
        """
        Añade una memoria al almacén vectorial
        Inspirado en SciBORG RAG indexing
        """
        try:
            # Generar embedding
            embedding = self._get_embedding(content)
            
            # Normalizar para similitud coseno
            embedding = embedding / np.linalg.norm(embedding)
            embedding = embedding.reshape(1, -1)
            
            # Obtener índice del agente
            agent_store = self._get_agent_index(agent_id)
            
            # Añadir al índice FAISS
            agent_store['index'].add(embedding)
            
            # Guardar metadatos
            metadata = {
                'memory_id': memory_id,
                'content': content,
                'memory_type': memory_type,
                'importance_score': importance_score,
                'tags': tags,
                'created_at': datetime.utcnow().isoformat(),
                'embedding_model': self.model_name
            }
            
            agent_store['metadata'].append(metadata)
            agent_store['memory_ids'].append(memory_id)
            
            logger.info(f"✅ Memoria {memory_id} añadida al vector store de {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo memoria al vector store: {e}")
            return False
    
    def semantic_search(self, agent_id: str, query: str, limit: int = 10, 
                       memory_type: str = None, min_score: float = 0.3) -> List[Dict]:
        """
        Búsqueda semántica avanzada
        Implementación basada en MemoryOS semantic segmentation
        """
        try:
            if agent_id not in self.vector_stores:
                logger.warning(f"⚠️ No hay vector store para agente {agent_id}")
                return []
            
            agent_store = self.vector_stores[agent_id]
            index = agent_store['index']
            
            if index.ntotal == 0:
                logger.warning(f"⚠️ Vector store vacío para agente {agent_id}")
                return []
            
            # Generar embedding de la consulta
            query_embedding = self._get_embedding(query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Buscar vectores más similares
            scores, indices = index.search(query_embedding, min(limit * 2, index.ntotal))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score < min_score:  # Filtrar por score mínimo
                    continue
                
                if idx >= len(agent_store['metadata']):
                    continue
                
                metadata = agent_store['metadata'][idx]
                
                # Filtrar por tipo de memoria si se especifica
                if memory_type and metadata['memory_type'] != memory_type:
                    continue
                
                result = {
                    'memory_id': metadata['memory_id'],
                    'content': metadata['content'],
                    'memory_type': metadata['memory_type'],
                    'importance_score': metadata['importance_score'],
                    'tags': metadata['tags'],
                    'semantic_score': float(score),
                    'created_at': metadata['created_at'],
                    'rank': i + 1
                }
                
                results.append(result)
                
                if len(results) >= limit:
                    break
            
            logger.info(f"🔍 Búsqueda semántica para '{query}': {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda semántica: {e}")
            return []
    
    def hybrid_search(self, agent_id: str, query: str, limit: int = 10,
                     memory_type: str = None) -> List[Dict]:
        """
        Búsqueda híbrida: semántica + tradicional
        Combina vector search + SQL search como en G-Memory
        """
        try:
            # Búsqueda semántica vectorial
            semantic_results = self.semantic_search(
                agent_id, query, limit=limit//2, memory_type=memory_type, min_score=0.2
            )
            
            # Búsqueda tradicional en BD
            traditional_results = db_manager.recall_memory(
                agent_id=agent_id,
                memory_type=memory_type,
                search_term=query,
                limit=limit//2
            )
            
            # Combinar y deduplicar resultados
            combined_results = []
            seen_memory_ids = set()
            
            # Añadir resultados semánticos (mayor prioridad)
            for result in semantic_results:
                memory_id = result['memory_id']
                if memory_id not in seen_memory_ids:
                    result['search_type'] = 'semantic'
                    combined_results.append(result)
                    seen_memory_ids.add(memory_id)
            
            # Añadir resultados tradicionales no duplicados
            for result in traditional_results:
                memory_id = result.get('id', 0)
                if memory_id not in seen_memory_ids:
                    # Convertir formato tradicional a formato híbrido
                    hybrid_result = {
                        'memory_id': memory_id,
                        'content': result['content'],
                        'memory_type': result['memory_type'],
                        'importance_score': result['importance_score'],
                        'tags': result['tags'],
                        'semantic_score': 0.0,  # No score semántico
                        'created_at': result['created_at'],
                        'search_type': 'traditional',
                        'rank': len(combined_results) + 1
                    }
                    combined_results.append(hybrid_result)
                    seen_memory_ids.add(memory_id)
            
            # Limitar resultados finales
            final_results = combined_results[:limit]
            
            logger.info(f"🔍 Búsqueda híbrida: {len(semantic_results)} semánticos + {len(traditional_results)} tradicionales = {len(final_results)} finales")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda híbrida: {e}")
            return []
    
    def migrate_existing_memories(self, agent_id: str) -> int:
        """
        Migra memorias existentes al sistema vectorial
        Proceso de migración incremental
        """
        try:
            # Obtener todas las memorias existentes del agente
            all_memories = db_manager.recall_memory(
                agent_id=agent_id,
                limit=1000  # Migrar todas
            )
            
            migrated_count = 0
            
            for memory in all_memories:
                memory_id = memory.get('id', 0)
                content = memory.get('content', '')
                memory_type = memory.get('memory_type', 'medium_term')
                importance_score = memory.get('importance_score', 5)
                tags = memory.get('tags', [])
                
                if content and memory_id:
                    success = self.add_memory_to_vector_store(
                        agent_id=agent_id,
                        memory_id=memory_id,
                        content=content,
                        memory_type=memory_type,
                        importance_score=importance_score,
                        tags=tags
                    )
                    
                    if success:
                        migrated_count += 1
            
            logger.info(f"✅ Migración completada: {migrated_count} memorias vectorizadas para {agent_id}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Error en migración de memorias: {e}")
            return 0
    
    def get_vector_stats(self, agent_id: str) -> Dict:
        """Obtiene estadísticas del vector store"""
        try:
            if agent_id not in self.vector_stores:
                return {
                    'total_vectors': 0,
                    'vector_dimension': self.vector_dim,
                    'embedding_model': self.model_name,
                    'status': 'not_initialized'
                }
            
            agent_store = self.vector_stores[agent_id]
            index = agent_store['index']
            
            # Estadísticas por tipo de memoria
            memory_type_counts = {}
            for metadata in agent_store['metadata']:
                memory_type = metadata['memory_type']
                memory_type_counts[memory_type] = memory_type_counts.get(memory_type, 0) + 1
            
            return {
                'total_vectors': index.ntotal,
                'vector_dimension': self.vector_dim,
                'embedding_model': self.model_name,
                'memory_types': memory_type_counts,
                'status': 'active',
                'faiss_index_type': 'IndexFlatIP'
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats vectoriales: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def save_vector_store(self, agent_id: str, filepath: str = None) -> bool:
        """Guarda el vector store en disco para persistencia"""
        try:
            if agent_id not in self.vector_stores:
                logger.warning(f"⚠️ No hay vector store para guardar: {agent_id}")
                return False
            
            if filepath is None:
                filepath = f"vector_store_{agent_id}.pkl"
            
            agent_store = self.vector_stores[agent_id]
            
            # Guardar índice FAISS
            faiss.write_index(agent_store['index'], f"{filepath}.faiss")
            
            # Guardar metadatos
            with open(f"{filepath}.meta", 'wb') as f:
                pickle.dump({
                    'metadata': agent_store['metadata'],
                    'memory_ids': agent_store['memory_ids'],
                    'model_name': self.model_name,
                    'vector_dim': self.vector_dim
                }, f)
            
            logger.info(f"✅ Vector store guardado: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando vector store: {e}")
            return False
    
    # ===============================
    # MÉTODOS DE COMPATIBILIDAD (NUEVOS)
    # ===============================
    
    async def search_memories(self, agent_id: str, query: str, limit: int = 10, 
                            memory_type: str = None) -> List[Dict[str, Any]]:
        """
        Método de compatibilidad para búsqueda de memorias
        Wrapper que combina búsqueda semántica + BD
        """
        try:
            # Búsqueda semántica vectorial
            semantic_results = self.semantic_search(
                agent_id=agent_id,
                query=query,
                limit=limit//2,
                memory_type=memory_type,
                min_score=0.3
            )
            
            # Búsqueda en BD como fallback
            db_results = []
            try:
                db_results = db_manager.get_agent_memories(
                    agent_id=agent_id,
                    memory_type=memory_type,
                    limit=limit//2
                )
            except Exception as e:
                logger.warning(f"⚠️ Error en búsqueda BD: {e}")
            
            # Combinar resultados
            combined_results = []
            
            # Añadir resultados semánticos
            for result in semantic_results:
                combined_results.append({
                    'memory_id': result['memory_id'],
                    'content': result['content'],
                    'memory_type': result['memory_type'],
                    'importance_score': result['importance_score'],
                    'semantic_score': result['semantic_score'],
                    'source': 'vector_search'
                })
            
            # Añadir resultados de BD
            for result in db_results:
                # Evitar duplicados
                if not any(r['memory_id'] == result['id'] for r in combined_results):
                    combined_results.append({
                        'memory_id': result['id'],
                        'content': result['content'],
                        'memory_type': result['memory_type'],
                        'importance_score': result['importance_score'],
                        'semantic_score': 0.5,  # Score por defecto
                        'source': 'database_search'
                    })
            
            # Ordenar por importancia y score semántico
            combined_results.sort(
                key=lambda x: (x['importance_score'], x['semantic_score']), 
                reverse=True
            )
            
            # Limitar resultados
            combined_results = combined_results[:limit]
            
            logger.info(f"🔍 Búsqueda de memorias para '{query}': {len(combined_results)} resultados")
            return combined_results
            
        except Exception as e:
            logger.error(f"❌ Error en search_memories: {e}")
            return []
    
    async def store_memory(self, agent_id: str, memory_type: str, content: str,
                          context: str = None, importance_score: int = 5,
                          conversation_id: str = None, tags: List[str] = None) -> int:
        """
        Método de compatibilidad para almacenar memoria
        Wrapper que almacena en BD + vector store
        """
        try:
            # 1. Almacenar en BD
            memory_id = db_manager.store_memory(
                agent_id=agent_id,
                memory_type=memory_type,
                content=content,
                context=context,
                importance_score=importance_score,
                conversation_id=conversation_id,
                tags=tags or []
            )
            
            if memory_id:
                # 2. Almacenar en vector store
                success = self.add_memory_to_vector_store(
                    agent_id=agent_id,
                    memory_id=memory_id,
                    content=content,
                    memory_type=memory_type,
                    importance_score=importance_score,
                    tags=tags or []
                )
                
                if success:
                    logger.info(f"✅ Memoria {memory_id} almacenada en BD y vector store")
                else:
                    logger.warning(f"⚠️ Memoria {memory_id} almacenada solo en BD")
                
                return memory_id
            else:
                logger.error(f"❌ Error almacenando memoria en BD")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error en store_memory: {e}")
            return 0

# Instancia global del sistema de memoria vectorial
vector_memory = VectorMemorySystem() 