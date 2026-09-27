# Objetivos de calidad medibles

| Característica | Métrica | Meta | Frecuencia |
|---|---|---|---|
| Usabilidad | Tasa de éxito de tareas | ≥80% | Por iteración |
| Usabilidad | Tiempo para reservar turno | <2 min | Por iteración |
| Usabilidad | Tiempo para reprogramar turno | <2 min | Por iteración |
| Fiabilidad | Errores por iteración | <1% de tareas | Por iteración |
| Seguridad/Privacidad | Datos personales en logs | 0 | Por iteración |
| Eficiencia | Tiempo de respuesta | <2s | Por iteración |
| Accesibilidad | Checklist WCAG básico | ≥90% cumplido | I3 |
| Deuda técnica | Ítems registrados y priorizados | 100% | Por iteración |

## Diferenciación de hallazgos

- **Defecto:** falla funcional (ej.: botón no responde).
- **Hallazgo de usabilidad:** dificultad de interacción (ej.: usuario no entiende el flujo).
- **Cambio de preferencia:** solicitud no crítica (ej.: “podrían agregar más campos”).
- **Deuda técnica:** solución provisoria que requerirá refactorización.
