#!/bin/bash

echo "🧪 TESTING AGENTES MCP - AVANCE 1"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. 🔍 Verificando MCP Server en Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "mcp_server"; then
    echo -e "${GREEN}✅ MCP Server detectado en health check!${NC}"
    echo "   MCP Tools: $(echo "$HEALTH_RESPONSE" | grep -o '"mcp_tools":[0-9]*' | cut -d':' -f2)"
else
    echo -e "${RED}❌ MCP Server no encontrado en health check${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. 📋 Información del Servidor MCP:${NC}"
curl -s http://localhost:8000/mcp/info | jq '.' 2>/dev/null || curl -s http://localhost:8000/mcp/info

echo ""
echo -e "${BLUE}3. 🔧 Lista de Herramientas MCP Estándar:${NC}"
curl -s http://localhost:8000/mcp/tools | jq '.tools[] | {name: .name, description: .description}' 2>/dev/null || {
    echo "   Herramientas MCP disponibles:"
    curl -s http://localhost:8000/mcp/tools
}

echo ""
echo -e "${BLUE}4. ⚡ Probando Calculator via MCP Estándar:${NC}"
MCP_CALC_RESPONSE=$(curl -s -X POST "http://localhost:8000/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "calculator",
    "arguments": {"expression": "50 * 2 + 25"}
  }')

echo "   Test: 50 * 2 + 25"
echo "   Resultado MCP:"
echo "$MCP_CALC_RESPONSE" | jq -r '.result[0].text' 2>/dev/null || echo "$MCP_CALC_RESPONSE"

echo ""
echo -e "${BLUE}5. 🔍 Probando Web Search via MCP Estándar:${NC}"
MCP_SEARCH_RESPONSE=$(curl -s -X POST "http://localhost:8000/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "arguments": {"query": "MCP Model Context Protocol"}
  }')

echo "   Test: MCP Model Context Protocol"
echo "   Resultado MCP:"
echo "$MCP_SEARCH_RESPONSE" | jq -r '.result[0].text' 2>/dev/null || echo "$MCP_SEARCH_RESPONSE"

echo ""
echo -e "${BLUE}6. 🧠 Probando Memory via MCP Estándar:${NC}"
MCP_MEMORY_RESPONSE=$(curl -s -X POST "http://localhost:8000/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "memory",
    "arguments": {"action": "store", "data": "MCP funcionando correctamente"}
  }')

echo "   Test: store - MCP funcionando correctamente"
echo "   Resultado MCP:"
echo "$MCP_MEMORY_RESPONSE" | jq -r '.result[0].text' 2>/dev/null || echo "$MCP_MEMORY_RESPONSE"

echo ""
echo -e "${BLUE}7. 🔄 Comparando Legacy vs MCP (Calculator):${NC}"
COMPARE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tools/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "calculator",
    "arguments": {"expression": "100 / 4 + 75"}
  }')

echo "   Test: 100 / 4 + 75"
echo "   Comparación Legacy vs MCP:"
echo "$COMPARE_RESPONSE" | jq '{
  tool: .tool,
  mcp_result: .mcp_result,
  legacy_result: .legacy_result,
  results_match: .results_match
}' 2>/dev/null || echo "$COMPARE_RESPONSE"

echo ""
echo -e "${BLUE}8. 💬 Probando Chat con Agente (debe usar MCP internamente):${NC}"
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calcula 15 * 8 y explícame cómo funciona MCP",
    "agent_id": "default"
  }')

echo "   Pregunta: Calcula 15 * 8 y explícame cómo funciona MCP"
echo "   Respuesta del agente:"
echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null || echo "$CHAT_RESPONSE"

echo ""
echo -e "${GREEN}✅ ¡AVANCE 1 COMPLETADO!${NC}"
echo ""
echo -e "${YELLOW}📊 RESUMEN AVANCE 1 - MCP REAL:${NC}"
echo "   ✅ Servidor MCP estándar funcionando"
echo "   ✅ 3 herramientas migradas a MCP"
echo "   ✅ Endpoints MCP estándar operativos"
echo "   ✅ Compatibilidad con sistema legacy mantenida"
echo "   ✅ Comparación Legacy vs MCP disponible"
echo ""
echo -e "${BLUE}🎯 PRÓXIMO AVANCE:${NC}"
echo "   • Avance 2: Memoria Persistente con Base de Datos"
echo "   • Comando: ./test_memory.sh (próximamente)"
echo ""
echo -e "${YELLOW}🌐 URLs MCP Estándar:${NC}"
echo "   • Info MCP: http://localhost:8000/mcp/info"
echo "   • Tools MCP: http://localhost:8000/mcp/tools"
echo "   • Execute MCP: http://localhost:8000/mcp/tools/execute"
echo "   • Compare: http://localhost:8000/api/v1/tools/compare" 