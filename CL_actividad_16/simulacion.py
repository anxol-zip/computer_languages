"""Simulación meteorológica paralela (libreta base de la clase, corregida).

Las funciones viven en un módulo y no en la libreta porque Python 3.14 arranca los procesos
con `forkserver`, que solo puede ejecutar funciones importables desde un archivo.
"""
import time
from multiprocessing import Pipe, Process

import numpy as np


# Fase 1. Particionamiento: cada proceso recibe una franja horizontal del dominio N x N
def inicializacion_subdominio(rank, n_proc, N, pert=1.01):
    # Si N no es divisible entre n_proc, los primeros procesos reciben una fila extra
    subgrid_rows = N // n_proc + (1 if rank < N % n_proc else 0)
    cols = N
    # Matriz local con bordes extras (ghost cells)
    grid = np.zeros((subgrid_rows + 2, cols + 2), dtype=np.float64)
    # Fila global donde empieza la franja de este proceso
    global_rows = rank * (N // n_proc) + min(rank, N % n_proc)
    for r in range(1, subgrid_rows + 1):
        gr = global_rows + (r - 1)
        for c in range(cols):
            dist = np.sqrt((gr - 50) ** 2 + (c - 50) ** 2)
            grid[r, c + 1] = 100 * pert * np.exp(-dist / 120)
    return grid, subgrid_rows, cols


# Fase 2. Comunicación: intercambio de bordes con el vecino del norte y el del sur
def intercambio_ghost_cells(grid, subgrid_rows, pipe_top, pipe_bottom):
    # Intercambio hacia el norte
    if pipe_top is not None:
        pipe_top.send(grid[1, :])
        grid[0, :] = pipe_top.recv()
    # Intercambio hacia el sur
    if pipe_bottom is not None:
        pipe_bottom.send(grid[subgrid_rows, :])
        grid[subgrid_rows + 1, :] = pipe_bottom.recv()
    # Condiciones físicas en la frontera del dominio (sin vecino): se copia la fila propia
    if pipe_top is None:
        grid[0, :] = grid[1, :]
    if pipe_bottom is None:
        grid[subgrid_rows + 1, :] = grid[subgrid_rows, :]


# Fase 3. Cómputo: cada celda pasa a ser el promedio de sus 4 vecinos
def calcular_paso_atmosferico(grid, subgrid_rows, cols):
    grid_next = grid.copy()
    grid_next[1:subgrid_rows + 1, 1:cols + 1] = 0.25 * (
        grid[0:subgrid_rows, 1:cols + 1]        # vecino del norte
        + grid[2:subgrid_rows + 2, 1:cols + 1]  # vecino del sur
        + grid[1:subgrid_rows + 1, 0:cols]      # vecino del oeste
        + grid[1:subgrid_rows + 1, 2:cols + 2]  # vecino del este
    )
    return grid_next


# Fase 4. Integración: ciclo SPMD que ejecuta cada worker
def worker_spmd(rank, num_proc, N, steps, pipe_top, pipe_bottom, result_pipe, pertubacion):
    grid, subgrid_rows, cols = inicializacion_subdominio(rank, num_proc, N, pertubacion)
    historico = []
    for step in range(steps):
        intercambio_ghost_cells(grid, subgrid_rows, pipe_top, pipe_bottom)
        grid = calcular_paso_atmosferico(grid, subgrid_rows, cols)
        # Muestreo periódico para visualización del fenómeno atmosférico
        if step % (steps // 10 if steps > 10 else 1) == 0:
            historico.append((step, grid[1:subgrid_rows + 1, 1:cols + 1].copy()))
    result_pipe.send(historico)


def ejecutar_simulacion(num_proc, N, steps, pertubacion=1.01):
    """Lanza num_proc workers conectados por pipes y devuelve el tiempo total en segundos."""
    # Un pipe por cada frontera entre dos franjas vecinas
    fronteras = [Pipe() for _ in range(num_proc - 1)]
    resultados = [Pipe(duplex=False) for _ in range(num_proc)]
    inicio = time.perf_counter()
    procesos = []
    for rank in range(num_proc):
        top = fronteras[rank - 1][1] if rank > 0 else None
        bottom = fronteras[rank][0] if rank < num_proc - 1 else None
        p = Process(target=worker_spmd,
                    args=(rank, num_proc, N, steps, top, bottom, resultados[rank][1], pertubacion))
        p.start()
        procesos.append(p)
    historicos = [lectura.recv() for lectura, _ in resultados]
    for p in procesos:
        p.join()
    return time.perf_counter() - inicio, historicos
