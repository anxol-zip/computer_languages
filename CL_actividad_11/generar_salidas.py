# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Manda cada ejercicio de ejercicios/ a los dos endpoints de complejidad y guarda
# el archivo que regresa la API en ejercicios/salidas/. Usa el TestClient de FastAPI,
# asi que no hace falta levantar el servidor:
#
#     uv run python generar_salidas.py

from pathlib import Path

from fastapi.testclient import TestClient

from cl_actividad_11.main import app

EJERCICIOS = Path(__file__).parent / "ejercicios"
SALIDAS = EJERCICIOS / "salidas"
ENDPOINTS = ["/complejidad/peor-caso", "/complejidad/mejor-caso"]

cliente = TestClient(app)
SALIDAS.mkdir(exist_ok=True)

for programa in sorted(EJERCICIOS.glob("*.py")):
    for endpoint in ENDPOINTS:
        with programa.open("rb") as archivo:
            respuesta = cliente.post(endpoint, files={"archivo": (programa.name, archivo, "text/x-python")})
        respuesta.raise_for_status()

        # el nombre lo decide la API en el encabezado Content-Disposition
        nombre = respuesta.headers["content-disposition"].split('filename="')[1].rstrip('"')
        (SALIDAS / nombre).write_text(respuesta.text, encoding="utf-8")
        print(f"{endpoint:<26} {programa.name:<24} -> salidas/{nombre}")
