# expert_system/inference_engine.py
# Motor de inferencia del sistema experto RECI
# Implementa encadenamiento hacia adelante (forward chaining)

from expert_system.knowledge_base import KnowledgeBase
from expert_system.working_memory import WorkingMemory

class InferenceEngine:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.memoria = WorkingMemory()
        self.reglas_disparadas = []
        self.conclusion_final = None
        self.confianza_final = 0.0

    def cargar_hechos(self, resultado_ml: dict):
        """
        Carga los atributos detectados por el modelo ML
        en la memoria de trabajo.
        """
        self.memoria.limpiar()
        self.reglas_disparadas = []
        self.conclusion_final = None
        self.confianza_final = 0.0
        self.memoria.agregar_hechos_desde_ml(resultado_ml)

    def ejecutar(self):
        """
        Ciclo principal de inferencia — encadenamiento hacia adelante.
        Evalúa todas las reglas contra los hechos actuales,
        acumula las que se cumplen y elige la conclusión
        con mayor confianza acumulada.
        """
        hechos = self.memoria.obtener_todos()
        reglas = self.kb.obtener_reglas()

        # Acumulador de confianza por categoría
        acumulador = {
            "VIDRIO":       0.0,
            "PLASTICO":     0.0,
            "ORGANICO":     0.0,
            "LATA":         0.0,
            "DESCONOCIDO":  0.0
        }

        # Evaluar cada regla contra los hechos
        for regla in reglas:
            if regla.evaluar(hechos):
                self.reglas_disparadas.append(regla)
                acumulador[regla.conclusion] += regla.confianza

        # Elegir la conclusión con mayor confianza acumulada
        hechos = self.memoria.obtener_todos()

        # PRIORIDAD ABSOLUTA: si confianza ML es baja y objeto desconocido → DESCONOCIDO
        if (hechos.get("confianza_ml") == "baja" and
                hechos.get("objeto_reconocido") == "desconocido"):
            self.conclusion_final = "DESCONOCIDO"
            self.confianza_final = 0.0

        elif all(v == 0.0 for v in acumulador.values()):
            self.conclusion_final = "DESCONOCIDO"
            self.confianza_final = 0.0

        else:
            self.conclusion_final = max(acumulador, key=acumulador.get)
            total = sum(acumulador.values())
            self.confianza_final = round(
                acumulador[self.conclusion_final] / total, 3
            ) if total > 0 else 0.0

        return self.conclusion_final, self.confianza_final, self.reglas_disparadas

    def obtener_explicacion(self):
        """
        Genera una explicación legible del razonamiento:
        qué reglas se dispararon y por qué se llegó a esa conclusión.
        """
        if not self.conclusion_final:
            return "No se ha ejecutado ninguna inferencia todavía."

        lineas = []
        lineas.append("=" * 60)
        lineas.append("  SISTEMA EXPERTO RECI — EXPLICACIÓN DEL RAZONAMIENTO")
        lineas.append("=" * 60)

        lineas.append(f"\n  HECHOS ANALIZADOS:")
        for atributo, valor in self.memoria.obtener_todos().items():
            lineas.append(f"    • {atributo:25} = {valor}")

        lineas.append(f"\n  REGLAS DISPARADAS ({len(self.reglas_disparadas)}):")
        if self.reglas_disparadas:
            for regla in self.reglas_disparadas:
                lineas.append(f"    ✓ [{regla.nombre}] → {regla.conclusion} "
                              f"(peso: {regla.confianza})")
                lineas.append(f"      {regla.explicacion}")
        else:
            lineas.append("    Ninguna regla se disparó.")

        lineas.append(f"\n  CONCLUSIÓN FINAL:  {self.conclusion_final}")
        lineas.append(f"  CONFIANZA:         {self.confianza_final * 100:.1f}%")

        if self.conclusion_final == "DESCONOCIDO":
            lineas.append("\n  ⚠ Objeto no clasificable — se solicita segunda captura.")
        elif self.conclusion_final == "LATA":
            lineas.append("\n  ⚠ Lata detectada — no pertenece a ningún compartimento RECI.")

        lineas.append("=" * 60)
        return "\n".join(lineas)

    def decision_hardware(self):
        """
        Traduce la conclusión a la instrucción física
        que recibirá el Raspberry Pi para mover el servo.
        """
        acciones = {
            "VIDRIO":       {"compuerta": "izquierda", "led": "azul",     "angulo_servo": 45,  "mensaje": "VIDRIO detectado — abriendo compartimento izquierdo"},
            "PLASTICO":     {"compuerta": "derecha",   "led": "verde",    "angulo_servo": 135, "mensaje": "PLÁSTICO detectado — abriendo compartimento derecho"},
            "ORGANICO":     {"compuerta": "ninguna",   "led": "rojo",     "angulo_servo": 0,   "mensaje": "⚠ Orgánico o papel — este objeto no pertenece a este tacho"},
            "LATA":         {"compuerta": "ninguna",   "led": "rojo",     "angulo_servo": 0,   "mensaje": "⚠ Lata detectada — este objeto no pertenece a este tacho"},
            "DESCONOCIDO":  {"compuerta": "ninguna",   "led": "rojo",     "angulo_servo": 0,   "mensaje": "⚠ Objeto no reconocido — por favor intente de nuevo"},
        }
        return acciones.get(self.conclusion_final, acciones["DESCONOCIDO"])
    
    def __repr__(self):
        return (f"InferenceEngine("
                f"conclusion={self.conclusion_final}, "
                f"confianza={self.confianza_final}, "
                f"reglas_disparadas={len(self.reglas_disparadas)})")