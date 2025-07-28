#!/bin/bash

echo "🚀 Iniciando AgentOS Backend - MVP"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está ejecutándose. Por favor inicia Docker primero."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde env.example..."
    cp env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tu GEMINI_API_KEY antes de continuar."
    echo "   Obtén tu API key en: https://aistudio.google.com/apikey"
    echo "   Luego ejecuta este script nuevamente."
    exit 1
fi

# Check if GEMINI_API_KEY is set
if grep -q "your_gemini_api_key_here" .env; then
    echo "⚠️  Por favor configura tu GEMINI_API_KEY en el archivo .env"
    echo "   Edita .env y reemplaza 'your_gemini_api_key_here' con tu API key real."
    echo "   Obtén tu API key en: https://aistudio.google.com/apikey"
    exit 1
fi

echo "✅ Configuración verificada"

# Build and start backend services
echo "🔨 Construyendo e iniciando backend..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Esperando que los servicios estén listos..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ ¡AgentOS Backend está funcionando!"
    echo ""
    echo "🌐 Servicios disponibles:"
    echo "   • Backend API: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo ""
    echo "🤖 Agentes disponibles:"
    echo "   • default - Asistente General"
    echo "   • researcher - Investigador IA" 
    echo "   • coder - Desarrollador IA"
    echo ""
    echo "🧪 Para probar el sistema:"
    echo "   chmod +x test_backend.sh && ./test_backend.sh"
    echo ""
    echo "📝 Ejemplo rápido con curl:"
    echo '   curl -X POST "http://localhost:8000/api/v1/chat" \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d "{\"message\": \"Hola, ¿cómo estás?\", \"agent_id\": \"default\"}"'
    echo ""
    echo "📊 Comandos útiles:"
    echo "   • Ver logs: docker-compose logs -f"
    echo "   • Reiniciar: docker-compose restart backend"
    echo "   • Detener: docker-compose down"
else
    echo "❌ Error: Algunos servicios no se iniciaron correctamente"
    echo "📋 Verificando estado de los servicios:"
    docker-compose ps
    echo ""
    echo "📝 Para ver logs de errores:"
    echo "   docker-compose logs backend"
fi 