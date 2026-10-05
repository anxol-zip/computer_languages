# Actividad 10 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Verifica por fuerza bruta la ecuacion x^n + y^n = z^n para todo
# x, y, z en {0, 1, ..., 100} y n en {1, 2, 3}, y vacia cada combinacion evaluada
# en un archivo de texto con la etiqueta "CUMPLE" o "NO CUMPLE".
#
# Es un problema decidible: el espacio de busqueda es finito (101^3 * 3 combinaciones),
# asi que el programa siempre termina y siempre da una respuesta.

import os

# ===== Elementos para archivo .txt de resultados =====
NUMERO_CUENTA = "201720"
NOMBRE = "Angel Rugerio Jimenez"
ACTIVIDAD = "Actividad 10 - Problemas decidibles y no decidibles"
MATERIA = "Lenguajes de Computacion - Otoño 2026"

RANGO = range(0, 101)   # x, y, z in {0, 1, ..., 100}
EXPONENTES = (1, 2, 3)  # n in {1, 2, 3}

ARCHIVO_RESULTADOS = f"A10_resultados_{NUMERO_CUENTA}.txt"


# ===== Funciones =====
# Definición para evaluar la expresión principal
def cumple(x: int, y: int, z: int, n: int) -> bool:
    return (x ** n + y ** n) == z ** n

# Bloque de identificación en el archivo de resultados (encabezado)
def bloque_identificacion() -> str:
    return (
        f"{str('=') * 80}"
        f"\n{MATERIA}\n"
        f"{ACTIVIDAD}\n"
        f"{NOMBRE} #{NUMERO_CUENTA}\n"
        f"Ecuacion: x^n + y^n = z^n, con x, y, z en {{0, ..., 100}} y n en {{1, 2, 3}}\n"
        f"Formato: (x, y, z), n -> CUMPLE/NO CUMPLE\n"
        f"{str('=') * 80}"
    )

# Función para evaluar y guardar TODAS las posibles combinaciones 
def evaluar_y_guardar(ruta: str) -> dict:
    # Conteo se hace igual a 0 para cada n en EXPONENTES
    conteo = {n: 0 for n in EXPONENTES}

    # Escribe los resultados en 'ruta' (el path del archivo) y regresa el conteo por n
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(bloque_identificacion() + "\n")

        # Evalúa todas las combinaciones de x, y, z y n
        for n in EXPONENTES:
            for x in RANGO:
                for y in RANGO:
                    for z in RANGO:
                        if cumple(x, y, z, n):
                            conteo[n] += 1 # Incrementa el conteo de combinaciones que cumplen la ecuación para este n
                            etiqueta = "SI CUMPLE :)"
                        else:
                            etiqueta = "NO CUMPLE :("
                        # Escribe la combinación evaluada y su resultado en el archivo
                        archivo.write(f"({x}, {y}, {z}), {n} -> {etiqueta}\n")

    # Regresa un diccionario con el conteo de combinaciones que cumplen la ecuación para cada n
    return conteo

# ===== Main =====
def main() -> None:
    # El txt se guarda junto a este script, sin importar desde donde se ejecute
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARCHIVO_RESULTADOS)
    # Aquí se evalúan todas las combinaciones y se guarda el resultado en el archivo
    conteo = evaluar_y_guardar(ruta)

    # Se imprime un resumen de los resultados en consola
    total = len(RANGO) ** 3 * len(EXPONENTES)
    print(bloque_identificacion())
    for n, cantidad in conteo.items():
        print(f"n = {n}: {cantidad} combinaciones CUMPLE de {len(RANGO) ** 3}")
    print(f"\nTotal evaluado: {total} combinaciones")
    print(f"\n[ Resultados guardados en: <{ruta}> ]")


if __name__ == "__main__":
    main()
