# Unidad 5 — Personas, equipo y comunicación

## Roles del equipo (3 integrantes)

| Integrante | Rol principal | Responsabilidades |
|---|---|---|
| Oscar Román | Product Owner / UX Lead | Define hipótesis, prioriza feedback, coordina pruebas con usuarios, diseña en Figma. |
| Maximiliano Gaona | Analista QA / Métricas | Define criterios de calidad, ejecuta pruebas de usabilidad, mantiene tablero y métricas. |
| Carlos Cano | DevOps / Configuración | Versiona prototipos, mantiene repo, pipeline CI, documenta decisiones y cambios. |

**Rotación de facilitador:** I1 → Oscar Román, I2 → Maximiliano Gaona, I3 → Carlos Cano, I4 → Oscar Román.

En las tablas del registro de riesgos, la columna «Resp.» usa las iniciales: **OR** (Oscar Román), **MG** (Maximiliano Gaona) y **CC** (Carlos Cano).

## Canales de comunicación

- **Diario:** WhatsApp o Discord para consultas rápidas.
- **Semanal:** Reunión de sincronización de 30 min (lunes).
- **GitHub:** Issues y commits para dejar trazabilidad de decisiones.

## Cómo se recoge el feedback sin convertir cada opinión en requisito

1. Se escucha a todos los usuarios de prueba.
2. Se agrupan los comentarios por temas (ej.: "confusión en el botón", "faltan campos").
3. Se prioriza según impacto en la usabilidad y frecuencia del hallazgo.
4. Solo se convierte en requisito si hay evidencia (varios usuarios, métrica afectada).
5. Todo cambio se registra en `decisiones.md` con justificación.

## Resolución de conflictos

Si hay desacuerdo en prioridades, se usa la evidencia de las pruebas (métricas, tasa de éxito) como árbitro. Si persiste, el facilitador de la iteración toma la decisión final y la documenta.
