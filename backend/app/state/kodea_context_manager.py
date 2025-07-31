from typing import List, Dict, Any, Optional
import json
import os
import re
from datetime import datetime
from pathlib import Path
from app.core.llm import LLMClient


class KodeaContextManager:
    """Gestor de contextos específico para el sistema de postulaciones de Kodea"""
    
    def __init__(self, memoria_path: str = None):
        # Si no se especifica ruta, buscar en backend/memoria relativo al directorio actual
        if memoria_path is None:
            # Buscar el directorio memoria desde diferentes ubicaciones posibles
            possible_paths = [
                Path("memoria"),  # Desde directorio raíz
                Path("backend/memoria"),  # Desde directorio raíz
                Path(__file__).parent.parent.parent / "memoria",  # Desde el archivo actual
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.memoria_path = path
                    break
            else:
                # Si no se encuentra, usar el directorio actual
                self.memoria_path = Path("memoria")
        else:
            self.memoria_path = Path(memoria_path)
        
        self.contextos_info = {}
        self.contextos_content = {}
        self.postulaciones_pasadas = {}
        self.llm_client = LLMClient()  # Cliente LLM para selección inteligente
        self.initiatives = [
            "Programa de Programación Escolar",
            "Bootcamps Tecnológicos", 
            "Mentorías",
            "Mujeres en Tech",
            "Zonas Rurales",
            "Personas con Discapacidad"
        ]
        
        # Cargar información de contextos
        self._load_contextos_info()
        self._load_contextos_content()
    
    def _load_contextos_info(self):
        """Carga la información de contextos desde contextos.json"""
        contextos_file = self.memoria_path / "contextos.json"
        if contextos_file.exists():
            with open(contextos_file, 'r', encoding='utf-8') as f:
                self.contextos_info = json.load(f)
        else:
            print(f"⚠️ Archivo contextos.json no encontrado en {self.memoria_path}")
    
    def _load_contextos_content(self):
        """Carga el contenido de todos los archivos de contexto"""
        if not self.contextos_info:
            print("⚠️ No se encontró información de contextos")
            return
            
        for contexto in self.contextos_info:
            nombre = contexto.get("nombre")
            if nombre:
                file_path = self.memoria_path / f"{nombre}.md"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.contextos_content[nombre] = f.read()
                else:
                    print(f"⚠️ Archivo {nombre}.md no encontrado")
    
    def identify_initiative(self, postulation_data: Dict[str, Any]) -> str:
        """Identifica la iniciativa de la postulación"""
        initiative = postulation_data.get("initiative", "")
        
        # Buscar coincidencias exactas
        for initiative_name in self.initiatives:
            if initiative_name.lower() in initiative.lower():
                return initiative_name
        
        # Si no hay coincidencia exacta, buscar palabras clave
        initiative_keywords = {
            "Programa de Programación Escolar": ["programación", "escolar", "escuela", "estudiantes"],
            "Bootcamps Tecnológicos": ["bootcamp", "intensivo", "formación", "tecnológico"],
            "Mentorías": ["mentor", "mentoría", "acompañamiento", "guía"],
            "Mujeres en Tech": ["mujeres", "femenino", "género", "tech"],
            "Zonas Rurales": ["rural", "campo", "comunidad", "remoto"],
            "Personas con Discapacidad": ["discapacidad", "inclusivo", "accesibilidad"]
        }
        
        for initiative_name, keywords in initiative_keywords.items():
            for keyword in keywords:
                if keyword.lower() in initiative.lower():
                    return initiative_name
        
        # Default
        return "Programa de Programación Escolar"
    
    def get_initiative_context(self, initiative: str) -> Dict[str, Any]:
        """Obtiene el contexto específico de una iniciativa"""
        # Contexto base de la organización
        org_context = self.contextos_content.get("kodea_organizacion", "")
        
        # Buscar postulaciones pasadas de la iniciativa
        initiative_postulations = self._get_initiative_postulations(initiative)
        
        return {
            "initiative": initiative,
            "organization_context": org_context,
            "past_postulations": initiative_postulations,
            "initiative_specific_context": self._get_initiative_specific_context(initiative)
        }
    
    def _get_initiative_postulations(self, initiative: str) -> List[Dict[str, Any]]:
        """Obtiene postulaciones pasadas de una iniciativa específica"""
        # Por ahora retornamos un ejemplo, esto debería venir de la base de datos
        return [
            {
                "postulation_id": f"{initiative}_2023_001",
                "fund_name": "Fondo Basal 2023",
                "status": "approved",
                "questions_and_answers": [
                    {
                        "question": "Describa la iniciativa y su impacto",
                        "answer": f"La iniciativa {initiative} ha beneficiado a más de 10,000 estudiantes...",
                        "quality_score": 9.2
                    }
                ]
            }
        ]
    
    def _get_initiative_specific_context(self, initiative: str) -> str:
        """Obtiene contexto específico de la iniciativa"""
        # Aquí se podrían cargar archivos específicos por iniciativa
        initiative_contexts = {
            "Programa de Programación Escolar": "Programa que lleva programación a escuelas públicas...",
            "Bootcamps Tecnológicos": "Formación intensiva en habilidades digitales...",
            "Mentorías": "Conectamos estudiantes con profesionales del sector tech...",
            "Mujeres en Tech": "Programa específico para promover la participación femenina...",
            "Zonas Rurales": "Llevamos tecnología a comunidades remotas...",
            "Personas con Discapacidad": "Programas inclusivos de educación tecnológica..."
        }
        return initiative_contexts.get(initiative, "")
    
    async def select_contexts_with_llm(self, question: str, initiative: str = None) -> Dict[str, Any]:
        """
        Selecciona contextos relevantes usando LLM según las reglas de contextos.md
        """
        try:
            # Construir descripción de contextos disponibles
            contextos_disponibles = []
            for contexto in self.contextos_info:
                nombre = contexto.get("nombre", "")
                descripcion = contexto.get("descripcion_corta", "")
                if nombre in self.contextos_content:
                    contextos_disponibles.append(f"- {nombre}: {descripcion}")
            
            contextos_disponibles_text = "\n".join(contextos_disponibles)
            
            # Prompt según las reglas de contextos.md
            prompt = f"""Eres un agente experto en asistencia a postulaciones de fondos. Tu objetivo es responder preguntas o resolver tareas relacionadas con fondos, bases, formularios, requisitos, criterios de evaluación, procesos administrativos, reglamentos y otras áreas relevantes.

Para poder responder de forma precisa, cuentas con múltiples contextos de conocimiento, cada uno definido por:

CONTEXTOS DISPONIBLES:
{contextos_disponibles_text}

REGLAS DE SELECCIÓN:
1. Analiza la pregunta/solicitud cuidadosamente
2. Identifica qué información específica se necesita
3. Selecciona SOLO los contextos que aportan información relevante
4. Prioriza contextos que contengan información específica sobre:
   - Requisitos y criterios del fondo
   - Estructura y formato de formularios
   - Información organizacional de Kodea
   - Ejemplos de postulaciones pasadas
   - Metodologías educativas

5. NO selecciones contextos irrelevantes solo porque contengan palabras similares
6. Siempre incluye el contexto de organización de Kodea si está disponible
7. Justifica tu selección explicando por qué cada contexto es relevante

PREGUNTA A ANALIZAR: {question}
INICIATIVA: {initiative or "No especificada"}

Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
{{
    "contextos_seleccionados": ["contexto1", "contexto2"],
    "justificacion": "Explicación detallada de por qué se seleccionaron estos contextos",
    "contextos_rechazados": ["contexto3"],
    "razon_rechazo": "Por qué no se seleccionaron estos contextos"
}}"""

            # Ejecutar LLM
            response = await self.llm_client.generate_response([{"role": "user", "content": prompt}])
            
            # Parsear respuesta
            return self._parse_llm_selection(response, list(self.contextos_content.keys()))
            
        except Exception as e:
            print(f"Error en selección LLM: {e}")
            # Fallback: incluir solo contexto de organización
            return {
                "contextos_seleccionados": ["kodea_organizacion"] if "kodea_organizacion" in self.contextos_content else [],
                "justificacion": f"Error en selección LLM: {str(e)}. Usando fallback.",
                "contextos_rechazados": [ctx for ctx in self.contextos_content.keys() if ctx != "kodea_organizacion"],
                "razon_rechazo": "Error en selección automática"
            }
    
    def _parse_llm_selection(self, llm_response: str, available_contexts: List[str]) -> Dict[str, Any]:
        """Parsea la respuesta del LLM para extraer contextos seleccionados"""
        try:
            # Intentar parsear como JSON
            if "{" in llm_response and "}" in llm_response:
                json_start = llm_response.find("{")
                json_end = llm_response.rfind("}") + 1
                json_str = llm_response[json_start:json_end]
                
                parsed = json.loads(json_str)
                
                # Validar que los contextos seleccionados existen
                selected = parsed.get("contextos_seleccionados", [])
                valid_selected = [ctx for ctx in selected if ctx in available_contexts]
                
                # Validar que los contextos rechazados existen
                rejected = parsed.get("contextos_rechazados", [])
                valid_rejected = [ctx for ctx in rejected if ctx in available_contexts]
                
                # Siempre incluir contexto de organización si está disponible
                if "kodea_organizacion" in available_contexts and "kodea_organizacion" not in valid_selected:
                    valid_selected.append("kodea_organizacion")
                    if "kodea_organizacion" in valid_rejected:
                        valid_rejected.remove("kodea_organizacion")
                
                return {
                    "contextos_seleccionados": valid_selected,
                    "justificacion": parsed.get("justificacion", ""),
                    "contextos_rechazados": valid_rejected,
                    "razon_rechazo": parsed.get("razon_rechazo", "")
                }
            
            # Si no es JSON válido, usar fallback
            return self._fallback_selection(available_contexts)
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return self._fallback_selection(available_contexts)
    
    def _fallback_selection(self, available_contexts: List[str]) -> Dict[str, Any]:
        """Selección de fallback cuando hay errores"""
        # Siempre incluir contexto de organización
        selected = ["kodea_organizacion"] if "kodea_organizacion" in available_contexts else []
        
        return {
            "contextos_seleccionados": selected,
            "justificacion": "Selección por fallback debido a error en LLM",
            "contextos_rechazados": [ctx for ctx in available_contexts if ctx not in selected],
            "razon_rechazo": "Error en selección automática"
        }
    
    async def build_question_context_intelligent(self, question: str, initiative_context: Dict[str, Any]) -> Dict[str, Any]:
        """Construye el contexto específico para una pregunta usando selección LLM"""
        # Seleccionar contextos usando LLM
        selection_result = await self.select_contexts_with_llm(
            question, 
            initiative_context.get("initiative")
        )
        
        selected_contexts = selection_result.get("contextos_seleccionados", [])
        
        # Construir contexto
        context_parts = []
        
        # Agregar contexto de la iniciativa
        context_parts.append(f"INICIATIVA: {initiative_context['initiative']}")
        context_parts.append(f"CONTEXTO DE INICIATIVA: {initiative_context['initiative_specific_context']}")
        
        # Agregar contextos seleccionados por LLM
        for context_name in selected_contexts:
            if context_name in self.contextos_content:
                context_parts.append(f"CONTEXTO {context_name.upper()}: {self.contextos_content[context_name]}")
        
        # Agregar postulaciones pasadas relevantes
        if initiative_context['past_postulations']:
            context_parts.append("POSTULACIONES PASADAS:")
            for postulation in initiative_context['past_postulations'][:2]:  # Solo las 2 más recientes
                context_parts.append(f"- {postulation['fund_name']}: {postulation['status']}")
                for qa in postulation['questions_and_answers']:
                    context_parts.append(f"  P: {qa['question']}")
                    context_parts.append(f"  R: {qa['answer'][:200]}...")
        
        full_context = "\n\n".join(context_parts)
        
        return {
            "context": full_context,
            "context_length": len(full_context),
            "selected_contexts": selected_contexts,
            "selection_result": selection_result,
            "initiative": initiative_context.get("initiative")
        }
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del estado de los contextos"""
        return {
            "contextos_loaded": len(self.contextos_content),
            "contextos_available": list(self.contextos_content.keys()),
            "initiatives_supported": self.initiatives,
            "memoria_path": str(self.memoria_path),
            "contextos_info": self.contextos_info
        }
    
    def add_postulation_to_history(self, postulation_data: Dict[str, Any]):
        """Agrega una postulación al historial (para futuras referencias)"""
        initiative = self.identify_initiative(postulation_data)
        postulation_id = postulation_data.get("postulation_id")
        
        if initiative not in self.postulaciones_pasadas:
            self.postulaciones_pasadas[initiative] = []
        
        self.postulaciones_pasadas[initiative].append({
            "postulation_id": postulation_id,
            "fund_name": postulation_data.get("fund_name"),
            "questions": postulation_data.get("questions", []),
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error_context(self, error: Exception, context: str = ""):
        """Agrega información de error al contexto de manera inteligente"""
        # Por ahora solo registramos el error, en el futuro se podría persistir
        error_summary = {
            "type": error.__class__.__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        print(f"Error en contexto: {error_summary}") 