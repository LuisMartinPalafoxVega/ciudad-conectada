import google.generativeai as genai
import os
from typing import List, Dict, Optional
import json

# Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    
    def verificar_duplicado(
        self,
        nuevo_titulo: str,
        nueva_descripcion: str,
        nueva_lat: float,
        nueva_lng: float,
        reportes_cercanos: List[Dict]
    ) -> Dict:
        """
        Verifica si un reporte es duplicado usando Gemini
        
        Returns:
            {
                "es_duplicado": bool,
                "similitud": float (0-100),
                "reportes_similares": [
                    {
                        "id": int,
                        "titulo": str,
                        "similitud": float,
                        "razon": str
                    }
                ]
            }
        """
        
        if not reportes_cercanos:
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }
        
        # Construir prompt para Gemini
        prompt = self._construir_prompt(
            nuevo_titulo,
            nueva_descripcion,
            nueva_lat,
            nueva_lng,
            reportes_cercanos
        )
        
        try:
            response = self.model.generate_content(prompt)
            resultado = self._parsear_respuesta(response.text)
            return resultado
            
        except Exception as e:
            print(f"❌ Error en Gemini: {e}")
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": [],
                "error": str(e)
            }
    
    def _construir_prompt(
        self,
        titulo: str,
        descripcion: str,
        lat: float,
        lng: float,
        reportes: List[Dict]
    ) -> str:
        """Construye el prompt para Gemini"""
        
        reportes_texto = ""
        for i, r in enumerate(reportes, 1):
            dist_km = self._calcular_distancia(lat, lng, r['latitud'], r['longitud'])
            reportes_texto += f"""
Reporte {i}:
- ID: {r['id']}
- Título: {r['titulo']}
- Descripción: {r['descripcion']}
- Distancia: {dist_km:.2f} km
- Estado: {r['estado']}
---
"""
        
        prompt = f"""
Eres un asistente que detecta reportes ciudadanos duplicados.

NUEVO REPORTE:
- Título: {titulo}
- Descripción: {descripcion}
- Ubicación: Lat {lat}, Lng {lng}

REPORTES EXISTENTES EN LA ZONA:
{reportes_texto}

TAREA:
Analiza si el nuevo reporte es duplicado de alguno existente. Considera:
1. **Similitud del problema**: ¿Hablan del mismo problema? (bache, fuga, alumbrado, etc)
2. **Ubicación**: ¿Están en el mismo lugar o muy cerca?
3. **Descripción**: ¿Describen el mismo incidente con palabras diferentes?

IMPORTANTE:
- Un bache en "Calle X esquina Y" es el MISMO que "hoyo en X y Y"
- "Fuga de agua en Hidalgo" es IGUAL a "derrame de agua en calle Hidalgo"
- Si la distancia es > 0.1 km, probablemente NO son duplicados (a menos que sea muy obvio)

RESPONDE EN FORMATO JSON:
{{
    "es_duplicado": true/false,
    "similitud": 0-100,
    "reportes_similares": [
        {{
            "id": número,
            "titulo": "título del reporte",
            "similitud": 0-100,
            "razon": "explicación breve de por qué es similar"
        }}
    ]
}}

SOLO responde con el JSON, sin texto adicional.
"""
        return prompt
    
    def _parsear_respuesta(self, texto: str) -> Dict:
        """Extrae el JSON de la respuesta de Gemini"""
        try:
            # Limpiar respuesta (a veces Gemini agrega ```json```)
            texto = texto.strip()
            if texto.startswith("```json"):
                texto = texto[7:]
            if texto.startswith("```"):
                texto = texto[3:]
            if texto.endswith("```"):
                texto = texto[:-3]
            
            resultado = json.loads(texto.strip())
            
            # Validar estructura
            if "es_duplicado" not in resultado:
                resultado["es_duplicado"] = False
            if "similitud" not in resultado:
                resultado["similitud"] = 0
            if "reportes_similares" not in resultado:
                resultado["reportes_similares"] = []
            
            return resultado
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de Gemini: {e}")
            print(f"Texto recibido: {texto}")
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }
    
    def _calcular_distancia(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcula distancia en km usando fórmula de Haversine"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

# Instancia global
gemini_service = GeminiService()