<!-- docs/plan.md: bloques de trabajo con criterio de aceptación, abiertos vs cerrados.
     No es la bitácora (docs/memoria.md) ni el análisis (docs/ring-track.md): aquí solo el checklist.
     Se actualiza en el mismo lote que cualquier cambio de estado. -->

# Plan — pista Ring

**Última actualización:** 2026-09-14 (eje escogido: percepción de infraestructura — ver `docs/perception.md`)
**Cierre de submission:** 2026-10-23, 12:00 PM PT · quedan ~5 semanas de trabajo real

## Abiertos

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

- [ ] **B4 · Fijar el alcance del demo.** El eje ya está escogido (`docs/perception.md`): percepción
      de infraestructura + contrato de degradación. Falta decidir **qué se mueve** al final del
      cable — móvil simulado en pantalla, rover barato, o solo una señal avanzar/esperar/detener
      hacia un tercero — y en qué categoría prioritaria se presenta (IoT home automation y access
      control son las naturales; accessibility o caretaking si el móvil asiste a una persona).
      *Criterio:* decisión escogida con fecha aquí, y la rebanada partida en entregas semanales.

- [ ] **B8 · Calibración y mapa de ocupación.** Homografía al plano del suelo desde cuatro
      correspondencias medidas, y rejilla 2D con **incertidumbre por celda** alimentada por el
      `bounding_box` de los eventos.
      *Criterio:* un objeto en una posición conocida cae dentro de la tolerancia declarada; el error
      medido queda escrito en `docs/memoria.md` — no "funciona", sino cuántos centímetros a cuántos
      metros. Las celdas ocluidas salen como **desconocido**, nunca como libre.

- [ ] **B9 · Contrato de degradación.** La tabla de `docs/perception.md` §6, en código y con tests.
      *Criterio:* cada fila tiene su test — cámara offline, celda desconocida en la trayectoria,
      confianza baja, homografía derivada, evento que contradice el frame. Todas terminan en la
      acción segura, y ninguna trata *desconocido* como *libre*.

- [ ] **B5 · Verificación de la firma HMAC-SHA256 del webhook.** Se necesita igual para no aceptar
      eventos falsos, y es el candidato natural al PR upstream de B6.
      *Criterio:* un evento con firma válida se acepta, uno con firma alterada se rechaza, y ambos
      casos quedan en tests.

- [ ] **B6 · Mini challenge — escoger uno.** Un proyecto gana como máximo un premio de pista y uno de
      mini challenge.
      *Open Source:* PR o fork (no necesita merge) a un repo público **dentro de la ventana**, con
      URL de la contribución, repo, usuario de GitHub y descripción. Candidato: B5 hacia
      `AmazonAppDev/ring-api-helloworld`.
      *AWS Builder:* Bedrock / AgentCore / Strands / Kiro Crew con integración documentada.

- [ ] **B7 · Video y submission.** El video tiene que ser bueno, no solo cumplir el tiempo.
      *Criterio:* enviado con margen, no el 10/23 a las 11:50.

## Reparto por semana

| Semana | Foco |
|---|---|
| 09/15 | B1 y B2 en paralelo (leer doc + arrancar trámite), B3 apenas haya token |
| 09/22 | B4 cerrado y B8 arrancado: calibración con medición real |
| 09/29 | B8 cerrado, B9 en código, B5 |
| 10/06 | Integración de punta a punta y B6 |
| 10/13 | Congelar alcance, B7 |
| 10/20 | Margen. Enviar |

## Cerrados

- [x] **2026-09-14 — Eje del proyecto escogido.** Cámaras Ring como capa de percepción de
      infraestructura, el escalón anterior al LIDAR: `docs/perception.md`. Incluye lo que la API da
      (sesión WHEP real, frames como `ImageData`, `bounding_box` con confianza), lo que no da
      (profundidad, sincronía, intrínsecos, streaming continuo, actuador), la homografía al plano del
      suelo como puente de píxeles a metros, dónde se rompe, y el contrato de degradación.

- [x] **2026-09-14 — Análisis de la pista.** `docs/ring-track.md`: superficie de la API leída del
      sample oficial clonado, el papel real del Playground, el corte entre modo access token y modo
      refresh token, cuatro ideas con riesgo y los dos mini challenges.
