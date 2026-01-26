"""
================================================================================
[Módulo: algoritmos.py]
================================================================================

Autores:
    - Victor Morales
    - Andres Saltos
    - Darwin Diaz
    - Juliana Burgos
    - Gabriel Tumbaco

Curso: Análisis de Algoritmos II PAO 2025 - Paralelo 2 - Grupo 2

Descripción:
    Módulo que contiene implementaciones de algoritmos clásicos utilizados en el proyecto de Bingo.

Referencias:
    - Algoritmos basados en: Cormen, T. H., et al. "Introduction to 
      Algorithms", 3rd ed. MIT Press, 2009.
    - Algoritmo de distancia de edición basado en: Wagner, R. A., y Fisher, M. J. 
      "The string-to-string correction problem". Journal of the ACM (JACM), 1974.
================================================================================
"""
from typing import List


def merge(A: List[str], p: int, q: int, r: int) -> None:
    n1 = q - p + 1
    n2 = r - q
    L = [None] * (n1 + 1)
    R = [None] * (n2 + 1)
    for i in range(n1):
        L[i] = A[p + i]
    for j in range(n2):
        R[j] = A[q + 1 + j]
    L[n1] = "\uffff"
    R[n2] = "\uffff"
    i = 0
    j = 0
    for k in range(p, r + 1):
        if L[i] <= R[j]:
            A[k] = L[i]
            i = i + 1
        else:
            A[k] = R[j]
            j = j + 1


def merge_sort(A: List[str], p: int, r: int) -> None:
    if p < r:
        q = (p + r) // 2
        merge_sort(A, p, q)
        merge_sort(A, q + 1, r)
        merge(A, p, q, r)


def busqueda_binaria(A: List[str], p: int, r: int, v: str) -> int:
    if p > r:
        return -1
    q = (p + r) // 2
    if A[q] == v:
        return q
    elif v < A[q]:
        return busqueda_binaria(A, p, q - 1, v)
    else:
        return busqueda_binaria(A, q + 1, r, v)


def distancia_edicion(X: str, Y: str) -> int:
    m = len(X)
    n = len(Y)
    c = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        c[i][0] = i
    for j in range(n + 1):
        c[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                c[i][j] = c[i - 1][j - 1]
            else:
                c[i][j] = 1 + min(c[i - 1][j], c[i][j - 1], c[i - 1][j - 1])
    return c[m][n]
