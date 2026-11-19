## Comparativa entre iteraciones

**Cómo se calcula:** la tasa de éxito es la proporción de usuarios que completó la tarea sin ayuda. El tiempo medio de la tarea promedia solo a quienes la completaron. El tiempo de respuesta del sistema promedia las 5 mediciones de la I4.

| Métrica | I1 | I2 | I3 | I4 | Tendencia |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tasa de éxito** | 80% | 80%* | 100% | 100% | 📈 Positiva (Alta usabilidad alcanzada) |
| **Tiempo medio de la tarea (usuario)** | 1m 40s | 1m 26s | 1m 06s | — | 📉 Positiva (Optimización de tiempos) |
| **Tiempo de respuesta del sistema** | — | — | — | 1.3 s | ✅ Cumple meta < 2 s |
| **Defectos / Retrabajo** | 1 | 2 | 0 | 0 | 📉 Positiva (Convergencia y estabilidad) |

*\*Nota en I2:* Durante la prueba inicial de la Iteración 2 se registró un $35\%$ de fallo (evento de cambio). Tras aplicar el rediseño del flujo hacia 3 pasos, la tasa de éxito subió al $80\%$.

---

## Análisis de Tendencias y Calidad Final

1. **Evolución de la Tasa de Éxito:** Se observa una curva de aprendizaje donde la reestructuración del flujo en la I2 permitió escalar la efectividad hasta alcanzar el $100\%$ en las iteraciones I3 e I4.
2. **Eficiencia en Tiempos:** El tiempo medio de la tarea se redujo desde $1\text{ min } 40\text{ s}$ en la I1 hasta $1\text{ min } 06\text{ s}$ en la I3. En la I4 se midió otra cosa, el tiempo de respuesta del sistema, que promedió $1.3\text{ s}$ en la prueba End-to-End, dentro de la meta de $2\text{ s}$.
3. **Control de Defectos:** El retrabajo se concentró en la I2 debido al conflicto de requisitos con el área administrativa. En I3 e I4 no se registraron defectos bloqueantes ni fallas de usabilidad.
