from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid

from app.agents.kodea_coordinator import KodeaCoordinator
from app.agents.kodea_analyzer import KodeaAnalyzer
from app.agents.kodea_writer import KodeaWriter
from app.agents.kodea_validator import KodeaValidator

router = APIRouter(prefix="/kodea", tags=["kodea"])

# Instancias de los agentes
coordinator = KodeaCoordinator()
analyzer = KodeaAnalyzer()
writer = KodeaWriter()
validator = KodeaValidator()


# Modelos Pydantic para requests
class PostulationRequest(BaseModel):
    postulation_id: str
    fund_name: str
    fund_description: str
    initiative: str
    questions: List[Dict[str, Any]]
    conversation_id: Optional[str] = None


class SingleQuestionRequest(BaseModel):
    question_id: str
    question_text: str
    fund_context: Dict[str, Any]
    initiative: str
    conversation_id: Optional[str] = None


class AnalysisRequest(BaseModel):
    postulation_id: str
    fund_name: str
    fund_description: str
    initiative: str
    conversation_id: Optional[str] = None


# Modelos Pydantic para responses
class PostulationResponse(BaseModel):
    status: str
    postulation_id: str
    conversation_id: Optional[str] = None
    steps_executed: Optional[List[Dict[str, Any]]] = None
    final_responses: Optional[Dict[str, Any]] = None
    execution_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SingleQuestionResponse(BaseModel):
    status: str
    question_id: str
    conversation_id: Optional[str] = None
    steps_executed: Optional[List[Dict[str, Any]]] = None
    answer: Optional[Dict[str, Any]] = None
    execution_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str
    postulation_id: str
    conversation_id: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    steps_executed: Optional[List[Dict[str, Any]]] = None
    execution_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/postulation/process", response_model=PostulationResponse)
async def process_postulation(request: PostulationRequest):
    """
    Procesa una postulación completa con todas sus preguntas
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await coordinator.process_postulation_request({
            "postulation_id": request.postulation_id,
            "fund_name": request.fund_name,
            "fund_description": request.fund_description,
            "initiative": request.initiative,
            "questions": request.questions,
            "conversation_id": conversation_id
        })
        
        return PostulationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/question/process", response_model=SingleQuestionResponse)
async def process_single_question(request: SingleQuestionRequest):
    """
    Procesa una pregunta individual de postulación
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await coordinator.process_single_question({
            "question_id": request.question_id,
            "question_text": request.question_text,
            "fund_context": request.fund_context,
            "initiative": request.initiative,
            "conversation_id": conversation_id
        })
        
        return SingleQuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/context", response_model=AnalysisResponse)
async def analyze_postulation_context(request: AnalysisRequest):
    """
    Analiza el contexto de una postulación específica
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await analyzer.analyze_postulation_context({
            "postulation_id": request.postulation_id,
            "fund_name": request.fund_name,
            "fund_description": request.fund_description,
            "initiative": request.initiative,
            "conversation_id": conversation_id
        })
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/writer/generate", response_model=SingleQuestionResponse)
async def generate_response(request: SingleQuestionRequest):
    """
    Genera una respuesta de alta calidad para una pregunta específica
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Primero analizar el contexto
        analysis_result = await analyzer.analyze_question_context({
            "question_id": request.question_id,
            "question_text": request.question_text,
            "fund_context": request.fund_context,
            "initiative": request.initiative,
            "conversation_id": conversation_id
        })
        
        if analysis_result["status"] != "success":
            raise Exception("Error en análisis de contexto")
        
        # Luego generar la respuesta
        result = await writer.generate_response(
            question_data={
                "question_id": request.question_id,
                "question_text": request.question_text,
                "fund_context": request.fund_context,
                "initiative": request.initiative,
                "conversation_id": conversation_id
            },
            context_data=analysis_result["analysis_results"]
        )
        
        return SingleQuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validator/validate-response", response_model=SingleQuestionResponse)
async def validate_single_response(request: SingleQuestionRequest):
    """
    Valida una respuesta individual de postulación
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await validator.validate_single_response(
            response_data=request.fund_context.get("response", {}),
            question_data={
                "question_id": request.question_id,
                "question_text": request.question_text,
                "fund_context": request.fund_context,
                "initiative": request.initiative,
                "conversation_id": conversation_id
            },
            fund_context=request.fund_context
        )
        
        return SingleQuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validator/validate-consistency")
async def validate_consistency(request: PostulationRequest):
    """
    Valida consistencia entre múltiples respuestas de una postulación
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await validator.validate_consistency(
            responses_data=[q.get("response", {}) for q in request.questions],
            postulation_context={
                "postulation_id": request.postulation_id,
                "fund_name": request.fund_name,
                "fund_description": request.fund_description,
                "initiative": request.initiative,
                "conversation_id": conversation_id
            }
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validator/validate-postulation")
async def validate_complete_postulation(request: PostulationRequest):
    """
    Valida una postulación completa
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        result = await validator.validate_complete_postulation({
            "postulation_id": request.postulation_id,
            "fund_name": request.fund_name,
            "fund_description": request.fund_description,
            "initiative": request.initiative,
            "questions": request.questions,
            "conversation_id": conversation_id
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def kodea_health():
    """
    Health check para el sistema de Kodea
    """
    return {
        "status": "healthy",
        "message": "Sistema de postulaciones Kodea funcionando",
        "services": {
            "coordinator": "active",
            "analyzer": "active",
            "writer": "active",
            "validator": "active"
        },
        "endpoints": {
            "process_postulation": "/kodea/postulation/process",
            "process_question": "/kodea/question/process",
            "analyze_context": "/kodea/analysis/context",
            "generate_response": "/kodea/writer/generate",
            "validate_response": "/kodea/validator/validate-response",
            "validate_consistency": "/kodea/validator/validate-consistency",
            "validate_postulation": "/kodea/validator/validate-postulation"
        }
    }


@router.get("/agents/info")
async def get_agents_info():
    """
    Obtiene información de todos los agentes de Kodea
    """
    return {
        "coordinator": coordinator.get_agent_info(),
        "analyzer": analyzer.get_agent_info(),
        "writer": writer.get_agent_info(),
        "validator": validator.get_agent_info()
    } 