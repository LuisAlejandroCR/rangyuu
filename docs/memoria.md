<!-- docs/memoria.md: bitácora por sesión. Qué se hizo (resultado verificable), qué NO se verificó
     y por qué, y dónde queda cada pendiente. No se documenta lo que se pidió: se documenta lo que
     quedó. -->

# Memoria

## 2026-09-15 — Reconciliación de ramas y oclusión

**Qué se hizo**

- Se descartó la implementación paralela de la rama `codex/rangyuu-rebuild` (rejilla propia, pipeline
  y contrato con `Verdict`) por duplicar lo que ya estaba en `main` con más validación. De esa rama
  se conservó solo lo que `main` no tenía.
- `SpatialState.mark_occluded` entra en `rangyuu/spatial.py`: una celda ocluida se borra y vuelve a
  desconocida; una oclusión anterior a la última observación se ignora. Tres pruebas nuevas.
- `python -m rangyuu` reproduce el fixture por el mismo normalizador y el mismo estado que usa el
  receptor HTTP, e imprime libre → ocupado → duplicado rechazado → `cell stale`.
- Entran `docs/verificacion.md` con ocho filas repetibles, `docs/setup-dev.md` con el paso a paso
  para entregar las credenciales de Ring, y `.env.example` versionado sin valores.
- La suite quedó en 40 pruebas pasando.

**Qué NO se verificó, y por qué**

- La oclusión se declara desde fuera; todavía no se deriva del frame. Queda en B8.
- Sigue sin haber una sola llamada contra la API real de Ring ni un error de homografía medido en
  centímetros.

**Dónde quedan los pendientes:** B1, B2, B3, B8 y B10 de [plan.md](plan.md).

## 2026-09-15 — Núcleo espacial, degradación y API del rover

**Qué se hizo**

- Se implementó DLT homogéneo con normalización Hartley, SVD y escala que no asume `h33 != 0`.
- Se añadió una rejilla espacial por dispositivo: calibración server-side, proyección del punto
  inferior central del bounding box, caducidad, deduplicación y ocupación derivada del tipo de evento.
- El receptor `POST /api/webhook/ring` valida HMAC sobre bytes originales, tamaño y JSON; el rover
  consulta `POST /api/rover/can-traverse` y recibe una decisión anclada a evidencia.
- El contrato de degradación exige evidencia explícita para `PROCEED`; las rutas desconocidas,
  obsoletas, ocupadas o contradictorias nunca autorizan tránsito.
- La suite local terminó con 34 pruebas pasando, más compilación Python y revisión de diff.

**Qué NO se verificó, y por qué**

- No se conectó una cuenta, webhook ni stream real de Ring. Las pruebas usan fixtures deterministas;
  el contacto real y las mediciones siguen en B1/B2/B3.
- La tolerancia geométrica está validada en casos sintéticos; todavía no hay un error medido en un
  sitio físico, por lo que B8 permanece abierto.
- La deduplicación vive en memoria y no persiste entre reinicios; es suficiente para el demo, no para
  un despliegue productivo. Queda como trabajo de endurecimiento antes de producción.

## 2026-09-14 — Producción del video y montaje USB-C

**Qué se hizo**

- ElevenLabs MCP quedó escogido como herramienta de producción para narración, audio y recursos del
  video, sin dependencia en el runtime de Rangyuu.
- Se documentó un guion de demo de menos de tres minutos en `docs/video.md`, con Ring visible en la
  integración y los estados `PROCEED`, `CUIDADO`, `PARA` y `UNKNOWN`.
- Se documentó en `docs/test-rig.md` el montaje base iPhone USB-C → portátil y la opción de
  capturadora HDMI-UVC para grabar la demo.
- Se dejó explícito que la depuración nativa con Xcode requiere Mac; en Windows el camino inicial es
  MP4, web o build remoto.

**Qué NO se verificó, y por qué**

- No se creó todavía el video ni se probó la conexión USB-C con un modelo concreto de iPhone,
  adaptador o capturadora. Queda pendiente en B7 y B11 de `docs/plan.md`.
- No se ha autenticado ElevenLabs MCP ni se ha generado un artefacto. La cuenta, permisos y costos
  quedan fuera del repositorio y deben validarse antes de producir.

## 2026-09-14 — Challenge 3 de ElevenLabs

**Qué se hizo**

- Se incorporó al plan la posibilidad de presentar el video de Rangyuu al Challenge 3: MCP de
  ElevenLabs, separado de la submission de Amazon.
- Quedó registrada la regla operativa: para esa entrada, todo elemento generado debe provenir de
  ElevenLabs; no se mezclará otra IA generativa en la cadena creativa.
- `docs/video.md` ahora contiene el tag de publicación, la cita del anuncio y la separación entre
  herramienta creativa y runtime del producto.

**Qué NO se verificó, y por qué**

- No se verificaron los canales concretos de Discord/X ni se creó todavía la publicación. Se hará al
  producir el artefacto, siguiendo el anuncio del reto suministrado en esta sesión.

## 2026-09-14 — Alcance de producto y fuentes de video

**Qué se hizo**

- Se fijó Rangyuu como una capa de contexto espacial general para robots y dispositivos autónomos,
  no como una automatización específica de garaje.
- Ring queda como sensor de infraestructura. El iPhone queda definido como fuente opcional de cámara
  a bordo; un rover digital será el consumidor de demostración.
- CCTV fue excluido del alcance y no será necesario comprar hardware físico.
- El contrato de producto queda reducido a `PROCEED`, `HOLD` y `UNKNOWN`, con razón y evidencia
  anclada a dispositivo, timestamp y celdas afectadas.
- Se añadió B0 para la rebanada vertical y B11 para MP4/WebRTC desde iPhone sin sustituir Ring.

**Qué NO se verificó, y por qué**

- No se verificó todavía que el Playground entregue suficientes dispositivos simultáneos para una
  demo multicámara. Mientras tanto, la segunda fuente se modelará como fixture explícito.
- No se verificó captura WebRTC desde Safari ni recepción fuera del navegador. El camino inicial será
  MP4 reproducible.
- No se ha escrito código ni se ha medido una trayectoria real. El pendiente queda en B0, B3, B8,
  B10 y B11 de `docs/plan.md`.

## 2026-09-14 — Frontera entre nube y local

**Qué se hizo**

- `docs/architecture.md`: decisión escogida de que la inferencia corre local y la nube queda para
  GPS, mensajería y alertas. La regla operativa quedó enunciada como "nada en el camino crítico
  espera a la red".
- Queda documentada la contradicción que esa decisión enfrenta: **el frame de Ring ya viajó por la
  nube de Amazon antes de llegar**, porque la sesión de live view se negocia contra
  `api.amazonvision.com` y los webhooks los entrega su backend. En consecuencia "local" se acota a
  dos propiedades sostenibles —ningún frame sale hacia un tercero a inferir, y ninguna decisión
  espera respuesta remota— y **no** a que el sensor sea independiente de la nube.
- Definidos los tres carriles con sus dos reglas duras: el carril de contexto nunca autoriza por sí
  solo y su ausencia se lee como desconocido; el carril asíncrono no tiene voto.
- Presupuesto de latencia partido en seis tramos, de los cuales cuatro son controlables.
- Modo sin nube: caducidad por celda y arranque en el estado seguro.
- `docs/plan.md`: entra B10 (runtime de inferencia local, con la prueba de cortar internet con el
  sistema andando); B9 absorbe la caducidad; B6 acota AWS al carril asíncrono.

**Qué NO se verificó, y por qué**

- **Si un dispositivo Ring expone RTSP u ONVIF local.** Se asume que no. Si lo hiciera, la §2 entera
  cambia de tono. → B1.
- **Si se puede sostener una sesión WHEP fuera del navegador**, y a qué costo. `aiortc` sostiene
  WebRTC, pero el `POST` del SDP offer y el manejo de la `Location` hay que escribirlos y no se
  probó nada. Es el riesgo técnico mayor del carril crítico. → B10.
- **Todos los números del presupuesto de latencia.** No hay un solo tramo medido. → B3, B10.
- **Qué equipo del sitio alcanza** para el modelo escogido. No se escogió modelo ni equipo. → B10.

**Dónde quedan los pendientes:** B1, B3, B9 y B10 de `docs/plan.md`.

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

## 2026-09-14 — Núcleo inicial verificable

**Qué se hizo**

- Se implementaron homografía planar, proyección, verificación HMAC-SHA256, ingesta de eventos y
  decisiones `PROCEED`/`HOLD`/`UNKNOWN` en `rangyuu/`.
- Se añadieron pruebas de núcleo en `tests/test_core.py`.

**Qué NO se verificó, y por qué**

- No hay integración contra Ring real ni receptor HTTP todavía.
- `pytest` no está instalado en el entorno; la compilación y la ejecución directa de todas las
  funciones de prueba pasaron.

**Dónde quedan los pendientes:** B0, B1, B2, B3, B8, B9, B10 y B11.
