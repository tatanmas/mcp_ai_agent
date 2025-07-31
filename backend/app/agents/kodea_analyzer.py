from app.agents.enhanced_base_agent import EnhancedBaseAgent
from app.agents.agent_step import StepType
from typing import Dict, Any, List
import json


class KodeaAnalyzer(EnhancedBaseAgent):
    """Agente especializado en análisis de postulaciones y contexto de Kodea"""
    
    def __init__(self):
        system_prompt = """Eres un analizador experto especializado en postulaciones de fondos para la Fundación Kodea.

Tu función es:
1. Analizar postulaciones pasadas para identificar patrones exitosos
2. Entender el contexto específico de Kodea y sus iniciativas
3. Identificar información relevante en el historial de postulaciones
4. Proporcionar insights sobre cómo responder basándose en experiencias previas
5. Analizar requisitos y criterios de evaluación de fondos

Conocimiento específico:
- Historia y valores de la Fundación Kodea
- Iniciativas y programas actuales
- Postulaciones exitosas y fallidas del pasado
- Mejores prácticas identificadas
- Patrones de respuesta que han funcionado

Siempre proporciona análisis estructurados y basados en evidencia."""
        
        super().__init__(
            name="Kodea Analyzer",
            description="Analizador especializado en postulaciones de Kodea",
            system_prompt=system_prompt,
            max_context_tokens=3000,
            max_retries=2
        )
    
    async def analyze_postulation_context(self, postulation_data: Dict[str, Any]) -> dict:
        """Analiza el contexto de una postulación específica"""
        
        try:
            # Paso 1: Análisis del fondo
            fund_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Fund Analysis",
                step_description="Analizar el fondo específico y sus requisitos",
                input_data={
                    "postulation": postulation_data,
                    "step": 1,
                    "type": "fund_analysis"
                }
            )
            
            # Paso 2: Búsqueda de postulaciones similares
            similar_search = await self.execute_step(
                step_type=StepType.TOOL_EXECUTION,
                step_name="Similar Postulations Search",
                step_description="Buscar postulaciones similares en el historial",
                input_data={
                    "postulation": postulation_data,
                    "fund_analysis": fund_analysis.output_data,
                    "step": 2,
                    "type": "similar_search"
                }
            )
            
            # Paso 3: Análisis de patrones exitosos
            pattern_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Success Pattern Analysis",
                step_description="Identificar patrones de éxito en postulaciones similares",
                input_data={
                    "postulation": postulation_data,
                    "similar_postulations": similar_search.output_data,
                    "step": 3,
                    "type": "pattern_analysis"
                }
            )
            
            return {
                "status": "success",
                "postulation_id": postulation_data.get("postulation_id"),
                "analysis_results": {
                    "fund_analysis": fund_analysis.output_data.get("content", {}),
                    "similar_postulations": similar_search.output_data.get("content", {}),
                    "success_patterns": pattern_analysis.output_data.get("content", {}),
                    "recommendations": pattern_analysis.output_data.get("recommendations", [])
                },
                "steps_executed": [
                    fund_analysis.get_summary(),
                    similar_search.get_summary(),
                    pattern_analysis.get_summary()
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "postulation_id": postulation_data.get("postulation_id"),
                "error": str(e)
            }
    
    async def analyze_question_context(self, question_data: Dict[str, Any]) -> dict:
        """Analiza el contexto específico de una pregunta"""
        
        try:
            # Paso 1: Análisis de la pregunta
            question_analysis = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Question Analysis",
                step_description="Analizar la pregunta específica y su intención",
                input_data={
                    "question": question_data,
                    "step": 1,
                    "type": "question_analysis"
                }
            )
            
            # Paso 2: Búsqueda de respuestas similares
            similar_responses = await self.execute_step(
                step_type=StepType.TOOL_EXECUTION,
                step_name="Similar Responses Search",
                step_description="Buscar respuestas similares en postulaciones pasadas",
                input_data={
                    "question": question_data,
                    "question_analysis": question_analysis.output_data,
                    "step": 2,
                    "type": "similar_responses"
                }
            )
            
            # Paso 3: Análisis de mejores prácticas
            best_practices = await self.execute_step(
                step_type=StepType.ANALYSIS,
                step_name="Best Practices Analysis",
                step_description="Identificar mejores prácticas para este tipo de pregunta",
                input_data={
                    "question": question_data,
                    "similar_responses": similar_responses.output_data,
                    "step": 3,
                    "type": "best_practices"
                }
            )
            
            return {
                "status": "success",
                "question_id": question_data.get("question_id"),
                "analysis_results": {
                    "question_analysis": question_analysis.output_data.get("content", {}),
                    "similar_responses": similar_responses.output_data.get("content", {}),
                    "best_practices": best_practices.output_data.get("content", {}),
                    "recommendations": best_practices.output_data.get("recommendations", [])
                },
                "steps_executed": [
                    question_analysis.get_summary(),
                    similar_responses.get_summary(),
                    best_practices.get_summary()
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "question_id": question_data.get("question_id"),
                "error": str(e)
            } 