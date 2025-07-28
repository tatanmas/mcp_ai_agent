#!/bin/bash

echo "🧪 AGENTOS V10 - TEST COMPLETO DEL SISTEMA"
echo "=========================================="
echo ""

# Verificar que el servidor esté corriendo
echo "🔍 Verificando que el servidor esté corriendo..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Servidor detectado en http://localhost:8000"
else
    echo "❌ Servidor no encontrado en http://localhost:8000"
    echo "   Asegúrate de que el contenedor Docker esté corriendo:"
    echo "   docker-compose up -d"
    exit 1
fi

echo ""
echo "🚀 Ejecutando tests completos del sistema..."
echo ""

# Ejecutar el test completo
python3 test_complete_system_v10.py

echo ""
echo "📋 RESUMEN DE LA EJECUCIÓN:"
echo "=========================="
echo "✅ Test completado"
echo "📊 Revisa los resultados arriba para verificar el estado del sistema"
echo ""
echo "🎯 VALIDACIONES SEGÚN DOCS10.MD:"
echo "- Integración MCP completa"
echo "- Agentes cognitivos especializados (3 agentes)"
echo "- Herramientas reales vía MCP"
echo "- API modular (V1 + V2)"
echo "- Estado persistente"
echo "- Control granular"
echo ""
echo "🔧 Si hay errores, verifica:"
echo "1. Que el contenedor Docker esté corriendo"
echo "2. Que el servidor esté accesible en http://localhost:8000"
echo "3. Que todas las dependencias estén instaladas"
echo "4. Los logs del contenedor: docker logs mvp_ai_agent-backend-1" 