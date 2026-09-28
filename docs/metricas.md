## Comparativa entre iteraciones

| Métrica | I1 | I2 | I3 | I4 | Tendencia |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tasa de éxito** | 80% | 80%* | 100% | 100% | 📈 Positiva (Alta usabilidad alcanzada) |
| **Tiempo medio de operación** | 1m 45s | 1m 30s | 1m 06s | 1.3s (Latencia) | 📉 Positiva (Optimización de tiempos) |
| **Defectos / Retrabajo** | 1 | 2 | 0 | 0 | 📉 Positiva (Convergencia y estabilidad) |

*\*Nota en I2:* Durante la prueba inicial de la Iteración 2 se registró un $40\%$ de fallo (evento de cambio). Tras aplicar el rediseño del flujo hacia 3 pasos, la tasa de éxito subió al $80\%$.

---

## Análisis de Tendencias y Calidad Final

1. **Evolución de la Tasa de Éxito:** Se observa una curva de aprendizaje donde la reestructuración del flujo en la I2 permitió escalar la efectividad hasta alcanzar el $100\%$ en las iteraciones I3 e I4.
2. **Eficiencia en Tiempos:** El tiempo medio de reserva/gestión se redujo gradualmente desde $1\text{ min } 45\text{ s}$ en la I1 hasta lograr respuestas de backend inmediatas ($1.3\text{ s}$) en la prueba de integración End-to-End de la I4.
3. **Control de Defectos:** El retrabajo se concentró en la I2 debido al conflicto de requisitos con el área administrativa. En I3 e I4 no se registraron defectos bloqueantes ni fallas de usabilidad.
