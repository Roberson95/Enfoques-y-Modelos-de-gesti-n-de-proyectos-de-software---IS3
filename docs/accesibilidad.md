# Unidad 7 — Checklist de accesibilidad de la aplicación SaludUni

**Fecha de revisión:** 19/11/2026
**Versión revisada:** SaludUni 1.2, con correcciones en la 1.2.1
**Referencia:** WCAG 2.1, nivel AA (criterios priorizados para una app móvil de turnos)
**Elaboración:** con asistencia de IA (ver `docs/ia-bitacora.md`)
**Responsable de validarlo:** Maximiliano Gaona (Analista QA y Métricas)

La Iteración 4 evaluó la accesibilidad sobre el prototipo. Este checklist aplica los mismos criterios a la aplicación real publicada. Los contrastes se calcularon con la fórmula de luminancia relativa de WCAG, y la navegación con teclado y los nombres accesibles se verificaron en Chrome.

## Resultado general

La versión 1.2 no cumplía 3 criterios: contraste (1.4.3), uso con teclado (2.1.1) y mensajes de estado (4.1.3). Los tres se corrigieron en la 1.2.1. Queda un criterio parcial: las etiquetas visibles de los campos (3.3.2).

**Cumplimiento en la 1.2.1:** 11 de 12 criterios cumplidos y 1 parcial (92 %). Supera la meta de ≥ 90 % de `docs/calidad.md`.

## Checklist

| Criterio WCAG | Qué se verificó | 1.2 | 1.2.1 |
|---|---|:---:|:---:|
| 1.1.1 Contenido no textual | Los íconos (emojis) acompañan siempre a un texto; el código QR tiene nombre accesible. | ✅ | ✅ |
| 1.3.1 Información y relaciones | Títulos con etiquetas de encabezado; listas desplegables y fechas con nombre accesible. | ⚠️ | ✅ |
| 1.4.1 Uso del color | Los estados del turno se muestran con texto (ACTIVO, ATENDIDO, CANCELADO) y los horarios ocupados se tachan, no solo cambian de color. | ✅ | ✅ |
| 1.4.3 Contraste mínimo (4,5:1) | Ver la tabla de contrastes. El verde, el gris y el rojo no alcanzaban el mínimo. | ❌ | ✅ |
| 1.4.4 Cambio de tamaño del texto | La página permite hacer zoom (no bloquea el gesto de ampliar). | ✅ | ✅ |
| 1.4.10 Ajuste del contenido | Diseño de una columna para celular, sin desplazamiento horizontal salvo en las filas de filtros. | ✅ | ✅ |
| 2.1.1 Teclado | Todos los botones son nativos. Las tarjetas de profesionales no se podían abrir con el teclado. | ❌ | ✅ |
| 2.4.7 Foco visible | Se mantiene el indicador de foco del navegador. | ✅ | ✅ |
| 2.5.8 Tamaño del objetivo | Botones y chips de al menos 24 × 24 px. | ✅ | ✅ |
| 3.1.1 Idioma de la página | `<html lang="es">`. | ✅ | ✅ |
| 3.3.2 Etiquetas o instrucciones | Los campos tienen nombre accesible, pero la mayoría muestra el texto de ayuda dentro del campo, que desaparece al escribir. | ⚠️ | ⚠️ |
| 4.1.3 Mensajes de estado | Los avisos (turno reservado, errores) no se anunciaban en los lectores de pantalla; ahora usan `role="status"`. | ❌ | ✅ |

## Contrastes medidos

| Modo | Elemento | Colores | Contraste 1.2 | Contraste 1.2.1 | Resultado |
|---|---|---|:---:|:---:|:---:|
| Claro | Texto principal sobre fondo | `#0f172a` sobre `#f1f3f7` | 16.07:1 | 16.07:1 | ✅ Cumple |
| Claro | Texto secundario (gris) sobre fondo | `#56657a` sobre `#f1f3f7` | 4.28:1 | 5.34:1 | ✅ Cumple |
| Claro | Botón verde con texto blanco | `#ffffff` sobre `#0f766e` | 3.74:1 | 5.47:1 | ✅ Cumple |
| Claro | Texto verde sobre tarjeta (menú activo, próximo turno) | `#0f766e` sobre `#ffffff` | 3.74:1 | 5.47:1 | ✅ Cumple |
| Claro | Etiqueta «ACTIVO» | `#0f766e` sobre `#e6f6f3` | 3.36:1 | 4.91:1 | ✅ Cumple |
| Claro | Etiqueta «CANCELADO» | `#b91c1c` sobre `#fee2e2` | 3.95:1 | 5.30:1 | ✅ Cumple |
| Claro | Etiqueta «ATENDIDO» | `#1e3a8a` sobre `#e0e7ff` | 8.41:1 | 8.41:1 | ✅ Cumple |
| Claro | Botón azul con texto blanco | `#ffffff` sobre `#1e3a8a` | 10.36:1 | 10.36:1 | ✅ Cumple |
| Oscuro | Texto principal sobre tarjeta | `#e8edf6` sobre `#162033` | 13.87:1 | 13.87:1 | ✅ Cumple |
| Oscuro | Texto secundario sobre tarjeta | `#94a3b8` sobre `#162033` | 6.36:1 | 6.36:1 | ✅ Cumple |
| Oscuro | Botón verde con texto blanco | `#ffffff` sobre `#0f766e` | 3.74:1 | 5.47:1 | ✅ Cumple |
| Oscuro | Texto verde sobre tarjeta | `#2dd4bf` sobre `#162033` | 4.36:1 | 8.76:1 | ✅ Cumple |
| Oscuro | Texto rojo sobre tarjeta (botón Cancelar) | `#f87171` sobre `#162033` | 3.37:1 | 5.89:1 | ✅ Cumple |
| Oscuro | Botón azul con texto blanco | `#ffffff` sobre `#3b5bc4` | 6.04:1 | 6.04:1 | ✅ Cumple |

## Pendiente

- **3.3.2:** agregar etiquetas visibles encima de los campos de usuario, contraseña y búsqueda.
- Probar la app con un lector de pantalla (TalkBack en Android o VoiceOver en iPhone) y con al menos un usuario de baja visión, como se hizo con U3 en la I4.
