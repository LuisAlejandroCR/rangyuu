<!-- docs/memoria.md: bitácora por sesión. Qué se hizo (resultado verificable), qué NO se verificó
     y por qué, y dónde queda cada pendiente. No se documenta lo que se pidió: se documenta lo que
     quedó. -->

# Memoria

## 2026-09-14 — Siembra del repo

**Qué se hizo**

- Repo inicializado con `README.md`, `AGENTS.md`, `docs/plan.md`, `docs/ring-track.md` y este archivo.
- `docs/ring-track.md`: análisis de la pista Ring a partir de dos fuentes — el texto oficial de
  "What to build" suministrado el 2026-09-14, y el repo `AmazonAppDev/ring-api-helloworld` (MIT)
  clonado y leído. Quedan documentados los siete endpoints `v1`, el live video por WHEP, los once
  tipos de evento de webhook, el corte entre modo access token y modo refresh token, y el papel del
  Developer Playground como sustituto del hardware.
- `docs/plan.md`: siete bloques abiertos con criterio de aceptación y reparto semanal hasta el cierre
  del 2026-10-23.

**Qué NO se verificó, y por qué**

- **La doc oficial de Ring** (`developer.amazon.com/docs/ring`): el dominio está bloqueado por el
  proxy de egreso del entorno donde se escribió esto. Todo lo de la API sale del sample clonado y de
  resultados de búsqueda. → B1.
- **Si el Playground entrega webhooks**, o si los eventos simulados solo llegan por el flujo de live
  view. Decide si B2 es urgente o no. → B1, B2.
- **Cuánto tarda el registro de app y el account linking** para obtener `client_id` y
  `client_secret`. → B2.
- **El reparto del premio por pista**: solo está confirmada la cifra agregada (~190K entre efectivo y
  créditos AWS), de fuente secundaria. → B1.
- **Ninguna idea se prototipó.** No se escribió una línea contra la API real. → B3, B4.

**Dónde quedan los pendientes:** bloques B1 a B7 de `docs/plan.md`.
