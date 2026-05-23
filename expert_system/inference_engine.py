# expert_system/inference_engine.py
# Motor de inferencia del sistema experto RECI
# Implementa encadenamiento hacia adelante (forward chaining)

from expert_system.knowledge_base import KnowledgeBase
from expert_system.working_memory import WorkingMemory
from expert_system.validator import AttributeValidator
from expert_system.backward_chaining import BackwardChainingEngine

class InferenceEngine:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.memoria = WorkingMemory()
        self.reglas_disparadas = []
        self.conclusion_final = None
        self.confianza_final = 0.0
        self.distribucion = {}
        self.validator = AttributeValidator() 
        self.errores_validacion = []           
        self.advertencias_validacion = []
        self.backward_engine = BackwardChainingEngine()
        self.resultado_backward = None
        self.score_backward = 0.0

    def cargar_hechos(self, resultado_ml: dict):
        """
        Carga los atributos detectados por el modelo ML
        en la memoria de trabajo.
        """
        self.memoria.limpiar()
        self.reglas_disparadas = []
        self.conclusion_final = None
        self.confianza_final = 0.0
        self.distribucion = {}
        self.errores_validacion = []         
        self.advertencias_validacion = []    

        # Validar antes de cargar
        es_valido, errores, advertencias = self.validator.validar(resultado_ml)
        self.errores_validacion = errores
        self.advertencias_validacion = advertencias
        self.resultado_backward = None
        self.score_backward = 0.0

        if not es_valido:
            # Bloquear inferencia si hay errores críticos
            self.conclusion_final = "DESCONOCIDO"
            self.confianza_final = 0.0
            return False

        self.memoria.agregar_hechos_desde_ml(resultado_ml)
        return True 

    def ejecutar(self):
        """
        Ciclo principal de inferencia — encadenamiento hacia adelante.
        Evalúa todas las reglas contra los hechos actuales,
        acumula las que se cumplen y elige la conclusión
        con mayor confianza acumulada.
        """
        if self.errores_validacion:
            return self.conclusion_final, self.confianza_final, []
    
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

        # PRIORIDAD ABSOLUTA: objeto desconocido con baja confianza
        if (hechos.get("confianza_ml") == "baja" and
                hechos.get("objeto_reconocido") == "desconocido"):
            self.conclusion_final = "DESCONOCIDO"
            self.confianza_final  = 0.0

        elif all(v == 0.0 for v in acumulador.values()):
            self.conclusion_final = "DESCONOCIDO"
            self.confianza_final  = 0.0

        else:
            # Eliminar categorías con 0 para el cálculo
            acumulador_activo = {k: v for k, v in acumulador.items() if v > 0}
            total = sum(acumulador_activo.values())
            self.conclusion_final = max(acumulador_activo, key=acumulador_activo.get)

            # Confianza real = peso de la categoría ganadora vs el total
            # Si todas las reglas apuntan a una sola categoría → confianza alta
            # Si hay competencia entre categorías → confianza más baja
            confianza_ganadora = acumulador_activo[self.conclusion_final]
            self.confianza_final = round(confianza_ganadora / total, 3)

            # Guardar distribución completa para explicación
            self.distribucion = {
                k: round(v / total, 3)
                for k, v in acumulador_activo.items()
            }
        
        # ── Encadenamiento hacia atrás como verificación ─────────
        # Verifica si la conclusión del forward chaining
        # es consistente con el backward chaining
        hechos_actuales = self.memoria.obtener_todos()
        resultado_bw, score_bw, _ = self.backward_engine.ejecutar(hechos_actuales)
        self.resultado_backward = resultado_bw
        self.score_backward = score_bw

        # Si backward contradice forward con alta confianza → advertir
        if (resultado_bw and
                self.conclusion_final not in ["DESCONOCIDO", "LATA"] and
                resultado_bw != self.conclusion_final and
                score_bw > 0.80):
            self.advertencias_validacion.append(
                type('Advertencia', (), {
                    '__repr__': lambda self: (
                        f"[ADVERTENCIA] backward_chaining: "
                        f"Forward dice {self.conclusion_fw} pero "
                        f"Backward sugiere {self.resultado_bw} "
                        f"(score: {self.score_bw*100:.1f}%)"
                    ),
                    'conclusion_fw': self.conclusion_final,
                    'resultado_bw':  resultado_bw,
                    'score_bw':      score_bw
                })()
            )

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

        # Mostrar advertencias de validación si existen
        if self.advertencias_validacion:
            lineas.append(f"\n  ⚠ ADVERTENCIAS DE VALIDACIÓN:")
            for a in self.advertencias_validacion:
                lineas.append(f"    • {a}")

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

        # Mostrar distribución si hubo competencia entre categorías
        if self.distribucion and len(self.distribucion) > 1:
            lineas.append(f"\n  DISTRIBUCIÓN DE CONFIANZA:")
            for cat, peso in sorted(self.distribucion.items(),
                                    key=lambda x: x[1], reverse=True):
                barra = "█" * int(peso * 20)
                lineas.append(f"    {cat:12} [{barra:20}] {peso*100:.1f}%")

        if self.conclusion_final == "DESCONOCIDO":
            lineas.append("\n  ⚠ Objeto no clasificable — se solicita segunda captura.")
        elif self.conclusion_final == "LATA":
            lineas.append("\n  ⚠ Lata detectada — no pertenece a ningún compartimento RECI.")

        lineas.append("=" * 60)

        # Resultado del encadenamiento hacia atrás
        if self.resultado_backward:
            consistente = self.resultado_backward == self.conclusion_final
            icono = "✅" if consistente else "⚠"
            lineas.append(f"\n  VERIFICACIÓN HACIA ATRÁS:")
            lineas.append(f"    {icono} Backward chaining: "
                         f"{self.resultado_backward} "
                         f"(score: {self.score_backward*100:.1f}%)")
            if consistente:
                lineas.append(f"    ✅ Consistente con la conclusión forward")
            else:
                lineas.append(f"    ⚠ Discrepancia — revisar con precaución")

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