from google import genai
import os
import json
from typing import List, Dict

class GeminiService:
    def __init__(self):
        # El cliente ya toma GEMINI_API_KEY del entorno
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

    def _parsear_respuesta(self, texto: str) -> Dict:
        texto = texto.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]

        try:
            return json.loads(texto)
        except:
            return {
                "es_duplicado": False,
                "similitud": 0,
                "reportes_similares": []
            }
