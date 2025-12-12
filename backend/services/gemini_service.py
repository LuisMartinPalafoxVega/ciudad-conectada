from google import genai
import os
import json
from typing import List, Dict


class GeminiService:
    def __init__(self):
        # Usa GEMINI_API_KEY automáticamente
        self.client = genai.Client()

    def verificar_duplicado(
        self,
        nuevo_titulo: str,
        nueva_descripcion: str,
        nueva_lat: float,
        nueva_lng: float,
        reportes_cercanos: List[Dict]
    ) -> Dict:

        # Si no hay reportes para comparar
        if not reportes_cercanos:
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }

        prompt = self._construir_prompt(
            nuevo_titulo,
            nueva_descripcion,
            nueva_lat,
            nueva_lng,
            reportes_cercanos
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return self._parsear_respuesta(response.text)

        except Exception as e:
            print("❌ Error en Gemini:", e)
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": [],
                "error": str(e)
            }

    def _construir_prompt(
        self,
        nuevo_titulo: str,
        nueva_descripcion: str,
        nueva_lat: float,
        nueva_lng: float,
        reportes_cercanos: List[Dict]
    ) -> str:

        texto_reportes = ""
        for r in reportes_cercanos:
            texto_reportes += (
                f"- ID: {r['id']}\n"
                f"  Título: {r['titulo']}\n"
                f"  Descripción: {r['descripcion']}\n"
                f"  Latitud: {r.get('latitud', r.get('lat'))}\n"
                f"  Longitud: {r.get('longitud', r.get('lng'))}\n\n"
            )

        prompt = f"""
Analiza si un nuevo reporte es duplicado.

Un reporte es duplicado si:
- Describe el mismo problema
- Está en la misma ubicación o muy cerca
- Tiene título/descripción similares

Responde SOLO con JSON válido.

Formato:

{{
  "es_duplicado": true/false,
  "similitud": número 0-100,
  "reportes_similares": [
      {{
        "id": número,
        "titulo": "texto",
        "similitud": número
      }}
  ]
}}

Nuevo reporte:
Título: "{nuevo_titulo}"
Descripción: "{nueva_descripcion}"
Latitud: {nueva_lat}
Longitud: {nueva_lng}

Reportes cercanos:
{texto_reportes}

Devuelve SOLO el JSON.
"""
        return prompt

    def _parsear_respuesta(self, texto: str) -> Dict:
        texto = texto.strip()

        # Quitar bloques ``` de Gemini
        if texto.startswith("```json"):
            texto = texto[len("```json"):].strip()
        if texto.startswith("```"):
            texto = texto[3:].strip()
        if texto.endswith("```"):
            texto = texto[:-3].strip()

        try:
            return json.loads(texto)
        except:
            print("⚠️ Gemini envió JSON inválido:", texto)
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }


# Instancia global
gemini_service = GeminiService()
