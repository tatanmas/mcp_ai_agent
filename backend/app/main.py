from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.kodea_agents import router as kodea_agents_router
from app.core.config import settings

app = FastAPI(
    title="Sistema de Agentes Inteligentes - Fundación Kodea",
    description="Red de agentes especializados para postulaciones de fondos con LangChain, PostgreSQL, Redis y ChromaDB",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(kodea_agents_router)

@app.get("/")
async def root():
    return {
        "message": "Sistema de Agentes Inteligentes - Fundación Kodea",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/kodea/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "backend": "running",
            "postgres": "configured",
            "redis": "configured",
            "chromadb": "configured"
        },
        "system": "kodea_agents"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 