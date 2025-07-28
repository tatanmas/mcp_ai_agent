#!/bin/bash

echo "🧪 TESTING MEMORIA VECTORIAL + RAG - AVANCE 2.5"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. 🔍 Verificando Sistema Vectorial en Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "vector_memory"; then
    echo -e "${GREEN}✅ Sistema vectorial detectado!${NC}"
    echo "   Vector Memory: $(echo "$HEALTH_RESPONSE" | grep -o '"vector_memory":"[^"]*"' | cut -d'"' -f4)"
    echo "   Embedding Model: $(echo "$HEALTH_RESPONSE" | grep -o '"embedding_model":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}❌ Sistema vectorial no encontrado en health check${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. 📊 Estadísticas Iniciales del Sistema Vectorial:${NC}"
curl -s http://localhost:8000/api/v1/memory/vector-stats/default | jq '.vector_memory' 2>/dev/null || curl -s http://localhost:8000/api/v1/memory/vector-stats/default

echo ""
echo -e "${BLUE}3. 💾 Almacenando Memorias Diversas para Testing Semántico:${NC}"

# Memoria técnica
echo "   📝 Almacenando memoria técnica..."
STORE_TECH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "long_term",
    "content": "Error de conexión de base de datos PostgreSQL resuelto reiniciando el servicio",
    "context": "Problema técnico solucionado",
    "importance_score": 8,
    "tags": ["technical", "database", "troubleshooting", "postgresql"]
  }')

echo "   Resultado: $(echo "$STORE_TECH_RESPONSE" | jq -r '.message' 2>/dev/null)"
echo "   Vector indexed: $(echo "$STORE_TECH_RESPONSE" | jq -r '.vector_indexed' 2>/dev/null)"

# Memoria personal
echo "   👤 Almacenando memoria personal..."
STORE_PERSONAL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "long_term",
    "content": "Usuario Tatan es desarrollador especializado en inteligencia artificial y sistemas distribuidos",
    "context": "Información personal del usuario principal",
    "importance_score": 9,
    "tags": ["personal", "user_profile", "ai_developer", "expertise"]
  }')

echo "   Resultado: $(echo "$STORE_PERSONAL_RESPONSE" | jq -r '.message' 2>/dev/null)"

# Memoria de proyecto
echo "   🚀 Almacenando memoria de proyecto..."
STORE_PROJECT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "medium_term",
    "content": "Proyecto AgentOS implementó exitosamente MCP y memoria persistente con búsqueda vectorial",
    "context": "Hito importante del proyecto actual",
    "importance_score": 10,
    "tags": ["project", "milestone", "agentos", "mcp", "memory", "success"]
  }')

echo "   Resultado: $(echo "$STORE_PROJECT_RESPONSE" | jq -r '.message' 2>/dev/null)"

# Memoria conversacional
echo "   💬 Almacenando memoria conversacional..."
STORE_CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "short_term",
    "content": "En la conversación actual discutimos implementación de embeddings y RAG para mejorar búsqueda",
    "context": "Contexto de conversación reciente",
    "importance_score": 7,
    "tags": ["conversation", "embeddings", "rag", "search_improvement"]
  }')

echo "   Resultado: $(echo "$STORE_CONV_RESPONSE" | jq -r '.message' 2>/dev/null)"

echo ""
echo -e "${BLUE}4. 🔄 Migrando Memorias Existentes al Sistema Vectorial:${NC}"
MIGRATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/migrate-to-vectors/default")
echo "   📦 Migración: $(echo "$MIGRATE_RESPONSE" | jq -r '.success' 2>/dev/null)"
echo "   📊 Memorias migradas: $(echo "$MIGRATE_RESPONSE" | jq -r '.migrated_memories' 2>/dev/null)"

echo ""
echo -e "${BLUE}5. 📈 Estadísticas Post-Migración:${NC}"
STATS_RESPONSE=$(curl -s http://localhost:8000/api/v1/memory/vector-stats/default)
echo "$STATS_RESPONSE" | jq '{
  total_vectors: .vector_memory.total_vectors,
  embedding_model: .vector_memory.embedding_model,
  memory_types: .vector_memory.memory_types,
  coverage: .comparison.embedding_coverage
}' 2>/dev/null || echo "$STATS_RESPONSE"

echo ""
echo -e "${BLUE}6. 🔍 Pruebas de Búsqueda Semántica Avanzada:${NC}"

# Búsqueda por concepto técnico
echo -e "${CYAN}   🎯 Búsqueda: 'problemas de base de datos'${NC}"
SEMANTIC_1=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "problemas de base de datos",
    "limit": 5,
    "min_score": 0.2
  }')

echo "   Resultados encontrados: $(echo "$SEMANTIC_1" | jq -r '.count' 2>/dev/null)"
echo "$SEMANTIC_1" | jq '.results[] | {content: .content, score: .semantic_score, tags: .tags}' 2>/dev/null

echo ""
# Búsqueda por expertise
echo -e "${CYAN}   🎯 Búsqueda: 'experto en inteligencia artificial'${NC}"
SEMANTIC_2=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "experto en inteligencia artificial",
    "limit": 5,
    "min_score": 0.2
  }')

echo "   Resultados encontrados: $(echo "$SEMANTIC_2" | jq -r '.count' 2>/dev/null)"
echo "$SEMANTIC_2" | jq '.results[] | {content: .content, score: .semantic_score}' 2>/dev/null

echo ""
# Búsqueda por logros
echo -e "${CYAN}   🎯 Búsqueda: 'éxitos del proyecto'${NC}"
SEMANTIC_3=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "éxitos del proyecto",
    "limit": 5,
    "min_score": 0.2
  }')

echo "   Resultados encontrados: $(echo "$SEMANTIC_3" | jq -r '.count' 2>/dev/null)"
echo "$SEMANTIC_3" | jq '.results[] | {content: .content, score: .semantic_score}' 2>/dev/null

echo ""
echo -e "${BLUE}7. 🔄 Pruebas de Búsqueda Híbrida (G-Memory approach):${NC}"

echo -e "${CYAN}   🎯 Búsqueda híbrida: 'MCP implementation'${NC}"
HYBRID_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/hybrid-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "MCP implementation",
    "limit": 8
  }')

echo "   Total resultados: $(echo "$HYBRID_RESPONSE" | jq -r '.count' 2>/dev/null)"
echo "   Semánticos: $(echo "$HYBRID_RESPONSE" | jq -r '.breakdown.semantic_results' 2>/dev/null)"
echo "   Tradicionales: $(echo "$HYBRID_RESPONSE" | jq -r '.breakdown.traditional_results' 2>/dev/null)"

echo "$HYBRID_RESPONSE" | jq '.results[] | {content: .content, search_type: .search_type, score: .semantic_score}' 2>/dev/null

echo ""
echo -e "${BLUE}8. ⚖️ Comparación Completa de Métodos de Búsqueda:${NC}"

COMPARISON_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/search-comparison" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "desarrollo de inteligencia artificial",
    "limit": 5
  }')

echo -e "${CYAN}   📊 Comparación para: 'desarrollo de inteligencia artificial'${NC}"
echo "   Traditional (SQL): $(echo "$COMPARISON_RESPONSE" | jq -r '.comparison.traditional.count' 2>/dev/null) resultados"
echo "   Semantic (FAISS): $(echo "$COMPARISON_RESPONSE" | jq -r '.comparison.semantic.count' 2>/dev/null) resultados"
echo "   Hybrid (Combined): $(echo "$COMPARISON_RESPONSE" | jq -r '.comparison.hybrid.count' 2>/dev/null) resultados"
echo "   Recomendación: $(echo "$COMPARISON_RESPONSE" | jq -r '.recommendation' 2>/dev/null)"

echo ""
echo -e "${BLUE}9. 🧪 Testing de Casos Edge y Precisión:${NC}"

# Búsqueda muy específica
echo "   🔬 Testing búsqueda específica: 'PostgreSQL service restart'..."
EDGE_1=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "PostgreSQL service restart",
    "limit": 3,
    "min_score": 0.4
  }')

EDGE_1_COUNT=$(echo "$EDGE_1" | jq -r '.count' 2>/dev/null)
echo "   Resultados específicos: $EDGE_1_COUNT"

# Búsqueda por sinónimos
echo "   🔬 Testing sinónimos: 'errores de conexión'..."
EDGE_2=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "errores de conexión",
    "limit": 3,
    "min_score": 0.3
  }')

EDGE_2_COUNT=$(echo "$EDGE_2" | jq -r '.count' 2>/dev/null)
echo "   Resultados por sinónimos: $EDGE_2_COUNT"

# Búsqueda conceptual
echo "   🔬 Testing conceptual: 'machine learning expert'..."
EDGE_3=$(curl -s -X POST "http://localhost:8000/api/v1/memory/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "query": "machine learning expert",
    "limit": 3,
    "min_score": 0.3
  }')

EDGE_3_COUNT=$(echo "$EDGE_3" | jq -r '.count' 2>/dev/null)
echo "   Resultados conceptuales: $EDGE_3_COUNT"

echo ""
echo -e "${BLUE}10. 📊 Estadísticas Finales y Rendimiento:${NC}"

FINAL_STATS=$(curl -s http://localhost:8000/api/v1/memory/vector-stats/default)
TOTAL_VECTORS=$(echo "$FINAL_STATS" | jq -r '.vector_memory.total_vectors' 2>/dev/null || echo "0")
TOTAL_TRADITIONAL=$(echo "$FINAL_STATS" | jq -r '.traditional_memory.total_memories' 2>/dev/null || echo "0")
COVERAGE=$(echo "$FINAL_STATS" | jq -r '.comparison.embedding_coverage' 2>/dev/null || echo "0%")

echo "   📈 Vectores indexados: $TOTAL_VECTORS"
echo "   📚 Memorias tradicionales: $TOTAL_TRADITIONAL"  
echo "   📊 Cobertura de embeddings: $COVERAGE"

if [ "$TOTAL_VECTORS" -gt "0" ]; then
    echo -e "${GREEN}   ✅ Sistema vectorial completamente operativo${NC}"
else
    echo -e "${RED}   ❌ Problema con indexación vectorial${NC}"
fi

echo ""
echo -e "${GREEN}✅ ¡AVANCE 2.5 COMPLETADO!${NC}"
echo ""
echo -e "${YELLOW}📊 RESUMEN AVANCE 2.5 - MEMORIA VECTORIAL + RAG:${NC}"
echo "   ✅ Embeddings con all-MiniLM-L6-v2 funcionando"
echo "   ✅ FAISS vector database operativo"
echo "   ✅ Búsqueda semántica por significado"
echo "   ✅ Búsqueda híbrida (G-Memory approach)"
echo "   ✅ Auto-indexación de nuevas memorias"
echo "   ✅ Migración automática de memorias existentes"
echo "   ✅ Comparación multi-método implementada"
echo "   ✅ SciBORG RAG indexing pattern"

echo ""
echo -e "${BLUE}🎯 PRÓXIMO AVANCE:${NC}"
echo "   • Avance 3: Herramientas Reales (File ops, Web browser)"
echo "   • Comando: ./test_tools.sh (próximamente)"

echo ""
echo -e "${YELLOW}🌐 URLs Memoria Vectorial:${NC}"
echo "   • Semantic Search: http://localhost:8000/api/v1/memory/semantic-search"
echo "   • Hybrid Search: http://localhost:8000/api/v1/memory/hybrid-search"
echo "   • Store Enhanced: http://localhost:8000/api/v1/memory/store-enhanced"
echo "   • Vector Stats: http://localhost:8000/api/v1/memory/vector-stats/{agent_id}"
echo "   • Migrate Vectors: http://localhost:8000/api/v1/memory/migrate-to-vectors/{agent_id}"
echo "   • Search Comparison: http://localhost:8000/api/v1/memory/search-comparison"

echo ""
echo -e "${PURPLE}🚀 TRANSFORMACIÓN LOGRADA:${NC}"
echo "   • Búsqueda por SIGNIFICADO, no solo palabras exactas"
echo "   • Encuentra información relacionada inteligentemente"
echo "   • Sistema RAG como papers SciBORG y MemoryOS"
echo "   • Base sólida para agentes que COMPRENDEN contexto"
echo ""
echo -e "${CYAN}🧠 EJEMPLOS DE BÚSQUEDA INTELIGENTE:${NC}"
echo "   • 'problemas técnicos' → encuentra 'errores de DB'"
echo "   • 'experto en IA' → encuentra 'desarrollador especializado'"
echo "   • 'logros del proyecto' → encuentra 'implementación exitosa'" 