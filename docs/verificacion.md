<!-- docs/verificacion.md: qué está comprobado, con qué comando, y qué sigue sin comprobar.
     Una fila pasa a ✅ solo cuando alguien que no la escribió puede repetir la comprobación.
     No es el plan (docs/plan.md) ni la bitácora (docs/memoria.md): es la evidencia.
     Toda corrección a un dato ya documentado entra aquí, fechada. -->

# Verificación

## Comprobado

| Qué | Cómo se repite | Estado | Fecha |
|---|---|---|---|
| **La app móvil habla en es/en/pt con dos voces, sin red.** 42 clips decodifican; un `require` faltante hace fallar `tsc` (TS2741); el bundle de iOS lista 42 assets `mp3`; la config ya no declara micrófono | `cd mobile && npx tsc --noEmit && npx expo export --platform ios` y contar `ext: mp3` en `dist/metadata.json` | ✅ (lógica y bundle; audio sin escuchar en teléfono) | 2026-10-21 |
| Suite completa, once de ellas en navegador real | `python -m pytest -q` → `186 passed, 1 skipped` (antes de este lote: `181 passed, 1 skipped`; la omitida es el clip de B11, que no existe) | ✅ | 2026-09-16 |
| **El carril del iPhone escribe en el mapa solo con una calibración medida y bajo el techo de 1,5 cm.** `Site` consulta la puerta de `onboard_calibration.verified_homography()` al construirse; con la plantilla sin llenar la respuesta es `None` y el carril observa sin escribir | `python -m pytest -q tests/test_calibration_onboard.py` → `13 passed, 1 skipped` | ✅ | 2026-09-16 |
| La puerta a bordo no es decorativa: hacer que `verified_homography` devuelva la matriz siempre tumba **7 pruebas** (3 de ellas nuevas, más `test_app_e2e.py::test_an_uncalibrated_phone_observes_but_never_writes_to_the_map`) | Sustituir el cuerpo de `rangyuu/onboard_calibration.py:verified_homography` por `return [[1,0,0],[0,1,0],[0,0,1]]` y correr `python -m pytest -q` → `7 failed, 179 passed, 1 skipped` | ✅ | 2026-09-16 |
| El cableado tampoco lo es: dejar `self.onboard_homography = None` fijo en `rangyuu/site.py` tumba la prueba que exige que una calibración medida **sí** abra el carril | Sustituir esa línea por `None` y correr `python -m pytest -q` → `1 failed, 185 passed, 1 skipped` | ✅ | 2026-09-16 |
| El banco de medición (`rangyuu/walk.py`) sigue sin escribir aunque mañana el fixture quede medido: pasa `onboard_calibration=None` a propósito, porque corre sobre homografía identidad | `python -m pytest -q tests/test_calibration_onboard.py -k bench` → `1 passed`; `rangyuu/walk.py:31-35` | ✅ | 2026-09-16 |

| Suite completa, 185 pruebas y una saltada | `python -m pytest -q` → `185 passed, 1 skipped` | ✅ | 2026-09-16 |

| Suite completa, 193 pruebas y una saltada | `python -m pytest -q` → `193 passed, 1 skipped` | ✅ | 2026-09-16 |
| **La interfaz sale en el idioma que pide el navegador**, en inglés y en castellano, y `<html lang>` lo acompaña | `python -m pytest tests/test_i18n_e2e.py::test_the_interface_follows_the_language_the_browser_asks_for` (dos `locale`, `es-ES` y `en-US`) | ✅ | 2026-09-16 |
| Un idioma que no está en la tabla **cae al inglés**, no a una pantalla en blanco | `python -m pytest tests/test_i18n_e2e.py::test_an_unknown_language_falls_back_to_english` (`locale="ja-JP"`) | ✅ | 2026-09-16 |
| La anulación de Sistema **le gana al navegador y sobrevive a una recarga**; volver a «el del navegador» devuelve el idioma del sistema | `python -m pytest tests/test_i18n_e2e.py::test_the_override_wins_over_the_browser_and_survives_a_reload` | ✅ | 2026-09-16 |
| **Traducir no mueve ninguna decisión**: `state`, `authorizes` y `decision` son idénticos antes y después de cambiar de idioma | `python -m pytest tests/test_i18n_e2e.py::test_changing_the_language_moves_no_decision` | ✅ | 2026-09-16 |
| La copia inglesa **no nombra el segundo destino por caminar**: ni `walk`, ni `pedestrian`, ni `step`, ni `on foot` | `python -m pytest tests/test_i18n_e2e.py::test_the_second_destination_is_never_named_after_walking_in_english` | ✅ | 2026-09-16 |
| **Ninguno de los dos idiomas desborda** las tarjetas ni la navegación inferior, a 390x844 y a 1280x900 | `python -m pytest tests/test_i18n_e2e.py::test_neither_language_overflows_the_cards_or_the_bottom_nav` | ✅ | 2026-09-16 |
| Un texto del servidor sin traducción **se muestra tal cual** en vez de esconderse | `python -m pytest tests/test_i18n_e2e.py::test_a_reason_with_no_translation_is_shown_as_is_rather_than_hidden` | ✅ | 2026-09-16 |
| Consola limpia en las tres pantallas, **en los dos idiomas** y en los dos viewports (cuatro combinaciones) | Sonda con Playwright que escucha `console` y `pageerror` desde antes de cargar, con `locale` `es-ES` y `en-US` | ✅ | 2026-09-16 || **Perder el enlace con el sitio retira la autorización** en vez de dejar el último estado en grande | `python -m pytest tests/test_app_e2e.py::test_losing_the_link_to_the_site_withdraws_the_authorisation` (sustituye `fetch` por uno que rechaza y espera a que la pantalla llegue a `SIN CERTEZA`) | ✅ | 2026-09-16 |
| La pantalla **dice** si autoriza, tomándolo del campo `authorizes`, en vez de dejarlo solo en el color | `python -m pytest tests/test_app_e2e.py::test_the_screen_says_whether_it_authorises_rather_than_only_colouring_it` | ✅ | 2026-09-16 |
| **La app carga sin un solo error de consola**, con el oyente puesto antes de `goto` | `python -m pytest tests/test_app_e2e.py::test_the_app_loads_without_a_single_console_error` | ✅ | 2026-09-16 |
| Las etiquetas de zona no se desbordan de la tarjeta ni quedan dentro del SVG | `python -m pytest tests/test_app_e2e.py::test_zone_names_are_legible_html_instead_of_svg_text_that_scales_with_the_grid` | ✅ | 2026-09-16 |
| **Todo el texto pequeño cumple WCAG AA contra el fondo real de su tarjeta**: peor caso 4,80:1 (`stamp` y `group-title`, 11-12 px, sobre `--ground`); antes 2,91:1. La pestaña activa pasó de 2,57:1 a 4,81:1 | Sonda con Playwright a 390x844 y 1280x900 que calcula la razón de contraste WCAG sobre los colores computados de cada token; cifras en `docs/memoria.md` 2026-09-16 | ✅ | 2026-09-16 |
| **Ningún objetivo táctil baja de 44 px** en las tres pantallas y los dos viewports; antes `Evidencia` 25 px, `Probar` 33 px, los `summary` 36 px | Misma sonda: recorre botones y `summary` visibles y lista los de altura < 44 px | ✅ | 2026-09-16 |
| El mapa dejó de tapar la decisión: en teléfono pasó de 500 px contra 154 del veredicto a **388 contra 204**, sin scroll horizontal en ningún viewport | Misma sonda (`getBoundingClientRect` de `.verdict` y `#map-now`) | ✅ | 2026-09-16 |
| Consola limpia en las tres pantallas a 390x844 **y** a 1280x900 | Misma sonda, escuchando `console` y `pageerror` desde antes de cargar | ✅ | 2026-09-16 || Un sitio sin calibración **medida** no autoriza | `python -m pytest -q tests/test_degradation_gates.py` → `10 passed`; invertir la puerta (`calibration_is_verified` devolviendo `True` sin medición) hace caer 5 pruebas | ✅ | 2026-09-16 |
| Recalibrar desde la interfaz retira la medición anterior | `rangyuu/webapp.py:127` pone `measured_error_cm = None`; prueba `test_recalibrating_drops_the_previous_measurement_and_the_authority` | ✅ | 2026-09-16 |
| CI remota verde en `main` tras la reconciliación de ramas | `gh run list --branch main --limit 4` → `Rangyuu CI` y `build-scan` en `success` (runs `35129388309`, `35129388771`); los previos `35125517257` y `35125517447` están en `failure` | ✅ | 2026-09-16 |
| Las tres ramas `codex/*` restantes no tienen trabajo único | `git merge-base --is-ancestor origin/<rama> main` → 0 para `ring-ui-less-is-more`, `block-geometry-dlt` y `north-navigation-ci` | ✅ | 2026-09-16 |
| `codex/rangyuu-rebuild` no aporta nada que `main` no tenga | auditoría concepto por concepto con prueba `archivo:línea`; ver `docs/memoria.md` 2026-09-16 | ✅ | 2026-09-16 |
| El worker programado ya no falla por un proveedor sin configurar | `GITHUB_EVENT_NAME=schedule` con `RANGYUU_PROVIDER_URL` vacío → salida 0 con aviso; `workflow_dispatch` → salida 1 | ✅ | 2026-09-16 |
| **Un detector de objetos ONNX local reconoce la moto que la heurística no podía**: en t=49,5 s devuelve `moto 0.69` y `persona 0.94`; en t=20 s y t=40 s no devuelve nada | SSD MobileNet v1 del ONNX Model Zoo con `onnxruntime 1.30`, sobre `walking_video.mp4` | ✅ | 2026-09-16 |
| **24 ms por frame de media, 34 ms de máximo**, sobre 585 frames a 464x832, en CPU | Misma corrida | ✅ | 2026-09-16 |
| El carril de visión **no frenó ni una vez** en toda la caminata: nada llegó nunca cerca en el corredor. Emitió 174 avisos, 20 dentro de los tramos marcados | Misma corrida, regla obstáculo = en el corredor **y** cerca | ✅ | 2026-09-16 |
| La regla se prueba **sin descargar el modelo**, con una sesión ONNX sustituida | `python -m pytest tests/test_vision.py` | ✅ | 2026-09-16 |
| Las pruebas de navegador esperan por condición, no por reloj: dos corridas seguidas en verde tras haber sido intermitentes | `python -m pytest tests/test_app_e2e.py tests/test_haptics_e2e.py` | ✅ | 2026-09-16 |
| **La precisión del detector a bordo está medida contra verdad de campo: 22 %.** Sobre la caminata de 58,5 s con dos tramos reales marcados —49-50 s y 55-56 s, una moto a lo lejos— de 180 lecturas de "obstáculo" solo 40 caen en esos tramos: **140 frenadas falsas**. Cobertura de los tramos reales: 67 % | `python -m rangyuu.walk walking_video.mp4` más el etiquetado suministrado el 2026-09-16 | ✅ | 2026-09-16 |
| Un criterio alternativo por mancha localizada se probó y es **peor**: 9-11 % de precisión. Las distribuciones se superponen (0,174 en los tramos reales contra 0,136 en el resto) | Barrido de umbrales sobre el mismo clip | ✅ | 2026-09-16 |
| **Una caminata real de 58,5 s grabada con el iPhone atraviesa el carril de a bordo**: 585 lecturas → 149 `AVANZA`, 256 `CUIDADO`, 180 `PARA`; 40 cambios de estado, unos 41 por minuto | `python -m rangyuu.walk walking_video.mp4` (el video no se versiona) | ✅ | 2026-09-15 |
| El carril de a bordo **degrada pero no autoriza**: un `OBSTACLE` lleva la pantalla a `PARA` aunque el mapa dijera libre | `python -m pytest tests/test_ui.py tests/test_onboard.py` | ✅ | 2026-09-15 |
| La histéresis es asimétrica: empeorar es inmediato, volver a `CLEAR` exige cuatro lecturas de acuerdo y 1,2 s | `python -m pytest tests/test_onboard.py::test_going_back_to_clear_needs_agreement_and_time` | ✅ | 2026-09-15 |
| **Cada estado tiene su patrón háptico** y solo avisa al cambiar: `AVANZA [35]`, `PARA [140,80,140]`; el mismo estado repetido no vuelve a vibrar | `python -m pytest tests/test_haptics_e2e.py` (se instrumenta `navigator.vibrate`) | ✅ | 2026-09-15 |
| Fuentes declara qué canales de aviso existen en el dispositivo, en vez de prometerlos | `python -m pytest tests/test_haptics_e2e.py::test_the_sources_screen_declares_which_channels_exist` | ✅ | 2026-09-15 |
| **El momento de la demo, probado en navegador**: una celda ocupada sobre la trayectoria deja la pantalla en `PARA` con la razón visible | `python -m pytest tests/test_app_e2e.py::test_an_occupied_cell_on_the_route_shows_para` | ✅ | 2026-09-15 |
| Las cinco pantallas renderizan sin errores de consola, sin scroll horizontal y con los cuatro estados válidos | `python -m pytest tests/test_app_e2e.py` (Playwright, 390x844) | ✅ | 2026-09-15 |
| **Un frame del teléfono sin calibrar observa pero no escribe celdas** | `python -m pytest tests/test_app_e2e.py::test_an_uncalibrated_phone_observes_but_never_writes_to_the_map` | ✅ | 2026-09-15 |
| **La app arranca sin credenciales y responde**: `AVANZA · camino libre` con la ruta sembrada, y cae a `SIN CERTEZA · hace rato que no llega imagen` cuando el feed envejece | `python -m rangyuu.serve` y `curl localhost:8080/api/space/now` | ✅ | 2026-09-15 |
| Los cuatro estados de pantalla derivan de las tres decisiones del núcleo, y **CUIDADO nunca suaviza un rechazo** | `python -m pytest tests/test_ui.py` | ✅ | 2026-09-15 |
| El borde HTTP de la app: seis lecturas, cuatro escrituras, 422 ante calibración incompleta o frame mal formado, 404 fuera de `web/` | `python -m pytest tests/test_webapp.py` | ✅ | 2026-09-15 |
| La pantalla de Fuentes muestra el **error medido contra puntos ajenos al ajuste (0,9 cm)**, no el error del ajuste (0,0 cm) | `curl localhost:8080/api/sources` | ✅ | 2026-09-15 |
| **El lazo completo corrió contra una sesión WHEP viva**: 400 frames a 1280x720, 1779 detecciones; decodificación 7,48 ms, inferencia 0,58 ms, decisión 0,10 ms → 8,16 ms por frame (~122 fps de capacidad contra 29 fps que entrega la cámara). Con el feed vivo el veredicto es `PROCEED`; al cortarlo pasa a `HOLD` por `feed stale` | `LocalRuntime` alimentado desde `rangyuu/live.py` con `RANGYUU_ACCESS_TOKEN` cargado | ✅ | 2026-09-15 |
| Presupuesto sobre archivo local, como control: 14,44 ms por frame a 1280x720 y 7,67 ms a 1024x576 | 200 y 486 frames por `LocalRuntime.on_frame` | ✅ | 2026-09-15 |
| **La inferencia no abre un socket**: se envenena `socket.socket` y `socket.create_connection` mientras se procesa un frame y el lazo sigue funcionando | `python -m pytest tests/test_runtime.py::test_inference_opens_no_socket` | ✅ | 2026-09-15 |
| **Corte de red con el sistema andando**: con la celda observada libre el veredicto es `PROCEED`; cuando dejan de llegar frames pasa a `UNKNOWN` por `feed stale`, sin que cambie nada más | `python -m pytest tests/test_runtime.py::test_the_network_cut_stops_authorizing_instead_of_holding_the_last_reading` | ✅ | 2026-09-15 |
| La calibración reporta **error en centímetros** por punto, y un punto fuera del ajuste se comprueba aparte | `python -m pytest tests/test_calibrate.py` | ✅ | 2026-09-15 |
| **Error métrico medido: 0,9 cm sobre 61 cm (1,6 %) a ~0,3–0,9 m del borde cercano.** Ajuste con cuatro marcas de cinta en un rectángulo de 0,90 x 1,50 m medido con cinta métrica; comprobación con tres cruces de junta de baldosa (0,305 m) **que no entraron en el ajuste**. Por tramo: 0,0 cm y 1,0 cm | `python -m pytest tests/test_calibration_home.py`, sobre `fixtures/home/calibration_points.json` | ✅ | 2026-09-15 |
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

| El script del PR upstream corre contra la API real: sin flags da `201`, `H264/90000`, 5 candidatos ICE y `DELETE → 200`; con `--frames 60` da 60 frames a 1280x720 y 23,4 fps | `python scripts/live_view.py --token <token>` en el fork | ✅ | 2026-09-15 |

## Correcciones a datos ya documentados

- **2026-09-16 — El carril de a bordo ya no frena, avisa.** Se había cableado para llevar la pantalla
  a `PARA`. Medido contra la caminata etiquetada, acierta el 22 % de sus "obstáculo": frenar con eso
  serían unas catorce paradas falsas por minuto. Ahora degrada a `CUIDADO` y el detector tendrá que
  ganarse el derecho a detener a alguien. Sobre la misma caminata, la pantalla pasa de 180 `PARA` a
  ninguno, con 25 cambios de estado en vez de 40.

- **2026-09-15 — Un objeto oscuro se leía como "demasiado oscuro para juzgar".** En la caminata, un
  vehículo negro tapando el paso salía `UNCERTAIN` en vez de `OBSTACLE`. Ninguno autoriza, así que
  nunca fue inseguro, pero la etiqueta mentía. Corregido comparando con el suelo bajo los pies: con
  suelo iluminado debajo, una franja oscura al frente es un objeto, no falta de luz.
- **2026-09-15 — El replay corría en tiempo de pared.** Procesaba 58 s de video en 3 s, así que la
  histéresis temporal no significaba nada y los estados parpadeaban cada 0,1 s. El reloj del sitio
  ahora sigue al video.

- **2026-09-15 — El modo caminata escribía celdas inventadas.** La revisión con Playwright destapó que
  un frame del iPhone se proyectaba con la homografía de la **cámara fija** y escribía celdas fuera del
  sitio (`[-2, 6]`). Corregido: una fuente sin calibración propia observa y lo declara, pero no toca el
  mapa.

- **2026-09-15 — `pytest` sí está instalado.** La bitácora del 2026-09-14 dice que no lo estaba y que
  las funciones de prueba se ejecutaron a mano. `python -m pytest --version` devuelve `pytest 9.1.1`
  en este entorno; la suite corre formalmente.

## Sin comprobar — ⏳ pendiente

- **La puerta de calibración solo cubre el camino de la app.** `78da540` cerró `Site.now()`, que es
  lo que sirve `serve`/`webapp`. El camino del webhook **no** la tiene: `spatial.py:67` pasa
  `homography_valid=device_id in self.calibrations`, es decir *ajustada*, no *medida*. Es la misma
  trampa del residuo ~0 en otra puerta. Cerrarla necesita un error medido **por dispositivo**, y B8
  dice que para la cámara de Ring ese número todavía no existe: inventarlo sería exactamente la
  ficción que la puerta evita. ⏳ pendiente, y dicho en el PR #4.
- **`session unavailable` es inalcanzable por la API de webhook.** La rama existe en `policy.py:20`,
  pero `spatial.py:67` fija `session_active=True`, así que nada puede dispararla por ese camino. La
  tercera de las "tres puertas" de `3101781` sigue abierta. ⏳ pendiente.

| Qué | Por qué no se pudo | Bloque |
|---|---|---|
| **Que el iPhone real quede calibrado contra el suelo real.** La puerta y su cableado están probados con fixtures sintéticos; lo que falta es físico: grabar el clip y anotar `fixtures/iphone/calibration_points.json` con píxeles y medidas de cinta, según `fixtures/iphone/MEDICIONES.md`. Inventar esos números daría un residuo de ajuste ~0 que no prueba nada, que es justo lo que esta puerta existe para impedir. Repetible el día que exista: `python -m pytest -q tests/test_calibration_onboard.py::test_the_recorded_clip_lands_under_the_declared_ceiling` (hoy `skipped`) | Nadie ha grabado el clip todavía; es un acto físico, no de código | B11 ⏳ pendiente |
| Cualquier llamada a la API real de Ring | No hay `RANGYUU_ACCESS_TOKEN` ni `client_id` en el entorno | B1, B2, B3 |
| **La vibración en un iPhone real.** Safari en iOS no expone la API de vibración; lo probado corre en Chromium, donde sí existe. En iPhone el aviso queda en tono y voz, y así lo declara la app | Requiere el teléfono con HTTPS o túnel | B12 |
| **Si algo obstruye el paso o solo está cerca del paso.** El detector nombra objetos, pero con una cámara sin calibrar no hay distancia, y sin distancia no se puede decidir obstrucción. Es la razón de que los avisos acierten entre 13 % y 20 % contra la verdad de campo | Necesita calibración a bordo o profundidad | B11 |
| El error a distancias mayores que 1,5 m, y con la cámara de Ring en vez de un teléfono | La foto medida cubre hasta 1,50 m de profundidad; más allá no hay marca medida. Dos intentos previos en video fallaron: cámara en mano, desenfoque de movimiento y las cuatro marcas nunca en el mismo frame | B8, B11 |
| Oclusión derivada del frame | `mark_occluded` existe y tiene pruebas, pero la oclusión se declara desde fuera | B8 |
| El tramo de actuación por LAN | No hay consumidor real todavía: el rover es digital y vive en el mismo proceso | B10 |
| Latencia glass-to-glass real | El clip es enlatado y trae su propio reloj sobreimpreso; contra una grabación no hay glass-to-glass que medir. Necesita dispositivo físico | B10 |
| La ruta real del endpoint de token OAuth | No está en el sample ni se pudo leer la doc oficial; queda en `RANGYUU_TOKEN_URL`, configurable, sin valor por defecto | B1, B2 |
| Sesión WHEP fuera del navegador | Nada escrito todavía; es el riesgo técnico mayor | B10 |
| Oclusión derivada del frame | `mark_occluded` existe y tiene pruebas, pero hoy la oclusión se declara desde fuera, no se detecta | B8 |
| Persistencia de la deduplicación entre reinicios | El registro de eventos vive en memoria | B10 |
