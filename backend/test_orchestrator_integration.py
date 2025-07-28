#!/usr/bin/env python3
"""
Test de Integración del Orquestador - Sistema Unificado AgentOS
Verifica cómo funciona realmente el sistema unificado
"""

import asyncio
import json
import requests
import time

def test_api_endpoints():
    """Probar endpoints de la API"""
    print("🌐 PROBANDO ENDPOINTS DE LA API")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Endpoint raíz
    print("\n1️⃣ Probando endpoint raíz...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Health check
    print("\n2️⃣ Probando health check...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 3: Status del sistema
    print("\n3️⃣ Probando status del sistema...")
    response = requests.get(f"{base_url}/api/v1/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 4: Información de arquitectura
    print("\n4️⃣ Probando información de arquitectura...")
    response = requests.get(f"{base_url}/api/v1/info/architecture")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_orchestrator_execution():
    """Probar ejecución del orquestador"""
    print("\n🎼 PROBANDO EJECUCIÓN DEL ORQUESTADOR")
    print("=" * 45)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Tarea simple
    print("\n1️⃣ Probando tarea simple...")
    payload = {
        "query": "Explica qué es la inteligencia artificial",
        "context": {},
        "priority": "normal",
        "optimization_level": "balanced"
    }
    
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/execute", json=payload)
    execution_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Tiempo de ejecución: {execution_time:.2f} segundos")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Tarea compleja
    print("\n2️⃣ Probando tarea compleja...")
    payload = {
        "query": "Investiga las tendencias de IA en 2024, analiza los datos y crea un resumen ejecutivo",
        "context": {"year": "2024", "focus": "trends"},
        "priority": "high",
        "optimization_level": "aggressive"
    }
    
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/execute", json=payload)
    execution_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Tiempo de ejecución: {execution_time:.2f} segundos")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_debug_endpoints():
    """Probar endpoints de debug"""
    print("\n🔧 PROBANDO ENDPOINTS DE DEBUG")
    print("=" * 35)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Debug del orquestador
    print("\n1️⃣ Probando debug del orquestador...")
    response = requests.get(f"{base_url}/api/v1/debug/orchestrator")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Test de orquestación
    print("\n2️⃣ Probando test de orquestación...")
    response = requests.post(f"{base_url}/api/v1/debug/test-orchestration")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def analyze_orchestrator_logs():
    """Analizar logs del orquestador"""
    print("\n📋 ANALIZANDO LOGS DEL ORQUESTADOR")
    print("=" * 40)
    
    import subprocess
    
    try:
        # Obtener logs del contenedor
        result = subprocess.run([
            "docker", "logs", "mvp_ai_agent-backend-1", "--tail", "50"
        ], capture_output=True, text=True)
        
        logs = result.stdout
        
        # Buscar líneas relacionadas con el orquestador
        orchestrator_lines = [line for line in logs.split('\n') if 'orchestrator' in line.lower()]
        
        print(f"📊 Logs del orquestador encontrados: {len(orchestrator_lines)}")
        
        for i, line in enumerate(orchestrator_lines[-10:], 1):  # Últimas 10 líneas
            print(f"{i}. {line}")
            
    except Exception as e:
        print(f"❌ Error obteniendo logs: {e}")

if __name__ == "__main__":
    print("🧪 TEST DE INTEGRACIÓN DEL ORQUESTADOR")
    print("=" * 50)
    
    # Probar endpoints
    test_api_endpoints()
    
    # Probar ejecución
    test_orchestrator_execution()
    
    # Probar debug
    test_debug_endpoints()
    
    # Analizar logs
    analyze_orchestrator_logs()
    
    print("\n🎉 TEST DE INTEGRACIÓN COMPLETADO") 