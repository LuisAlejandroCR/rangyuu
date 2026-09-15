<!-- docs/plan.md: bloques de trabajo con criterio de aceptación, abiertos vs cerrados.
     No es la bitácora (docs/memoria.md) ni el análisis (docs/ring-track.md): aquí solo el checklist.
     Se actualiza en el mismo lote que cualquier cambio de estado. -->

# Plan — pista Ring

**Última actualización:** 2026-09-15 (alcance: capa espacial general; Ring como infraestructura,
iPhone opcional como cámara a bordo, rover digital como consumidor; CCTV excluido)
**Cierre de submission:** 2026-10-23, 12:00 PM PT · quedan ~5 semanas de trabajo real

## Abiertos

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

- [ ] **B3 · Primer contacto real con la API, con mediciones.** El cliente ya está escrito y
      probado sin red (`rangyuu/ring_client.py`): resuelve el token del Playground o lo intercambia
      por refresh, refresca antes de expirar, rechaza `http://` y no filtra credenciales en el error.
      Falta ejecutarlo contra Ring.
      *Criterio:* salida real de `GET /v1/devices` y de un evento simulado pegada en
      `docs/verificacion.md`, más las seis mediciones de `docs/perception.md` §7: resolución y fps del
      WHEP, latencia glass-to-glass, duración máxima de sesión, sesiones simultáneas por cuenta, si
      `/capabilities` expone intrínsecos, y —la que más pesa— **si el live view simulado entrega video
      sintético o un clip enlatado**. Si es enlatado, B8 necesita dispositivo físico o un clip propio.

- [x] **2026-09-14 — B4 · Alcance del demo escogido.** Rangyuu no será un producto fijo para un garaje
      ni una solución CCTV. Será una capa espacial reutilizable para robots y dispositivos autónomos.
      Ring es la fuente de infraestructura; un video del iPhone puede representar el sensor a bordo;
      el consumidor visible será un rover digital. Hardware físico queda como extensión opcional.

- [ ] **B8 · Calibración medida y oclusión derivada del frame.** La rejilla ya está hecha:
      `rangyuu/spatial.py` mantiene celda, confianza, caducidad y deduplicación desde el
      `bounding_box`, y `mark_occluded` devuelve una celda ocluida a **desconocido**, nunca a libre
      (con pruebas). Falta lo que no se puede escribir sin escena real.
      *Criterio:* (1) homografía calibrada con cuatro correspondencias **medidas**, con el error
      escrito en `docs/verificacion.md` en centímetros a una distancia dada —no "funciona"—; y (2) la
      oclusión se **deriva del frame** en vez de declararse desde fuera.

- [ ] **B10 · Runtime de inferencia local.** La señalización WHEP ya está resuelta y probada contra
      Ring (`rangyuu/whep.py`, 2026-09-15): abrir y cerrar sesión desde un proceso Python no requiere
      navegador. Falta el tramo de media.
      *Criterio:* frames H264 **decodificados** fuera del navegador con un cliente WebRTC —`aiortc`
      todavía no está instalado—, inferencia local medida en milisegundos, **cero llamadas de
      inferencia a terceros**, y el presupuesto de `docs/architecture.md` §5 con número real por
      tramo. Prueba obligatoria: **cortar internet con el sistema andando** y verificar que toma la
      acción segura en vez de quedarse con la última lectura.

- [ ] **B11 · Adaptador de cámara a bordo (iPhone, opcional en vivo).** Primero soportar MP4 como
      fixture reproducible en `fixtures/iphone/`; después, si queda tiempo, añadir captura WebRTC
      desde Safari. El iPhone nunca reemplaza la llamada real a Ring y se etiqueta como
      `IPHONE_ONBOARD`.

- [ ] **B6 · Mini challenge — escoger uno.** Un proyecto gana como máximo un premio de pista y uno de
      mini challenge.
      *Open Source:* PR o fork (no necesita merge) a un repo público **dentro de la ventana**, con
      URL de la contribución, repo, usuario de GitHub y descripción. Candidato: B5 hacia
      `AmazonAppDev/ring-api-helloworld`.
      *AWS Builder:* Bedrock / AgentCore / Strands / Kiro Crew con integración documentada — **todo
      en el carril asíncrono** (`docs/architecture.md` §7): redactar la alerta, entrenar o exportar el
      modelo que corre local, transportar la mensajería. Nunca en el lazo de control.

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
