import os
import random
from typing import Dict, List, Set, Optional, Tuple
from constantes import IDIOMAS, RUTA_REPOSITORIO
from algoritmos import merge_sort, busqueda_binaria, distancia_edicion


class RepositorioPalabras:
    def __init__(self, ruta_base: str = None):
        self.ruta_base = ruta_base or RUTA_REPOSITORIO
        self.palabras: Dict[str, List[str]] = {idioma: [] for idioma in IDIOMAS}
        self.palabras_extraidas: Dict[str, Set[str]] = {idioma: set() for idioma in IDIOMAS}
        self._cargar_palabras()

    def _cargar_palabras(self):
        archivos = {
            "SP": "palabras_SP.txt",
            "EN": "palabras_EN.txt",
            "PT": "palabras_PT.txt",
            "DT": "palabras_DT.txt"
        }
        for idioma, archivo in archivos.items():
            ruta = os.path.join(self.ruta_base, archivo)
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.palabras[idioma].append(linea.lower())
                if self.palabras[idioma]:
                    merge_sort(self.palabras[idioma], 0, len(self.palabras[idioma]) - 1)
            except FileNotFoundError:
                print(f"Advertencia: No se encontró {ruta}")
            except Exception as e:
                print(f"Error al cargar {ruta}: {e}")

    def palabra_existe(self, idioma: str, palabra: str) -> bool:
        if idioma not in self.palabras or not self.palabras[idioma]:
            return False
        palabra = palabra.lower().strip()
        n = len(self.palabras[idioma])
        indice = busqueda_binaria(self.palabras[idioma], 0, n - 1, palabra)
        return indice != -1

    def sugerir_palabra(self, idioma: str, palabra: str, limite: int = 2) -> Optional[Tuple[str, int]]:
        if idioma not in self.palabras or not self.palabras[idioma]:
            return None
        palabra = palabra.lower().strip()
        mejor_sugerencia = None
        menor_distancia = limite + 1
        for candidata in self.palabras[idioma]:
            dist = distancia_edicion(palabra, candidata)
            if dist < menor_distancia:
                menor_distancia = dist
                mejor_sugerencia = candidata
                if menor_distancia == 1:
                    break
        if mejor_sugerencia is None:
            return None
        return (mejor_sugerencia, menor_distancia)

    def extraer_palabra(self, idioma: str) -> Optional[str]:
        if idioma not in self.palabras:
            return None
        disponibles = set(self.palabras[idioma]) - self.palabras_extraidas[idioma]
        if not disponibles:
            return None
        palabra = random.choice(list(disponibles))
        self.palabras_extraidas[idioma].add(palabra)
        return palabra

    def reiniciar_ronda(self, idioma: str = None):
        if idioma:
            self.palabras_extraidas[idioma].clear()
        else:
            for lang in IDIOMAS:
                self.palabras_extraidas[lang].clear()

    def obtener_total_palabras(self, idioma: str) -> int:
        return len(self.palabras.get(idioma, []))

    def obtener_palabras_restantes(self, idioma: str) -> int:
        total = self.obtener_total_palabras(idioma)
        extraidas = len(self.palabras_extraidas.get(idioma, set()))
        return total - extraidas

    def obtener_estadisticas(self) -> Dict:
        stats = {}
        for idioma in IDIOMAS:
            stats[IDIOMAS[idioma]["nombre"]] = {
                "total": self.obtener_total_palabras(idioma),
                "extraidas": len(self.palabras_extraidas[idioma]),
                "restantes": self.obtener_palabras_restantes(idioma)
            }
        return stats
