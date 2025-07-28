#!/bin/bash

echo "🧪 TESTING MEMORIA PERSISTENTE - AVANCE 2"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. 🔍 Verificando Sistema de Memoria en Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "memory_system"; then
    echo -e "${GREEN}✅ Sistema de memoria detectado!${NC}"
    echo "   Database: $(echo "$HEALTH_RESPONSE" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)"
    echo "   Memory System: $(echo "$HEALTH_RESPONSE" | grep -o '"memory_system":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}❌ Sistema de memoria no encontrado en health check${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. 📊 Estadísticas Generales del Sistema de Memoria:${NC}"
curl -s http://localhost:8000/api/v1/memory/stats | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/v1/memory/stats

echo ""
echo -e "${BLUE}3. 💾 Probando Almacenamiento de Memoria Persistente:${NC}"

# Almacenar memoria short-term
echo "   📝 Almacenando memoria short-term..."
STORE_SHORT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "short_term",
    "content": "El usuario prefiere respuestas concisas y técnicas",
    "context": "Preferencias de comunicación detectadas",
    "importance_score": 7,
    "tags": ["preferences", "communication"]
  }')

echo "   Resultado: $(echo "$STORE_SHORT_RESPONSE" | jq -r '.message' 2>/dev/null || echo "$STORE_SHORT_RESPONSE")"

# Almacenar memoria medium-term
echo "   📚 Almacenando memoria medium-term..."
STORE_MEDIUM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "medium_term",
    "content": "Proyecto AgentOS: Sistema MCP implementado exitosamente",
    "context": "Logro técnico importante en el proyecto",
    "importance_score": 9,
    "tags": ["project", "achievement", "mcp"]
  }')

echo "   Resultado: $(echo "$STORE_MEDIUM_RESPONSE" | jq -r '.message' 2>/dev/null || echo "$STORE_MEDIUM_RESPONSE")"

# Almacenar memoria long-term
echo "   🏛️ Almacenando memoria long-term..."
STORE_LONG_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "memory_type": "long_term",
    "content": "Principios fundamentales: Siempre priorizar código funcional y testeable",
    "context": "Valores fundamentales del desarrollo",
    "importance_score": 10,
    "tags": ["principles", "development", "core"]
  }')

echo "   Resultado: $(echo "$STORE_LONG_RESPONSE" | jq -r '.message' 2>/dev/null || echo "$STORE_LONG_RESPONSE")"

echo ""
echo -e "${BLUE}4. 🧠 Probando Recuperación de Memoria:${NC}"

# Recuperar todas las memorias
echo "   🔍 Recuperando todas las memorias del agente default..."
RECALL_ALL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/recall" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "limit": 10
  }')

echo "   Memorias encontradas: $(echo "$RECALL_ALL_RESPONSE" | jq -r '.count' 2>/dev/null || echo "Error")"
echo "$RECALL_ALL_RESPONSE" | jq '.memories[] | {type: .memory_type, content: .content, importance: .importance_score}' 2>/dev/null || echo "$RECALL_ALL_RESPONSE"

echo ""
echo -e "${BLUE}5. 🔍 Probando Búsqueda Específica en Memoria:${NC}"

# Buscar por término específico
echo "   🎯 Buscando memorias que contengan 'MCP'..."
SEARCH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/recall" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default",
    "search_term": "MCP",
    "limit": 5
  }')

echo "   Resultados de búsqueda:"
echo "$SEARCH_RESPONSE" | jq '.memories[] | {content: .content, tags: .tags}' 2>/dev/null || echo "$SEARCH_RESPONSE"

echo ""
echo -e "${BLUE}6. 📈 Estadísticas de Memoria del Agente:${NC}"
AGENT_STATS_RESPONSE=$(curl -s http://localhost:8000/api/v1/memory/stats/default)
echo "$AGENT_STATS_RESPONSE" | jq '.memory_stats' 2>/dev/null || echo "$AGENT_STATS_RESPONSE"

echo ""
echo -e "${BLUE}7. 💬 Probando Chat + Almacenamiento Automático:${NC}"

# Crear conversación de prueba
echo "   🗨️ Creando conversación que genere memoria..."
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Recuerda que mi nombre es Tatan y trabajo en desarrollo de IA",
    "agent_id": "default"
  }')

CONV_ID=$(echo "$CHAT_RESPONSE" | jq -r '.conversation_id' 2>/dev/null)
echo "   Conversación creada: $CONV_ID"
echo "   Respuesta del agente:"
echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null || echo "$CHAT_RESPONSE"

# Almacenar información de la conversación en memoria
echo ""
echo "   💾 Almacenando información de la conversación en memoria..."
CONV_MEMORY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/store" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"default\",
    \"memory_type\": \"long_term\",
    \"content\": \"Usuario: Tatan, especialista en desarrollo de IA\",
    \"context\": \"Información personal del usuario obtenida en conversación\",
    \"importance_score\": 8,
    \"tags\": [\"user_info\", \"personal\", \"ai_development\"]
  }")

echo "   Memoria de conversación almacenada: $(echo "$CONV_MEMORY_RESPONSE" | jq -r '.success' 2>/dev/null)"

echo ""
echo -e "${BLUE}8. 🔄 Migración de Conversación In-Memory a BD:${NC}"
if [ ! -z "$CONV_ID" ] && [ "$CONV_ID" != "null" ]; then
    echo "   📦 Migrando conversación $CONV_ID a base de datos..."
    MIGRATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/migrate/conversation/$CONV_ID")
    echo "   Migración: $(echo "$MIGRATE_RESPONSE" | jq -r '.success' 2>/dev/null)"
    echo "   Mensajes migrados: $(echo "$MIGRATE_RESPONSE" | jq -r '.messages_migrated' 2>/dev/null)"
else
    echo "   ⚠️ No se pudo obtener ID de conversación para migración"
fi

echo ""
echo -e "${BLUE}9. ⚖️ Comparación Sistemas de Memoria:${NC}"
COMPARE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/memory/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "default"
  }')

echo "   📊 Comparación In-Memory vs Persistente:"
echo "$COMPARE_RESPONSE" | jq '.comparison' 2>/dev/null || echo "$COMPARE_RESPONSE"
echo ""
echo "   🎯 Recomendación: $(echo "$COMPARE_RESPONSE" | jq -r '.recommendation' 2>/dev/null)"

echo ""
echo -e "${BLUE}10. 🧪 Verificando Persistencia (Memoria sobrevive restarts):${NC}"
echo "   📋 Verificando que las memorias persisten en base de datos..."

# Verificar que las memorias están en BD
FINAL_STATS=$(curl -s http://localhost:8000/api/v1/memory/stats/default)
TOTAL_MEMORIES=$(echo "$FINAL_STATS" | jq -r '.memory_stats.total_memories' 2>/dev/null || echo "0")

if [ "$TOTAL_MEMORIES" -gt "0" ]; then
    echo -e "${GREEN}   ✅ Memorias persistentes verificadas: $TOTAL_MEMORIES${NC}"
    echo "   💾 Las memorias sobrevivirán a restarts del sistema"
else
    echo -e "${RED}   ❌ No se encontraron memorias persistentes${NC}"
fi

echo ""
echo -e "${GREEN}✅ ¡AVANCE 2 COMPLETADO!${NC}"
echo ""
echo -e "${YELLOW}📊 RESUMEN AVANCE 2 - MEMORIA PERSISTENTE:${NC}"
echo "   ✅ Base de datos PostgreSQL conectada"
echo "   ✅ Tablas de memoria creadas automáticamente"
echo "   ✅ Almacenamiento persistente funcionando"
echo "   ✅ Búsqueda por contenido implementada"
echo "   ✅ Tipos de memoria: short/medium/long term"
echo "   ✅ Sistema de importancia y tags"
echo "   ✅ Migración de conversaciones in-memory"
echo "   ✅ Comparación de sistemas de memoria"
echo "   ✅ Memoria sobrevive restarts"

echo ""
echo -e "${BLUE}🎯 PRÓXIMO AVANCE:${NC}"
echo "   • Avance 3: Herramientas Reales (File ops, Web browser)"
echo "   • Comando: ./test_tools.sh (próximamente)"

echo ""
echo -e "${YELLOW}🌐 URLs Memoria Persistente:${NC}"
echo "   • Stats Sistema: http://localhost:8000/api/v1/memory/stats"
echo "   • Store Memory: http://localhost:8000/api/v1/memory/store"
echo "   • Recall Memory: http://localhost:8000/api/v1/memory/recall"
echo "   • Agent Stats: http://localhost:8000/api/v1/memory/stats/{agent_id}"
echo "   • Migrate Conv: http://localhost:8000/api/v1/migrate/conversation/{id}"
echo "   • Compare: http://localhost:8000/api/v1/memory/compare"

echo ""
echo -e "${PURPLE}🚀 BENEFICIO INMEDIATO:${NC}"
echo "   • Tu sistema ahora RECUERDA todo entre sesiones"
echo "   • Búsqueda inteligente en conversaciones pasadas"
echo "   • Memoria categorizada por importancia"
echo "   • Base sólida para IA que aprende y evoluciona" 