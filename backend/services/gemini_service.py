from google import genai
import os
import json
from typing import List, Dict


class GeminiService:
    def __init__(self):
        # Usa la variable de entorno GEMINI_API_KEY automáticamente
        self.client = genai.Client()

    def verificar_duplicado(
        self,
        nuevo_titulo: str,
        nueva_descripcion: str,
        nueva_lat: float,
        nueva_lng: float,
        reportes_cercanos: List[Dict]
    ) -> Dict:

        if not reportes_cercanos:
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }

        # Construir prompt
        prompt = self._construir_prompt(
            nuevo_titulo,
            nueva_descripcion,
            nueva_lat,
            nueva_lng,
            reportes_cercanos
        )

        try:
            # 👉 Petición a Gemini 2.5 Flash (API nueva "genai")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            texto = response.text
            return self._parsear_respuesta(texto)

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

        # Ajustar si el back envía "latitud" y "longitud"
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
Analiza si un nuevo reporte es DUPLICADO de reportes anteriores.

Un reporte se considera duplicado cuando:
- describe el mismo problema,
- ocurre en la misma ubicación o muy cerca,
- es de la misma categoría,
- usa títulos o palabras similares.

Responde SOLO con JSON válido. Sin explicaciones.

Formato estricto:

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
Latitud: {nuevo_lat}
Longitud: {nueva_lng}

Reportes a comparar:
{texto_reportes}

Devuelve SOLO el JSON.
"""
        return prompt

    def _parsear_respuesta(self, texto: str) -> Dict:
        texto = texto.strip()

        # Eliminar bloques ``` si aparecen
        if texto.startswith("```json"):
            texto = texto[len("```json"):].strip()
        if texto.startswith("```"):
            texto = texto[3:].strip()
        if texto.endswith("```"):
            texto = texto[:-3].strip()

        try:
            return json.loads(texto)
        except Exception:
            print("⚠️ Gemini devolvió JSON inválido:", texto)
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }


# Instancia global
gemini_service = GeminiService()
