import random
import os
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field

RUTA_REPOSITORIO = os.path.join(os.path.dirname(__file__), "repositorio")

IDIOMAS = {
    "SP": {"nombre": "Español", "max_palabras": 24},
    "EN": {"nombre": "Inglés", "max_palabras": 14},
    "PT": {"nombre": "Portugués", "max_palabras": 20},
    "DT": {"nombre": "Dutch", "max_palabras": 10}
}


@dataclass
class Carton:
    id: str
    idioma: str
    palabras: Set[str]
    aciertos: int = 0
    palabras_marcadas: Set[str] = field(default_factory=set)

    @property
    def max_palabras(self) -> int:
        return IDIOMAS[self.idioma]["max_palabras"]

    @property
    def es_ganador(self) -> bool:
        return self.aciertos == len(self.palabras)

    def marcar_palabra(self, palabra: str) -> bool:
        if palabra in self.palabras and palabra not in self.palabras_marcadas:
            self.palabras_marcadas.add(palabra)
            self.aciertos += 1
            return True
        return False

    def reiniciar(self):
        self.aciertos = 0
        self.palabras_marcadas.clear()

    def __str__(self) -> str:
        return f"[{self.id}] {IDIOMAS[self.idioma]['nombre']} - {self.aciertos}/{len(self.palabras)} palabras"


class GestorBingo:
    def __init__(self, repositorio: 'RepositorioPalabras' = None):
        self._repositorio = repositorio
        self.cartones: Dict[str, Dict[str, Carton]] = {idioma: {} for idioma in IDIOMAS}
        self.indice_palabras: Dict[str, Dict[str, List[str]]] = {idioma: {} for idioma in IDIOMAS}
        self.orden_rondas: List[str] = list(IDIOMAS.keys())
        self.ronda_actual: int = 0
        self.palabras_anunciadas: Dict[str, List[str]] = {idioma: [] for idioma in IDIOMAS}
        self.ganadores: Dict[str, List[str]] = {idioma: [] for idioma in IDIOMAS}

    @property
    def repositorio(self) -> 'RepositorioPalabras':
        if self._repositorio is None:
            self._repositorio = RepositorioPalabras()
        return self._repositorio

    def validar_palabras_en_repositorio(self, idioma: str, palabras: Set[str]) -> Tuple[bool, List[str]]:
        palabras_repositorio = set(self.repositorio.palabras.get(idioma, []))
        palabras_invalidas = [p for p in palabras if p not in palabras_repositorio]
        return len(palabras_invalidas) == 0, palabras_invalidas

    def validar_id_carton(self, id_carton: str) -> Tuple[bool, str]:
        if len(id_carton) != 8:
            return False, "El ID debe tener exactamente 8 caracteres"
        prefijo = id_carton[:2].upper()
        sufijo = id_carton[2:]
        if prefijo not in IDIOMAS:
            return False, f"Prefijo de idioma inválido: {prefijo}. Válidos: {list(IDIOMAS.keys())}"
        if not sufijo.isdigit():
            return False, "Los últimos 6 caracteres deben ser numéricos"
        return True, prefijo

    def agregar_carton(self, id_carton: str, palabras: List[str]) -> Tuple[bool, str]:
        es_valido, resultado = self.validar_id_carton(id_carton)
        if not es_valido:
            return False, resultado
        idioma = resultado
        id_carton = id_carton.upper()
        if id_carton in self.cartones[idioma]:
            return False, f"Ya existe un cartón con ID: {id_carton}"
        max_palabras = IDIOMAS[idioma]["max_palabras"]
        if len(palabras) > max_palabras:
            return False, f"El cartón excede el máximo de {max_palabras} palabras para {IDIOMAS[idioma]['nombre']}"
        palabras_normalizadas = {p.strip().lower() for p in palabras if p.strip()}
        todas_validas, palabras_invalidas = self.validar_palabras_en_repositorio(idioma, palabras_normalizadas)
        if not todas_validas:
            if len(palabras_invalidas) <= 5:
                return False, f"Palabras no encontradas en el repositorio de {IDIOMAS[idioma]['nombre']}: {', '.join(palabras_invalidas)}"
            else:
                return False, f"Palabras no encontradas en el repositorio de {IDIOMAS[idioma]['nombre']}: {', '.join(palabras_invalidas[:5])}... (+{len(palabras_invalidas)-5} más)"
        carton = Carton(id=id_carton, idioma=idioma, palabras=palabras_normalizadas)
        self.cartones[idioma][id_carton] = carton
        for palabra in palabras_normalizadas:
            if palabra not in self.indice_palabras[idioma]:
                self.indice_palabras[idioma][palabra] = []
            self.indice_palabras[idioma][palabra].append(id_carton)
        return True, f"Cartón {id_carton} agregado correctamente"

    def cargar_desde_archivo(self, ruta_archivo: str) -> Tuple[int, int, List[str]]:
        cargados = 0
        fallidos = 0
        errores = []
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                for num_linea, linea in enumerate(archivo, 1):
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split()
                    if len(partes) < 2:
                        errores.append(f"Línea {num_linea}: Formato inválido (se requiere ID y al menos 1 palabra)")
                        fallidos += 1
                        continue
                    id_carton = partes[0]
                    palabras = partes[1:]
                    exito, mensaje = self.agregar_carton(id_carton, palabras)
                    if exito:
                        cargados += 1
                    else:
                        errores.append(f"Línea {num_linea}: {mensaje}")
                        fallidos += 1
        except FileNotFoundError:
            errores.append(f"Archivo no encontrado: {ruta_archivo}")
        except Exception as e:
            errores.append(f"Error al leer archivo: {str(e)}")
        return cargados, fallidos, errores

    def iniciar_partida(self):
        random.shuffle(self.orden_rondas)
        self.ronda_actual = 0
        for idioma in IDIOMAS:
            for carton in self.cartones[idioma].values():
                carton.reiniciar()
            self.palabras_anunciadas[idioma].clear()
            self.ganadores[idioma].clear()
        return self.orden_rondas.copy()

    def obtener_idioma_actual(self) -> Optional[str]:
        if self.ronda_actual < len(self.orden_rondas):
            return self.orden_rondas[self.ronda_actual]
        return None

    def anunciar_palabra(self, palabra: str) -> List[Carton]:
        idioma = self.obtener_idioma_actual()
        if idioma is None:
            return []
        palabra = palabra.strip().lower()
        self.palabras_anunciadas[idioma].append(palabra)
        nuevos_ganadores = []
        if palabra in self.indice_palabras[idioma]:
            ids_cartones = self.indice_palabras[idioma][palabra]
            for id_carton in ids_cartones:
                carton = self.cartones[idioma][id_carton]
                if not carton.es_ganador:
                    if carton.marcar_palabra(palabra):
                        if carton.es_ganador:
                            nuevos_ganadores.append(carton)
                            self.ganadores[idioma].append(id_carton)
        return nuevos_ganadores

    def avanzar_ronda(self) -> Tuple[bool, str]:
        self.ronda_actual += 1
        if self.ronda_actual >= len(self.orden_rondas):
            return False, "Todas las rondas han finalizado"
        nuevo_idioma = self.orden_rondas[self.ronda_actual]
        return True, f"Ronda de {IDIOMAS[nuevo_idioma]['nombre']}"

    def obtener_estadisticas(self) -> Dict:
        stats = {
            "total_cartones": sum(len(c) for c in self.cartones.values()),
            "por_idioma": {},
            "orden_rondas": [IDIOMAS[i]["nombre"] for i in self.orden_rondas],
            "ronda_actual": self.ronda_actual + 1 if self.ronda_actual < len(self.orden_rondas) else "Finalizado"
        }
        for idioma, cartones in self.cartones.items():
            stats["por_idioma"][IDIOMAS[idioma]["nombre"]] = {
                "cartones": len(cartones),
                "palabras_anunciadas": len(self.palabras_anunciadas[idioma]),
                "ganadores": len(self.ganadores[idioma])
            }
        return stats

    def obtener_estado_cartones(self, idioma: str = None) -> List[Dict]:
        resultado = []
        idiomas_a_revisar = [idioma] if idioma else IDIOMAS.keys()
        for lang in idiomas_a_revisar:
            if lang in self.cartones:
                for carton in self.cartones[lang].values():
                    resultado.append({
                        "id": carton.id,
                        "idioma": IDIOMAS[lang]["nombre"],
                        "progreso": f"{carton.aciertos}/{len(carton.palabras)}",
                        "es_ganador": carton.es_ganador
                    })
        return resultado


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
            except FileNotFoundError:
                print(f"Advertencia: No se encontró {ruta}")
            except Exception as e:
                print(f"Error al cargar {ruta}: {e}")

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