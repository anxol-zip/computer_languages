# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Endpoints del analizador de complejidad:
#   - POST /complejidad/peor-caso   -> Big-O
#   - POST /complejidad/mejor-caso  -> Big-Omega
# Los dos reciben un archivo .py y regresan el mismo programa anotado.

from pathlib import PurePath

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from complejidad import analizar

router = APIRouter(prefix="/complejidad", tags=["Complejidad (Actividad 11)"])


async def leer_programa(archivo: UploadFile) -> str:
    """Lee el archivo subido y comprueba que sea un programa de Python valido."""
    contenido = await archivo.read()
    try:
        codigo = contenido.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="El archivo debe ser texto en UTF-8.")

    if not codigo.strip():
        raise HTTPException(status_code=400, detail="El archivo esta vacio.")

    # El analisis es linea por linea y se apoya en la sangria, asi que primero se
    # confirma que el programa sea Python sintacticamente correcto.
    try:
        compile(codigo, archivo.filename or "programa.py", "exec")
    except SyntaxError as error:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo no es un programa de Python valido (linea {error.lineno}): {error.msg}",
        )
    return codigo


def archivo_anotado(codigo: str, nombre: str, modo: str, sufijo: str) -> Response:
    """Regresa el programa anotado como archivo descargable."""
    anotado = analizar(codigo, modo)
    base = PurePath(nombre or "programa.py").stem
    if not base.isascii():
        base = "programa"   # el encabezado HTTP solo admite ASCII
    return Response(
        content=anotado,
        media_type="text/x-python; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{base}_{sufijo}.py"'},
    )


@router.post("/peor-caso", summary="Complejidad en el peor caso (Big-O)")
async def complejidad_peor_caso(archivo: UploadFile = File(..., description="Programa en Python (.py)")):
    """Regresa el mismo programa con la complejidad Big-O de cada linea como comentario
    y un bloque final con la suma de las complejidades y la de mayor grado."""
    codigo = await leer_programa(archivo)
    return archivo_anotado(codigo, archivo.filename, "peor", "big_o")


@router.post("/mejor-caso", summary="Complejidad en el mejor caso (Big-Omega)")
async def complejidad_mejor_caso(archivo: UploadFile = File(..., description="Programa en Python (.py)")):
    """Regresa el mismo programa con la complejidad Big-Omega de cada linea como comentario
    y un bloque final con la suma de las complejidades y la de mayor grado."""
    codigo = await leer_programa(archivo)
    return archivo_anotado(codigo, archivo.filename, "mejor", "big_omega")
