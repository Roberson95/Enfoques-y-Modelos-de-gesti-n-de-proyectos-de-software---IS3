# Registro de decisiones

## D1 — Evento de cambio obligatorio (Iteración 2)

**Fecha:** (19/11/2026)
**Contexto:** En la prueba de la iteración 2, el 35 % de participantes no logró reprogramar un turno y el personal administrativo solicitó agregar más campos.

**Interpretación del equipo:** El problema principal no parece ser falta de campos, sino comprensión del flujo de reprogramación. Agregar campos ahora aumentaría complejidad y podría empeorar la usabilidad.

**Decisión:** Rediseñar el flujo de reprogramación. Postergar la solicitud de nuevos campos hasta tener evidencia de que son necesarios.

**Acciones:**
1. Rediseñar el flujo de reprogramación.
2. Probar nueva versión con 5 usuarios.
3. Actualizar hipótesis, estimaciones y objetivos de calidad.

**Nueva meta para I3:** ≥80 % de usuarios reprograma sin ayuda y en menos de 2 minutos.

---

## D2 — Pasar del prototipo a una aplicación funcional

**Fecha:** 24/10/2026 (primer despliegue en PythonAnywhere, según el registro de errores del hosting)
**Contexto:** El producto validado en las iteraciones era un prototipo en Figma con una API simulada. Para que el servicio de salud pudiera usarlo con turnos compartidos entre usuarios hacía falta un backend real.

**Decisión:** Construir la aplicación SaludUni como página web con backend en Python y base de datos SQLite, publicada en https://saluduni.pythonanywhere.com/. Se eligió una app web y no una app nativa para que funcione en cualquier celular sin instalar nada.

**Versiones:**
- **1.0 (24/10/2026):** reserva, reprogramación y cancelación; agenda del médico; panel admin con turnos, profesionales, especialidades y usuarios.
- **1.1 (06/11/2026):** cambio y restablecimiento de contraseñas.
- **1.2 (19/11/2026):** horarios propios por profesional, acceso de profesionales, registro de actividad y descarga de copia de la base.

**Backlog derivado de las iteraciones:** estado «Ausente» y acceso directo para marcarlo (sugerencia de U2 en I3), campo «motivo de consulta» visible solo para el profesional (I3), recordatorios de turno y campos administrativos postergados en D1.

**Código:** carpeta `saluduni1.2/`. Pruebas automáticas en `tests/`.

---

## D3 — Retirar la base de datos del repositorio

**Fecha:** 19/11/2026
**Contexto:** En la revisión del repositorio se detectó que `saluduni1.2/saluduni.db` estaba subido al repositorio público. Contiene cuentas de usuario, contraseñas cifradas y el registro de actividad con IP. Esto materializa el riesgo R3.

**Decisión:** Borrar el archivo del repositorio, agregar `*.db` al `.gitignore` para que no vuelva a subirse y cambiar las contraseñas de las cuentas que figuraban en esa base. Las copias de seguridad se guardan fuera del repositorio, en un lugar privado.

**Acciones:**
1. Eliminar `saluduni1.2/saluduni.db` del repositorio.
2. Actualizar `.gitignore`.
3. Cambiar la contraseña del admin y pedir al resto de los usuarios que cambien la suya.
4. Reabrir R3 en `docs/riesgos.md` y agregar la meta correspondiente en `docs/calidad.md`.
