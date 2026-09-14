<!-- docs/plan.md: bloques de trabajo con criterio de aceptación, abiertos vs cerrados.
     No es la bitácora (docs/memoria.md) ni el análisis (docs/ring-track.md): aquí solo el checklist.
     Se actualiza en el mismo lote que cualquier cambio de estado. -->

# Plan — pista Ring

**Última actualización:** 2026-09-14 (alcance: capa espacial general; Ring como infraestructura,
iPhone opcional como cámara a bordo, rover digital como consumidor; CCTV excluido)
**Cierre de submission:** 2026-10-23, 12:00 PM PT · quedan ~5 semanas de trabajo real

## Abiertos

- [ ] **B0 · Producto y contrato de salida.** Implementar el flujo mínimo
      `Ring/fixture → Observation → mapa espacial → can-traverse() → rover digital`. El contrato
      debe devolver `PROCEED`, `HOLD` o `UNKNOWN`, una razón legible y evidencia (`device_id`,
      timestamp y celdas afectadas). Ningún estado desconocido puede autorizar tránsito.

- [ ] **B1 · Cerrar las cinco incógnitas contra la doc oficial.** `developer.amazon.com/docs/ring`
      no se pudo leer desde el entorno donde se escribió `docs/ring-track.md`.
      *Criterio de aceptación:* las cinco preguntas de `docs/ring-track.md` §6 respondidas en
      `docs/memoria.md`, cada una con URL y fecha de lectura. La que decide el calendario:
      **si el Playground entrega webhooks o solo eventos por el flujo de live view.**

- [ ] **B2 · Registro de app y account linking.** Bloquea webhooks, procesadores de video y
      overlays, que en el sample oficial solo existen en modo refresh token.
      *Criterio:* `client_id` y `client_secret` emitidos, flujo OAuth completado y un
      `RING_REFRESH_TOKEN` propio renovando solo. **Arranca el mismo día que B1** — es trámite, no
      código, y no se sabe cuánto tarda.

- [ ] **B3 · Primer contacto real con la API, con mediciones.** Token del Playground →
      `GET /v1/devices` propio y un evento simulado (Package, Vehicle o Motion) de punta a punta.
      *Criterio:* salida real pegada en `docs/memoria.md`, más las seis mediciones de
      `docs/perception.md` §7: resolución y fps del WHEP, latencia glass-to-glass, duración máxima de
      sesión, sesiones simultáneas por cuenta, si `/capabilities` expone intrínsecos, y —la que más
      pesa— **si el live view simulado entrega video sintético o un clip enlatado**. Si es enlatado,
      B8 necesita dispositivo físico o un clip propio, y eso cambia el plan completo.

- [x] **2026-09-14 — B4 · Alcance del demo escogido.** Rangyuu no será un producto fijo para un garaje
      ni una solución CCTV. Será una capa espacial reutilizable para robots y dispositivos autónomos.
      Ring es la fuente de infraestructura; un video del iPhone puede representar el sensor a bordo;
      el consumidor visible será un rover digital. Hardware físico queda como extensión opcional.

- [ ] **B8 · Calibración y mapa de ocupación.** Homografía al plano del suelo desde cuatro
      correspondencias medidas, y rejilla 2D con **incertidumbre por celda** alimentada por el
      `bounding_box` de los eventos.
      *Criterio:* un objeto en una posición conocida cae dentro de la tolerancia declarada; el error
      medido queda escrito en `docs/memoria.md` — no "funciona", sino cuántos centímetros a cuántos
      metros. Las celdas ocluidas salen como **desconocido**, nunca como libre.

- [ ] **B10 · Runtime de inferencia local.** Consumir la sesión WHEP desde un proceso propio —no el
      navegador— y correr el modelo en el equipo del sitio.
      *Criterio:* frames decodificados fuera del navegador (WHEP es WebRTC con señalización HTTP: el
      `POST` del SDP offer y el manejo de la `Location` hay que escribirlos, y **no se sabe cuánto
      cuesta**), inferencia local medida en milisegundos, **cero llamadas de inferencia a terceros**,
      y el presupuesto de `docs/architecture.md` §5 con número real por tramo. Prueba obligatoria:
      **cortar internet con el sistema andando** y verificar que toma la acción segura en vez de
      quedarse con la última lectura.

- [ ] **B11 · Adaptador de cámara a bordo (iPhone, opcional en vivo).** Primero soportar MP4 como
      fixture reproducible en `fixtures/iphone/`; después, si queda tiempo, añadir captura WebRTC
      desde Safari. El iPhone nunca reemplaza la llamada real a Ring y se etiqueta como
      `IPHONE_ONBOARD`.

- [ ] **B9 · Contrato de degradación.** La tabla de `docs/perception.md` §6, en código y con tests.
      *Criterio:* cada fila tiene su test — cámara offline, celda desconocida en la trayectoria,
      confianza baja, homografía derivada, evento que contradice el frame. Todas terminan en la
      acción segura, y ninguna trata *desconocido* como *libre*. Incluye la **caducidad** de
      `docs/architecture.md` §6: una celda observada hace más de la ventana declarada vuelve a
      desconocido, y el sistema arranca en el estado seguro, no en el permisivo.

- [ ] **B5 · Verificación de la firma HMAC-SHA256 del webhook.** Se necesita igual para no aceptar
      eventos falsos, y es el candidato natural al PR upstream de B6.
      *Criterio:* un evento con firma válida se acepta, uno con firma alterada se rechaza, y ambos
      casos quedan en tests.

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
