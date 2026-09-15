<!-- docs/verificacion.md: qué está comprobado, con qué comando, y qué sigue sin comprobar.
     Una fila pasa a ✅ solo cuando alguien que no la escribió puede repetir la comprobación.
     No es el plan (docs/plan.md) ni la bitácora (docs/memoria.md): es la evidencia.
     Toda corrección a un dato ya documentado entra aquí, fechada. -->

# Verificación

## Comprobado

| Qué | Cómo se repite | Estado | Fecha |
|---|---|---|---|
| Suite completa del núcleo, 85 pruebas | `python -m pytest -q` → `85 passed` | ✅ | 2026-09-15 |
| La calibración reporta **error en centímetros** por punto, y un punto fuera del ajuste se comprueba aparte | `python -m pytest tests/test_calibrate.py` | ✅ | 2026-09-15 |
| **Media H264 decodificada fuera del navegador**: 1172 frames en 39,9 s | `rangyuu/live.py` con `aiortc 1.15.0`, contra el `Playground Device` | ✅ | 2026-09-15 |
| **Resolución efectiva 1280x720**, por debajo del `max_resolution: 1080` que declara `/capabilities` | Misma corrida | ✅ | 2026-09-15 |
| **~29 fps**; primer frame a **~1,4 s** de abrir la sesión | Misma corrida | ✅ | 2026-09-15 |
| **La media dura ~40 s y se corta**: 1172 frames exactos, luego nada. No es un stream continuo | Dos sesiones consecutivas, idéntico corte | ✅ | 2026-09-15 |
| **El live view simulado es un clip enlatado**: dos sesiones distintas entregan el mismo contenido frame a frame (diferencia media 0,1–2,2 por píxel, atribuible al recodificado y al reloj sobreimpreso) | Comparación perceptual de siete frames muestreados en dos sesiones | ✅ | 2026-09-15 |
| **El clip es un comedero de pájaros en la nieve**, no una entrada ni un garaje | `fixtures/ring/playground_frame_120.png` | ✅ | 2026-09-15 |
| El token del Playground caduca: emitido ~13:13, muerto a las 13:58 con `401` | Reintento de `GET /v1/devices` | ✅ | 2026-09-15 |
| **Sesión WHEP abierta desde un proceso Python, sin navegador.** `POST …/media/streaming/whep/sessions` con SDP offer → `201`, SDP answer y `Location` de sesión; `DELETE` la cierra y responde 2xx | `rangyuu/whep.py`, probado contra el `Playground Device` el 2026-09-15 | ✅ | 2026-09-15 |
| El `Location` es una URL absoluta del propio dispositivo con un parámetro `?location=<token>` | Misma prueba | ✅ | 2026-09-15 |
| El answer ofrece **solo video H264** (payload 96, `sendonly`, `rtcp-mux`), sin línea de audio | Misma prueba | ✅ | 2026-09-15 |
| Hay candidatos ICE host IPv4 e IPv6 y **TCP 443 pasivo**, así que la sesión no exige UDP saliente | Misma prueba | ✅ | 2026-09-15 |
| **Cuatro sesiones simultáneas** sobre el mismo dispositivo: ninguna rechazada; señalización ~0,7 s cada una | Cuatro `open()` seguidos y sus cuatro `close()` | ✅ | 2026-09-15 |
| **Primer contacto real con Ring**: `GET /v1/devices` devuelve un `Playground Device` | `python -c "from rangyuu.ring_client import RingClient; print(RingClient().devices())"` con `RANGYUU_ACCESS_TOKEN` cargado | ✅ | 2026-09-15 |
| La API responde en **JSON:API** (`{"data":[{type,id,attributes,relationships}]}`), no en objetos planos | Misma llamada; el cliente desenvuelve el sobre en `resource()` | ✅ | 2026-09-15 |
| `/status` del dispositivo simulado: `online: true`, con `reported_at` | `RingClient().device_status(<id>)` | ✅ | 2026-09-15 |
| `/location` devuelve **solo país y estado** (`US`, `CA`), no coordenadas | `RingClient().location(<id>)` | ✅ | 2026-09-15 |
| **`/capabilities` NO expone intrínsecos de cámara.** Da `codecs: [AVC]`, `ratio: 16:9`, `max_resolution: 1080`, `supported_resolutions: [1080]`, y configuraciones de `motion_zones` y `privacy_zones` | `RingClient().capabilities(<id>)` | ✅ | 2026-09-15 |
| Cliente de Ring sin red: token del Playground, intercambio de refresh, expiración y rotación | `python -m pytest tests/test_ring_client.py` | ✅ | 2026-09-15 |
| El cliente rechaza `http://`, ids de dispositivo con `/` o `?`, y no filtra el token en el error | `python -m pytest tests/test_ring_client.py` | ✅ | 2026-09-15 |
| Precedencia de configuración: la variable de entorno gana sobre `.env.local` | `python -m pytest tests/test_config.py` | ✅ | 2026-09-15 |
| Demo sin credenciales: libre → ocupado → duplicado rechazado → caducado | `python -m rangyuu` | ✅ | 2026-09-15 |
| DLT normalizado: correspondencias degeneradas y punto al infinito fallan en vez de adivinar | `python -m pytest tests/test_geometry.py` | ✅ | 2026-09-15 |
| Firma HMAC-SHA256 sobre los bytes originales del cuerpo; alterada rechaza con 401 | `python -m pytest tests/test_security.py tests/test_api_contract.py` | ✅ | 2026-09-15 |
| Contrato de degradación: sin evidencia explícita no hay `PROCEED` | `python -m pytest tests/test_core.py` | ✅ | 2026-09-15 |
| Caducidad: celda más vieja que `max_age` responde `cell stale` | `python -m pytest tests/test_spatial.py::test_lifecycle_unknown_stale_and_occupied` | ✅ | 2026-09-15 |
| Oclusión: una celda ocluida vuelve a desconocida, nunca a libre | `python -m pytest tests/test_spatial.py::test_occlusion_returns_a_cell_to_unknown_never_to_free` | ✅ | 2026-09-15 |
| Un evento repetido no vuelve a entrar; dos dispositivos no comparten celdas | `python -m pytest tests/test_spatial.py` | ✅ | 2026-09-15 |

## Correcciones a datos ya documentados

- **2026-09-15 — `pytest` sí está instalado.** La bitácora del 2026-09-14 dice que no lo estaba y que
  las funciones de prueba se ejecutaron a mano. `python -m pytest --version` devuelve `pytest 9.1.1`
  en este entorno; la suite corre formalmente.

## Sin comprobar — ⏳ pendiente

| Qué | Por qué no se pudo | Bloque |
|---|---|---|
| Cualquier llamada a la API real de Ring | No hay `RANGYUU_ACCESS_TOKEN` ni `client_id` en el entorno | B1, B2, B3 |
| Error métrico de la homografía en centímetros | La maquinaria está escrita y probada (`rangyuu/calibrate.py`); falta la entrada. Se intentó con el original `test_home_video.MOV` (3840x2160, 60 fps, 131 s, HEVC) usando las juntas de baldosa de **30,5 x 30,5 cm** como rejilla de referencia: a 1:1 las juntas tienen contraste casi nulo contra la baldosa y arrastran desenfoque de movimiento, así que **no se pueden marcar intersecciones con precisión de píxel**. Sin esa precisión, el error en centímetros que saliera sería inventado | B8, B11 |
| Latencia glass-to-glass real | El clip es enlatado y trae su propio reloj sobreimpreso; contra una grabación no hay glass-to-glass que medir. Necesita dispositivo físico | B10 |
| La ruta real del endpoint de token OAuth | No está en el sample ni se pudo leer la doc oficial; queda en `RANGYUU_TOKEN_URL`, configurable, sin valor por defecto | B1, B2 |
| Sesión WHEP fuera del navegador | Nada escrito todavía; es el riesgo técnico mayor | B10 |
| Oclusión derivada del frame | `mark_occluded` existe y tiene pruebas, pero hoy la oclusión se declara desde fuera, no se detecta | B8 |
| Persistencia de la deduplicación entre reinicios | El registro de eventos vive en memoria | B10 |
