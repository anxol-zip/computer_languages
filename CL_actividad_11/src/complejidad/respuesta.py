# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Limpieza de la respuesta del modelo.
#
# Aunque el prompt pide "sin bloques de markdown", el modelo casi siempre envuelve el
# codigo en ```lenguaje ... ``` y a veces agrega texto antes o despues. Pasa tambien en
# el ejemplo del profesor: ejemplo_profesor/clases-1_comentado.cpp empieza con
# "**Analisis de complejidad algoritmica**", asi que ese archivo .cpp ya no compila.
# Aqui se recupera solo el codigo, para que el archivo que regresa la API sea valido.

import re

BLOQUE_DE_CODIGO = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)


def limpiar_respuesta(texto: str) -> str:
    bloques = BLOQUE_DE_CODIGO.findall(texto)
    if bloques:
        # si hay varios bloques, el que trae el codigo comentado es el mas largo
        codigo = max(bloques, key=len)
    else:
        codigo = texto
    return codigo.strip("\n") + "\n"
