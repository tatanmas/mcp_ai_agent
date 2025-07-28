# 🚀 Backend MVP - AgentOS (5 minutos)

**Prueba de concepto simple: Backend con Gemini + 3 Agentes IA funcionando**

## ✅ Qué necesitas

1. **Docker Desktop** ejecutándose
2. **API Key de Gemini** - [Obtener aquí](https://aistudio.google.com/apikey)

## 🏃‍♂️ Inicio Súper Rápido

```bash
# 1. Configurar
chmod +x start.sh
./start.sh
# (Te pedirá configurar la API key en .env)

# 2. Editar .env con tu API key real
nano .env  # cambiar: GEMINI_API_KEY=tu_api_key_aqui

# 3. Iniciar
./start.sh

# 4. Probar todo
chmod +x test_backend.sh
./test_backend.sh
```

**¡Ya está!** En 2-3 minutos tienes:
- ✅ API funcionando en http://localhost:8000
- ✅ 3 agentes IA listos para usar
- ✅ Sistema de herramientas básico
- ✅ Memoria de conversación

## 🤖 Agentes Disponibles

| Agente ID | Nombre | Especialidad | Herramientas |
|-----------|---------|--------------|--------------|
| `default` | Asistente General | Tareas generales | web_search, calculator, memory |
| `researcher` | Investigador IA | Investigación | web_search, pdf_analysis, data_visualization, memory |
| `coder` | Desarrollador IA | Programación | code_execution, github_search, documentation, memory |

## 🧪 Pruebas Rápidas

### Ejemplo 1: Calculadora
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calcula 25 * 47 + 123", 
    "agent_id": "default"
  }'
```

### Ejemplo 2: Investigación
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Busca información sobre IA en 2025", 
    "agent_id": "researcher"
  }'
```

### Ejemplo 3: Programación
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Crea una función Python para ordenar una lista", 
    "agent_id": "coder"
  }'
```

## 📋 API Endpoints

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/` | GET | Info básica |
| `/health` | GET | Estado del sistema |
| `/docs` | GET | Documentación Swagger |
| `/api/v1/agents` | GET | Lista de agentes |
| `/api/v1/chat` | POST | Chat con agentes |

## 🔍 Lo que está funcionando AHORA

✅ **Arquitectura base**: FastAPI + Gemini + PostgreSQL + Redis
✅ **3 agentes especializados** con personalidades únicas  
✅ **Sistema de herramientas** básico pero funcional
✅ **Memoria de conversación** mantenida por agente
✅ **Parsing de herramientas** automático 
✅ **API REST** completa y documentada

## 🚀 Próximos pasos para evolucionar

### Fase 1: MCP Real (próximos días)
- [ ] Integración verdadera con Model Context Protocol
- [ ] Herramientas de tiempo real (web search real)
- [ ] Sistema de memoria vectorial

### Fase 2: AutoGen Integration (próxima semana)
- [ ] Agentes colaborativos múltiples
- [ ] Orquestación avanzada de tareas
- [ ] Memoria de largo plazo

### Fase 3: Comercialización (próximas semanas)
- [ ] Frontend profesional
- [ ] Dashboard de analytics
- [ ] API comercial
- [ ] Sistema de facturación

## 🛠️ Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Reiniciar solo el backend
docker-compose restart backend

# Entrar al container para debug
docker-compose exec backend bash

# Ver estado de servicios
docker-compose ps

# Limpiar todo y empezar de nuevo
docker-compose down -v
./start.sh
```

## 🐛 Debug rápido

```bash
# ¿Backend responde?
curl http://localhost:8000/health

# ¿Base de datos conectada?
docker-compose logs db

# ¿API key configurada?
cat .env | grep GEMINI

# ¿Agentes disponibles?
curl http://localhost:8000/api/v1/agents
```

## 💡 Casos de uso INMEDIATOS

Con este MVP ya puedes:

1. **Asistente empresarial básico** - Respuestas inteligentes con cálculos
2. **Investigador automático** - Búsquedas y análisis 
3. **Generador de código** - Asistente de programación
4. **API para integración** - Usar desde cualquier app

## 🎯 Arquitectura actual

```
Cliente (curl/Postman/tu app)
    ↓ (HTTP/REST)
FastAPI Backend 
    ↓ (API calls)
Google Gemini 2.5 Pro
    ↓ (tool execution)
Sistema de Herramientas Simuladas
    ↓ (persistence) 
PostgreSQL + Redis
```

---

**¡Este MVP ya es funcional y escalable!** 🚀  
Podemos evolucionarlo paso a paso sin romper nada. 