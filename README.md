# AgentOS - Sistema Avanzado de Agentes IA

Un sistema de agentes de IA de próxima generación que combina AutoGen, Model Context Protocol (MCP), y Gemini 2.5 Pro para crear agentes comercializables e hiper-inteligentes.

## 🚀 Características Principales

- **Multi-Agente Inteligente**: Powered by AutoGen para orquestación avanzada
- **Model Context Protocol (MCP)**: Integración estandarizada con herramientas externas
- **Gemini 2.5 Pro**: Function calling y capacidades multimodales
- **Interfaz Moderna**: Frontend Next.js con UI/UX de última generación
- **API RESTful**: Backend FastAPI escalable y seguro
- **Dockerizado**: Despliegue fácil y escalable
- **Arquitectura Modular**: Diseño para escalar de simple a complejo

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Agents     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (AutoGen)     │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Multi-Agent   │
│ • Agent Creator │    │ • MCP Server    │    │ • Tool Calling  │
│ • Chat UI       │    │ • Auth & Security│   │ • Memory        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │   External      │
                       │   Services      │
                       │                 │
                       │ • Gemini API    │
                       │ • MCP Tools     │
                       │ • Databases     │
                       └─────────────────┘
```

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: API REST moderna y performante
- **AutoGen**: Framework de agentes múltiples
- **MCP SDK**: Model Context Protocol
- **Pydantic**: Validación de datos
- **SQLAlchemy**: ORM y base de datos
- **PostgreSQL**: Base de datos principal

### Frontend
- **Next.js 14**: Framework React con App Router
- **TypeScript**: Tipado estático
- **Tailwind CSS**: Styling moderno
- **Shadcn/UI**: Componentes reutilizables
- **React Query**: Estado del servidor

### IA & Agentes
- **Gemini 2.5 Pro**: Modelo base con function calling
- **AutoGen Studio**: Orquestación de agentes
- **MCP Protocol**: Integración estándar de herramientas
- **LangChain**: Utilidades adicionales de IA

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación local
- **PostgreSQL**: Base de datos
- **Redis**: Cache y sesiones
- **Nginx**: Proxy reverso

## 🚦 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo)
- Python 3.11+ (para desarrollo)
- API Key de Google Gemini

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/agent-os.git
cd agent-os

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Levantar todo el stack
docker-compose up -d

# La aplicación estará disponible en:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Desarrollo Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
agent-os/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── agents/         # Lógica de agentes AutoGen
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración y seguridad
│   │   ├── db/             # Modelos y migrations
│   │   ├── mcp/            # Servidores MCP
│   │   └── services/       # Servicios de negocio
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Aplicación Next.js
│   ├── src/
│   │   ├── app/           # App Router
│   │   ├── components/    # Componentes React
│   │   ├── lib/           # Utilidades
│   │   └── types/         # Tipos TypeScript
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Orquestación completa
├── docs/                   # Documentación
└── README.md
```

## 🤖 Tipos de Agentes Disponibles

### 1. Agente de Investigación
- Búsqueda web inteligente
- Análisis de contenido
- Síntesis de información

### 2. Agente de Desarrollo
- Generación de código
- Review automático
- Documentación técnica

### 3. Agente de Marketing
- Análisis de mercado
- Creación de contenido
- Estrategias SEO

### 4. Agente de Finanzas
- Análisis financiero
- Reportes automáticos
- Gestión de presupuestos

### 5. Agente Personalizado
- Configurable via UI
- Herramientas personalizadas
- Flujos de trabajo específicos

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# API Keys
GEMINI_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=opcional_para_comparaciones

# Base de datos
DATABASE_URL=postgresql://user:password@db:5432/agentdb
REDIS_URL=redis://redis:6379/0

# Seguridad
SECRET_KEY=tu_secret_key_muy_seguro
JWT_SECRET=tu_jwt_secret

# MCP Configuration
MCP_SERVER_PORT=8001
ENABLE_MCP_TOOLS=true

# Features
ENABLE_MULTIMODAL=true
ENABLE_VOICE_AGENTS=false
MAX_AGENTS_PER_USER=10
```

### Configuración de Agentes

Los agentes se configuran en `backend/app/agents/config/`:

```python
# ejemplo_config.py
agent_config = {
    "name": "Investigador Avanzado",
    "description": "Especialista en investigación y análisis",
    "model": "gemini-2.5-pro",
    "temperature": 0.7,
    "max_tokens": 4096,
    "tools": [
        "web_search",
        "pdf_analysis", 
        "data_visualization"
    ],
    "memory_type": "enhanced",
    "collaboration_mode": True
}
```

## 🛡️ Seguridad y Autenticación

- **JWT Authentication**: Tokens seguros para autenticación
- **Rate Limiting**: Protección contra abuso
- **CORS Configuration**: Configuración segura de CORS
- **Input Validation**: Validación robusta con Pydantic
- **SQL Injection Protection**: Uso de ORM SQLAlchemy
- **API Key Management**: Gestión segura de claves

## 📊 Monitoreo y Analytics

- **Health Checks**: Endpoints de salud para cada servicio
- **Métricas de Agentes**: Tiempo de respuesta, éxito/fallo
- **Usage Analytics**: Uso de recursos y costos
- **Error Tracking**: Logging detallado de errores
- **Performance Metrics**: Métricas de rendimiento en tiempo real

## 🌐 API Documentation

La documentación completa de la API está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

```
GET /api/v1/agents/              # Listar agentes
POST /api/v1/agents/             # Crear agente
GET /api/v1/agents/{id}          # Obtener agente
PUT /api/v1/agents/{id}          # Actualizar agente
DELETE /api/v1/agents/{id}       # Eliminar agente

POST /api/v1/chat/               # Iniciar conversación
POST /api/v1/chat/{id}/message   # Enviar mensaje
GET /api/v1/chat/{id}/history    # Historial de chat

GET /api/v1/tools/               # Herramientas disponibles
POST /api/v1/tools/custom        # Crear herramienta personalizada
```

## 🚀 Despliegue en Producción

### Docker Compose (Recomendado)

```bash
# Producción
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Aplicar manifiestos
kubectl apply -f k8s/
```

### Variables de Producción

```bash
# Configuración de producción
NODE_ENV=production
ENVIRONMENT=production
DEBUG=false
DATABASE_POOL_SIZE=20
REDIS_MAX_CONNECTIONS=50
```

## 📈 Roadmap

### Q1 2025
- [x] Arquitectura base con AutoGen + MCP
- [x] Integración Gemini 2.5 Pro
- [x] UI/UX moderna
- [ ] Agentes especializados básicos
- [ ] Sistema de autenticación completo

### Q2 2025
- [ ] Marketplace de agentes
- [ ] API pública para terceros
- [ ] Integraciones empresariales
- [ ] Agentes con memoria a largo plazo
- [ ] Análisis de sentimientos avanzado

### Q3 2025
- [ ] Agentes de voz (Voice Agents)
- [ ] Integración con plataformas de terceros
- [ ] Dashboard de analytics avanzado
- [ ] Automatización de workflows
- [ ] SDK para desarrolladores

### Q4 2025
- [ ] IA multimodal completa
- [ ] Agentes autónomos
- [ ] Marketplace de herramientas MCP
- [ ] Integración blockchain
- [ ] Modelo de negocio SaaS completo

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/agent-os/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/agent-os/discussions)
- **Email**: support@agent-os.com

## 🙏 Agradecimientos

- **AutoGen Team** por el framework de agentes
- **Anthropic** por el Model Context Protocol
- **Google** por Gemini API
- **FastAPI** y **Next.js** communities
- **Open Source Community** por las librerías utilizadas

---

⭐ **¡Si te gusta este proyecto, dale una estrella en GitHub!** ⭐ 