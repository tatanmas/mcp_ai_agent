#!/bin/bash

echo "🧪 Probando AgentOS Backend"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1. 🔍 Verificando si el backend está funcionando..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend está funcionando!${NC}"
else
    echo -e "${RED}❌ Backend no responde. ¿Está ejecutándose?${NC}"
    echo "   Ejecuta: docker-compose up -d backend"
    exit 1
fi

echo ""
echo "2. 📋 Información del sistema:"
echo "   API: $(curl -s http://localhost:8000/ | grep -o '"message":"[^"]*"' | cut -d'"' -f4)"

echo ""
echo "3. 🤖 Probando lista de agentes:"
curl -s http://localhost:8000/api/v1/agents | jq '.agents[] | {id: .id, name: .name, tools: .tools}' 2>/dev/null || {
    echo "   Instalando jq para mejor formato..."
    curl -s http://localhost:8000/api/v1/agents
}

echo ""
echo "4. 💬 Probando chat con el Asistente General:"
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, calcula 25 * 4 + 10",
    "agent_id": "default"
  }')

echo "   Pregunta: Hola, calcula 25 * 4 + 10"
echo "   Respuesta del agente:"
echo "$RESPONSE" | jq -r '.response' 2>/dev/null || echo "$RESPONSE"

echo ""
echo "5. 🔬 Probando chat con el Investigador IA:"
RESPONSE2=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Busca información sobre inteligencia artificial",
    "agent_id": "researcher"
  }')

echo "   Pregunta: Busca información sobre inteligencia artificial"
echo "   Respuesta del investigador:"
echo "$RESPONSE2" | jq -r '.response' 2>/dev/null || echo "$RESPONSE2"

echo ""
echo "6. 💻 Probando chat con el Desarrollador IA:"
RESPONSE3=$(curl -s -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explica qué es una función Python",
    "agent_id": "coder"
  }')

echo "   Pregunta: Explica qué es una función Python"
echo "   Respuesta del desarrollador:"
echo "$RESPONSE3" | jq -r '.response' 2>/dev/null || echo "$RESPONSE3"

echo ""
echo -e "${GREEN}✅ ¡Pruebas completadas!${NC}"
echo ""
echo "🌐 Para más pruebas:"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Agentes: http://localhost:8000/api/v1/agents"
echo ""
echo "📝 Ejemplo de uso con curl:"
echo '   curl -X POST "http://localhost:8000/api/v1/chat" \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"message\": \"Tu pregunta aquí\", \"agent_id\": \"default\"}"' 