from app.agents.enhanced_base_agent import EnhancedBaseAgent
from app.agents.agent_step import StepType
from typing import Dict, Any, List
import json


class KodeaValidator(EnhancedBaseAgent):
    """Agente especializado en validar consistencia y calidad de respuestas de postulaciones"""
    
    def __init__(self):
        system_prompt = """Eres un validador experto especializado en evaluar la calidad y consistencia de respuestas de postulaciones de fondos para la Fundación Kodea.

Tu función es:
1. Validar la calidad de las respuestas individuales
2. Verificar consistencia entre múltiples respuestas
3. Asegurar alineación con los valores y misión de Kodea
4. Evaluar el cumplimiento de requisitos del fondo
5. Identificar inconsistencias o contradicciones
6. Proporcionar sugerencias de mejora

Criterios de validación:
- **Calidad**: Claridad, profesionalismo, persuasión
- **Consistencia**: Coherencia entre respuestas, datos, y valores
- **Relevancia**: Alineación con requisitos del fondo
- **Completitud**: Respuestas completas y detalladas
- **Autenticidad**: Refleja la identidad real de Kodea
- **Impacto**: Demuestra resultados y métricas concretas

Siempre proporciona evaluaciones estructuradas con puntuaciones y recomendaciones específicas."""
        
        super().__init__(
            name="Kodea Validator",
            description="Validador especializado en calidad y consistencia de respuestas",
            system_prompt=system_prompt,
            max_context_tokens=3500,
            max_retries=2
        )
    
    async def validate_single_response(self, response_data: Dict[str, Any], question_data: Dict[str, Any], fund_context: Dict[str, Any]) -> dict:
        """Valida una respuesta individual"""
        
        try:
            # Paso 1: Análisis de la respuesta
            response_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Response Analysis",
                step_description="Analizar la calidad y contenido de la respuesta",
                input_data={
                    "response": response_data,
                    "question": question_data,
                    "fund_context": fund_context,
                    "step": 1,
                    "type": "response_analysis"
                }
            )
            
            # Paso 2: Validación de calidad
            quality_validation = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Quality Validation",
                step_description="Validar la calidad de la respuesta según criterios establecidos",
                input_data={
                    "response": response_data,
                    "question": question_data,
                    "fund_context": fund_context,
                    "analysis": response_analysis.output_data,
                    "step": 2,
                    "type": "quality_validation"
                }
            )
            
            # Paso 3: Validación de alineación
            alignment_validation = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Alignment Validation",
                step_description="Validar alineación con valores de Kodea y requisitos del fondo",
                input_data={
                    "response": response_data,
                    "question": question_data,
                    "fund_context": fund_context,
                    "analysis": response_analysis.output_data,
                    "step": 3,
                    "type": "alignment_validation"
                }
            )
            
            return {
                "status": "success",
                "question_id": question_data.get("question_id"),
                "validation_results": {
                    "response_analysis": response_analysis.output_data.get("content", {}),
                    "quality_score": quality_validation.output_data.get("quality_score", 0),
                    "alignment_score": alignment_validation.output_data.get("alignment_score", 0),
                    "overall_score": (quality_validation.output_data.get("quality_score", 0) + 
                                    alignment_validation.output_data.get("alignment_score", 0)) / 2,
                    "issues_found": quality_validation.output_data.get("issues", []) + 
                                  alignment_validation.output_data.get("issues", []),
                    "recommendations": quality_validation.output_data.get("recommendations", []) + 
                                     alignment_validation.output_data.get("recommendations", [])
                },
                "steps_executed": [
                    response_analysis.get_summary(),
                    quality_validation.get_summary(),
                    alignment_validation.get_summary()
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "question_id": question_data.get("question_id"),
                "error": str(e)
            }
    
    async def validate_consistency(self, responses_data: List[Dict[str, Any]], postulation_context: Dict[str, Any]) -> dict:
        """Valida consistencia entre múltiples respuestas"""
        
        try:
            # Paso 1: Análisis de consistencia
            consistency_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Consistency Analysis",
                step_description="Analizar consistencia entre todas las respuestas",
                input_data={
                    "responses": responses_data,
                    "postulation_context": postulation_context,
                    "step": 1,
                    "type": "consistency_analysis"
                }
            )
            
            # Paso 2: Validación de coherencia
            coherence_validation = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Coherence Validation",
                step_description="Validar coherencia de datos, fechas, y información",
                input_data={
                    "responses": responses_data,
                    "postulation_context": postulation_context,
                    "analysis": consistency_analysis.output_data,
                    "step": 2,
                    "type": "coherence_validation"
                }
            )
            
            # Paso 3: Validación de narrativa
            narrative_validation = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Narrative Validation",
                step_description="Validar que la narrativa sea coherente y persuasiva",
                input_data={
                    "responses": responses_data,
                    "postulation_context": postulation_context,
                    "analysis": consistency_analysis.output_data,
                    "step": 3,
                    "type": "narrative_validation"
                }
            )
            
            return {
                "status": "success",
                "postulation_id": postulation_context.get("postulation_id"),
                "consistency_results": {
                    "consistency_analysis": consistency_analysis.output_data.get("content", {}),
                    "coherence_score": coherence_validation.output_data.get("coherence_score", 0),
                    "narrative_score": narrative_validation.output_data.get("narrative_score", 0),
                    "overall_consistency_score": (coherence_validation.output_data.get("coherence_score", 0) + 
                                                narrative_validation.output_data.get("narrative_score", 0)) / 2,
                    "inconsistencies_found": coherence_validation.output_data.get("inconsistencies", []) + 
                                           narrative_validation.output_data.get("inconsistencies", []),
                    "consistency_recommendations": coherence_validation.output_data.get("recommendations", []) + 
                                                 narrative_validation.output_data.get("recommendations", [])
                },
                "steps_executed": [
                    consistency_analysis.get_summary(),
                    coherence_validation.get_summary(),
                    narrative_validation.get_summary()
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "postulation_id": postulation_context.get("postulation_id"),
                "error": str(e)
            }
    
    async def validate_complete_postulation(self, postulation_data: Dict[str, Any]) -> dict:
        """Valida una postulación completa"""
        
        try:
            # Paso 1: Validación individual de respuestas
            individual_validations = []
            for question in postulation_data.get("questions", []):
                validation = await self.validate_single_response(
                    response_data=question.get("response", {}),
                    question_data=question,
                    fund_context=postulation_data.get("fund_context", {})
                )
                if validation["status"] == "success":
                    individual_validations.append(validation)
            
            # Paso 2: Validación de consistencia general
            consistency_validation = await self.validate_consistency(
                responses_data=[q.get("response", {}) for q in postulation_data.get("questions", [])],
                postulation_context=postulation_data
            )
            
            # Paso 3: Evaluación final
            final_evaluation = await self.execute_step(
                step_type=StepType.VALIDATION,
                step_name="Final Evaluation",
                step_description="Evaluación final de la postulación completa",
                input_data={
                    "individual_validations": individual_validations,
                    "consistency_validation": consistency_validation,
                    "postulation_data": postulation_data,
                    "step": 3,
                    "type": "final_evaluation"
                }
            )
            
            return {
                "status": "success",
                "postulation_id": postulation_data.get("postulation_id"),
                "final_validation": {
                    "individual_scores": [v["validation_results"]["overall_score"] for v in individual_validations],
                    "average_individual_score": sum([v["validation_results"]["overall_score"] for v in individual_validations]) / len(individual_validations) if individual_validations else 0,
                    "consistency_score": consistency_validation["consistency_results"]["overall_consistency_score"],
                    "final_score": final_evaluation.output_data.get("final_score", 0),
                    "overall_assessment": final_evaluation.output_data.get("assessment", ""),
                    "critical_issues": final_evaluation.output_data.get("critical_issues", []),
                    "final_recommendations": final_evaluation.output_data.get("recommendations", [])
                },
                "individual_validations": individual_validations,
                "consistency_validation": consistency_validation
            }
            
        except Exception as e:
            return {
                "status": "error",
                "postulation_id": postulation_data.get("postulation_id"),
                "error": str(e)
            } 