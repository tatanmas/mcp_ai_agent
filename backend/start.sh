#!/bin/bash

echo "🚀 Iniciando Sistema de Agentes Inteligentes con LangChain..."

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Copiando env.example..."
    cp env.example .env
    echo "📝 Por favor, edita el archivo .env con tus credenciales de Google Gemini"
    echo "   Específicamente, agrega tu GOOGLE_API_KEY"
    exit 1
fi

# Verificar que GOOGLE_API_KEY está configurada
if ! grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env; then
    echo "✅ Variables de entorno configuradas"
else
    echo "❌ Por favor, configura tu GOOGLE_API_KEY en el archivo .env"
    exit 1
fi

# Levantar servicios con Docker Compose
echo "🐳 Levantando servicios con Docker Compose..."
docker-compose up --build -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 15

# Verificar que la aplicación esté funcionando
echo "🔍 Verificando estado de la aplicación..."
curl -f http://localhost:8001/ || {
    echo "❌ La aplicación no está respondiendo"
    echo "📋 Logs de la aplicación:"
    docker-compose logs backend
    exit 1
}

echo "✅ Sistema iniciado correctamente!"
echo "🌐 API disponible en: http://localhost:8001"
echo "📚 Documentación en: http://localhost:8001/docs"
echo "🔍 Health check en: http://localhost:8001/agents/health"
echo ""
echo "🧪 Para probar el sistema:"
echo "curl -X POST http://localhost:8001/agents/query \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"¿Cuáles son las mejores prácticas para microservicios?\"}'"
echo ""
echo "📊 Servicios disponibles:"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
echo "- ChromaDB: localhost:8000"
echo "- Backend: localhost:8001" 