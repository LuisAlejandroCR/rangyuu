<!-- ring-brainstorm.md: análisis de la pista Ring del Amazon Developer Hackathon 2026 e ideas de
     proyecto. Fuentes: el texto oficial de "What to build" (suministrado el 2026-09-14), el repo
     AmazonAppDev/ring-api-helloworld leído en clon local, y resultados de búsqueda sobre las
     release notes del Ring Appstore API. developer.amazon.com está bloqueado desde el entorno donde
     se escribió esto: la §5 marca qué falta confirmar en la fuente primaria. -->

# Pista Ring — qué hay de verdad y qué construir

**Fecha:** 2026-09-14 · Cierre de submission: **2026-10-23, 12:00 PM PT**

## Decisión de producto — 2026-09-14

La línea elegida es **Rangyuu como capa de contexto espacial para dispositivos autónomos**. No es una
automatización fija de garaje ni una solución CCTV. Ring aporta observaciones desde la infraestructura;
una cámara de iPhone puede representar el punto de vista a bordo; el consumidor de la demo será un
rover digital. Rangyuu publica ocupación, confianza y cobertura, y responde si una trayectoria es
`PROCEED`, `HOLD` o `UNKNOWN` con evidencia anclada.

El alcance inicial no requiere comprar hardware. Los videos del iPhone se tratarán primero como
fixtures MP4 reproducibles; la captura WebRTC en vivo es una extensión. Ningún fixture sustituye la
integración real con Ring exigida por la pista. CCTV queda fuera del producto y del plan.

---

## 1. Lo que pide la pista

> Build a new app or extend an existing one using Ring APIs, SDKs, simulators, or devices.
> **A physical Ring device is not required.**
> Priority categories: **access control, business systems, IoT home automation, accessibility,
> caretaking**.

---

## 2. El "simulador": qué es exactamente

No hay un emulador de dispositivo tipo Android Emulator. Lo que existe es el
**Ring Developer Playground** (`developer.amazon.com/ring/console/playground`):

- Te da un **access token corto (~30 min)** que sirve contra todas las APIs de Ring. **Sin registrar
  app, sin OAuth, sin credenciales de cliente y sin suscripción Ring activa.**
- Incluye **simulación de eventos de live view** para **Package, Vehicle y Motion**, con el flujo
  **WebRTC/WHEP completo** y streaming de live view.

Esa es la razón por la que la pista dice que no hace falta hardware: el Playground emite los eventos
y el video. Es también la razón por la que hay poca info suelta — es reciente y casi todo vive
detrás de `developer.amazon.com/docs/ring`, que es la fuente que tienes que leer entera.

## 3. La superficie real de la API (leída del sample oficial)

`AmazonAppDev/ring-api-helloworld` — MIT, Python + Next.js 14. Base: `https://api.amazonvision.com`.

| Endpoint | Qué devuelve |
|---|---|
| `GET /v1/devices` | Lista de dispositivos accesibles |
| `GET /v1/devices/{id}/status` | Online / offline |
| `GET /v1/devices/{id}/capabilities` | Códecs de video, detección de movimiento, mejoras de imagen |
| `GET /v1/devices/{id}/location` | País y estado (cumplimiento) |
| `GET /v1/devices/{id}/configurations` | **Zonas de movimiento y zonas de privacidad**, ajustes de imagen |
| `GET /v1/history/devices/{id}/events` | Histórico: movimiento, timbre, live views |
| `GET /v1/users/me` | Cuenta |
| Live video | **WHEP** (WebRTC-HTTP Egress Protocol) |

**Webhooks firmados con HMAC-SHA256.** Tipos de evento documentados: `motion_detected`,
`button_press`, `person_detected`, `device_added`, `device_removed`, `device_online`,
`device_offline`, `app_integration_added`, `app_integration_removed`, `subscription_activated`,
`subscription_deactivated`. El payload trae `confidence`, `bounding_box` y `thumbnail_url` — o sea,
puedes reaccionar a **quién/qué** sin procesar el video tú mismo.

### El detalle que decide tu calendario

El sample tiene **dos modos de auth** y no son equivalentes:

| Modo | Cómo | Qué habilita |
|---|---|---|
| **Access token** (Playground) | Pegar el token, 30 min | Descubrimiento de dispositivos + **live streaming** |
| **Refresh token** (OAuth) | Registrar app → `client_id`, `client_secret`, account linking | Todo lo anterior **+ webhooks + procesadores de video + overlays** |

**Si tu proyecto vive de reaccionar a eventos, necesitas el modo OAuth — y eso implica registrar la
app.** Empieza ese trámite el primer día, no la última semana. Para desarrollar mientras tanto, el
sample trae `POST /api/webhook/test` que inyecta payloads sintéticos con la misma forma real.

---

## 4. Ideas, ordenadas por lo que ya tienes construido

### A · El cerrojo en la puerta ⭐ (access control + business systems)
La cámara ve; un agente decide; **pero no puede exceder la regla de la casa o del negocio.** Un
`person_detected` o un `package` dispara un plan —abrir, avisar, registrar, pagar al mensajero— y el
motor de políticas decide si eso está permitido, con tope, allowlist y horario, y emite un **recibo
firmado de cada verdicto**: permitido, negado, y por cuál regla.
*Reutiliza:* Cerrojo casi entero — motor de políticas, recibos, herramientas MCP, suite de inyección.
*Demo:* el Playground simula la llegada; el agente propone abrir fuera de horario; el cerrojo niega
con razón legible. Y el mismo pedido con texto que intenta reescribir las reglas.
*Por qué gana:* la pista premia funcionalidad nueva sobre las APIs. Todos van a conectar la cámara a
un LLM; el hueco es que nadie pone un límite que no dependa de pedirle por favor al modelo.

### B · Cuidado de mayores sin mirar a nadie (caretaking)
De los eventos de movimiento se deriva la rutina —salió, volvió, hoy no hubo movimiento a las 9— y
la familia recibe **la señal, nunca el video**. La divulgación mínima de `creva-zk` aplicada al caso
donde una cámara es éticamente más incómoda: vigilar a tu mamá.
*Reutiliza:* la tesis de revelación mínima y la regla de `actty` de que sin ancla no se afirma.
*Por qué gana:* es el demo con más carga humana de las cinco categorías, y la objeción obvia
—"¿entonces mi familia me ve todo el día?"— la respondes de frente en vez de esquivarla.
*Costo:* más código nuevo que A; el modelo de rutina hay que construirlo.

### C · Cadena de custodia de entregas (business systems)
`AidTrace` trasplantado a la puerta de un negocio: cada paquete que llega queda con evidencia
verificable —evento, marca de tiempo, miniatura, firma— y un timeline auditable por el dueño.
Sirve para farmacias, tiendas y logística de última milla, que es terreno que ya conoces.
*Reutiliza:* custodia, QR, offline-first y el patrón de prueba de AidTrace.

### D · La puerta, narrada (accessibility)
`button_press` + `person_detected` + `bounding_box` + miniatura → aviso descriptivo en español para
quien no oye el timbre o no ve bien quién está afuera. Encaja con el mini challenge de AWS Builder
si la descripción la genera Bedrock.
*Costo:* bajo. Es la idea más pequeña de las cuatro — buena como segunda superficie de A o B, floja
sola frente a una bolsa de 190K.

---

## 5. Los dos mini challenges, que aquí salen casi gratis

- **Open Source.** Pide un proyecto open source nuevo con licencia, **o** una contribución (rama,
  fork o PR) a un repo público **durante la ventana del hackathon**, con URL de la contribución,
  repo, usuario de GitHub y una descripción corta. No necesita estar mergeado. La jugada natural:
  un PR a `AmazonAppDev/ring-api-helloworld` con lo que te falte a ti de todos modos —
  **verificación de la firma HMAC-SHA256 del webhook**, o la documentación en español. Es contribución
  real, on-theme, y sale del mismo trabajo.
- **AWS Builder.** Basta usar servicios AWS con integraciones documentadas (Bedrock, AgentCore,
  Strands SDK, Kiro Crew, SageMaker). Construir con Kiro Crew califica por sí solo.

Un proyecto gana como máximo **un premio de pista + un premio de mini challenge**, así que apila
solo uno de los dos.

---

## 6. Qué NO se verificó

- **`developer.amazon.com` está bloqueado** desde el entorno de análisis. Todo lo de la API viene del
  sample oficial clonado y de búsquedas; **la doc de Ring hay que leerla directo** antes de comprometerse.
- **Si el Playground entrega webhooks** o si los eventos simulados solo llegan por el flujo de live
  view. Es la pregunta que decide si necesitas registrar la app el día uno.
- **Cuánto tarda el registro de app / account linking** para conseguir `client_id` y `client_secret`.
- **El reparto del premio por pista** — solo está confirmada la cifra agregada (~190K entre efectivo
  y créditos AWS).
- **Ninguna idea se prototipó.** Esto es análisis, no trabajo entregado.
