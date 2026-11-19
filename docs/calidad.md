# Objetivos de calidad medibles

| Característica | Métrica | Meta | Frecuencia |
|---|---|---|---|
| Usabilidad | Tasa de éxito de tareas | ≥80% | Por iteración |
| Usabilidad | Tiempo para reservar turno | <2 min | Por iteración |
| Usabilidad | Tiempo para reprogramar turno | <2 min | Por iteración |
| Fiabilidad | Errores por iteración | <1% de tareas | Por iteración |
| Seguridad/Privacidad | Datos clínicos en logs (diagnóstico, motivo de consulta) | 0 | Por iteración |
| Seguridad/Privacidad | Bases de datos o credenciales subidas al repositorio | 0 | Cada commit |
| Eficiencia | Tiempo de respuesta | <2s | Por iteración |
| Accesibilidad | Checklist WCAG básico | ≥90% cumplido | I3 |
| Deuda técnica | Ítems registrados y priorizados | 100% | Por iteración |

## Aclaración sobre el registro de actividad

El registro de actividad de SaludUni 1.2 guarda usuario, perfil, acción, fecha e IP, porque sin esos datos no sirve para auditar quién hizo cada cambio. No guarda datos clínicos. Solo el perfil Administrador puede consultarlo, y el sistema conserva como máximo los últimos 50 000 registros.

## Diferenciación de hallazgos

- **Defecto:** falla funcional (ej.: botón no responde).
- **Hallazgo de usabilidad:** dificultad de interacción (ej.: usuario no entiende el flujo).
- **Cambio de preferencia:** solicitud no crítica (ej.: “podrían agregar más campos”).
- **Deuda técnica:** solución provisoria que requerirá refactorización.
