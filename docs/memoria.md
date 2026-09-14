<!-- docs/memoria.md: bitácora por sesión. Qué se hizo (resultado verificable), qué NO se verificó
     y por qué, y dónde queda cada pendiente. No se documenta lo que se pidió: se documenta lo que
     quedó. -->

# Memoria

## 2026-09-14 — Eje del proyecto

**Qué se hizo**

- `docs/perception.md`: queda escrito el eje — las cámaras Ring como capa de percepción de
  infraestructura, previa al LIDAR, con la distinción entre sensado a bordo y de infraestructura como
  base del argumento.
- Verificado **leyendo el código del sample**, no la documentación: el live view es una sesión WHEP
  real (`POST /v1/devices/{id}/media/streaming/whep/sessions`, SDP offer → answer, `Location` de
  sesión, `DELETE` para cerrar) y el sistema de plugins expone
  `process(frame: ImageData, canvas, video)`, o sea acceso a píxeles crudos con overlay. La visión por
  computador sobre frames reales es viable por ese camino.
- Documentados siete límites duros (sin profundidad, sin intrínsecos publicados, sin sincronía ni
  IMU, latencia de red, streaming bajo demanda, `/location` es país y estado y no coordenadas, y no
  existe API de actuación), la homografía al plano del suelo como puente de píxeles a metros, seis
  modos de falla y el contrato de degradación.
- `docs/plan.md`: B3 pasa a exigir seis mediciones; B4 se reescribe como alcance del demo; entran
  B8 (calibración y mapa de ocupación) y B9 (contrato de degradación con un test por fila).

**Qué NO se verificó, y por qué**

- **Las seis mediciones de `docs/perception.md` §7.** No hay token de Ring todavía. La que decide el
  diseño: si el live view simulado del Playground entrega video sintético o un clip enlatado — si es
  enlatado, calibrar contra él no es real y B8 necesita hardware o un clip propio. → B3.
- **Si `/capabilities` expone parámetros intrínsecos de cámara.** Sin ellos la calibración es manual
  y el error es mayor. → B1, B3.
- **La precisión alcanzable de la homografía** a las distancias de un garaje o una entrada. No se
  midió nada: no hay cifra de error y no debe citarse ninguna hasta que B8 la produzca. → B8.
- **Nada de esto se probó contra la API.** El eje está escrito, no demostrado.

**Dónde quedan los pendientes:** B1, B3, B8 y B9 de `docs/plan.md`.

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
