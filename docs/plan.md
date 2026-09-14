<!-- docs/plan.md: bloques de trabajo con criterio de aceptación, abiertos vs cerrados.
     No es la bitácora (docs/memoria.md) ni el análisis (docs/ring-track.md): aquí solo el checklist.
     Se actualiza en el mismo lote que cualquier cambio de estado. -->

# Plan — pista Ring

**Última actualización:** 2026-09-14 (repo sembrado; sin código todavía)
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

- [ ] **B3 · Primer contacto real con la API.** Token del Playground → `GET /v1/devices` propio y un
      evento simulado (Package, Vehicle o Motion) visto de punta a punta.
      *Criterio:* salida real pegada en `docs/memoria.md`, con la forma del payload y qué campos
      traen de verdad `confidence`, `bounding_box` y `thumbnail_url`.

- [ ] **B4 · Decidir la idea y escribir la rebanada.** Recomendada: §4A, el motor de políticas en la
      puerta. Alternativas vivas: §4B (caretaking), §4C (custodia), §4D (accesibilidad).
      *Criterio:* decisión escogida escrita con fecha en este archivo, y la rebanada partida en
      entregas semanales mergeables.

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
| 09/22 | B4 cerrado y primera rebanada en código |
| 09/29 | Rebanada central + B5 |
| 10/06 | Segunda superficie y B6 |
| 10/13 | Congelar alcance, B7 |
| 10/20 | Margen. Enviar |

## Cerrados

- [x] **2026-09-14 — Análisis de la pista.** `docs/ring-track.md`: superficie de la API leída del
      sample oficial clonado, el papel real del Playground, el corte entre modo access token y modo
      refresh token, cuatro ideas con riesgo y los dos mini challenges.
