from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime


class ContextManager:
    """Gestiona la ventana de contexto para optimizar tokens"""
    
    def __init__(self, max_tokens: int = 4000, max_messages: int = 20):
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.context_window: List[Dict[str, Any]] = []
        self.system_prompts: List[str] = []
        self.important_context: List[Dict[str, Any]] = []
    
    def add_system_prompt(self, prompt: str):
        """Agrega un prompt del sistema"""
        self.system_prompts.append(prompt)
    
    def add_to_context(self, role: str, content: str, metadata: Optional[Dict] = None, priority: int = 1):
        """Agrega mensaje al contexto con prioridad"""
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "priority": priority,  # 1=alta, 2=media, 3=baja
            "timestamp": datetime.now().isoformat(),
            "estimated_tokens": self._estimate_tokens(content)
        }
        
        self.context_window.append(message)
        self._optimize_context()
    
    def add_important_context(self, key: str, content: str, expires_at: Optional[datetime] = None):
        """Agrega contexto importante que debe mantenerse"""
        important_item = {
            "key": key,
            "content": content,
            "added_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None
        }
        self.important_context.append(important_item)
    
    def get_context_window(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """Obtiene la ventana de contexto optimizada"""
        context = []
        
        # Agregar prompts del sistema
        if include_system and self.system_prompts:
            system_content = "\n\n".join(self.system_prompts)
            context.append({
                "role": "system",
                "content": system_content,
                "metadata": {"type": "system_prompts"},
                "priority": 1
            })
        
        # Agregar contexto importante
        for item in self.important_context:
            if not item.get("expires_at") or datetime.fromisoformat(item["expires_at"]) > datetime.now():
                context.append({
                    "role": "system",
                    "content": f"Contexto importante - {item['key']}: {item['content']}",
                    "metadata": {"type": "important_context", "key": item["key"]},
                    "priority": 1
                })
        
        # Agregar mensajes del contexto
        context.extend(self.context_window)
        
        return context
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del contexto actual"""
        total_tokens = sum(msg.get("estimated_tokens", 0) for msg in self.context_window)
        system_tokens = sum(self._estimate_tokens(prompt) for prompt in self.system_prompts)
        
        return {
            "total_messages": len(self.context_window),
            "total_tokens": total_tokens + system_tokens,
            "max_tokens": self.max_tokens,
            "token_usage_percentage": ((total_tokens + system_tokens) / self.max_tokens) * 100,
            "system_prompts_count": len(self.system_prompts),
            "important_context_count": len(self.important_context),
            "needs_optimization": (total_tokens + system_tokens) > self.max_tokens * 0.8
        }
    
    def _optimize_context(self):
        """Optimiza el contexto cuando se excede el límite de tokens"""
        summary = self.get_context_summary()
        
        if summary["needs_optimization"]:
            # Ordenar por prioridad y timestamp (más reciente primero)
            self.context_window.sort(key=lambda x: (x["priority"], x["timestamp"]), reverse=True)
            
            # Mantener solo los mensajes más importantes
            optimized_window = []
            current_tokens = sum(self._estimate_tokens(prompt) for prompt in self.system_prompts)
            
            for message in self.context_window:
                message_tokens = message.get("estimated_tokens", 0)
                if current_tokens + message_tokens <= self.max_tokens * 0.8:
                    optimized_window.append(message)
                    current_tokens += message_tokens
                else:
                    break
            
            self.context_window = optimized_window
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima el número de tokens en un texto (aproximación simple)"""
        # Aproximación: 1 token ≈ 4 caracteres para inglés, 2-3 para español
        return len(text) // 3
    
    def clear_context(self, keep_system: bool = True):
        """Limpia el contexto"""
        self.context_window = []
        if not keep_system:
            self.system_prompts = []
        self.important_context = []
    
    def summarize_context(self) -> str:
        """Crea un resumen del contexto para reducir tokens"""
        if len(self.context_window) <= 5:
            return "Contexto actual es corto, no necesita resumen."
        
        # Tomar los mensajes más importantes
        important_messages = [msg for msg in self.context_window if msg["priority"] == 1]
        
        if not important_messages:
            return "No hay mensajes importantes para resumir."
        
        summary_parts = []
        for msg in important_messages[-3:]:  # Últimos 3 mensajes importantes
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_parts.append(f"{role}: {content}")
        
        return f"Resumen del contexto: {' | '.join(summary_parts)}"
    
    def add_error_context(self, error: Exception, context: str = ""):
        """Agrega información de error al contexto de manera inteligente"""
        error_summary = {
            "type": error.__class__.__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        # No agregar stack traces completos, solo información relevante
        error_content = f"Error: {error_summary['type']} - {error_summary['message']}"
        if context:
            error_content += f" (Contexto: {context})"
        
        self.add_to_context(
            role="system",
            content=error_content,
            metadata={"type": "error", "error_data": error_summary},
            priority=2  # Prioridad media para errores
        )
    
    def get_relevant_context(self, query: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """Obtiene contexto relevante basado en una consulta"""
        if not self.context_window:
            return []
        
        # Búsqueda simple por palabras clave
        query_words = set(re.findall(r'\w+', query.lower()))
        
        relevant_messages = []
        for message in self.context_window:
            content_words = set(re.findall(r'\w+', message["content"].lower()))
            relevance_score = len(query_words.intersection(content_words))
            
            if relevance_score > 0:
                relevant_messages.append({
                    **message,
                    "relevance_score": relevance_score
                })
        
        # Ordenar por relevancia y prioridad
        relevant_messages.sort(key=lambda x: (x["relevance_score"], -x["priority"]), reverse=True)
        
        return relevant_messages[:max_items] 