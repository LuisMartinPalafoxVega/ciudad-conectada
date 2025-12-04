"""
Script de prueba para verificar que el sistema de urgencia funciona
Ejecutar desde: python test_urgencia.py
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar API Key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ ERROR: ANTHROPIC_API_KEY no está definida en .env")
    exit(1)

print("✅ ANTHROPIC_API_KEY encontrada")

# Intentar importar y probar la librería
try:
    from anthropic import Anthropic
    print("✅ Librería anthropic importada correctamente")
    
    # Crear cliente
    client = Anthropic(api_key=api_key)
    print("✅ Cliente de Anthropic inicializado")
    
    # Prueba simple
    print("\n🧪 Haciendo prueba de conexión...")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Responde brevemente: ¿qué es una fuga de agua?"
            }
        ]
    )
    
    print("✅ Conexión exitosa a Claude API!")
    print(f"\n📝 Respuesta de prueba:\n{message.content[0].text}")
    
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("   Ejecuta: pip install -r requirements.txt")
    exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("   Verifica que:")
    print("   1. ANTHROPIC_API_KEY es correcta")
    print("   2. Tienes conexión a internet")
    print("   3. Tu cuenta de Anthropic tiene saldo/cuota")
    exit(1)

print("\n" + "="*50)
print("✅ ¡Sistema de IA listo para usar!")
print("="*50)
