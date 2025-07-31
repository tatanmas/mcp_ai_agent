from app.agents.enhanced_base_agent import EnhancedBaseAgent
from app.agents.agent_step import StepType
from app.state.kodea_context_manager import KodeaContextManager
from typing import Dict, Any, List
import json


class KodeaCoordinator(EnhancedBaseAgent):
    """Coordinador principal para el sistema de postulaciones de Kodea"""
    
    def __init__(self):
        system_prompt = """Eres el coordinador principal del sistema de postulaciones de la Fundación Kodea.

Tu función es:
1. Analizar las consultas de postulación que recibes
2. Identificar la iniciativa específica de la postulación
3. Coordinar la ejecución de los agentes especializados en el orden correcto
4. Asegurar que se use el contexto relevante para cada pregunta
5. Validar que el resultado final cumpla con los estándares de Kodea

Agentes especializados disponibles:
- ANALYZER: Analiza postulaciones pasadas y contexto de Kodea
- WRITER: Genera respuestas de alto estándar
- VALIDATOR: Valida consistencia y calidad de respuestas
- RESEARCHER: Investiga información específica de fondos

Siempre responde de manera estructurada y profesional."""
        
        super().__init__(
            name="Kodea Coordinator",
            description="Coordinador principal para postulaciones de fondos",
            system_prompt=system_prompt,
            max_context_tokens=4000,
            max_retries=3
        )
        
        # Inicializar gestor de contextos simplificado
        self.context_manager = KodeaContextManager()
    
    async def process_postulation_request(self, request_data: Dict[str, Any]) -> dict:
        """Procesa una solicitud de postulación completa"""
        
        try:
            # Paso 1: Identificación de iniciativa y contexto inicial
            initiative_step = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Initiative Identification",
                step_description="Identificar la iniciativa específica y cargar contexto inicial",
                input_data={
                    "request": request_data,
                    "step": 1,
                    "type": "initiative_identification"
                }
            )
            
            # Identificar iniciativa
            initiative = self.context_manager.identify_initiative(request_data)
            initiative_context = self.context_manager.get_initiative_context(initiative)
            
            # Paso 2: Análisis de la solicitud con contexto de iniciativa
            analysis_step = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Postulation Analysis",
                step_description="Analizar la solicitud de postulación con contexto de iniciativa",
                input_data={
                    "request": request_data,
                    "initiative": initiative,
                    "initiative_context": initiative_context,
                    "step": 2,
                    "type": "postulation_analysis"
                }
            )
            
            # Paso 3: Generación de respuestas con contexto específico por pregunta
            responses = []
            for i, question in enumerate(request_data.get("questions", [])):
                # Construir contexto específico para esta pregunta usando LLM
                question_context_result = await self.context_manager.build_question_context_intelligent(
                    question.get("question_text", ""),
                    initiative_context
                )
                
                # Generar respuesta con contexto específico
                response_step = await self.execute_step(
                    step_type=StepType.GENERATION,
                    step_name=f"Response Generation - Question {i+1}",
                    step_description=f"Generar respuesta para pregunta {i+1} con contexto específico seleccionado por LLM",
                    input_data={
                        "question": question,
                        "question_context": question_context_result["context"],
                        "selected_contexts": question_context_result["selected_contexts"],
                        "selection_justification": question_context_result.get("selection_result", {}).get("justificacion", ""),
                        "initiative_context": initiative_context,
                        "step": 3,
                        "question_number": i+1,
                        "type": "response_generation"
                    }
                )
                
                responses.append({
                    "question_id": question.get("question_id"),
                    "question_text": question.get("question_text"),
                    "response": response_step.output_data.get("content", ""),
                    "context_used": question_context_result["context"][:500] + "..." if len(question_context_result["context"]) > 500 else question_context_result["context"],
                    "selected_contexts": question_context_result["selected_contexts"],
                    "context_selection_justification": question_context_result.get("selection_result", {}).get("justificacion", ""),
                    "context_length": question_context_result["context_length"]
                })
            
            # Paso 4: Validación de consistencia entre respuestas
            consistency_step = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Consistency Validation",
                step_description="Validar consistencia entre todas las respuestas generadas",
                input_data={
                    "request": request_data,
                    "responses": responses,
                    "initiative_context": initiative_context,
                    "step": 4,
                    "type": "consistency_validation"
                }
            )
            
            # Paso 5: Revisión final y ajustes
            final_review_step = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Final Review",
                step_description="Revisión final de calidad y ajustes necesarios",
                input_data={
                    "request": request_data,
                    "responses": responses,
                    "consistency_validation": consistency_step.output_data,
                    "initiative_context": initiative_context,
                    "step": 5,
                    "type": "final_review"
                }
            )
            
            # Agregar postulación al historial para futuras referencias
            self.context_manager.add_postulation_to_history(request_data)
            
            return {
                "status": "success",
                "postulation_id": request_data.get("postulation_id"),
                "conversation_id": request_data.get("conversation_id"),
                "initiative_identified": initiative,
                "context_summary": self.context_manager.get_context_summary(),
                "steps_executed": [
                    initiative_step.get_summary(),
                    analysis_step.get_summary(),
                    consistency_step.get_summary(),
                    final_review_step.get_summary()
                ],
                "final_responses": {resp["question_id"]: resp for resp in responses},
                "execution_summary": self.get_execution_summary()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "postulation_id": request_data.get("postulation_id"),
                "error": str(e),
                "execution_summary": self.get_execution_summary()
            }
    
    async def process_single_question(self, question_data: Dict[str, Any]) -> dict:
        """Procesa una pregunta individual de postulación"""
        
        try:
            # Paso 1: Identificación de iniciativa
            initiative = self.context_manager.identify_initiative(question_data)
            initiative_context = self.context_manager.get_initiative_context(initiative)
            
            # Paso 2: Construcción de contexto específico para la pregunta usando LLM
            question_context_result = await self.context_manager.build_question_context_intelligent(
                question_data.get("question_text", ""),
                initiative_context
            )
            
            # Paso 3: Análisis de la pregunta con contexto
            analysis_step = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Question Analysis",
                step_description="Analizar la pregunta específica con contexto relevante seleccionado por LLM",
                input_data={
                    "question": question_data,
                    "question_context": question_context_result["context"],
                    "selected_contexts": question_context_result["selected_contexts"],
                    "selection_justification": question_context_result.get("selection_result", {}).get("justificacion", ""),
                    "initiative_context": initiative_context,
                    "step": 1,
                    "type": "question_analysis"
                }
            )
            
            # Paso 4: Generación de respuesta
            response_step = await self.execute_step(
                step_type=StepType.GENERATION,
                step_name="Answer Generation",
                step_description="Generar respuesta de alta calidad con contexto específico seleccionado por LLM",
                input_data={
                    "question": question_data,
                    "question_context": question_context_result["context"],
                    "analysis": analysis_step.output_data,
                    "initiative_context": initiative_context,
                    "step": 2,
                    "type": "answer_generation"
                }
            )
            
            return {
                "status": "success",
                "question_id": question_data.get("question_id"),
                "conversation_id": question_data.get("conversation_id"),
                "initiative_identified": initiative,
                "context_used": question_context_result["context"][:500] + "..." if len(question_context_result["context"]) > 500 else question_context_result["context"],
                "selected_contexts": question_context_result["selected_contexts"],
                "context_selection_justification": question_context_result.get("selection_result", {}).get("justificacion", ""),
                "context_length": question_context_result["context_length"],
                "steps_executed": [
                    analysis_step.get_summary(),
                    response_step.get_summary()
                ],
                "answer": {"content": response_step.output_data.get("content", "")},
                "execution_summary": self.get_execution_summary()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "question_id": question_data.get("question_id"),
                "error": str(e),
                "execution_summary": self.get_execution_summary()
            } 