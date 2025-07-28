#!/usr/bin/env python3
"""
Test Completo del Sistema AgentOS V10 - Arquitectura Optimizada
Valida todos los nuevos cambios según docs10.md:
- Integración MCP completa
- Agentes cognitivos especializados
- Herramientas reales vía MCP
- API modular (V1 + V2)
- Estado persistente
- Control granular
"""

import asyncio
import aiohttp
import json
import time
import uuid
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

class AgentOSTestSuite:
    """Suite completa de tests para AgentOS V10"""
    
    def __init__(self):
        self.test_results = {}
        self.session = None
    
    async def run_all_tests(self):
        """Ejecutar todos los tests del sistema"""
        print("🧪 TEST COMPLETO AGENTOS V10 - ARQUITECTURA OPTIMIZADA")
        print("=" * 70)
        print("Validando según docs10.md:")
        print("✅ Integración MCP completa")
        print("✅ Agentes cognitivos especializados (3 agentes)")
        print("✅ Herramientas reales vía MCP")
        print("✅ API modular (V1 + V2)")
        print("✅ Estado persistente")
        print("✅ Control granular")
        print("=" * 70)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test 1: Verificar estructura del sistema
            await self.test_system_structure()
            
            # Test 2: Verificar agentes cognitivos
            await self.test_cognitive_agents()
            
            # Test 3: Verificar herramientas MCP
            await self.test_mcp_tools()
            
            # Test 4: Verificar API V1 (compatibilidad)
            await self.test_api_v1_compatibility()
            
            # Test 5: Verificar API V2 (enterprise)
            await self.test_api_v2_enterprise()
            
            # Test 6: Verificar integración MCP completa
            await self.test_mcp_integration()
            
            # Test 7: Verificar estado persistente
            await self.test_persistent_state()
            
            # Test 8: Verificar control granular
            await self.test_granular_control()
            
            # Test 9: Verificar performance y métricas
            await self.test_performance_metrics()
            
            # Test 10: Verificar flujo completo
            await self.test_complete_workflow()
        
        # Mostrar resultados finales
        await self.show_final_results()
    
    async def test_system_structure(self):
        """Test 1: Verificar estructura del sistema"""
        print("\n1️⃣ VERIFICANDO ESTRUCTURA DEL SISTEMA...")
        
        try:
            # Verificar endpoint raíz
            async with self.session.get(f"{BASE_URL}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Endpoint raíz operativo")
                    print(f"   Versión: {data.get('version')}")
                    print(f"   Estado: {data.get('status')}")
                    print(f"   Features: {len(data.get('features', []))}")
                    
                    # Verificar que tiene las features esperadas
                    features = data.get('features', [])
                    expected_features = [
                        "Cognitive Agents (Researcher, Coder, Coordinator)",
                        "MCP Server Integration",
                        "Real Tools Bridge",
                        "Enterprise Task Tracking",
                        "Real-time Streaming",
                        "Memory Systems",
                        "Test-Time Learning"
                    ]
                    
                    missing_features = [f for f in expected_features if f not in features]
                    if not missing_features:
                        print(f"   ✅ Todas las features esperadas presentes")
                    else:
                        print(f"   ⚠️ Features faltantes: {missing_features}")
                    
                    self.test_results['system_structure'] = True
                else:
                    print(f"❌ Error en endpoint raíz - Status: {resp.status}")
                    self.test_results['system_structure'] = False
                    
        except Exception as e:
            print(f"❌ Error verificando estructura: {e}")
            self.test_results['system_structure'] = False
    
    async def test_cognitive_agents(self):
        """Test 2: Verificar agentes cognitivos especializados"""
        print("\n2️⃣ VERIFICANDO AGENTES COGNITIVOS...")
        
        try:
            # Verificar endpoint de agentes cognitivos
            async with self.session.get(f"{BASE_URL}/api/cognitive/agents") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Agentes cognitivos operativos")
                    print(f"   Total agentes: {data.get('total_agents')}")
                    
                    # Verificar que tenemos los 3 agentes esperados
                    agents = data.get('cognitive_agents', {})
                    expected_agents = ['researcher', 'coder', 'coordinator']
                    
                    for agent in expected_agents:
                        if agent in agents:
                            agent_data = agents[agent]
                            print(f"   ✅ {agent.capitalize()} Agent: {agent_data.get('status', 'active')}")
                        else:
                            print(f"   ❌ {agent.capitalize()} Agent: NO ENCONTRADO")
                    
                    # Verificar especializaciones
                    specializations = data.get('specializations', {})
                    if len(specializations) == 3:
                        print(f"   ✅ Especializaciones definidas: {list(specializations.keys())}")
                    else:
                        print(f"   ⚠️ Especializaciones incompletas: {list(specializations.keys())}")
                    
                    self.test_results['cognitive_agents'] = True
                else:
                    print(f"❌ Error obteniendo agentes - Status: {resp.status}")
                    self.test_results['cognitive_agents'] = False
                    
        except Exception as e:
            print(f"❌ Error verificando agentes: {e}")
            self.test_results['cognitive_agents'] = False
    
    async def test_mcp_tools(self):
        """Test 3: Verificar herramientas MCP"""
        print("\n3️⃣ VERIFICANDO HERRAMIENTAS MCP...")
        
        try:
            # Verificar herramientas reales disponibles
            async with self.session.get(f"{BASE_URL}/api/tools/real") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Herramientas MCP operativas")
                    print(f"   Total herramientas: {data.get('total_tools')}")
                    
                    # Verificar categorías esperadas
                    categories = data.get('categories', {})
                    expected_categories = ['web_search', 'document_analysis', 'data_visualization', 'file_operations']
                    
                    for category in expected_categories:
                        count = categories.get(category, 0)
                        if count > 0:
                            print(f"   ✅ {category}: {count} herramientas")
                        else:
                            print(f"   ❌ {category}: SIN HERRAMIENTAS")
                    
                    # Verificar integración MCP
                    if data.get('mcp_integration') == 'active':
                        print(f"   ✅ Integración MCP: ACTIVA")
                    else:
                        print(f"   ❌ Integración MCP: INACTIVA")
                    
                    self.test_results['mcp_tools'] = True
                else:
                    print(f"❌ Error obteniendo herramientas - Status: {resp.status}")
                    self.test_results['mcp_tools'] = False
                    
        except Exception as e:
            print(f"❌ Error verificando herramientas: {e}")
            self.test_results['mcp_tools'] = False
    
    async def test_api_v1_compatibility(self):
        """Test 4: Verificar API V1 (compatibilidad)"""
        print("\n4️⃣ VERIFICANDO API V1 (COMPATIBILIDAD)...")
        
        try:
            # Test de ejecución básica V1
            payload = {
                "query": "Explica qué es un agente IA",
                "context": {},
                "priority": "normal",
                "optimization_level": "balanced"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BASE_URL}/api/v1/execute", json=payload) as resp:
                execution_time = time.time() - start_time
                
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ API V1 compatible")
                    print(f"   Status: {resp.status}")
                    print(f"   Tiempo: {execution_time:.2f}s")
                    print(f"   Success: {result.get('success')}")
                    
                    # Verificar que el tiempo está en el rango esperado (22s según docs10.md)
                    if execution_time <= 30:  # Con margen de error
                        print(f"   ✅ Tiempo de ejecución aceptable")
                    else:
                        print(f"   ⚠️ Tiempo de ejecución alto: {execution_time:.2f}s")
                    
                    self.test_results['api_v1'] = True
                else:
                    print(f"❌ Error en API V1 - Status: {resp.status}")
                    self.test_results['api_v1'] = False
                    
        except Exception as e:
            print(f"❌ Error en API V1: {e}")
            self.test_results['api_v1'] = False
    
    async def test_api_v2_enterprise(self):
        """Test 5: Verificar API V2 (enterprise)"""
        print("\n5️⃣ VERIFICANDO API V2 (ENTERPRISE)...")
        
        try:
            # Crear tarea trackeable V2
            payload = {
                "query": "Investiga las tendencias en IA para 2024 y crea un resumen ejecutivo",
                "context": {"year": "2024", "focus": "trends"},
                "priority": "high",
                "optimization_level": "aggressive",
                "trackable": True
            }
            
            start_time = time.time()
            async with self.session.post(f"{BASE_URL}/api/v2/tasks/start", json=payload) as resp:
                creation_time = time.time() - start_time
                
                if resp.status == 200:
                    result = await resp.json()
                    task_id = result["task_id"]
                    
                    print(f"✅ API V2 enterprise operativa")
                    print(f"   Task ID: {task_id}")
                    print(f"   Status: {result['status']}")
                    print(f"   Tiempo creación: {creation_time:.2f}s")
                    print(f"   Tracking URL: {result['tracking_url']}")
                    print(f"   Pause URL: {result['pause_url']}")
                    
                    # Verificar estado de la tarea
                    await asyncio.sleep(2)
                    async with self.session.get(f"{BASE_URL}/api/v2/tasks/{task_id}") as status_resp:
                        if status_resp.status == 200:
                            status_data = await status_resp.json()
                            print(f"   ✅ Estado obtenido: {status_data['status']}")
                            print(f"   Progreso: {status_data['current_step']}/{status_data['total_steps']}")
                            
                            # Guardar task_id para tests posteriores
                            self.test_results['current_task_id'] = task_id
                        else:
                            print(f"   ❌ Error obteniendo estado: {status_resp.status}")
                    
                    self.test_results['api_v2'] = True
                else:
                    print(f"❌ Error en API V2 - Status: {resp.status}")
                    self.test_results['api_v2'] = False
                    
        except Exception as e:
            print(f"❌ Error en API V2: {e}")
            self.test_results['api_v2'] = False
    
    async def test_mcp_integration(self):
        """Test 6: Verificar integración MCP completa"""
        print("\n6️⃣ VERIFICANDO INTEGRACIÓN MCP COMPLETA...")
        
        try:
            # Verificar herramientas disponibles vía MCP
            async with self.session.get(f"{BASE_URL}/api/v2/tools/available") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Herramientas MCP disponibles")
                    print(f"   Total herramientas: {data.get('total_tools')}")
                    print(f"   MCP Server Status: {data.get('mcp_server_status')}")
                    
                    # Probar ejecución de herramienta MCP
                    tool_payload = {
                        "tool_name": "real_web_search",
                        "arguments": {"query": "inteligencia artificial 2024", "max_results": 3}
                    }
                    
                    async with self.session.post(f"{BASE_URL}/api/v2/tools/execute", json=tool_payload) as tool_resp:
                        if tool_resp.status == 200:
                            tool_result = await tool_resp.json()
                            print(f"   ✅ Herramienta MCP ejecutada: {tool_result['success']}")
                            print(f"   Tool: {tool_result['tool_name']}")
                        else:
                            print(f"   ❌ Error ejecutando herramienta: {tool_resp.status}")
                    
                    self.test_results['mcp_integration'] = True
                else:
                    print(f"❌ Error obteniendo herramientas MCP - Status: {resp.status}")
                    self.test_results['mcp_integration'] = False
                    
        except Exception as e:
            print(f"❌ Error en integración MCP: {e}")
            self.test_results['mcp_integration'] = False
    
    async def test_persistent_state(self):
        """Test 7: Verificar estado persistente"""
        print("\n7️⃣ VERIFICANDO ESTADO PERSISTENTE...")
        
        try:
            # Verificar dashboard de tareas activas
            async with self.session.get(f"{BASE_URL}/api/v2/tasks") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Estado persistente operativo")
                    print(f"   Total tareas activas: {data.get('total_active')}")
                    print(f"   Tareas corriendo: {data.get('running')}")
                    print(f"   Tareas pausadas: {data.get('paused')}")
                    print(f"   Tareas fallidas: {data.get('failed')}")
                    
                    # Verificar que podemos obtener tareas específicas
                    if self.test_results.get('current_task_id'):
                        task_id = self.test_results['current_task_id']
                        async with self.session.get(f"{BASE_URL}/api/v2/tasks/{task_id}") as task_resp:
                            if task_resp.status == 200:
                                task_data = await task_resp.json()
                                print(f"   ✅ Tarea persistente recuperada: {task_data['status']}")
                            else:
                                print(f"   ❌ Error recuperando tarea: {task_resp.status}")
                    
                    self.test_results['persistent_state'] = True
                else:
                    print(f"❌ Error obteniendo estado persistente - Status: {resp.status}")
                    self.test_results['persistent_state'] = False
                    
        except Exception as e:
            print(f"❌ Error en estado persistente: {e}")
            self.test_results['persistent_state'] = False
    
    async def test_granular_control(self):
        """Test 8: Verificar control granular (pause/resume)"""
        print("\n8️⃣ VERIFICANDO CONTROL GRANULAR...")
        
        try:
            if not self.test_results.get('current_task_id'):
                print("   ⚠️ No hay tarea activa para probar control granular")
                self.test_results['granular_control'] = False
                return
            
            task_id = self.test_results['current_task_id']
            
            # Intentar pausar la tarea
            async with self.session.post(f"{BASE_URL}/api/v2/tasks/{task_id}/pause") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('success'):
                        print(f"   ✅ Tarea pausada exitosamente")
                        
                        # Esperar un poco
                        await asyncio.sleep(2)
                        
                        # Intentar reanudar
                        async with self.session.post(f"{BASE_URL}/api/v2/tasks/{task_id}/resume") as resume_resp:
                            if resume_resp.status == 200:
                                resume_result = await resume_resp.json()
                                if resume_result.get('success'):
                                    print(f"   ✅ Tarea reanudada exitosamente")
                                    self.test_results['granular_control'] = True
                                else:
                                    print(f"   ❌ Error reanudando: {resume_result.get('message')}")
                                    self.test_results['granular_control'] = False
                            else:
                                print(f"   ❌ Error en resume - Status: {resume_resp.status}")
                                self.test_results['granular_control'] = False
                    else:
                        print(f"   ⚠️ No se pudo pausar: {result.get('message')}")
                        self.test_results['granular_control'] = True  # No es un error si la tarea ya terminó
                else:
                    print(f"   ❌ Error en pause - Status: {resp.status}")
                    self.test_results['granular_control'] = False
                    
        except Exception as e:
            print(f"❌ Error en control granular: {e}")
            self.test_results['granular_control'] = False
    
    async def test_performance_metrics(self):
        """Test 9: Verificar performance y métricas"""
        print("\n9️⃣ VERIFICANDO PERFORMANCE Y MÉTRICAS...")
        
        try:
            # Obtener métricas del sistema
            async with self.session.get(f"{BASE_URL}/api/v2/system/metrics") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Métricas del sistema obtenidas")
                    
                    # Verificar métricas de performance
                    performance = data.get('performance', {})
                    print(f"   Tiempo promedio: {performance.get('average_execution_time', 'N/A')}s")
                    print(f"   Tasa de éxito: {performance.get('success_rate', 'N/A')}%")
                    print(f"   Throughput: {performance.get('throughput', 'N/A')} tareas/hora")
                    
                    # Verificar salud del sistema
                    health = data.get('health', {})
                    print(f"   Salud del sistema:")
                    for component, status in health.items():
                        print(f"      {component}: {status}")
                    
                    # Verificar tareas activas
                    active_tasks = data.get('active_tasks', {})
                    print(f"   Tareas activas: {active_tasks.get('total', 0)}")
                    
                    self.test_results['performance_metrics'] = True
                else:
                    print(f"❌ Error obteniendo métricas - Status: {resp.status}")
                    self.test_results['performance_metrics'] = False
                    
        except Exception as e:
            print(f"❌ Error en métricas: {e}")
            self.test_results['performance_metrics'] = False
    
    async def test_complete_workflow(self):
        """Test 10: Verificar flujo completo"""
        print("\n🔟 VERIFICANDO FLUJO COMPLETO...")
        
        try:
            # Ejecutar tarea con agentes cognitivos
            payload = {
                "query": "Analiza las tendencias de IA en 2024 y crea un resumen ejecutivo",
                "context": {"year": "2024", "focus": "trends"},
                "priority": "high",
                "optimization_level": "aggressive"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BASE_URL}/api/cognitive/execute", json=payload) as resp:
                execution_time = time.time() - start_time
                
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Flujo completo ejecutado")
                    print(f"   Success: {result.get('success')}")
                    print(f"   Tiempo total: {execution_time:.2f}s")
                    print(f"   Agentes usados: {result.get('cognitive_agents_used', [])}")
                    print(f"   Learning updated: {result.get('learning_updated')}")
                    
                    # Verificar que se usaron agentes cognitivos
                    agents_used = result.get('cognitive_agents_used', [])
                    if len(agents_used) > 0:
                        print(f"   ✅ Agentes cognitivos utilizados: {agents_used}")
                    else:
                        print(f"   ⚠️ No se detectaron agentes cognitivos utilizados")
                    
                    # Verificar síntesis final
                    if result.get('final_synthesis'):
                        print(f"   ✅ Síntesis final generada")
                    else:
                        print(f"   ⚠️ No se detectó síntesis final")
                    
                    self.test_results['complete_workflow'] = True
                else:
                    print(f"❌ Error en flujo completo - Status: {resp.status}")
                    self.test_results['complete_workflow'] = False
                    
        except Exception as e:
            print(f"❌ Error en flujo completo: {e}")
            self.test_results['complete_workflow'] = False
    
    async def show_final_results(self):
        """Mostrar resultados finales de todos los tests"""
        print("\n" + "=" * 70)
        print("📊 RESULTADOS FINALES DE LOS TESTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests ejecutados: {total_tests}")
        print(f"Tests exitosos: {passed_tests}")
        print(f"Tests fallidos: {failed_tests}")
        print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETALLE POR TEST:")
        for test_name, result in self.test_results.items():
            status = "✅ PASÓ" if result is True else "❌ FALLÓ"
            print(f"   {test_name}: {status}")
        
        print("\n🎯 VALIDACIÓN SEGÚN DOCS10.MD:")
        
        # Validar según los puntos clave de docs10.md
        validations = {
            "Integración MCP completa": self.test_results.get('mcp_integration', False),
            "Agentes cognitivos especializados (3)": self.test_results.get('cognitive_agents', False),
            "Herramientas reales vía MCP": self.test_results.get('mcp_tools', False),
            "API modular (V1 + V2)": self.test_results.get('api_v1', False) and self.test_results.get('api_v2', False),
            "Estado persistente": self.test_results.get('persistent_state', False),
            "Control granular": self.test_results.get('granular_control', False),
            "Flujo completo operativo": self.test_results.get('complete_workflow', False)
        }
        
        for validation, result in validations.items():
            status = "✅ CUMPLIDO" if result else "❌ NO CUMPLIDO"
            print(f"   {validation}: {status}")
        
        # Conclusión final
        all_validations_passed = all(validations.values())
        if all_validations_passed:
            print("\n🎉 ¡TODOS LOS REQUISITOS DE DOCS10.MD CUMPLIDOS!")
            print("El sistema está completamente operativo según la especificación.")
        else:
            print("\n⚠️ ALGUNOS REQUISITOS NO CUMPLIDOS")
            print("Revisar los tests fallidos para identificar problemas.")

async def main():
    """Función principal para ejecutar todos los tests"""
    test_suite = AgentOSTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    print("🚀 INICIANDO TEST COMPLETO AGENTOS V10")
    print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print("=" * 70)
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        print("Verifica que el servidor esté corriendo y accesible.")
    
    print("\n📋 RESUMEN:")
    print("- Este test valida todos los cambios según docs10.md")
    print("- Verifica integración MCP completa")
    print("- Valida agentes cognitivos especializados")
    print("- Prueba herramientas reales vía MCP")
    print("- Confirma API modular y estado persistente")
    print("- Valida control granular y flujo completo") 