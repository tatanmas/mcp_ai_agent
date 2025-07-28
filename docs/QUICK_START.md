# 🚀 Inicio Rápido - AgentOS MVP (10 minutos)

Este es un MVP funcional de un sistema de agentes IA con Gemini, AutoGen y MCP. ¡Perfecto para probar y luego escalar!

## ✅ Prerrequisitos

1. **Docker Desktop** instalado y ejecutándose
2. **API Key de Google Gemini** - [Obtener aquí](https://aistudio.google.com/apikey)

## 🏃‍♂️ Pasos de Instalación

### 1. Clonar y Configurar

```bash
# Si no tienes el repo, créalo
git clone <este-repo> agent-os
cd agent-os

# Hacer ejecutable el script de inicio
chmod +x start.sh
```

### 2. Configurar API Key

```bash
# El script creará el archivo .env automáticamente
./start.sh

# Edita el archivo .env con tu API key
nano .env  # o usar tu editor favorito

# Cambia esta línea:
# GEMINI_API_KEY=your_gemini_api_key_here
# Por:
# GEMINI_API_KEY=tu_api_key_real_aqui
```

### 3. Iniciar Todo el Sistema

```bash
# Ejecutar de nuevo para iniciar
./start.sh
```

**¡Eso es todo!** En 2-3 minutos tendrás:

- ✅ Frontend en http://localhost:3000
- ✅ Backend API en http://localhost:8000
- ✅ Documentación API en http://localhost:8000/docs
- ✅ Base de datos PostgreSQL configurada
- ✅ Redis para cache configurado

## 🤖 ¿Qué Puedes Probar?

### Agentes Disponibles:

1. **Asistente General**
   - Herramientas: web_search, calculator, memory
   - Ideal para preguntas generales

2. **Investigador IA**
   - Herramientas: web_search, pdf_analysis, data_visualization, memory
   - Perfecto para investigación profunda

3. **Desarrollador IA**
   - Herramientas: code_execution, github_search, documentation, memory
   - Especialista en programación

### Preguntas de Prueba:

```
📊 Para el Asistente General:
- "Calcula cuánto es 25 * 47 + 123"
- "Busca información sobre inteligencia artificial"

🔍 Para el Investigador:
- "Investiga las tendencias de IA en 2025"
- "Analiza los beneficios de la automatización"

💻 Para el Desarrollador:
- "Crea una función Python para ordenar una lista"
- "Explica qué es un API REST"
```

## 🛠️ Arquitectura Actual (MVP)

```
Frontend (Next.js + TypeScript)
    ↓ (REST API)
Backend (FastAPI + Gemini)
    ↓
• Agentes con personalidades únicas
• Sistema de herramientas básico
• Memoria de conversación
• Base de datos PostgreSQL
• Cache Redis
```

## 🚀 Escalabilidad Futura

Esta base MVP está preparada para crecer a:

### Corto Plazo:
- ✅ Integración completa MCP
- ✅ AutoGen multi-agente
- ✅ Memoria vectorial
- ✅ Herramientas de tiempo real

### Mediano Plazo:
- 🔄 Sistema de memoria avanzado (corto/mediano/largo plazo)
- 🔄 Agentes colaborativos
- 🔄 Marketplace de herramientas
- 🔄 Dashboard de analytics

### Largo Plazo:
- 🔄 Agentes autónomos
- 🔄 Integración blockchain
- 🔄 SaaS completo
- 🔄 SDK para desarrolladores

## 🔧 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un servicio específico
docker-compose restart backend
docker-compose restart frontend

# Detener todo
docker-compose down

# Limpiar y reiniciar desde cero
docker-compose down -v
./start.sh

# Entrar al backend para debug
docker-compose exec backend bash

# Ver estado de los servicios
docker-compose ps
```

## 🐛 Solución de Problemas

### El frontend no carga:
```bash
# Verificar que el backend esté funcionando
curl http://localhost:8000/health

# Si no responde, verificar logs
docker-compose logs backend
```

### Errores de API Key:
```bash
# Verificar que la API key esté configurada
cat .env | grep GEMINI

# Probar la API key manualmente
curl -H "Authorization: Bearer tu_api_key" https://generativelanguage.googleapis.com/v1/models
```

### Base de datos no conecta:
```bash
# Reiniciar servicios de base de datos
docker-compose restart db redis

# Verificar que estén funcionando
docker-compose ps
```

## 📊 Métricas del MVP

- **Tiempo de setup**: ~5 minutos
- **Memoria RAM**: ~2GB
- **Espacio disco**: ~1GB
- **Puertos usados**: 3000, 8000, 5432, 6379

## 🎯 Próximos Pasos

1. **Probar la funcionalidad básica** - Chatear con los 3 agentes
2. **Experimentar con herramientas** - Calculadora, búsqueda, memoria
3. **Revisar el código** - Entender la arquitectura modular
4. **Planificar escalabilidad** - ¿Qué características necesitas?

## 💡 Casos de Uso Comercializables

### Inmediatos:
- 🏢 **Asistente empresarial** con acceso a datos internos
- 🛍️ **Soporte al cliente** con IA contextual
- 📊 **Análisis de datos** automatizado

### Escalables:
- 🤖 **Marketplace de agentes** especializados
- 🔧 **Automatización de workflows** empresariales
- 🎯 **SaaS de agentes** por industria

---

**¡Tu sistema está listo para evolucionar de MVP a un producto comercial completo!** 🚀

¿Preguntas? Revisa los logs o la documentación de la API en http://localhost:8000/docs 