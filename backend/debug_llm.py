#!/usr/bin/env python3
"""
Script de debug para el LLM
"""

import asyncio
import sys

# Agregar el directorio app al path
sys.path.append('/app')

from app.agents.kodea_coordinator import KodeaCoordinator

async def debug_llm():
    """Debug del LLM"""
    print("🔍 Debug del LLM...")
    
    try:
        # Inicializar coordinador
        coordinator = KodeaCoordinator()
        
        # Datos de prueba
        test_question = {
            "question_id": "test_q1",
            "question_text": "¿Cuáles son los requisitos para postular al fondo basal?",
            "fund_context": {
                "fund_name": "Fondo Basal 2024",
                "fund_description": "Fondo para educación tecnológica"
            },
            "initiative": "Programa de Programación Escolar",
            "conversation_id": "test_conv_002"
        }
        
        print("🧪 Procesando pregunta individual...")
        
        # Paso 1: Identificación de iniciativa
        initiative = coordinator.context_manager.identify_initiative(test_question)
        initiative_context = coordinator.context_manager.get_initiative_context(initiative)
        print(f"✅ Iniciativa: {initiative}")
        
        # Paso 2: Construcción de contexto
        question_context_result = await coordinator.context_manager.build_question_context_intelligent(
            test_question.get("question_text", ""),
            initiative_context
        )
        print(f"✅ Contexto construido: {question_context_result['context_length']} caracteres")
        
        # Paso 3: Debug del paso de análisis
        print("🧪 Debug del paso de análisis...")
        from app.agents.agent_step import StepType
        analysis_step = await coordinator.execute_step(
            StepType.ANALYSIS,
            "Question Analysis",
            "Analizar la pregunta específica",
            {
                "question": test_question,
                "question_context": question_context_result["context"],
                "selected_contexts": question_context_result["selected_contexts"],
                "selection_justification": question_context_result.get("selection_result", {}).get("justificacion", ""),
                "initiative_context": initiative_context,
                "step": 1,
                "type": "question_analysis"
            }
        )
        
        print(f"✅ Paso de análisis completado: {analysis_step.status}")
        print(f"✅ Output del análisis: {analysis_step.output_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_llm()) 