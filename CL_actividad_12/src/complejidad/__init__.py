# Actividad 11 - Lenguajes de Computacion (reutilizada en la Actividad 12)
# Angel Rugerio Jimenez  #201720
#
# Analizador de complejidad linea por linea para programas en Python.
#
# El analisis es un pipeline de cuatro etapas, una por modulo:
#
#   codigo --escaner--> lineas logicas --arbol--> arbol de bloques
#          --analizador--> arbol con complejidades --reporte--> archivo anotado
#
# notacion.py tiene la representacion de una complejidad que comparten las etapas,
# y rutas.py expone el analisis como endpoints de FastAPI.

from complejidad.analizador import Analizador
from complejidad.arbol import construir_arbol
from complejidad.escaner import escanear
from complejidad.notacion import SIMBOLOS, UNO
from complejidad.reporte import anotar_lineas, resumen_final


def analizar(codigo: str, modo: str) -> str:
    """Regresa el programa anotado con su complejidad. modo: "peor" o "mejor"."""
    if modo not in SIMBOLOS:
        raise ValueError(f"Modo desconocido: {modo}")

    lineas = codigo.splitlines()
    logicas = escanear(lineas)                                  # etapa 1
    raiz = construir_arbol(logicas)                             # etapa 2
    Analizador(raiz, modo).analizar_bloque(                     # etapa 3
        raiz.hijos, UNO, {"funcion": None, "recursion": None, "salida": False})
    salida = anotar_lineas(lineas, raiz)                        # etapa 4
    bloque = resumen_final(raiz, modo)

    return "\n".join(salida + bloque) + "\n"
