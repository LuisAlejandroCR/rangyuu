<!-- docs/memoria.md: bitácora por sesión. Qué se hizo (resultado verificable), qué NO se verificó
     y por qué, y dónde queda cada pendiente. No se documenta lo que se pidió: se documenta lo que
     quedó. -->

# Memoria

## 2026-09-16 — B11: la puerta de calibración a bordo, conectada al carril

**Qué se hizo**

- `Site.onboard_homography` estaba inicializado a `None` en `site.py` y **nadie lo escribía nunca**:
  la puerta de `site.py` que impide que el iPhone escriba en el mapa era una puerta sin bisagra. Ahora
  `Site.__init__` la toma de `onboard_calibration.verified_homography()`, que solo entrega la matriz
  si el fixture está declarado medido y su error **contra puntos fuera del ajuste** cae bajo 1,5 cm.
- El argumento `onboard_calibration` es inyectable, como `calibration` / `measured_error_cm`: acepta
  el fixture anotado, el centinela `SHIPPED_FIXTURE` (por defecto: lee el del repo) o `None`
  («este sitio no tiene calibración a bordo»). Un fixture ilegible o a medio llenar devuelve `None`
  en vez de tumbar el sitio.
- `rangyuu/walk.py` pasa `onboard_calibration=None` explícito. Es un banco de medición del detector
  sobre homografía identidad: si mañana el fixture del iPhone queda medido, el banco **no** debe
  empezar a escribir celdas, porque con identidad esas celdas serían inventadas. `serve.build_site`
  se queda con el fixture del repo y no necesitó cambiar más que un comentario.
- **Hoy el comportamiento es idéntico al de ayer**: la plantilla sigue en `"status": "pending"`, así
  que la respuesta es `None` y el carril observa sin escribir. Lo que cambió es que el día que el
  clip se anote, el carril empieza a escribir solo.
- Suite: `181 passed, 1 skipped` antes → **`186 passed, 1 skipped`** después (`python -m pytest -q`).

**Que las pruebas nuevas prueban algo, comprobado por mutación**

- `verified_homography` devolviendo la matriz siempre → `7 failed, 179 passed, 1 skipped`.
- `self.onboard_homography = None` fijo en `site.py` → `1 failed, 185 passed, 1 skipped`, la que
  exige que una calibración medida **sí** abra el carril. Ambas mutaciones revertidas.

**Qué NO se verificó, y por qué**

- **El clip real no existe.** No se grabó metraje ni se midió con cinta: es un acto físico. La prueba
  `test_the_recorded_clip_lands_under_the_declared_ceiling` sigue en `skipped` y **B11 sigue abierto**.
  Las pruebas de este lote usan fixtures sintéticos (`SYNTHETIC` / `SYNTHETIC_OFF`), que sirven para
  probar la puerta y no pretenden describir ninguna lente real.
- No se rellenó `fixtures/iphone/calibration_points.json` ni se tocó el techo de 1,5 cm. Con números
  inventados el residuo del ajuste daría ~0 y «probaría» una calibración falsa: exactamente el error
  que esta puerta existe para impedir.
- `python -m rangyuu.walk` no se ejercitó: necesita `av`, un clip y el modelo ONNX, nada de eso se
  versiona. El cambio en ese archivo es un argumento de construcción, cubierto por prueba unitaria.

## 2026-09-16 — La interfaz habla el idioma de quien mira

**Qué se hizo**

Segundo lote del mismo PR, separado a propósito del de interfaz para que se revisen aparte.

- **Toda cadena visible salió del marcado y del JS a una sola tabla**, `web/i18n.js`. Sin
  dependencias, sin build, sin assets remotos: dos objetos y una función de búsqueda. `app.js` ya no
  escribe ni una cadena: o sale de `t()`, o viene del servidor y pasa por `s()`.
- **Dos orígenes de texto, dos tablas.** `UI` por clave; `SERVER` indexado por el valor que el
  núcleo manda ya resuelto —razones de `ui.py`, detalles de `CUIDADO`, etiquetas de fuente, razones
  de calibración, las cuatro esquinas—. **El servidor no se tocó**: las etiquetas de calibración
  siguen viajando en castellano en el cuerpo del POST y vuelven como claves de `per_point_cm`; solo
  se traducen al mostrarlas.
- **Inglés y castellano.** Por defecto el del navegador (`navigator.languages`), inglés de respaldo
  si ninguno coincide. Una clave que falte cae al inglés; un texto del servidor sin traducción se
  muestra **tal cual** antes que en blanco.
- **Anulación explícita en Sistema**, guardada en `localStorage`, con `try/catch` en cada lectura y
  cada escritura. Cambiar de idioma **vuelve a pintar lo que ya se tenía en memoria**, sin pedirle
  nada al sitio: probado que `state`, `authorizes` y `decision` no se mueven al cambiarlo.
- **El nombre en inglés del segundo destino es "On board", no "Walk".** B4 dice que el consumidor es
  cualquier vehículo autónomo o asistido; traducir *Caminata* literalmente estrecharía el producto a
  gente a pie en el idioma que leen los jurados. Hay una prueba que falla si *walk*, *pedestrian*,
  *step* u *on foot* reaparecen en la copia inglesa. **En castellano sigue siendo "Caminata".**
- **La voz también cambia de idioma** (`utterance.lang`), pero **el patrón de vibración y el tono
  no**: son la firma del estado y se aprenden de memoria.
- Verificado en navegador real en **los dos idiomas** a 390x844 y 1280x900: consola limpia en las
  cuatro combinaciones, sin scroll horizontal y sin etiquetas desbordando la navegación inferior
  —el caso que importa, porque el castellano es 20-30 % más largo—. Suite en **193 pruebas**.

**Qué NO se verificó, y por qué**

- Solo Chromium. Safari en iOS sigue sin probarse por falta de HTTPS o túnel. ⏳ pendiente, B12.
- **El ícono de la pestaña sigue siendo una persona caminando**, que en inglés contradice el nombre
  neutral. No se cambió porque en castellano la etiqueta sigue siendo *Caminata* y ahí el ícono es
  correcto; queda anotado en el PR como pendiente de decisión. ⏳ pendiente.
- Los nombres de zona (*entrada*, *pasillo*, *puerta*) **no se traducen a propósito**: son dato del
  sitio, no de la interfaz. Un sitio real nombra sus zonas como quiera.
- Nadie con lector de pantalla probó la app; lo que se comprobó es que el `<select>` tiene nombre
  accesible y que `aria-current="page"` sigue en la pestaña activa. ⏳ pendiente.

**Dónde quedan los pendientes:** B12, junto a iPhone real y sesión WHEP viva.
## 2026-09-16 — La pantalla deja de autorizar cuando se queda sin dato

**Qué se hizo**

Tercera pasada sobre la interfaz, sobre los tres destinos ya consolidados y el lenguaje visual ya
alineado con Ring. No se tocó el contrato de datos ni la derivación de los cuatro estados.

- **El hallazgo que importa: perder el enlace con el sitio no retiraba la autorización.** Con el
  proceso caído, `refresh()` solo cambiaba la razón en letra chica y dejaba el `AVANZA` verde en
  grande, con la hora congelada. La app autorizaba tránsito sobre evidencia que ya no tenía. Ahora
  cae a `SIN CERTEZA · sin enlace con el sitio` y el sello dice `sin enlace`. Esto **no asciende
  nada**: solo retira, que es lo que la caminata ya hacía en `paintWalk`.
- **Los cuatro estados se distinguen sin leer.** La tarjeta lleva riel lateral y halo del color del
  estado, y una ficha que dice **`autoriza el paso` / `no autoriza el paso`** tomada del campo
  `authorizes` del propio contrato, no deducida del color. El color del estado cambia **sin
  transición**: con el fundido de 0,25 s el riel seguía verde un cuarto de segundo después de que
  la palabra ya dijera `PARA`.
- **Contraste: todo el texto pequeño estaba por debajo de WCAG AA y ahora pasa.** `--ink-3` daba
  3,11:1 sobre blanco y 2,91:1 sobre el fondo; el cian de acción daba 2,73:1 como texto y 2,57:1 en
  la pestaña activa. Medido token por token contra el fondo real de su tarjeta: el peor caso quedó
  en **4,80:1**. Se separó el cian en dos densidades —`--blue` pinta, `--blue-ink` escribe— para no
  perder el color de Ring en los rellenos.
- **Ningún objetivo táctil baja de 44 px.** Antes: `Evidencia` 25 px, `Probar` 33 px, los `summary`
  36 px. Ahora la sonda no encuentra ninguno por debajo en ninguna pantalla ni viewport.
- **El mapa dejó de tapar a la decisión.** Medía 500 px contra 154 px del veredicto en un teléfono;
  ahora 388 contra 204, y ambos entran juntos. El relleno de la ruta pasó a translúcido porque
  **tapaba justo la celda ocupada que sostiene un `PARA`**, y el rosa de ocupado se oscureció.
- **Las zonas salieron del SVG.** Su texto se medía en unidades del viewBox, así que el mismo
  `font-size` salía enorme y desbordando la tarjeta en la rejilla de 4 celdas. Son fichas HTML.
- **Se fue el panel de depuración.** `RING_INFRASTRUCTURE` e `IPHONE_ONBOARD` aparecían crudos en
  Sistema; el detalle de celda mostraba `estado: free`. Se traducen en la capa de presentación, con
  el contrato intacto (`tests/test_webapp.py:56` sigue exigiendo las constantes en el JSON).
- **La consola quedó limpia.** `navigator.vibrate()` antes del primer gesto lo descarta el navegador
  y lo anota como **error**; el audio, como advertencia. Ahora ambos canales esperan al gesto que
  `unlock()` ya recibía, y la vibración pendiente se emite en cuanto llega.
- **El botón de parar cayó al pulgar.** Estaba clavado con un `sticky` que dejaba ~300 px de vacío
  entre él y la navegación.

**Qué NO se verificó, y por qué**

- Nada de esto se vio en un **iPhone real**: sigue faltando HTTPS o túnel, y Safari no da cámara en
  HTTP. Las medidas son de Chromium a 390x844 y 1280x900. ⏳ pendiente, dentro de B12.
- Las advertencias de `AudioContext` se eliminaron **no reproduciendo** antes del gesto; que el tono
  suene de verdad en Safari iOS no se comprobó, porque no hay dispositivo. ⏳ pendiente.
- El contraste se midió con la fórmula WCAG sobre los colores calculados, no con una herramienta
  externa; el script vive fuera del repo y las cifras están en [verificacion.md](verificacion.md).

**Dónde quedan los pendientes:** B12, en las dos filas de iPhone real y sesión WHEP viva.
## 2026-09-16 — Reconciliación de ramas y CI verde en main

**Qué se hizo**

- `main` avanzó por fast-forward a `a31ba64`, absorbiendo los tres commits de
  `codex/north-navigation-ci`: simplificación visual de la app, detector ONNX local y el prompt de
  arranque. La suite siguió en 163 pruebas.
- **Eso arregló CI.** `Rangyuu CI` y `build-scan` venían fallando en `main` (run `35125517257` y
  `35125517447`) y pasan en el tip nuevo (`35129388309` y `35129388771`). Era el pendiente de
  ejecución remota que B12 declaraba sin cerrar; ahora tiene número de run, no una afirmación.
- `agent-worker.yml` fallaba en cada disparo programado —cada 6 h— porque `RANGYUU_PROVIDER_URL`
  no está configurado. Ahora una corrida programada sin proveedor sale con aviso y código 0; un
  `workflow_dispatch` manual sigue fallando fuerte, porque ahí alguien pidió la llamada a propósito.
- `.claude/worktrees/` entró a `.gitignore`. Los agentes en paralelo escriben ahí y esa es
  exactamente la forma del accidente que metió un video privado al historial.
- `docs/setup-dev.md` decía que la suite termina en `43 passed`. El número real es `163`. Corregido.

**Reconciliación de ramas, concepto por concepto**

- `codex/ring-ui-less-is-more`, `codex/block-geometry-dlt` y `codex/north-navigation-ci` quedaron
  probadas como **contenidas por completo** en `main` (`git merge-base --is-ancestor`). No hay nada
  que rescatar en ellas.
- `codex/rangyuu-rebuild` (59 commits atrás) se auditó entera: **nada que portar**. Cada capacidad
  vive hoy en `main` con otro nombre —la rejilla en `spatial.py`, el pipeline repartido entre
  `runtime.py` y `api.py`— y en varios casos `main` es **más estricto**: su `observation_from_event`
  (`ring.py:12-18`) levanta excepción donde el viejo rellenaba con `"unknown"`/`0.0`. Portarlo habría
  sido una regresión. `path_cells()` y `load_events()` son lo único ausente, y no tienen llamador.

**Qué NO se verificó, y por qué**

- El carril de a bordo (`python -m rangyuu.walk`) no se ejercitó: necesita `av`, un clip y el modelo
  ONNX, y ninguno se versiona. ⏳ pendiente, sin relación con este lote.
- Nada de este lote tocó la red: sin token fresco no se ejercitó la API de Ring. ⏳ pendiente.

**Dónde quedan los pendientes:** el hueco de calibración detectado al auditar
`claude/stellar-project-setup-gd0ba3` viaja en su propio PR y **todavía no está en `main`**; ver
abajo, en la nota de PR #4.

## PR #4 — mergeado (`78da540`)

Auditando `claude/stellar-project-setup-gd0ba3` apareció un hueco real y vivo en `main`: `Site.now()`
autorizaba tránsito con `calibration=None`, y `_calibration()` derivaba `valid` del residuo del
propio ajuste —el número ~0 que no prueba nada (Lección 3)—. Además, recalibrar desde la interfaz
conservaba el error medido de la matriz **anterior**, regalándole a una homografía nueva una prueba
que no se ganó. B9 decía "una prueba por fila, ninguna autoriza": era cierto de la tabla de
decisión, pero **no de extremo a extremo en la fila de calibración**.

El arreglo vive en `salvage/stellar-degradation-gates` (`4f0f3be`) y está medido: **173 pruebas**
(163 + 10), y al invertir la puerta para que una calibración sin medir cuente como verificada
**fallan 5 de ellas**, entre ellas la que retira la medición al sitio que se envía. No hay regresión
en la app: `serve.py:41` sigue pasando los 0,9 cm reales, bajo el techo de 1,5 cm, así que sigue
autorizando; la puerta solo muerde cuando el número falta.

Mergeado el 2026-09-16 como `78da540`. `main` queda en **173 pruebas** y `serve.py:41` sigue pasando
los 0,9 cm reales, así que la app sigue autorizando: la puerta solo muerde cuando el número falta.

**Las "tres puertas" de `3101781`, una por una.** El mensaje de aquel commit prometía cerrar tres
puertas entre observar y autorizar. Contra `main` de hoy:

1. **Calibración** — estaba realmente abierta. Cerrada por `78da540`, pero **solo en el camino de
   `Site`**, que es el que sirven `serve` y `webapp`. El camino del webhook sigue sin la puerta.
2. **Vivacidad del feed** — ya estaba cerrada en `main`, y con mejor código que el de la rama:
   `runtime.py:93-94` (`feed_is_stale` → `"feed stale"`), medido bajo B10 al cortar la red. Nada que
   portar; resucitar la versión vieja habría sido una regresión.
3. **Sesión activa** — **sigue abierta**. La rama existe en `policy.py:20`, pero `spatial.py:67` fija
   `session_active=True` y por ese camino nada puede dispararla. La puerta está puesta y no tiene
   picaporte.

O sea: una cerrada hoy, una que ya lo estaba, una todavía abierta. Las dos que faltan quedan en
[verificacion.md](verificacion.md) como ⏳ pendiente, con el motivo: cerrarlas pide un error medido
**por dispositivo**, y B8 dice que para la cámara de Ring ese número no existe todavía.


## 2026-09-16 — Tres destinos y CI instalable

**Qué se hizo**

- La navegación quedó reducida a Ahora, Caminata y Sistema. El mapa, sus zonas, el detalle de celda
  y la evidencia viven juntos en Ahora; fuentes y calibración viven en Sistema.
- `pyproject.toml` declara únicamente el paquete Python `rangyuu`, evitando que Setuptools confunda
  `web/` y `fixtures/` con paquetes de primer nivel.
- `provider-pr.yml` instala el proyecto antes de ejecutar Pytest y usa permisos de solo lectura.
- La suite completa pasó en 163 pruebas, incluidas las pruebas ONNX que aparecieron durante la
  integración paralela. El wheel `rangyuu-0.1.0` se construyó correctamente en aislamiento.

**Qué NO se verificó, y por qué**

- Los workflows reparados todavía no corrieron en GitHub sobre esta rama; la verificación local
  reproduce la instalación y las pruebas, pero el estado remoto solo existe después del push.
- No se modificó ni se versionó la integración ONNX en curso; esos archivos pertenecen al trabajo
  paralelo y esta rama solo comprobó que sus pruebas conviven con el cambio.

**Dónde quedan los pendientes:** ejecución remota de CI y pruebas en iPhone dentro de B12.

## 2026-09-16 — La interfaz deja de parecer un panel técnico

**Qué se hizo**

- Se comparó la web con las referencias visuales de Ring suministradas y se corrigió la brecha
  principal: el color ya coincidía, pero la jerarquía seguía dando el mismo peso a título, dato,
  mapa, leyenda y navegación.
- `web/index.html` y `web/styles.css`: cada pantalla ahora tiene una sola lectura dominante, tarjetas
  blancas amplias sobre fondo frío, radios de 24 px, un único cian de acción, rótulos secundarios
  discretos y navegación inferior con iconos propios en SVG. No se añadieron dependencias ni assets
  remotos.
- La acción de evidencia pasó dentro del encabezado del mapa y la leyenda se redujo a cuatro claves
  cortas. Fuentes conserva todas las mediciones, pero las presenta como grupos secundarios.
- `web/app.js`: la pestaña activa expone `aria-current="page"`; el cambio no toca el contrato de
  datos ni deriva estados nuevos.
- Revisión en navegador real a 390x844 y 1024x900 sin errores ni advertencias de consola. La suite
  completa pasó: 151 pruebas.

**Qué NO se verificó, y por qué**

- No se probó la interfaz en Safari ni en un iPhone físico; el entorno disponible ejecutó Chromium.
- No se hizo una prueba de usabilidad con una persona caminando. La simplificación visual está
  verificada por inspección y regresión funcional, no por desempeño humano medido.

**Dónde quedan los pendientes:** las dos verificaciones siguen en B12 de [plan.md](plan.md).

## 2026-09-16 — Detector ONNX local: ve la moto que la heurística no veía

**Qué se hizo**

- `rangyuu/vision.py`: detección de objetos con **ONNX en local** —`onnxruntime 1.30`, SSD MobileNet
  v1 del ONNX Model Zoo—. Ningún frame sale de la máquina, igual que el resto del carril crítico.
- **Ve lo que la heurística no podía:** en t=49,5 s devuelve `moto 0.69` y `persona 0.94`; en t=20 s
  y t=40 s, nada. La diferencia con las texturas es que **nombra** el objeto en vez de adivinar por
  contraste.
- Coste medido: **24 ms por frame de media, 34 ms de máximo** sobre 585 frames a 464x832, en CPU.
  Entra en el presupuesto del lazo, que ya estaba en 8,16 ms.
- La regla es geométrica, no solo de clase: **obstáculo = objeto en el corredor y cerca**; el mismo
  objeto lejos es aviso. Sobre esta caminata **no frenó ni una vez**, porque nada llegó nunca cerca
  del corredor, y emitió 174 avisos, 20 de ellos dentro de los tramos marcados.
- El modelo **no se versiona**: son 29 MB y se configura con `RANGYUU_ONNX_MODEL`. Sin esa variable
  el sitio cae en la heurística de texturas **y lo declara** en Fuentes; nunca finge tener modelo.
  Las diez pruebas nuevas corren sin descargar nada, sustituyendo la sesión ONNX.
- Se arreglaron tres pruebas de navegador intermitentes: esperaban por reloj y ahora esperan por
  condición. Dos corridas seguidas en verde. Suite en 163 pruebas.

**Qué NO se verificó, y por qué**

- **La precisión contra la verdad de campo no mejoró de forma concluyente.** Medida contra las dos
  ventanas marcadas, los avisos aciertan entre el 13 % y el 20 % según cuánto se estreche el
  corredor. La razón es que el detector encuentra objetos **que sí están ahí** —sillas, autos
  estacionados, personas— pero que no obstruyen el paso, y con una sola cámara sin calibrar **no hay
  forma de decidir si algo obstruye**: falta distancia. Eso es B11, no más ajuste de umbrales.
- **Un clip con dos ventanas no valida un detector.** Sirvió para descartar la heurística; para
  aceptar esta hace falta más metraje etiquetado.
- El modelo no se probó en el teléfono ni con el carril alimentado en vivo.

**Dónde quedan los pendientes:** B11, B12 y B7 de [plan.md](plan.md).

## 2026-09-16 — La precisión del detector a bordo, medida: 22 %

**Qué se hizo**

- Se recibió la verdad de campo de la caminata: dos tramos con algo real en el camino —**49-50 s y
  55-56 s, una moto a lo lejos**—. Con eso se pudo medir lo que ayer quedó explícitamente sin medir.
- **El resultado es malo y queda escrito: 22 % de precisión.** De 180 lecturas de "obstáculo", 40
  caen en esos tramos y **140 son frenadas falsas** en 58 segundos. La cobertura de los tramos reales
  es del 67 %.
- Se probó un criterio alternativo —mancha localizada en vez de contraste global— y es **peor**:
  9-11 %. Las distribuciones se superponen casi por completo (0,174 en los tramos reales contra 0,136
  en el resto). Con este método, una moto lejana no es separable de la variación normal de la escena.
- **Consecuencia aplicada, no solo anotada:** el carril de a bordo deja de poder llevar la pantalla a
  `PARA` y ahora degrada a `CUIDADO`. Detener a una persona catorce veces por minuto sin razón es
  peor que no avisar. Sobre la misma caminata, la pantalla pasa de 180 `PARA` a ninguno y de 40
  cambios de estado a 25.
- Suite en 151 pruebas.

**Qué NO se verificó, y por qué**

- **Si un detector de objetos entrenado resuelve esto.** Es el camino obvio —una moto a 15 m es
  exactamente lo que un modelo detecta y una diferencia de texturas no—, pero no se probó ninguno.
  Queda como el siguiente bloque de B11.
- **La medición sale de un solo clip con dos tramos etiquetados.** Es suficiente para descartar el
  método actual, no para validar el que venga: ajustar umbrales contra dos ventanas es sobreajustar.

**Dónde quedan los pendientes:** B11 y B12 de [plan.md](plan.md).

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
