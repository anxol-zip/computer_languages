def main() -> None:
    """Comando `cl-actividad-11`: levanta el servicio en http://127.0.0.1:8000."""
    import uvicorn

    uvicorn.run("cl_actividad_11.main:app", host="127.0.0.1", port=8000)
