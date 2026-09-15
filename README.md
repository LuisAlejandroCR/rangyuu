<!-- README.md: portada del repo. Qué es esto, en qué estado está y en qué orden leer.
     El análisis vive en docs/ring-track.md; el checklist accionable en docs/plan.md;
     el qué-se-hizo/qué-no-se-verificó en docs/memoria.md. -->

# rangyuu

Repo de trabajo para **Build, Ship, Shape: Amazon Developer Hackathon** (2026), **pista Ring**.

El repositorio de trabajo es privado mientras se desarrolla. La entrega final tendrá que ser pública,
con licencia open source, instrucciones reproducibles y una demostración funcional.

## Estado — 2026-09-14

**Todavía no hay código.** Pista escogida: Ring. Rangyuu será una **capa de contexto espacial para
agentes y dispositivos autónomos**: Ring aporta percepción desde la infraestructura, el iPhone puede
representar la cámara a bordo y un rover digital consume decisiones `PROCEED`, `HOLD` o `UNKNOWN`.
No se usará CCTV y no se dependerá de hardware físico para la demo. El alcance y las puertas técnicas
están en `docs/plan.md`.

## Fechas

| Cuándo | Qué |
|---|---|
| **2026-10-23, 12:00 PM PT** | Cierre de submission |
| 2026-11-09 → 11-20 | Judging |
| ~2026-12-03 | Ganadores |

## Orden de lectura

1. `AGENTS.md` — cómo se trabaja y cómo se documenta aquí.
2. `docs/plan.md` — qué está abierto y qué está cerrado hoy.
3. `docs/perception.md` — el eje: qué se puede sensar con una cámara fija, qué no, y qué pasa cuando falla.
4. `docs/architecture.md` — dónde corre cada cosa: inferencia local, y la nube solo donde no hay prisa.
5. `docs/ring-track.md` — la API de Ring, el Playground y las ideas con su riesgo.
6. `docs/setup-dev.md` — cómo correr el núcleo y cómo entregar las credenciales de Ring.
7. `docs/verificacion.md` — qué está comprobado, con qué comando, y qué sigue pendiente.
8. `docs/memoria.md` — qué se hizo y qué quedó sin verificar, por sesión.
9. `docs/video.md` y `docs/test-rig.md` — producción del video y montaje de pruebas sin hardware.

## La pista, en tres líneas

Se construye contra las **Ring APIs**; **no hace falta un dispositivo físico** porque el
**Developer Playground** entrega token corto y simula eventos de Package, Vehicle y Motion con
WebRTC/WHEP. Categorías prioritarias: access control, business systems, IoT home automation,
accessibility, caretaking. Encima de la pista se puede apilar **un** mini challenge
(Open Source **o** AWS Builder).

## Producto en una frase

**Rangyuu convierte observaciones de cámaras Ring en un mapa espacial con ocupación, confianza y
caducidad, para que cualquier dispositivo pueda consultar si una trayectoria es transitable.**

El producto es general; el rover digital es solamente el consumidor visible de la demostración. El
iPhone, si se usa, representa el sensor a bordo del rover. Los videos grabados son fixtures de prueba,
no sustituyen la integración real con Ring.

## Código disponible

```sh
python -m pytest        # suite completa del núcleo
python -m rangyuu.serve # la app en http://localhost:8080, sin credenciales ni hardware
python -m rangyuu       # demo en terminal: libre → ocupado → duplicado rechazado → caducado
```

| Módulo | Qué hace |
|---|---|
| `rangyuu/geometry.py` | DLT normalizado con SVD: lleva píxeles al plano del suelo en metros. |
| `rangyuu/spatial.py` | Estado espacial por dispositivo: celdas, confianza, caducidad, oclusión y deduplicación. |
| `rangyuu/policy.py` | El contrato de salida: sin evidencia explícita no hay `PROCEED`. |
| `rangyuu/ring.py` | Firma HMAC-SHA256 del webhook y conversión de evento Ring a `Observation`. |
| `rangyuu/ring_client.py` | Cliente de solo lectura de la API de Ring: token, refresco y descubrimiento de dispositivos. |
| `rangyuu/config.py` | Configuración: entorno primero, `.env.local` después. |
| `rangyuu/calibrate.py` | Correspondencias medidas → homografía **y error en centímetros** (medido: 0,9 cm sobre 61 cm). |
| `web/` + `rangyuu/webapp.py` | La app: seis pantallas servidas por el propio proceso ([app.md](docs/app.md)). |
| `rangyuu/ui.py` | Los cuatro estados de pantalla, derivados de las tres decisiones del núcleo. |
| `rangyuu/site.py` | Lo que un sitio sabe: zonas, calibración y bitácora de decisiones. |
| `rangyuu/detect.py` | Detección de movimiento local, sin red: nunca sale un frame a inferir. |
| `rangyuu/runtime.py` | El lazo del sitio con presupuesto por tramo y el perro guardián del feed. |
| `rangyuu/live.py` | Recibe y decodifica la media H264 fuera del navegador (requiere `aiortc`). |
| `rangyuu/whep.py` | Señalización WHEP: abre y cierra la sesión de live view sin navegador. |
| `rangyuu/api.py` | El borde HTTP: `POST /api/webhook/ring` y `POST /api/rover/can-traverse`. |
| `rangyuu/__main__.py` | La demo offline que reproduce `tests/fixtures/b0_events.json`. |

Las credenciales y el entorno están en [docs/setup-dev.md](docs/setup-dev.md); la evidencia
repetible, en [docs/verificacion.md](docs/verificacion.md).
