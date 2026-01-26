"""
================================================================================
[Módulo: bingo_p.py]
================================================================================

Autores:
    - Victor Morales
    - Andres Saltos
    - Darwin Diaz
    - Juliana Burgos
    - Gabriel Tumbaco

Curso: Análisis de Algoritmos II PAO 2025 - Paralelo 2 - Grupo 2

Descripción:
    Módulo principal que integra las constantes, algoritmos y clases necesarias 
    para la implementación del proyecto de Bingo.

Referencias:
    - Algoritmos basados en: Cormen, T. H., et al. "Introduction to 
      Algorithms", 3rd ed. MIT Press, 2009.
================================================================================
"""
from constantes import IDIOMAS, RUTA_REPOSITORIO
from algoritmos import (
    merge,
    merge_sort,
    busqueda_binaria,
    distancia_edicion
)
from carton import Carton
from repositorio import RepositorioPalabras
from gestor import GestorBingo

__all__ = [
    'IDIOMAS',
    'RUTA_REPOSITORIO',
    'merge',
    'merge_sort',
    'busqueda_binaria',
    'distancia_edicion',
    'Carton',
    'RepositorioPalabras',
    'GestorBingo'
]
