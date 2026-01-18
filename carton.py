from typing import Set
from dataclasses import dataclass, field
from constantes import IDIOMAS


@dataclass
class Carton:
    id: str
    idioma: str
    palabras: Set[str]
    jugador_id: str = "N/A"
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
        return f"[{self.id}] Jugador: {self.jugador_id} - {IDIOMAS[self.idioma]['nombre']} - {self.aciertos}/{len(self.palabras)} palabras"
