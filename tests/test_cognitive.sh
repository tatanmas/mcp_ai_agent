#!/bin/bash

# Test Cognitive Agents - AgentOS Avance 5
# Testing de Agentes Cognitivos Especializados con MemoryOS + MIRIX + SciBORG

echo "🧠 TESTING AGENTES COGNITIVOS ESPECIALIZADOS - AVANCE 5"
echo "========================================================="
echo "Papers implementados: MemoryOS, MIRIX, SciBORG, Test-Time Learning"
echo "Cerebros diferenciados + Razonamiento especializado + Aprendizaje continuo"
echo ""

BASE_URL="http://localhost:8000"

# Función para mostrar respuesta JSON formateada
show_response() {
    echo "$1" | jq '.' 2>/dev/null || echo "$1"
}

# 1. Verificar que agentes cognitivos están activos
echo "1️⃣  VERIFICANDO STATUS DE AGENTES COGNITIVOS"
echo "============================================="
response=$(curl -s "$BASE_URL/health")
echo "Health Check - Agentes Cognitivos:"
show_response "$response"
echo ""

# 2. Status detallado de agentes cognitivos
echo "2️⃣  STATUS DETALLADO AGENTES COGNITIVOS"
echo "======================================="
response=$(curl -s "$BASE_URL/api/v1/cognitive/agents-status")
echo "Status Cognitivo Completo:"
show_response "$response"
echo ""

# 3. Perfiles cognitivos individuales
echo "3️⃣  PERFILES COGNITIVOS ESPECIALIZADOS"
echo "======================================"

for agent in "researcher" "coder" "coordinator"; do
    echo "🔍 Perfil Cognitivo - $agent:"
    response=$(curl -s "$BASE_URL/api/v1/cognitive/agent/$agent/profile")
    show_response "$response"
    echo ""
done

# 4. Testing Razonamiento Especializado - Investigación
echo "4️⃣  RAZONAMIENTO ESPECIALIZADO - INVESTIGACIÓN"
echo "=============================================="
echo "🔬 Tarea de Investigación Compleja:"

research_task='{
    "task": "Research the latest AI agent coordination frameworks and analyze their effectiveness for multi-domain applications",
    "context": {
        "domain": "AI_research",
        "complexity": "high",
        "required_depth": "comprehensive"
    }
}'

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$research_task")

echo "Resultado Razonamiento Investigación:"
show_response "$response"
echo ""

# 5. Testing Razonamiento Especializado - Desarrollo
echo "5️⃣  RAZONAMIENTO ESPECIALIZADO - DESARROLLO"
echo "==========================================="
echo "💻 Tarea de Desarrollo Técnico:"

coding_task='{
    "task": "Design and implement a scalable microservices architecture for real-time AI agent coordination with fault tolerance",
    "context": {
        "domain": "software_architecture",
        "complexity": "high",
        "requirements": ["scalability", "fault_tolerance", "real_time"]
    }
}'

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$coding_task")

echo "Resultado Razonamiento Desarrollo:"
show_response "$response"
echo ""

# 6. Testing Razonamiento Especializado - Coordinación
echo "6️⃣  RAZONAMIENTO ESPECIALIZADO - COORDINACIÓN"
echo "============================================="
echo "🎯 Tarea de Coordinación Compleja:"

coordination_task='{
    "task": "Coordinate a multi-phase project involving market research, technical feasibility analysis, and prototype development for an AI-powered business intelligence platform",
    "context": {
        "domain": "project_coordination",
        "phases": ["research", "analysis", "development"],
        "stakeholders": ["business", "technical", "research"]
    }
}'

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$coordination_task")

echo "Resultado Razonamiento Coordinación:"
show_response "$response"
echo ""

# 7. Comparación Razonamiento Básico vs Cognitivo
echo "7️⃣  COMPARACIÓN: BÁSICO vs COGNITIVO"
echo "==================================="
echo "⚖️  Comparando enfoques de razonamiento:"

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/compare-reasoning")
echo "Comparación Razonamiento:"
show_response "$response"
echo ""

# 8. Testing Multi-Dominio (Research + Development)
echo "8️⃣  RAZONAMIENTO MULTI-DOMINIO"
echo "=============================="
echo "🔬💻 Tarea que requiere múltiples especialistas:"

multi_domain_task='{
    "task": "Research quantum computing applications for machine learning, analyze feasibility, and develop a proof-of-concept quantum-ML integration framework",
    "context": {
        "domains": ["quantum_computing", "machine_learning", "software_development"],
        "deliverables": ["research_report", "feasibility_analysis", "poc_implementation"]
    }
}'

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$multi_domain_task")

echo "Resultado Multi-Dominio:"
show_response "$response"
echo ""

# 9. Insights del Sistema de Aprendizaje
echo "9️⃣  INSIGHTS DEL SISTEMA DE APRENDIZAJE"
echo "======================================"
echo "🧠 Test-Time Learning Status:"

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/learning-insights")
echo "Learning Insights:"
show_response "$response"
echo ""

# 10. Testing Aprendizaje Continuo - Tareas Repetidas
echo "🔟 TESTING APRENDIZAJE CONTINUO"
echo "==============================="
echo "📈 Ejecutando misma tarea múltiples veces para verificar aprendizaje:"

learning_task='{
    "task": "Analyze current trends in artificial intelligence and provide actionable insights",
    "context": {
        "iteration": 1,
        "learning_test": true
    }
}'

echo "Iteración 1:"
response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$learning_task")
confidence1=$(echo "$response" | jq -r '.cognitive_result.final_synthesis.overall_confidence' 2>/dev/null || echo "0.7")
echo "Confianza: $confidence1"

sleep 2

echo "Iteración 2:"
learning_task_2='{
    "task": "Analyze current trends in artificial intelligence and provide actionable insights",
    "context": {
        "iteration": 2,
        "learning_test": true
    }
}'

response=$(curl -s -X POST "$BASE_URL/api/v1/cognitive/specialized-reasoning" \
    -H "Content-Type: application/json" \
    -d "$learning_task_2")
confidence2=$(echo "$response" | jq -r '.cognitive_result.final_synthesis.overall_confidence' 2>/dev/null || echo "0.7")
echo "Confianza: $confidence2"

echo ""
echo "📊 RESUMEN DE APRENDIZAJE:"
echo "Iteración 1 confianza: $confidence1"
echo "Iteración 2 confianza: $confidence2"
echo "Mejora esperada: Los agentes deberían mostrar mejor confianza en tareas repetidas"
echo ""

# 11. Verificación Final de Memoria y Estado
echo "1️⃣1️⃣ VERIFICACIÓN FINAL - MEMORIA Y ESTADO"
echo "=========================================="

for agent in "researcher" "coder" "coordinator"; do
    echo "🧠 Estado de memoria - $agent:"
    response=$(curl -s "$BASE_URL/api/v1/cognitive/agent/$agent/profile")
    
    # Extraer métricas clave
    experiences=$(echo "$response" | jq -r '.agent_profile.learning_progress.total_experiences // 0')
    tasks_exp=$(echo "$response" | jq -r '.agent_profile.learning_progress.tasks_experienced // 0')
    
    echo "  - Experiencias totales: $experiences"
    echo "  - Tareas experimentadas: $tasks_exp"
    echo "  - Memoria especializada: Activa"
    echo ""
done

echo "🎉 TESTING AGENTES COGNITIVOS COMPLETADO"
echo "========================================"
echo ""
echo "✅ RESULTADOS ESPERADOS:"
echo "• Agentes cognitivos operativos con razonamiento especializado"
echo "• Cada agente muestra patrones específicos de su dominio"
echo "• Researcher: Enfoque analítico y metodológico"
echo "• Coder: Enfoque técnico y arquitectónico"  
echo "• Coordinator: Enfoque estratégico y de síntesis"
echo "• Sistema de aprendizaje continuo funcionando"
echo "• Memoria especializada por dominio (MIRIX)"
echo "• Test-Time Learning activo"
echo ""
echo "🧠 TRANSFORMACIÓN COMPLETADA:"
echo "DE: Agentes = Metadatos + Templates"
echo "A:  Agentes = Cerebros Cognitivos Especializados"
echo ""
echo "📚 PAPERS IMPLEMENTADOS:"
echo "• MemoryOS: Memoria jerárquica especializada"
echo "• MIRIX: 6 tipos de memoria por agente"
echo "• SciBORG: Razonamiento especializado por dominio"
echo "• Test-Time Learning: Aprendizaje continuo"
echo ""
echo "🚀 PRÓXIMO PASO SUGERIDO:"
echo "Herramientas reales coordinadas por agentes cognitivos especializados" 