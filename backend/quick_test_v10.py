#!/usr/bin/env python3
"""
Test Rápido AgentOS V10 - Verificación Básica
Test rápido para verificar que el sistema esté funcionando
"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8000"

async def quick_test():
    """Test rápido del sistema"""
    print("🚀 TEST RÁPIDO AGENTOS V10")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Verificar que el servidor responde
        print("\n1️⃣ Verificando servidor...")
        try:
            async with session.get(f"{BASE_URL}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Servidor operativo - Versión: {data.get('version')}")
                else:
                    print(f"❌ Error en servidor - Status: {resp.status}")
                    return
        except Exception as e:
            print(f"❌ No se puede conectar al servidor: {e}")
            print("   Asegúrate de que el contenedor Docker esté corriendo:")
            print("   docker-compose up -d")
            return
        
        # Test 2: Verificar agentes cognitivos
        print("\n2️⃣ Verificando agentes cognitivos...")
        try:
            async with session.get(f"{BASE_URL}/api/cognitive/agents") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    agents = data.get('cognitive_agents', {})
                    print(f"✅ {len(agents)} agentes cognitivos activos")
                    for agent in agents.keys():
                        print(f"   - {agent.capitalize()} Agent")
                else:
                    print(f"❌ Error obteniendo agentes - Status: {resp.status}")
        except Exception as e:
            print(f"❌ Error en agentes: {e}")
        
        # Test 3: Verificar herramientas MCP
        print("\n3️⃣ Verificando herramientas MCP...")
        try:
            async with session.get(f"{BASE_URL}/api/tools/real") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tools_count = data.get('total_tools', 0)
                    print(f"✅ {tools_count} herramientas MCP disponibles")
                    
                    categories = data.get('categories', {})
                    for category, count in categories.items():
                        if count > 0:
                            print(f"   - {category}: {count} herramientas")
                else:
                    print(f"❌ Error obteniendo herramientas - Status: {resp.status}")
        except Exception as e:
            print(f"❌ Error en herramientas: {e}")
        
        # Test 4: Test rápido de API V1
        print("\n4️⃣ Probando API V1...")
        try:
            payload = {
                "query": "¿Qué es un agente IA?",
                "context": {},
                "priority": "normal",
                "optimization_level": "balanced"
            }
            
            start_time = time.time()
            async with session.post(f"{BASE_URL}/api/v1/execute", json=payload) as resp:
                execution_time = time.time() - start_time
                
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ API V1 funcional - Tiempo: {execution_time:.2f}s")
                    print(f"   Success: {result.get('success')}")
                else:
                    print(f"❌ Error en API V1 - Status: {resp.status}")
        except Exception as e:
            print(f"❌ Error en API V1: {e}")
        
        # Test 5: Test rápido de API V2
        print("\n5️⃣ Probando API V2...")
        try:
            payload = {
                "query": "Crea un resumen sobre IA",
                "context": {},
                "priority": "normal",
                "optimization_level": "balanced",
                "trackable": True
            }
            
            async with session.post(f"{BASE_URL}/api/v2/tasks/start", json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    task_id = result.get('task_id')
                    print(f"✅ API V2 funcional - Task ID: {task_id}")
                else:
                    print(f"❌ Error en API V2 - Status: {resp.status}")
        except Exception as e:
            print(f"❌ Error en API V2: {e}")
        
        # Test 6: Verificar métricas del sistema
        print("\n6️⃣ Verificando métricas...")
        try:
            async with session.get(f"{BASE_URL}/api/v2/system/metrics") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    health = data.get('health', {})
                    print(f"✅ Sistema saludable:")
                    for component, status in health.items():
                        print(f"   - {component}: {status}")
                else:
                    print(f"❌ Error obteniendo métricas - Status: {resp.status}")
        except Exception as e:
            print(f"❌ Error en métricas: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 TEST RÁPIDO COMPLETADO")
    print("=" * 40)
    print("✅ Si todos los tests pasaron, el sistema está operativo")
    print("❌ Si hay errores, ejecuta el test completo: python3 test_complete_system_v10.py")

if __name__ == "__main__":
    asyncio.run(quick_test()) 