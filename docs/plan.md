<!-- docs/plan.md: bloques de trabajo con criterio de aceptación, abiertos vs cerrados.
     No es la bitácora (docs/memoria.md) ni el análisis (docs/ring-track.md): aquí solo el checklist.
     Se actualiza en el mismo lote que cualquier cambio de estado. -->

# Plan — pista Ring

**Última actualización:** 2026-09-15 (alcance: capa espacial general; Ring como infraestructura,
iPhone opcional como cámara a bordo, rover digital como consumidor; CCTV excluido)
**Cierre de submission:** 2026-10-23, 12:00 PM PT · quedan ~5 semanas de trabajo real

## Abiertos

- [ ] **B12 · La app.** Tres destinos principales, especificados en
      [app.md](app.md): Ahora, Caminata y Sistema. Corre
      como web app servida por el propio proceso (`python -m rangyuu.serve`), porque compilar
      nativo para iOS exige un Mac.
      *Tomado por Codex el 2026-09-16:* consolidar la arquitectura de información alrededor de
      Ahora, Caminata y Sistema, y reparar los tres flujos de CI que hoy fallan antes de validar.
      *Hecho el 2026-09-16:* Espacio y Evidencia quedaron dentro del mapa de Ahora; Fuentes y
      Configurar se unieron en Sistema. Setuptools ahora empaqueta solo `rangyuu` y `provider-pr`
      instala el proyecto antes de probar. Suite completa en 163 pruebas y wheel construido.
      *Tomado por Codex el 2026-09-16:* revisión visual y simplificación de la interfaz contra las
      referencias de Ring suministradas, sin cambiar el contrato de datos ni las decisiones.
      *Hecho el 2026-09-16:* jerarquía reducida a una decisión dominante por pantalla, superficies
      blancas amplias con radio consistente, cian único de acción, metadato subordinado y navegación
      inferior con iconos. Revisado a 390x844 y 1024x900; suite completa en 151 pruebas.
      *Hecho el 2026-09-15:* las seis pantallas existen y se alimentan del núcleo real; los cuatro
      estados de pantalla derivan de las tres decisiones con reglas probadas.
      *Hecho también:* revisión en navegador real con Playwright y seis pruebas de extremo a extremo;
      interfaz alineada al lenguaje visual de la app de Ring para que integrarla sea trivial.
      *Hecho el 2026-09-16:* `main` absorbió `codex/north-navigation-ci` por fast-forward y con eso
      **CI remota quedó verde** —`Rangyuu CI` y `build-scan` venían fallando en `main`—. El worker
      programado ya no falla por falta de `RANGYUU_PROVIDER_URL`. Cierra el pendiente de ejecución
      remota; la evidencia son los números de run en [verificacion.md](verificacion.md).
      *Falta:* (1) probar el **modo caminata en un iPhone real**, que necesita HTTPS o túnel porque
      Safari no da cámara en HTTP; (2) **calibración a bordo del teléfono**, sin la cual la caminata
      observa pero no escribe en el mapa; (3) alimentar la app desde una **sesión WHEP viva** en vez
      del sembrado inicial; y (4) la vista de evidencia con imagen al tocar una celda.

- [ ] **B6 · Mini challenge: Open Source — listo para enviar, sin abrir.** Escogido Open Source sobre
      AWS Builder: la contribución sale del trabajo que ya existía y no agrega superficie de nube.
      El trabajo está hecho y probado contra la API real: fork `LuisAlejandroCR/ring-api-helloworld`,
      rama `add-whep-live-view-script`, commit `ed293da` — `scripts/live_view.py` abre una sesión WHEP
      desde la terminal y con `--frames` mide resolución y fps reales.
      *Criterio:* abrir el PR **cuando el proyecto esté terminado**, no antes. Se abrió el 2026-09-15
      como <https://github.com/AmazonAppDev/ring-api-helloworld/pull/23> y se cerró el mismo día por
      decisión escogida; reabrirlo es un clic y conserva la URL.

- [ ] **B1 · Cerrar las cinco incógnitas contra la doc oficial.** `developer.amazon.com/docs/ring`
      no se pudo leer desde el entorno donde se escribió `docs/ring-track.md`.
      *Criterio de aceptación:* las cinco preguntas de `docs/ring-track.md` §6 respondidas en
      `docs/memoria.md`, cada una con URL y fecha de lectura. La que decide el calendario:
      **si el Playground entrega webhooks o solo eventos por el flujo de live view.**

- [ ] **B2 · Registro de app y account linking.** La app quedó creada el 2026-09-15 con nombre
      interno `Rangyuu` y scopes mínimos —Cameras and Doorbells, más Account and Lifecycle, que es
      automático—. Falta la mitad que desbloquea webhooks.
      *Criterio:* `client_id` y `client_secret` emitidos y cargados en `.env.local`, flujo OAuth
      completado y un `RANGYUU_REFRESH_TOKEN` propio renovando solo contra `RANGYUU_TOKEN_URL` —cuya ruta
      exacta sigue sin verificarse y por eso es configurable, no está codificada.

- [x] **2026-09-14 — B4 · Alcance del demo escogido.** Rangyuu no será un producto fijo para un garaje
      ni una solución CCTV. Será una capa espacial reutilizable para robots y dispositivos autónomos.
      Ring es la fuente de infraestructura; un video del iPhone puede representar el sensor a bordo;
      el consumidor visible será un rover digital. Hardware físico queda como extensión opcional.

- [ ] **B8 · Calibración medida y oclusión derivada del frame.** La mitad métrica está cerrada el
      2026-09-15: homografía ajustada sobre cuatro marcas en un rectángulo de 0,90 x 1,50 m medido
      con cinta, y **error de 0,9 cm sobre 61 cm (1,6 %)** contra juntas de baldosa que no entraron en
      el ajuste, con prueba de regresión en `tests/test_calibration_home.py`.
      *Añadido el 2026-09-16:* auditando `claude/stellar-project-setup-gd0ba3` se encontró que la
      medición de 0,9 cm era **decorativa**: `Site.now()` autorizaba con `calibration=None` y la
      validez salía del residuo del propio ajuste, que siempre da ~0 (Lección 3); recalibrar desde
      la interfaz heredaba el error medido de la matriz anterior. El arreglo está medido —173
      pruebas, 5 caen al invertir la puerta— y entró en `main` como `78da540`. La medición de 0,9 cm
      pasó de decorativa a **portante**: `serve.py:41` la pasa y por eso la app sigue autorizando.
      *Falta todavía:* la misma puerta en el **camino del webhook** (`spatial.py:67` valida
      *ajustada*, no *medida*) y `session unavailable`, inalcanzable porque ese mismo renglón fija
      `session_active=True`. Ambas piden un error medido **por dispositivo**, que es justo lo que
      falta abajo.
      *Falta:* (1) el error **más allá de 1,50 m**, que es donde la homografía se degrada y hoy no hay
      marca medida; (2) el mismo error **con la cámara de Ring**, no con un teléfono; y (3) la
      oclusión **derivada del frame** en vez de declararse desde fuera.

- [ ] **B10 · Runtime de inferencia local.** Cerrado salvo un tramo. El lazo completo corrió contra
      una **sesión WHEP viva**: 400 frames a 1280x720, decodificación 7,48 ms, **inferencia 0,58 ms**,
      decisión 0,10 ms → 8,16 ms por frame, ~122 fps de capacidad contra los 29 fps que entrega la
      cámara. Con el feed vivo autoriza; al cortarlo cae a `HOLD` por `feed stale`. Que no haya
      inferencia de terceros está probado envenenando `socket`.
      *Falta solo:* el tramo de **actuación por LAN**, que no se puede medir hasta que el consumidor
      viva fuera del proceso.

- [ ] **B11 · Metraje propio como fuente de calibración — prioridad alta desde el 2026-09-15.**
      Deja de ser opcional: es la única fuente con plano de suelo medible, porque el clip del
      Playground no lo tiene. Grabar con el iPhone una escena con cuatro puntos **medidos con cinta**,
      guardarla en `fixtures/iphone/` y calibrar contra ella.
      *Criterio:* MP4 reproducible en el repo, las cuatro correspondencias anotadas con su medición
      real, y el error de B8 calculado contra ellas. Se etiqueta `IPHONE_ONBOARD` y nunca reemplaza la
      llamada real a Ring.
      *Añadido el 2026-09-16:* el carril de a bordo tiene dos implementaciones. La heurística de
      texturas quedó medida en **22 % de precisión** y solo avisa. El detector ONNX local
      (`rangyuu/vision.py`, 24 ms por frame) **sí reconoce la moto marcada**, pero con una cámara sin
      calibrar no hay distancia, y sin distancia no se decide si un objeto obstruye: por eso sus
      avisos aciertan entre 13 % y 20 %.
      *Lo que desbloquea el resto:* **calibración a bordo del teléfono**. Con ella el objeto detectado
      cae en una celda y el carril puede frenar con fundamento.
      *Hecho el 2026-09-16 — todo el camino de código, nada de metraje:*
      (1) la **puerta**, `rangyuu/onboard_calibration.py`: `verified_homography()` devuelve la matriz
      solo si el fixture está declarado `measured` y su error contra puntos **fuera del ajuste** cae
      bajo 1,5 cm; en cualquier otro caso devuelve `None`, que es la respuesta segura.
      (2) la **plantilla**, `fixtures/iphone/calibration_points.json`, deliberadamente sin llenar
      (`"status": "pending"`), y el **protocolo de grabación**, `fixtures/iphone/MEDICIONES.md`.
      (3) el **cableado**: `Site.__init__` ya no deja `onboard_homography` en `None` para siempre —
      lo toma de la puerta, con `onboard_calibration` inyectable para las pruebas. `serve.build_site`
      usa el fixture del repo; `rangyuu/walk.py` pasa `onboard_calibration=None` a propósito, porque
      es un banco de medición sobre homografía identidad y escribir celdas con ella sería inventarlas.
      Efecto hoy: **byte por byte el comportamiento anterior** —observa y no escribe—, y el día que se
      anote el clip el carril empieza a escribir sin tocar una línea de código.
      *Falta, y es lo único que falta para cerrar el bloque:* **grabar el clip y medir con cinta**.
      Es un acto físico que nadie ha hecho. Sin él la prueba
      `test_the_recorded_clip_lands_under_the_declared_ceiling` queda en `skipped` y el bloque en
      ⏳ **pendiente**. Rellenar el fixture con números inventados no vale: el residuo del ajuste da
      ~0 siempre y no prueba nada. Evidencia del resto en [verificacion.md](verificacion.md).

- [ ] **B7 · Video y submission.** Producir el video en inglés, menor de tres minutos, usando
      ElevenLabs MCP solo como herramienta de narración/producción y documentando su feedback.
      *Criterio:* Ring aparece funcionando en código y pantalla; el video se envía con margen, no el
      10/23 a las 11:50. Guion y montaje: `docs/video.md` y `docs/test-rig.md`.

## Reparto por semana

| Semana | Foco |
|---|---|
| 09/15 | B1/B2/B3: API, Playground, duración, fuentes y primer frame |
| 09/22 | B0 cerrado; B8 monocámara y mapa espacial |
| 09/29 | B8 multicámara/fixtures, B9 degradación, B10 runtime local, B5 HMAC |
| 10/06 | B0 integrado con rover digital; B11 iPhone grabado y, si procede, WebRTC |
| 10/13 | UX, mediciones, documentación, friction log y video |
| 10/20 | Margen; enviar antes del 21/10 |

## Cerrados

- [x] **2026-09-15 — B3 · Primer contacto real con la API, con mediciones.** `GET /v1/devices`,
      `/status`, `/location` y `/capabilities` respondidos contra Ring; sesión WHEP abierta y cerrada
      desde Python; media H264 decodificada fuera del navegador. Las seis mediciones de
      `docs/perception.md` §7 quedan respondidas salvo la latencia glass-to-glass, que no existe
      contra un clip enlatado y se mueve a B10. Evidencia en [verificacion.md](verificacion.md).

- [x] **2026-09-15 — B0 · Producto y contrato de salida.** El fixture Ring pasa por validación de
      firma HMAC, `Observation`, homografía/calibración server-side, rejilla de ocupación y
      `POST /api/rover/can-traverse`. La decisión incluye razón, evidencia y `authorizes`; solo
      `PROCEED` autoriza tránsito. Verificado con 34 tests. No se verificó contra la API real de
      Ring; eso sigue en B3.

- [x] **2026-09-15 — B9 · Contrato de degradación.** Estado inicial seguro, caducidad, cámara/sesión
      no disponibles, homografía inválida, trayectorias desconocidas, baja confianza y contradicción
      terminan en `HOLD`/`WAIT` o `UNKNOWN` sin autorización. Las decisiones de avance exigen
      evidencia anclada a dispositivo, timestamp y celdas.

- [x] **2026-09-15 — B5 · Verificación HMAC-SHA256.** El receptor verifica los bytes originales del
      cuerpo antes de parsear JSON, usa comparación constante y rechaza firma ausente, alterada o
      con formato inválido. Casos cubiertos por tests HTTP.

- [x] **2026-09-14 — Frontera de nube y local.** `docs/architecture.md`: tres carriles (crítico en
      el sitio, contexto de nube degradable, asíncrono sin voto), el presupuesto de latencia por
      tramo, la caducidad de la ocupación y el arranque en estado seguro. Queda escrito que el frame
      de Ring ya pasó por su nube por construcción, así que "local" acota a dos propiedades —ningún
      frame va a un tercero a inferir, ninguna decisión espera a la red— y no a la independencia del
      sensor.

- [x] **2026-09-14 — Eje del proyecto escogido.** Cámaras Ring como capa de percepción de
      infraestructura, el escalón anterior al LIDAR: `docs/perception.md`. Incluye lo que la API da
      (sesión WHEP real, frames como `ImageData`, `bounding_box` con confianza), lo que no da
      (profundidad, sincronía, intrínsecos, streaming continuo, actuador), la homografía al plano del
      suelo como puente de píxeles a metros, dónde se rompe, y el contrato de degradación.

- [x] **2026-09-14 — Análisis de la pista.** `docs/ring-track.md`: superficie de la API leída del
      sample oficial clonado, el papel real del Playground, el corte entre modo access token y modo
      refresh token, cuatro ideas con riesgo y los dos mini challenges.
