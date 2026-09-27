# Registro de riesgos

| ID | Riesgo (causa-evento-efecto) | Prob. | Impacto | Prioridad | Respuesta | Disparador | Responsable |
|---|---|---|---|---|---|---|---|
| R1 | Flujo de reprogramación poco claro → 35% falla en I2 → insatisfacción | Alta | Alto | Crítica | Rediseñar y probar con usuarios | 35% falla en I2 | A |
| R2 | Baja accesibilidad → usuarios con discapacidad no pueden usar → exclusión | Media | Alto | Alta | Checklist WCAG | Hallazgo de usuario | B |
| R3 | Datos clínicos expuestos en logs → violación de privacidad → sanción | Media | Muy alto | Crítica | Datos simulados, logs sin datos personales | Auditoría interna | C |
| R4 | Integración simulada inestable → errores en CI → retraso | Media | Alto | Alta | Mocks y pruebas de contrato | Error en CI | C |
| R5 | Muestra de 5 usuarios no representativa → conclusiones sesgadas → malas decisiones | Alta | Medio | Alta | Complementar con encuestas | Baja diversidad | B |
| R6 | Sesgo al interpretar feedback → requisitos incorrectos → retrabajo | Media | Medio | Media | Triangulación con métricas | Opiniones contradictorias | A |
| R7 | Tiempos de respuesta >2s → usuarios abandonan → baja adopción | Media | Alto | Alta | Pruebas de rendimiento | >2s en prueba | C |
| R8 | Retrabajo por cambios de requisitos → sobrecosto → retraso | Alta | Medio | Alta | Backlog priorizado y registro de decisiones | Cambio no planificado | A |
| R9 | Deuda técnica por prototipos descartables → código no reutilizable → retraso | Alta | Medio | Media | Etiquetar prototipos descartables | Código no reutilizable | C |
| R10 | Conflictos admin vs. usuarios → priorización incorrecta → insatisfacción | Media | Medio | Media | Reunión de revisión y criterios objetivos | Solicitud admin I2 | B |

## Riesgos residuales y secundarios

(Completar después de cada iteración)
