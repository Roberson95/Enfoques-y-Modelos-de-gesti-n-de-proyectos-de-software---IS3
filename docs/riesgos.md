# Registro de riesgos

| ID | Riesgo (causa-evento-efecto) | Prob. | Impacto | Prioridad | Respuesta | Disparador | Resp. | Estado actual |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: | :--- |
| **R1** | Flujo de reprogramación poco claro → 35% falla en I2 → insatisfacción | Alta | Alto | Crítica | Rediseñar y probar con usuarios | 35% falla en I2 | A | **Materializado / Mitigado (I2)** |
| **R2** | Baja accesibilidad → usuarios con discapacidad no pueden usar → exclusión | Media | Alto | Alta | Checklist WCAG | Hallazgo de usuario | B | Activo (Monitoreo continuo) |
| **R3** | Datos clínicos expuestos en logs → violación de privacidad → sanción | Media | Muy alto | Crítica | Datos simulados, logs sin datos personales | Auditoría interna | C | **Activo (Foco principal I3)** |
| **R4** | Integración simulada inestable → errores en CI → retraso | Media | Alto | Alta | Mocks y pruebas de contrato | Error en CI | C | Activo (Próximo en I4) |
| **R5** | Muestra de 5 usuarios no representativa → conclusiones sesgadas → malas decisiones | Alta | Medio | Alta | Complementar con encuestas | Baja diversidad | B | Activo (Monitoreo continuo) |
| **R6** | Sesgo al interpretar feedback → requisitos incorrectos → retrabajo | Media | Medio | Media | Triangulación con métricas | Opiniones contradictorias | A | Activo (Monitoreo continuo) |
| **R7** | Tiempos de respuesta >2s → usuarios abandonan → baja adopción | Media | Alto | Alta | Pruebas de rendimiento | >2s en prueba | C | Activo (Próximo en I4) |
| **R8** | Retrabajo por cambios de requisitos → sobrecosto → retraso | Alta | Medio | Alta | Backlog priorizado y registro de decisiones | Cambio no planificado | A | Activo (Gestionado en I2) |
| **R9** | Deuda técnica por prototipos descartables → código no reutilizable → retraso | Alta | Medio | Media | Etiquetar prototipos descartables | Código no reutilizable | C | Activo (Monitoreo continuo) |
| **R10** | Conflictos admin vs. usuarios → priorización incorrecta → insatisfacción | Media | Medio | Media | Reunión de revisión y criterios objetivos | Solicitud admin I2 | B | **Materializado / Mitigado (I2)** |

---

## Riesgos residuales y secundarios

* **Riesgo residual de R1:** Pequeña fricción residual en usuarios no familiarizados con aplicaciones móviles. Se mitiga manteniendo textos de ayuda contextuales en la vista de confirmación.
* **Riesgo secundario de R10:** Posible disconformidad temporal del área administrativa por la postergación de sus campos obligatorios. Se mitiga incluyendo la vista simplificada en el panel administrativo de la Iteración 3.
