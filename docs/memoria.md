<!-- docs/memoria.md: bitácora por sesión. Qué se hizo (resultado verificable), qué NO se verificó
     y por qué, y dónde queda cada pendiente. No se documenta lo que se pidió: se documenta lo que
     quedó. -->

# Memoria

## 2026-09-15 — El carril de a bordo: la caminata real, con su límite

**Qué se hizo**

- Se recibió `walking_video.mp4`: una caminata real de 58,5 s grabada con el iPhone, 464x832 a 60 fps.
  Es exactamente el caso que el arreglo de la mañana había dejado al descubierto: **una cámara a
  bordo sin calibración no puede escribir celdas métricas**. En vez de fingirlas, se le dio su propio
  carril.
- `rangyuu/onboard.py`: `ForwardClearance` compara la franja de suelo **bajo los pies** —que se sabe
  suelo— con la franja de **unos pasos adelante**. No habla de metros ni de profundidad: responde
  `CLEAR`, `OBSTACLE` o `UNCERTAIN`.
- **Ese carril degrada pero no autoriza.** Un `OBSTACLE` lleva la pantalla a `PARA` aunque el mapa
  diga libre; un `UNCERTAIN` la baja a `CUIDADO`. Es la regla de `docs/architecture.md` §3 aplicada.
- **`ClearanceFilter` con histéresis asimétrica:** empeorar es inmediato, volver a `CLEAR` exige
  cuatro lecturas de acuerdo y 1,2 s. Sin eso el estado parpadeaba varias veces por segundo, que
  como ayuda a la caminata es inservible y como aviso háptico, insoportable.
- `python -m rangyuu.walk <video>` reproduce un clip y responde con números: sobre esta caminata,
  585 lecturas → 149 `AVANZA`, 256 `CUIDADO`, 180 `PARA`, con 40 cambios de estado (~41 por minuto).
- Suite en 147 pruebas.

**Qué NO se verificó, y por qué**

- **La tasa de falsos positivos.** El detector reacciona a *cualquier* cambio de superficie: un
  cambio de baldosa, una sombra dura o una alfombra se leen igual que un obstáculo. Sobre esta
  caminata no hay etiquetado cuadro a cuadro, así que **no se puede afirmar cuántos de esos 180
  `PARA` eran reales**. Es el número que falta antes de ponerle esto a una persona.
- **La cadencia de 41 cambios por minuto no está validada con nadie caminando.** Puede ser correcta o
  agotadora; se sabrá probándola.
- Nada de esto se probó en un iPhone en vivo: el clip se reprodujo desde archivo.

**Dónde quedan los pendientes:** B11 y B12 de [plan.md](plan.md).

## 2026-09-15 — Aviso háptico por estado, con su límite dicho

**Qué se hizo**

- `web/haptics.js`: un patrón propio por estado en tres canales —vibración, tono y voz—, con
  detección de cada canal antes de usarlo. `AVANZA` es un toque corto, `PARA` dos golpes largos,
  `CUIDADO` dos toques y `SIN CERTEZA` tres espaciados.
- **Solo avisa cuando el estado cambia.** Un aviso que se repite cada dos segundos deja de leerse
  como aviso; hay una prueba que lo fija.
- El aviso dejó de vivir solo en la pantalla de caminata: la principal también avisa, porque el
  cambio a `PARA` no debería exigir estar mirando.
- Fuentes muestra **qué canales existen de verdad** en el dispositivo, con un botón para probarlos.
- Cinco pruebas nuevas en navegador real, instrumentando `navigator.vibrate` antes de cargar la
  página. Suite en 132 pruebas.

**Qué NO se verificó, y por qué**

- **La vibración en un iPhone.** Safari en iOS **no expone la API de vibración**: lo probado corre en
  Chromium, donde sí existe. En iPhone el aviso queda en tono y voz, y la app lo declara en vez de
  prometer algo que no puede dar. Es la razón de que haya tres canales y no uno. → B12.
- El tono exige un gesto previo del usuario para que el navegador habilite audio. Se desbloquea con
  el primer toque, pero no se probó el caso de una pantalla que arranca sin que nadie la toque.

**Dónde quedan los pendientes:** B12 y B11 de [plan.md](plan.md).

## 2026-09-15 — Revisión con Playwright y estilo de Ring

**Qué se hizo**

- Se revisaron las seis pantallas en un navegador real a 390x844 con Playwright, y quedaron seis
  pruebas de extremo a extremo en `tests/test_app_e2e.py`, que se saltan solas donde no haya
  navegador. La decisiva: **una celda ocupada sobre la trayectoria deja la pantalla en `PARA`**.
- **Bug encontrado y corregido gracias a esa revisión:** el modo caminata proyectaba el frame del
  teléfono con la homografía de la **cámara fija** y escribía celdas que nadie observó, fuera del
  sitio (`[-2, 6]`). Ahora una fuente sin calibración propia observa, lo declara en Fuentes, y **no
  toca el mapa**.
- Cinco arreglos de interfaz que salieron de mirar las capturas: el estado en la bitácora de
  evidencia no tenía color; las etiquetas de zona se pisaban unas a otras sobre el mapa; el mapa
  dibujaba un marco de celdas vacías; el panel de calibración aparecía vacío; y el botón de parar
  estaba rojo aunque no hubiera nada que parar.
- **El tamaño de celda dejó de ser decorativo:** `POST /api/space/config` rehace la rejilla y
  **dice cuántas observaciones descarta**, porque cambiar la escala invalida lo observado.
- **Decisión escogida: se adopta el lenguaje visual de la app de Ring** —fondo claro, tarjetas
  blancas agrupadas, azul de acción, verde de *Conectado*, navegación inferior— para que integrarla
  del lado de ellos sea trivial. Lo que no se copia es el centro: ahí va el mapa y la decisión, no
  una cuadrícula de cámaras.
- Suite en 127 pruebas.

**Qué NO se verificó, y por qué**

- **La app en un iPhone real.** Todo lo probado corre en Chromium de escritorio emulando un teléfono;
  la cámara de Safari exige HTTPS o túnel. → B12, B11.
- **La calibración a bordo del teléfono**, que es lo que desbloquearía que la caminata escriba en el
  mapa. Hoy solo observa. → B11.

**Dónde quedan los pendientes:** B12, B11, B8 y B2 de [plan.md](plan.md).

## 2026-09-15 — La app: seis pantallas sobre el núcleo real

**Qué se hizo**

- `docs/app.md` fija el producto: Ring responde *qué pasa en casa*, Rangyuu responde *¿puedo avanzar
  por este espacio?*. De ahí salen las cinco pantallas —Ahora, Caminata, Espacio, Fuentes,
  Configurar— más Evidencia, que muestra **decisiones, no clips**.
- **Los cuatro estados de pantalla no son un contrato nuevo.** `rangyuu/ui.py` los deriva de las tres
  decisiones del núcleo con una regla explícita: `CUIDADO` es un `PROCEED` con margen escaso
  —confianza cerca del umbral, observación por caducar, u ocupado adyacente al camino— y **nunca
  asciende un rechazo**. Diez pruebas lo fijan.
- `rangyuu/site.py` reúne runtime, zonas nombradas, calibración y una bitácora corta de decisiones,
  registrando solo las transiciones. `rangyuu/webapp.py` expone seis lecturas y cuatro escrituras y
  sirve `web/`. `rangyuu/serve.py` arranca todo **sin credenciales ni hardware**.
- La interfaz (`web/`) no tiene build ni dependencias: HTML, CSS y JS que piden JSON al proceso
  local. Un color por estado, el rojo solo en `PARA`, y `SIN CERTEZA` en violeta apagado porque es
  una ausencia, no una alarma. El video no aparece por defecto en ninguna pantalla.
- Verificado en el navegador: `AVANZA · camino libre` con el mapa y la trayectoria dibujados, y la
  pantalla de Fuentes mostrando el **error medido de 0,9 cm**, no el 0,0 cm del ajuste —que no prueba
  nada— tras corregirlo al detectarlo.
- Suite en 120 pruebas.

**Qué NO se verificó, y por qué**

- **El modo caminata en un iPhone real.** Safari solo da cámara en HTTPS o `localhost`, así que
  probarlo en el teléfono exige certificado o túnel. En el navegador de escritorio la pantalla
  funciona; con cámara del teléfono, sin probar. → B12, B11.
- **La app alimentada por una sesión WHEP viva.** Hoy el suelo se siembra como observado y un hilo lo
  refresca; el lazo real existe (`LocalRuntime`) y está medido, pero no está conectado a la app.
- La vista de evidencia muestra celda, fuente, edad y confianza, pero todavía **no muestra la imagen**
  al tocar una celda.

**Dónde quedan los pendientes:** B12, B11, B8 y B2 de [plan.md](plan.md).

## 2026-09-15 — B6: PR al sample oficial de Ring

**Qué se hizo**

- Escogido **Open Source** como mini challenge, sobre AWS Builder: la contribución sale del trabajo
  que ya existía —la señalización WHEP desde Python— y no agrega superficie de nube al producto.
- Identificado el hueco leyendo el repo: `scripts/` cubre los siete endpoints REST, pero **live view
  solo existe dentro del hook de React** `app/hooks/useWebRTCStream.ts`. Quien integre desde Python o
  desde un servicio sin navegador tiene que deducir la señalización del código React.
- PR preparado y abierto brevemente como
  <https://github.com/AmazonAppDev/ring-api-helloworld/pull/23>, y **cerrado el mismo día por decisión
  escogida: se reabrirá cuando el proyecto esté terminado.** Rama
  `LuisAlejandroCR:add-whep-live-view-script`. Añade `scripts/live_view.py` en el estilo de la casa
  —`argparse`, `--token`, `--device-id` opcional con autodescubrimiento, `curl` equivalente impreso—,
  una fila en la tabla del README y `aiortc`/`av` como dependencias **opcionales y comentadas**.
- Probado contra la API real antes de enviarlo: `201`, `H264/90000`, cinco candidatos ICE y
  `DELETE → 200`; con `--frames 60`, 60 frames a 1280x720 y 23,4 fps.

**Qué NO se verificó, y por qué**

- **Si lo mergean.** El challenge no lo exige —pide la URL de la contribución dentro de la ventana—,
  pero el PR está cerrado a propósito hasta terminar el proyecto, y el repo tiene siete PRs de
  dependabot abiertos, así que la respuesta puede tardar.
- El script no se probó contra un **dispositivo Ring físico**, solo contra el Playground.

**Dónde quedan los pendientes:** B1, B2, B8, B11 y B7 de [plan.md](plan.md).

## 2026-09-15 — Lazo de control local, medido y con el corte de red probado

**Qué se hizo**

- `rangyuu/detect.py`: detección de movimiento por sustracción de fondo, en numpy y **sin ninguna
  dependencia de red**. Es deliberadamente simple; un modelo más pesado entra detrás de la misma
  firma `detect()`.
- `rangyuu/runtime.py`: el lazo del sitio —frame, inferencia, estado espacial, decisión— con
  presupuesto por tramo y un perro guardián: si no llega un frame dentro de la ventana declarada, el
  veredicto deja de autorizar.
- **Presupuesto medido sobre 200 frames reales a 1280x720**, que es lo que entrega el WHEP:
  decodificación **13,63 ms**, inferencia local **0,66 ms**, decisión **0,14 ms**; total **14,44 ms**
  por frame, ~69 fps de capacidad. A 1024x576 baja a 7,67 ms. Los tres números entraron en
  `docs/architecture.md` §5, que hasta hoy no tenía ninguno.
- **La prueba obligatoria de B10 pasa:** con la celda observada libre el veredicto es `PROCEED`;
  cuando dejan de llegar frames pasa a `UNKNOWN` por `feed stale`, sin que cambie nada más en el
  estado. Es el corte de red, y termina en la acción segura.
- Que la inferencia no hable con terceros está probado, no afirmado: una prueba envenena
  `socket.socket` y `socket.create_connection` mientras se procesa el frame.
- Suite en 98 pruebas.

**Qué NO se verificó, y por qué**

- **El tramo de actuación por LAN**: el rover es digital y vive en el mismo proceso, así que no hay
  salto de red que medir. → B10.
- ~~El lazo contra una sesión WHEP viva~~ — **hecho más tarde el mismo día, con token nuevo**: 400
  frames a 1280x720, 1779 detecciones, y el presupuesto real quedó en **8,16 ms por frame**
  (decodificación 7,48, inferencia 0,58, decisión 0,10), ~122 fps de capacidad contra los 29 fps que
  entrega la cámara. Con el feed vivo el veredicto es `PROCEED`; al cortarlo, `HOLD` por `feed stale`.
- **La calidad del detector**: sobre video de cámara en mano marca movimiento en casi todo el cuadro
  —1907 detecciones en 486 frames—, porque el fondo se mueve con la cámara. Sirve con cámara fija,
  que es el caso de Ring; no sirve para una cámara a bordo en movimiento. → B11.

**Dónde quedan los pendientes:** B8, B10 y B11 de [plan.md](plan.md).

## 2026-09-15 — Homografía calibrada y medida: 0,9 cm sobre 61 cm

**Qué se hizo**

- Con una **foto fija** (960x1280) de un pasillo, cuatro marcas de cinta negra en las esquinas de un
  rectángulo de **0,90 x 1,50 m medido con cinta métrica**, se ajustó la homografía al plano del
  suelo. Los centros de las marcas se leyeron a ~±2 px sobre recortes ampliados.
- **La comprobación es independiente**: tres cruces de junta de baldosa —lado **0,305 m** medido—
  sobre una misma línea del piso, que **no entraron en el ajuste**. Proyectadas dan 0,601 m contra
  0,610 m reales: **0,9 cm de error sobre 61 cm, 1,6 %**, a 0,3–0,9 m del borde cercano. Por tramo:
  0,0 cm y 1,0 cm. Las tres caen en una recta con 1,9 cm de deriva lateral, así que el ajuste no está
  torcido.
- Los puntos quedan versionados en `fixtures/home/calibration_points.json` y
  `tests/test_calibration_home.py` los convierte en prueba de regresión con techo declarado de
  1,5 cm: si alguien toca la geometría, la cifra deja de sostenerse y la suite falla.
- **La imagen no se versiona.** `.gitignore` ahora excluye `*.jpeg`, `*.jpg` y `*.png` salvo el frame
  del Playground. Solo entran las coordenadas.
- Suite en 88 pruebas.

**Qué NO se verificó, y por qué**

- **El error más allá de 1,50 m de profundidad**: no hay marca medida más lejos, y es justo donde la
  homografía se degrada más rápido. → B8, B11.
- **El error con la cámara de Ring**, que tiene otra óptica y otra altura. Lo medido vale para esta
  foto y esta pose. → B8.
- Dos intentos previos en video fallaron y quedó escrito por qué: cámara en mano, desenfoque de
  movimiento, y las cuatro marcas nunca en el mismo frame.

**Dónde quedan los pendientes:** B8 —oclusión derivada del frame y error a más distancia— y B11 de
[plan.md](plan.md).

## 2026-09-15 — Maquinaria de calibración, y por qué el primer video no sirve

**Qué se hizo**

- `rangyuu/calibrate.py`: convierte correspondencias medidas en homografía **y en un error en
  centímetros**, por punto y en agregado. `check_point()` mide un punto que no entró en el ajuste,
  que es la única comprobación honesta: los cuatro puntos del ajuste siempre dan error ~0 y no
  prueban nada. Ocho pruebas.
- Se revisó `test_home_video.mp4` (44,8 s, 464x832, ~40 fps, 1819 frames) suministrado el 2026-09-15,
  junto con las medidas: mueble de vidrios 110x80x28 cm y recuadro de hilo en el piso de 1,50 x 0,90 m.

**Qué NO se verificó, y por qué**

- **No se calibró nada con ese video, y no se escribió ningún error en centímetros.** Dos razones,
  ambas verificadas sobre los frames: la cámara va **en mano y en movimiento** —el desplazamiento
  medio entre frames muestreados va de 2,8 a 36,4 niveles de gris—, así que cada frame tendría su
  propia homografía; y en ningún frame revisado se ven **las cuatro esquinas** del recuadro de hilo a
  la vez. Una homografía exige cámara fija y los cuatro puntos visibles en el mismo frame.
- El archivo está a 464x832, resolución baja para marcar esquinas con precisión de píxel; el error de
  clic se traduce directo en error en centímetros.

- Se recibió después el original `test_home_video.MOV`: 3840x2160, 60 fps, 131 s, HEVC —muy superior
  al MP4 de 464x832— y la medida de la baldosa, **30,5 x 30,5 cm**. Se intentó usar la rejilla de
  juntas como referencia métrica, que es grande y está en el plano del suelo.
- **Tampoco alcanzó, y la razón está medida:** a escala 1:1 las juntas tienen contraste casi nulo
  contra la baldosa y arrastran desenfoque de movimiento por cámara en mano con poca luz. No se
  pueden marcar intersecciones con precisión de píxel, y sin eso el error en centímetros sería
  inventado. No se escribió ninguna cifra.

**Dónde quedan los pendientes:** B8 y B11 de [plan.md](plan.md), a la espera de una toma con cámara
apoyada, cuatro marcas de **alto contraste** en posiciones medidas, y las cuatro en el mismo frame.

## 2026-09-15 — El live view del Playground es un clip enlatado

**Qué se hizo**

- `rangyuu/live.py` recibe la media de la sesión WHEP con `aiortc 1.15.0` y mide lo que un fixture no
  puede: resolución, fps, tiempo al primer frame, duración y cuántos frames distintos llegaron.
- Medido contra el `Playground Device`: **1280x720 a ~29 fps**, primer frame a **~1,4 s**, y la media
  **se corta a los ~40 s** tras 1172 frames exactos. No es un stream continuo. La resolución efectiva
  está por debajo del `max_resolution: 1080` que declara `/capabilities`.
- **El live view simulado es un clip enlatado, no video sintético ni una cámara viva.** Dos sesiones
  consecutivas entregan el mismo contenido frame a frame —diferencia media de 0,1 a 2,2 por píxel,
  atribuible al recodificado y al reloj sobreimpreso—, con idéntico corte a los 1172 frames.
- La escena es **un comedero de pájaros en la nieve** (`fixtures/ring/playground_frame_120.png`), no
  una entrada ni un garaje. **Consecuencia asumida:** ese clip no tiene plano de suelo ni geometría
  conocida, así que **no se puede medir contra él el error de una homografía**. B8 pasa a depender de
  metraje propio y B11 deja de ser opcional.
- El token del Playground se confirmó de vida corta: emitido ~13:13, muerto a las 13:58 con `401`.
- Suite en 77 pruebas. B3 queda cerrado.

**Qué NO se verificó, y por qué**

- **La latencia glass-to-glass no se puede medir contra una grabación**: el clip trae su propio reloj
  sobreimpreso y no hay un instante físico contra el que compararlo. Necesita dispositivo real. → B10.
- No se buscó el techo de sesiones simultáneas; cuatro funcionaron.
- El parámetro `?location=<token>` del `Location` de sesión sigue sin investigarse.

**Dónde quedan los pendientes:** B1, B2, B8, B10 y B11 de [plan.md](plan.md).

## 2026-09-15 — Sesión WHEP real, desde Python y sin navegador

**Qué se hizo**

- `rangyuu/whep.py`: señalización WHEP completa —`POST` del SDP offer, lectura del `Location` de
  sesión, `DELETE` para cerrar—, sin dependencias y con transporte inyectable. Once pruebas cubren
  offer malformado, `Location` relativo, sesión sin `Location`, rechazo del servidor, cuerpo que no
  es SDP y URLs en texto plano.
- **Se abrió una sesión real contra el `Playground Device`**: respuesta `201`, SDP answer válido y
  `Location` absoluto; el `DELETE` la cerró con 2xx. Queda resuelto el riesgo técnico mayor que
  `docs/architecture.md` §4 daba por desconocido: **sostener WHEP fuera del navegador no requiere
  nada exótico**, la señalización es HTTP corriente.
- Medido del answer: solo video **H264** (payload 96, `sendonly`, `rtcp-mux`), sin línea de audio;
  candidatos ICE host IPv4 e IPv6 y **TCP 443 pasivo**, así que la sesión no exige UDP saliente.
- Medido por experimento: **cuatro sesiones simultáneas** sobre el mismo dispositivo, ninguna
  rechazada, ~0,7 s de señalización cada una. No se buscó el techo. El multi-cámara de
  `docs/perception.md` §4 no está bloqueado por este límite.
- Suite en 74 pruebas.

**Qué NO se verificó, y por qué**

- **Resolución y fps efectivos, latencia glass-to-glass y duración máxima de sesión.** Las tres
  exigen **decodificar** la media, no solo señalizar; hace falta un cliente WebRTC —`aiortc` no está
  instalado—. → B10.
- **Si el live view simulado entrega video sintético o un clip enlatado.** Sigue siendo la medición
  que más pesa y depende de lo mismo. → B3.
- El `Location` trae un parámetro `?location=<token>` cuyo significado y caducidad no se investigaron.

**Dónde quedan los pendientes:** B1, B2, B3, B8 y B10 de [plan.md](plan.md).

## 2026-09-15 — Primer contacto real con la API de Ring

**Qué se hizo**

- Con `RANGYUU_ACCESS_TOKEN` del Playground cargado en `.env.local`, `GET /v1/devices` devolvió un
  dispositivo real: `Playground Device`, un Doorbell Pro simulado. Primera llamada verificada contra
  Ring del proyecto.
- **La API responde en JSON:API**, no en objetos planos: `{"data":[{type,id,attributes,relationships}]}`
  con un `meta.time`. El cliente devolvía lista vacía porque buscaba una clave `devices`; ahora
  desenvuelve el sobre en `resource()` y entrega diccionarios planos con `id` y `type`. Un sobre
  inesperado da vacío, nunca una suposición. Seis pruebas nuevas.
- Se añadió `location()` al cliente. Medido: `/location` devuelve solo país y estado (`US`, `CA`),
  `/status` devuelve `online: true` con `reported_at`.
- **`/capabilities` no expone intrínsecos de cámara**: da `codecs: [AVC]`, `ratio: 16:9`,
  `max_resolution: 1080`, `supported_resolutions: [1080]` y configuraciones de `motion_zones` y
  `privacy_zones`. Queda contestada una de las seis mediciones de `docs/perception.md` §7, y confirma
  que la calibración es manual por homografía.
- Suite en 63 pruebas.

**Qué NO se verificó, y por qué**

- Las otras cinco mediciones exigen abrir una sesión WHEP viva, que todavía no se escribió. La que
  más pesa sigue abierta: **si el live view simulado entrega video sintético o un clip enlatado**.
- Solo hay un dispositivo simulado en la cuenta, así que el multi-cámara de `docs/perception.md` §4
  sigue sin poder probarse contra Ring.
- No se probó ningún webhook: eso depende del `client_id` y del account linking. → B2.

**Dónde quedan los pendientes:** B1, B2, B3, B8 y B10 de [plan.md](plan.md).

## 2026-09-15 — Un solo prefijo de variables: `RANGYUU_`

**Qué se hizo**

- Todas las variables de entorno pasan a `RANGYUU_*`, vengan de Ring o sean propias:
  `RANGYUU_ACCESS_TOKEN`, `RANGYUU_CLIENT_ID`, `RANGYUU_CLIENT_SECRET`, `RANGYUU_REFRESH_TOKEN`,
  `RANGYUU_TOKEN_URL`, `RANGYUU_WEBHOOK_SECRET`, `RANGYUU_WEBHOOK_URL`, `RANGYUU_PROVIDER_URL` y
  `RANGYUU_PROVIDER_TOKEN`. Decisión escogida el 2026-09-15: un único prefijo en todo el proyecto;
  lo que cada variable contiene lo dice su nombre, no su prefijo.
- Alcanzados por el cambio: `.env.example`, `AGENTS.md`, `rangyuu/ring_client.py`,
  `rangyuu/service.py`, las pruebas y los cuatro documentos que citaban nombres de variables.
- Suite en 57 pruebas.

**Qué NO se verificó, y por qué**

- Si hay un despliegue vivo leyendo los nombres anteriores, dejará de encontrar el secreto. No se
  pudo comprobar desde aquí: hay que revisar las variables del servicio desplegado y los secrets del
  repositorio en GitHub.

**Dónde quedan los pendientes:** B1, B2, B3 y B8 de [plan.md](plan.md).

## 2026-09-15 — Cliente de Ring, probado sin cuenta

**Qué se hizo**

- `rangyuu/ring_client.py`: cliente de solo lectura contra `https://api.amazonvision.com`. Usa el
  access token del Playground tal cual, o lo intercambia por el refresh token cuando las cuatro
  variables están presentes, y lo renueva un minuto antes de expirar. Expone `devices()`,
  `device_status()`, `capabilities()` y `me()`.
- El transporte es inyectable, así que las once pruebas de `tests/test_ring_client.py` cubren
  refresco, expiración, rotación del refresh token, error 401, JSON inválido y rechazo de `http://`
  **sin tocar la red ni necesitar una cuenta**.
- Higiene de credenciales verificada por prueba: el `repr` de `Credentials` no imprime ningún valor y
  el mensaje de error no contiene el token. Un `device_id` con `/` o `?` no llega a la red.
- La app de Ring quedó creada con nombre interno `Rangyuu` y scopes mínimos. Suite en 57 pruebas.

**Qué NO se verificó, y por qué**

- **La ruta del endpoint de intercambio del token OAuth.** No está en el sample y la doc oficial
  sigue sin leerse, así que no se inventó: vive en `RING_TOKEN_URL`, sin valor por defecto, y el
  cliente falla claro si no está. → B1, B2.
- Ninguna llamada real todavía: no hay `client_id` ni token cargados. → B2, B3.

**Dónde quedan los pendientes:** B1, B2, B3 y B8 de [plan.md](plan.md).

## 2026-09-15 — Configuración por `RING_*` y carga de `.env.local`

**Qué se hizo**

- `rangyuu/config.py` lee la configuración del entorno y, si falta, de `.env.local`. Una variable de
  entorno real **siempre gana** sobre el archivo, para que un secreto de Cloud Run no quede tapado por
  un `.env.local` viejo dentro de la imagen. Tres pruebas cubren la precedencia.
- Los nombres de variables quedan bajo una sola regla en todo el proyecto: `RING_*` es lo que Ring
  emite, `RANGYUU_*` es configuración propia. El receptor espera `RING_WEBHOOK_SECRET` sin respaldo,
  y el worker de GitHub Actions pasa de `AGENT_PROVIDER_*` a `RANGYUU_PROVIDER_*`, que es lo que
  `rangyuu/provider.py` ya leía. `docs/cloud-run.md` y `docs/agent-worker.md` quedan alineados.
- La app de Ring quedó creada con el nombre interno `Rangyuu` y scopes mínimos: Cameras and
  Doorbells, más Account and Lifecycle, que es automático. Los demás grupos de sensores quedaron en
  Off por divulgación mínima.
- Suite en 43 pruebas.

**Qué NO se verificó, y por qué**

- Todavía no hay `client_id`, `client_secret` ni secreto de webhook cargados; nada se probó contra
  Ring. El `Ring Appstore Schedule` no contiene las reglas de datos: están en *Program Requirements*
  y *Content Policy*, que siguen sin leerse y condicionan B6 y `docs/architecture.md` §1.

**Dónde quedan los pendientes:** B1, B2, B3, B6 y B8 de [plan.md](plan.md).

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
