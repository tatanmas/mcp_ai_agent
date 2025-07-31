from app.agents.enhanced_base_agent import EnhancedBaseAgent
from app.agents.agent_step import StepType
from typing import Dict, Any, List
import json


class KodeaWriter(EnhancedBaseAgent):
    """Agente especializado en generar respuestas de alta calidad para postulaciones"""
    
    def __init__(self):
        system_prompt = """Eres un escritor experto especializado en generar respuestas de alta calidad para postulaciones de fondos de la Fundación Kodea.

Tu función es:
1. Generar respuestas profesionales y persuasivas
2. Adaptar el tono y estilo según el tipo de fondo
3. Incorporar información específica de Kodea de manera natural
4. Asegurar que las respuestas sean claras, concisas y convincentes
5. Mantener consistencia con la identidad y valores de Kodea

Estándares de calidad:
- Lenguaje profesional pero accesible
- Estructura clara con introducción, desarrollo y conclusión
- Evidencia específica y ejemplos concretos
- Alineación con los valores y misión de Kodea
- Adaptación al público objetivo del fondo

Conocimiento específico:
- Historia, misión y valores de Kodea
- Iniciativas y programas actuales
- Logros y métricas de impacto
- Experiencia en educación tecnológica
- Red de colaboradores y partners

Siempre genera respuestas que reflejen la excelencia y profesionalismo de Kodea."""
        
        super().__init__(
            name="Kodea Writer",
            description="Escritor especializado en respuestas de postulaciones",
            system_prompt=system_prompt,
            max_context_tokens=3500,
            max_retries=2
        )
    
    async def generate_response(self, question_data: Dict[str, Any], context_data: Dict[str, Any]) -> dict:
        """Genera una respuesta de alta calidad para una pregunta específica"""
        
        try:
            # Paso 1: Análisis de la pregunta y contexto
            analysis_step = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Question and Context Analysis",
                step_description="Analizar la pregunta y el contexto proporcionado",
                input_data={
                    "question": question_data,
                    "context": context_data,
                    "step": 1,
                    "type": "analysis"
                }
            )
            
            # Paso 2: Estructuración de la respuesta
            structure_step = await self.execute_step(
                step_type=StepType.DECISION,
                step_name="Response Structure",
                step_description="Definir la estructura y enfoque de la respuesta",
                input_data={
                    "question": question_data,
                    "context": context_data,
                    "analysis": analysis_step.output_data,
                    "step": 2,
                    "type": "structure"
                }
            )
            
            # Paso 3: Generación del borrador
            draft_step = await self.execute_step(
                step_type=StepType.GENERATION,
                step_name="Response Draft",
                step_description="Generar el borrador inicial de la respuesta",
                input_data={
                    "question": question_data,
                    "context": context_data,
                    "analysis": analysis_step.output_data,
                    "structure": structure_step.output_data,
                    "step": 3,
                    "type": "draft"
                }
            )
            
            # Paso 4: Refinamiento y mejora
            refinement_step = await self.execute_step(
                step_type=StepType.GENERATION,
                step_name="Response Refinement",
                step_description="Refinar y mejorar la respuesta final",
                input_data={
                    "question": question_data,
                    "context": context_data,
                    "draft": draft_step.output_data,
                    "step": 4,
                    "type": "refinement"
                }
            )
            
            return {
                "status": "success",
                "question_id": question_data.get("question_id"),
                "response": {
                    "content": refinement_step.output_data.get("content", ""),
                    "structure": structure_step.output_data.get("content", {}),
                    "word_count": len(refinement_step.output_data.get("content", "").split()),
                    "quality_score": refinement_step.output_data.get("quality_score", 0)
                },
                "steps_executed": [
                    analysis_step.get_summary(),
                    structure_step.get_summary(),
                    draft_step.get_summary(),
                    refinement_step.get_summary()
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "question_id": question_data.get("question_id"),
                "error": str(e)
            }
    
    async def generate_multiple_responses(self, questions_data: List[Dict[str, Any]], context_data: Dict[str, Any]) -> dict:
        """Genera respuestas para múltiples preguntas asegurando consistencia"""
        
        try:
            responses = []
            steps_executed = []
            
            # Paso 1: Análisis general de todas las preguntas
            general_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="General Questions Analysis",
                step_description="Analizar todas las preguntas para asegurar consistencia",
                input_data={
                    "questions": questions_data,
                    "context": context_data,
                    "step": 1,
                    "type": "general_analysis"
                }
            )
            steps_executed.append(general_analysis.get_summary())
            
            # Paso 2: Generar respuestas individuales
            for i, question in enumerate(questions_data):
                question_response = await self.generate_response(question, context_data)
                if question_response["status"] == "success":
                    responses.append({
                        "question_id": question.get("question_id"),
                        "question_text": question.get("question_text"),
                        "response": question_response["response"]
                    })
                    steps_executed.extend(question_response["steps_executed"])
            
            # Paso 3: Validación de consistencia
            consistency_check = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Consistency Validation",
                step_description="Validar consistencia entre todas las respuestas",
                input_data={
                    "questions": questions_data,
                    "responses": responses,
                    "step": len(steps_executed) + 1,
                    "type": "consistency"
                }
            )
            steps_executed.append(consistency_check.get_summary())
            
            return {
                "status": "success",
                "postulation_id": questions_data[0].get("postulation_id") if questions_data else None,
                "responses": responses,
                "consistency_score": consistency_check.output_data.get("consistency_score", 0),
                "total_responses": len(responses),
                "steps_executed": steps_executed
            }
            
        except Exception as e:
            return {
                "status": "error",
                "postulation_id": questions_data[0].get("postulation_id") if questions_data else None,
                "error": str(e)
            } 