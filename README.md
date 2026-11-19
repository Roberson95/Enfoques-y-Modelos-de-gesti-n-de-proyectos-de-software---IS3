# TP 3 — Enfoque Iterativo: Sistema de Turnos Universitario

**Materia:** Ingeniería de Software III — LCIK (FPUNA)  
**Año:** 2026  
**Equipo:** 3 integrantes  
**Repositorio:** [Enfoques-y-Modelos-de-gesti-n-de-proyectos-de-software---IS3](https://github.com/Roberson95/Enfoques-y-Modelos-de-gesti-n-de-proyectos-de-software---IS3.git)

---

## Integrantes y Roles

- **Oscar Román:** Product Owner & UX Lead (Responsable de $I_1$)
- **Maximiliano Gaona:** Analista QA & Métricas (Responsable de $I_2$)
- **Carlos Cano:** DevOps & Configuración (Responsable de $I_3$)

---

## Descripción del Proyecto

Aplicación móvil de turnos para el servicio de salud universitario. Se aplica un **enfoque iterativo** para refinar la solución mediante aprendizaje y retroalimentación de usuarios en 4 iteraciones de 2 semanas cada una.

### Delimitación de Conceptos (Unidad 1)
- **Proyecto:** Esfuerzo temporal para validar y desarrollar las 4 iteraciones de la solución móvil.
- **Producto:** Aplicación móvil y panel administrativo para la gestión de turnos del servicio de salud.
- **Operación:** Mantenimiento del servicio, soporte técnico y atención médica continua.

---

## Índice de Documentación de Gestión (`docs/`)

Para evaluar el desarrollo del trabajo por unidades, acceder a los siguientes artefactos:

- 📄 [Unidad 2 — Selección y Justificación del Enfoque Iterativo](docs/enfoque.md)
- 📄 [Unidad 5 — Personas, Equipo, Matriz RACI y Comunicación](docs/personas.md)
- 📄 [Unidades 3 y 4 — Planificación General y Estimaciones](docs/iteraciones/plan-general.md)
- 📄 [Unidad 3 — Registro de Decisiones y Evento de Cambio](docs/decisiones.md)
- 📄 [Unidad 6 — Registro de 10 Riesgos y Mitigación](docs/riesgos.md)
- 📄 [Unidad 7 — Objetivos y Criterios de Calidad](docs/calidad.md)
- 📄 [Unidad 7 — Checklist de accesibilidad de la aplicación](docs/accesibilidad.md)
- 📄 [Unidad 9 — Tablero de Monitoreo y Métricas](docs/metricas.md)
- 📄 [Anexo D — Bitácora de Uso Responsable de IA](docs/ia-bitacora.md)

### Control de Iteraciones
- 📁 [Iteración 1: Validar flujo básico de reserva](docs/iteraciones/i1.md)
- 📁 [Iteración 2: Validar reprogramación y Evento de Cambio](docs/iteraciones/i2.md)
- 📁 [Iteración 3: Validar panel admin y privacidad](docs/iteraciones/i3.md)
- 📁 [Iteración 4: Validar integración simulada y rendimiento](docs/iteraciones/i4.md)

---

## Resumen de Iteraciones

| Iteración | Objetivo | Producto Esperado | Criterio de Éxito |
|---|---|---|---|
| **I1** | Validar flujo básico de reserva | Prototipo navegable en Figma | $\ge 4/5$ usuarios completa sin ayuda |
| **I2** | Validar reprogramación y cancelación | Prototipo ajustado tras prueba | $\ge 80\%$ reprograma sin ayuda |
| **I3** | Validar panel admin y privacidad | Prototipo con vista administrativa | Admin opera sin hallazgos críticos |
| **I4** | Validar integración simulada y rendimiento | Versión candidata | Cumple tiempos de respuesta $<2\text{s}$ |

---

## Aplicación SaludUni

Además de los prototipos de las iteraciones, el equipo construyó la aplicación web **SaludUni**, publicada en **https://saluduni.pythonanywhere.com/** (versión actual: 1.2). El paso del prototipo a la aplicación está registrado en la decisión D2 de [`docs/decisiones.md`](docs/decisiones.md).

- Funciona en el navegador de cualquier celular o computadora, sin instalar nada.
- Perfiles: Alumno, Profesor, Profesional de salud y Administrador.
- Backend en Python (solo biblioteca estándar) con base de datos SQLite.
- Historial de versiones: [`saluduni1.2/cambios.txt`](saluduni1.2/cambios.txt).

**Probarla en una computadora:** con Python 3.8 o superior, ejecutar `python saluduni1.2/server.py` y abrir http://127.0.0.1:8000. La base de datos se crea sola la primera vez.

> La base de datos (`saluduni.db`) **no se sube al repositorio** porque contiene datos personales. El `.gitignore` la excluye.

---

## Estructura del Repositorio

- `docs/` — Documentación de gestión del proyecto.
- `docs/iteraciones/` — Plan general y registro de cada iteración.
- `saluduni1.2/` — Código fuente de la aplicación (`server.py`, `index.html`, `app_wsgi.py`) e historial de cambios.
- `tests/` — Pruebas automáticas de la API.
- `.github/workflows/` — Pipeline de integración continua: compila el código, verifica que no haya bases de datos subidas y ejecuta las pruebas.

---

## Flujo de Trabajo y Contribución

- Cada integrante trabaja en ramas con la nomenclatura `feat/nombre-tarea` o `docs/nombre-artefacto`.
- Los mensajes de commit se redactan en modo imperativo (ej. `Agrega registro de riesgos`).
- Todo cambio relevante en el alcance o diseño se registra formalmente en `docs/decisiones.md`.
