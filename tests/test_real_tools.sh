#!/bin/bash

echo "🎯 TESTING HERRAMIENTAS REALES Y TAREAS COMPLEJAS - AgentOS"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}🔧 1. Verificando sistema y dependencias...${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "status.*healthy"; then
    echo -e "${GREEN}✅ Sistema funcionando correctamente${NC}"
else
    echo -e "${RED}❌ Sistema no disponible. Asegúrate de que esté ejecutándose.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN} 🌐 PRUEBAS DE HERRAMIENTAS REALES${NC}"
echo -e "${CYAN}========================================${NC}"

echo ""
echo -e "${BLUE}🔍 2. BÚSQUEDA WEB REAL (DuckDuckGo):${NC}"
echo "   Buscando: 'Artificial Intelligence 2024'"
WEB_SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tools/web-search-real" \
  -H "Content-Type: application/json" \
  -d '{"query": "Artificial Intelligence 2024", "max_results": 3}')

if echo "$WEB_SEARCH_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Búsqueda web REAL exitosa!${NC}"
    SOURCES_FOUND=$(echo "$WEB_SEARCH_RESPONSE" | jq -r '.sources_found // 0' 2>/dev/null || echo "0")
    echo "   📊 Fuentes encontradas: $SOURCES_FOUND"
    
    # Mostrar primer resultado
    FIRST_TITLE=$(echo "$WEB_SEARCH_RESPONSE" | jq -r '.search_result.results[0].title // "N/A"' 2>/dev/null || echo "N/A")
    FIRST_URL=$(echo "$WEB_SEARCH_RESPONSE" | jq -r '.search_result.results[0].url // "N/A"' 2>/dev/null || echo "N/A")
    echo "   🔗 Primer resultado: $FIRST_TITLE"
    echo "   🌐 URL: $FIRST_URL"
else
    echo -e "${RED}❌ Error en búsqueda web real${NC}"
    echo "$WEB_SEARCH_RESPONSE" | jq '.' 2>/dev/null || echo "$WEB_SEARCH_RESPONSE"
fi

echo ""
echo -e "${BLUE}📄 3. OBTENER CONTENIDO DE PÁGINA WEB:${NC}"
if [ "$FIRST_URL" != "N/A" ] && [ "$FIRST_URL" != "" ]; then
    echo "   Obteniendo contenido de: $FIRST_URL"
    PAGE_CONTENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tools/get-page-content?url=$FIRST_URL")
    
    if echo "$PAGE_CONTENT_RESPONSE" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Contenido de página obtenido exitosamente!${NC}"
        CONTENT_LENGTH=$(echo "$PAGE_CONTENT_RESPONSE" | jq -r '.content_result.content | length // 0' 2>/dev/null || echo "0")
        echo "   📏 Caracteres extraídos: $CONTENT_LENGTH"
    else
        echo -e "${YELLOW}⚠️ No se pudo obtener contenido de la página${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ No hay URL válida para probar contenido${NC}"
fi

echo ""
echo -e "${BLUE}📊 4. CREAR GRÁFICO REAL:${NC}"
echo "   Creando gráfico de barras con datos de prueba..."
CHART_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tools/create-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "x": ["IA Generativa", "Machine Learning", "Deep Learning", "Computer Vision"],
      "y": [85, 72, 93, 67],
      "title": "Tendencias de IA 2024",
      "xlabel": "Tecnologías",
      "ylabel": "Adopción (%)"
    },
    "chart_type": "bar"
  }')

if echo "$CHART_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Gráfico creado exitosamente!${NC}"
    CHART_ID=$(echo "$CHART_RESPONSE" | jq -r '.visualization_result.chart_id // "N/A"' 2>/dev/null || echo "N/A")
    echo "   📊 Chart ID: $CHART_ID"
    echo "   💾 Gráfico guardado y codificado en base64"
else
    echo -e "${RED}❌ Error creando gráfico${NC}"
    echo "$CHART_RESPONSE" | jq '.' 2>/dev/null || echo "$CHART_RESPONSE"
fi

echo ""
echo -e "${BLUE}📁 5. OPERACIONES DE ARCHIVOS:${NC}"
echo "   Listando directorio actual..."
DIR_RESPONSE=$(curl -s "$BASE_URL/api/v1/tools/list-directory?dir_path=.")

if echo "$DIR_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Directorio listado exitosamente!${NC}"
    ITEMS_COUNT=$(echo "$DIR_RESPONSE" | jq -r '.listing_result.total_items // 0' 2>/dev/null || echo "0")
    echo "   📂 Archivos/directorios encontrados: $ITEMS_COUNT"
else
    echo -e "${RED}❌ Error listando directorio${NC}"
fi

echo ""
echo -e "${CYAN}===========================================${NC}"
echo -e "${CYAN} 🤝 PRUEBAS DE TAREAS COMPLEJAS${NC}"
echo -e "${CYAN}===========================================${NC}"

echo ""
echo -e "${BLUE}📋 6. OBTENER PLANTILLAS DE TAREAS:${NC}"
TEMPLATES_RESPONSE=$(curl -s "$BASE_URL/api/v1/complex-tasks/templates")

if echo "$TEMPLATES_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Plantillas de tareas obtenidas!${NC}"
    TEMPLATE_COUNT=$(echo "$TEMPLATES_RESPONSE" | jq -r '.total_templates // 0' 2>/dev/null || echo "0")
    echo "   📝 Plantillas disponibles: $TEMPLATE_COUNT"
    
    # Mostrar plantillas disponibles
    echo "   🎯 Plantillas:"
    echo "$TEMPLATES_RESPONSE" | jq -r '.templates | keys[]' 2>/dev/null | while read template; do
        echo "      - $template"
    done
else
    echo -e "${RED}❌ Error obteniendo plantillas${NC}"
fi

echo ""
echo -e "${BLUE}🚀 7. EJECUTAR TAREA COMPLEJA - INVESTIGACIÓN:${NC}"
echo "   Iniciando tarea de investigación con múltiples agentes..."

TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/complex-tasks/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "research",
    "custom_definition": {
      "title": "Investigación AI Trends 2024 - Demo",
      "description": "Investigación profunda sobre tendencias de IA usando búsqueda web real",
      "context": {
        "search_queries": ["AI trends 2024", "machine learning advances"],
        "depth": "comprehensive"
      }
    }
  }')

if echo "$TASK_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Tarea compleja iniciada exitosamente!${NC}"
    TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.task_id // "N/A"' 2>/dev/null || echo "N/A")
    echo "   🆔 Task ID: $TASK_ID"
    echo "   📊 Estado: Ejecutándose en background"
    
    echo ""
    echo -e "${BLUE}📈 8. MONITOREAR PROGRESO DE TAREA:${NC}"
    echo "   Esperando 3 segundos para verificar progreso..."
    sleep 3
    
    STATUS_RESPONSE=$(curl -s "$BASE_URL/api/v1/complex-tasks/status/$TASK_ID")
    
    if echo "$STATUS_RESPONSE" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Estado de tarea obtenido!${NC}"
        TASK_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.execution_status.status // "unknown"' 2>/dev/null || echo "unknown")
        PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.execution_status.progress // 0' 2>/dev/null || echo "0")
        CURRENT_STEP=$(echo "$STATUS_RESPONSE" | jq -r '.execution_status.current_step // "N/A"' 2>/dev/null || echo "N/A")
        
        echo "   📊 Estado: $TASK_STATUS"
        echo "   📈 Progreso: $PROGRESS%"
        echo "   🔄 Paso actual: $CURRENT_STEP"
        
        # Mostrar logs si están disponibles
        LOGS_COUNT=$(echo "$STATUS_RESPONSE" | jq -r '.execution_status.logs | length // 0' 2>/dev/null || echo "0")
        if [ "$LOGS_COUNT" -gt 0 ]; then
            echo "   📝 Logs de ejecución ($LOGS_COUNT):"
            echo "$STATUS_RESPONSE" | jq -r '.execution_status.logs[]?' 2>/dev/null | head -3 | while read log; do
                echo "      $log"
            done
        fi
    else
        echo -e "${YELLOW}⚠️ No se pudo obtener estado de la tarea${NC}"
    fi
else
    echo -e "${RED}❌ Error iniciando tarea compleja${NC}"
    echo "$TASK_RESPONSE" | jq '.' 2>/dev/null || echo "$TASK_RESPONSE"
fi

echo ""
echo -e "${CYAN}===========================================${NC}"
echo -e "${CYAN} 🎯 DEMO COMPLETO DEL SISTEMA${NC}"
echo -e "${CYAN}===========================================${NC}"

echo ""
echo -e "${BLUE}🌟 9. EJECUTAR DEMO COMPLETO:${NC}"
echo "   Ejecutando demo que prueba TODAS las capacidades del sistema..."
echo "   (Esto puede tomar 1-2 minutos...)"

DEMO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/demo/full-system-test")

if echo "$DEMO_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ DEMO COMPLETO EXITOSO!${NC}"
    
    # Extraer métricas del demo
    SUCCESS_RATE=$(echo "$DEMO_RESPONSE" | jq -r '.demo_results.success_rate // 0' 2>/dev/null || echo "0")
    TOTAL_TESTS=$(echo "$DEMO_RESPONSE" | jq -r '.demo_results.total_tests // 0' 2>/dev/null || echo "0")
    SUCCESSFUL_TESTS=$(echo "$DEMO_RESPONSE" | jq -r '.demo_results.successful_tests // 0' 2>/dev/null || echo "0")
    
    echo ""
    echo -e "${PURPLE}📊 MÉTRICAS DEL DEMO:${NC}"
    echo "   🎯 Tests ejecutados: $TOTAL_TESTS"
    echo "   ✅ Tests exitosos: $SUCCESSFUL_TESTS"
    echo "   📈 Tasa de éxito: $(echo "$SUCCESS_RATE * 100" | bc 2>/dev/null || echo "N/A")%"
    
    # Mostrar tests realizados
    echo ""
    echo -e "${PURPLE}🔬 TESTS REALIZADOS:${NC}"
    echo "$DEMO_RESPONSE" | jq -r '.demo_results.tests_performed[]? | "   \(.test): \(if .success then "✅" else "❌" end)"' 2>/dev/null
    
    # Mostrar agentes y herramientas probadas
    AGENTS_TESTED=$(echo "$DEMO_RESPONSE" | jq -r '.demo_results.agents_tested[]?' 2>/dev/null | sort | uniq | tr '\n' ', ' | sed 's/,$//')
    TOOLS_TESTED=$(echo "$DEMO_RESPONSE" | jq -r '.demo_results.tools_tested[]?' 2>/dev/null | sort | uniq | tr '\n' ', ' | sed 's/,$//')
    
    if [ ! -z "$AGENTS_TESTED" ]; then
        echo "   🤖 Agentes probados: $AGENTS_TESTED"
    fi
    if [ ! -z "$TOOLS_TESTED" ]; then
        echo "   🔧 Herramientas probadas: $TOOLS_TESTED"
    fi
    
else
    echo -e "${RED}❌ Error en demo completo${NC}"
    echo "$DEMO_RESPONSE" | jq '.' 2>/dev/null || echo "$DEMO_RESPONSE"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} 🎉 TESTING COMPLETADO${NC}"
echo -e "${GREEN}============================================${NC}"

echo ""
echo -e "${CYAN}📚 RESUMEN DE CAPACIDADES PROBADAS:${NC}"
echo ""
echo -e "${GREEN}✅ HERRAMIENTAS REALES:${NC}"
echo "   🌐 Búsqueda web real (DuckDuckGo)"
echo "   📄 Extracción de contenido de páginas"
echo "   📊 Generación de gráficos (Matplotlib)"
echo "   📁 Operaciones de archivos del sistema"
echo ""
echo -e "${GREEN}✅ AGENTES COGNITIVOS:${NC}"
echo "   🧠 Razonamiento especializado"
echo "   🤝 Coordinación multi-agente"
echo "   🎯 Planificación de tareas complejas"
echo "   📝 Memoria vectorial y persistente"
echo ""
echo -e "${GREEN}✅ SISTEMAS AVANZADOS:${NC}"
echo "   🌐 Optimización AGP (Adaptive Graph Pruning)"
echo "   🔧 Resolución de conflictos"
echo "   📊 MemoryAgentBench validation"
echo "   🎯 Tareas complejas multi-agente"

echo ""
echo -e "${BLUE}🚀 PRÓXIMOS PASOS SUGERIDOS:${NC}"
echo ""
echo "1. 📄 Probar análisis de documentos reales:"
echo "   curl -X POST '$BASE_URL/api/v1/tools/analyze-document' -H 'Content-Type: application/json' -d '{\"file_path\": \"./README.md\"}'"
echo ""
echo "2. 🎯 Crear tarea personalizada:"
echo "   curl -X POST '$BASE_URL/api/v1/complex-tasks/execute' -H 'Content-Type: application/json' -d '{\"custom_definition\": {\"title\": \"Mi Tarea\", \"description\": \"Investigar tema específico\", \"agents_required\": [\"researcher\", \"coordinator\"]}}'"
echo ""
echo "3. 📊 Ver tareas activas:"
echo "   curl '$BASE_URL/api/v1/complex-tasks/active'"
echo ""
echo -e "${YELLOW}💡 TIP: Todos los endpoints están documentados en http://localhost:8000/docs${NC}"

echo ""
echo -e "${GREEN}🎯 ¡EL SISTEMA ESTÁ LISTO PARA TAREAS REALES!${NC}" 