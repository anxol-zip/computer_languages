# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Conexion con el modelo de lenguaje. Cumple el papel de generate_response() del
# notebook del profesor, pero en lugar de un modelo local (Ollama con llama3.2) usa la
# API de Gemini en la nube, con la libreria oficial google-genai, igual que en el
# taller "Construye tu primer chatbot con IA". Responde en segundos y no consume
# recursos de la computadora. Necesita la variable de entorno GOOGLE_API_KEY (se
# crea gratis en aistudio.google.com).
#
# A diferencia del notebook, si algo falla se lanza un error en vez de regresar el
# mensaje como si fuera la respuesta, para que el endpoint no entregue un archivo
# con el texto del error.
#
# Variables de entorno:
#   GOOGLE_API_KEY      API key de Gemini (obligatoria)
#   CL_MODELO           modelo principal                  (gemini-flash-latest)
#   CL_MODELO_RESPALDO  modelo si el principal esta saturado (gemini-flash-lite-latest)

import asyncio
import os

from google import genai
from google.genai import errors, types

MODELO = os.getenv("CL_MODELO", "gemini-flash-latest")
MODELO_RESPALDO = os.getenv("CL_MODELO_RESPALDO", "gemini-flash-lite-latest")

# El rol va como system instruction: es texto que el modelo recibe antes del prompt
# y define quien es y como responde (Parte 1 del taller). Es la primera linea del
# template del profesor.
SISTEMA = "Eres un experto en análisis de complejidad algorítmica."


class ErrorDelModelo(Exception):
    """El modelo no esta disponible o regreso algo que no se puede usar."""

    def __init__(self, mensaje: str, codigo_http: int = 503):
        super().__init__(mensaje)
        self.codigo_http = codigo_http


def explicar_error(error: errors.APIError, modelo: str) -> ErrorDelModelo:
    """Traduce los errores comunes de la API, como explicar_error() del taller."""
    if error.code == 429:
        return ErrorDelModelo("Se alcanzo el limite de uso de Gemini. Espera un minuto; si persiste, "
                              f"se acabo la cuota diaria de {modelo}. Detalle: {error.message}", 429)
    if error.code == 503:
        return ErrorDelModelo(f"Gemini esta saturado en este momento; intenta de nuevo en unos minutos. "
                              f"Detalle: {error.message}")
    if error.code in (400, 401, 403):
        return ErrorDelModelo(f"Problema con la API key de Gemini o con la solicitud: {error.message}")
    return ErrorDelModelo(f"Error {error.code} de Gemini: {error.message}")


async def generar_respuesta(prompt: str) -> tuple:
    """Regresa (texto de la respuesta, nombre del modelo que contesto)."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise ErrorDelModelo("Falta la variable de entorno GOOGLE_API_KEY con la API key de Gemini.")

    cliente = genai.Client()    # toma la API key de GOOGLE_API_KEY
    config = types.GenerateContentConfig(system_instruction=SISTEMA, temperature=0)

    # 429 = muchas solicitudes seguidas (como en el taller) y 503 = el modelo esta
    # saturado. Los dos son temporales: se reintenta una vez con el modelo principal y,
    # si sigue sin responder, una vez mas con el de respaldo.
    intentos = [(MODELO, 0), (MODELO, 10), (MODELO_RESPALDO, 0)]
    for modelo, espera in intentos:
        await asyncio.sleep(espera)
        try:
            respuesta = await cliente.aio.models.generate_content(
                model=modelo, contents=prompt, config=config,
            )
        except errors.APIError as error:
            if error.code in (429, 503) and modelo != MODELO_RESPALDO:
                continue
            raise explicar_error(error, modelo)
        if not respuesta.text:
            raise ErrorDelModelo("Gemini regreso una respuesta vacia.")
        return respuesta.text, modelo
