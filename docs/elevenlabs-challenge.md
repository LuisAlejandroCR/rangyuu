<!-- docs/elevenlabs-challenge.md: el plan de la entrada al Challenge 3 de ElevenLabs — dirección
     creativa del film, guion narrado en inglés, prompts listos para ejecutar y costo en créditos.
     Se distingue de docs/video.md, que decide *qué se cuenta* y fija la política del video:
     aquello es la política; esto es la producción —cómo se filma, qué se dice literalmente,
     cuánto cuesta y cuándo se envía—. -->

# Challenge 3 · Build with ElevenLabs MCP — plan de entrada

**Escrito el 2026-09-16. Dirección creativa reescrita el mismo día** alrededor de un brief de film
centrado en una persona, entregado por quien firma la submission y tratado como dirección canónica
(§3). **Lo que se reemplazó es la dirección creativa, no la investigación:** las tablas de créditos,
la estrategia de *un máster, dos cortes* y el análisis de cumplimiento siguen en pie.

Nada de este documento está ejecutado. **No se generó ni un segundo de audio, imagen o video, y no
se gastó ni un crédito.** Es un plan de producción; lo que aquí se llama "costo" es una estimación
citada, no una factura.

**Herramienta MCP disponible en esta sesión: ninguna.** Se revisó el inventario de conectores de la
sesión y solo hay tres (Claude Docs, visualize, scheduled-tasks). **No hay MCP de ElevenLabs
conectado**, así que nada de lo que sigue se probó contra la API real: los nombres de herramientas y
los costos salen de documentación pública, no de una llamada.

Este documento hereda, sin contradecirla, la decisión de [video.md](video.md): **ElevenLabs es
herramienta de narración y producción, nunca parte del runtime.** rangyuu tiene que funcionar con
ElevenLabs apagado, y funciona.

---

## 0. La regla que gobierna cada palabra de este documento

**rangyuu no frena hoy.** El destino del producto es tecnología pasiva que actúa sobre el vehículo
—el modelo es el freno de emergencia de un auto: la cámara ve el obstáculo y frena, no pregunta—, y
el núcleo ya está diseñado así: `policy.py:34` devuelve `HOLD` salvo que se cumpla *todo* (cobertura,
sesión, homografía válida, celda libre, sin `unknown`, sin `stale`, sin contradicción). La ausencia
de evidencia positiva es una negativa, no una duda.

Pero el carril a bordo acierta **13-20 %** cuando avisa, y la heurística de textura quedó medida en
**22 % con 140 frenadas falsas en 58 segundos**, razón por la cual se degradó a propósito de `PARA`
a `CUIDADO`. Lección 5, textual: **"frenar hay que ganárselo"**.

**Consecuencia para el guion:** el freno de emergencia se nombra como **principio y destino**, jamás
como capacidad actual. Ninguna línea de narración de este documento dice ni insinúa que rangyuu
detenga un vehículo hoy. Una afirmación sin evidencia repetible no entra —y menos que en ningún otro
lado entra en la copia de marketing, que es la que va a ver un desconocido.

La palanca que reemplaza al adjetivo es el **número medido**. Hay suficientes:

| Hecho | Número | Dónde vive |
|---|---|---|
| Homografía calibrada contra juntas fuera del ajuste | **0,9 cm de error sobre 61 cm (1,6 %)** | [plan.md](plan.md) B3, [memoria.md](memoria.md) 2026-09-15 |
| Presupuesto del lazo sobre 400 frames de sesión WHEP viva a 1280x720 | decodificación **7,48 ms** + inferencia **0,58 ms** + decisión **0,10 ms** = **8,16 ms/frame** | [architecture.md](architecture.md) §5 |
| Capacidad contra entrega de la cámara | **~122 fps** disponibles contra **29 fps** reales — factor 4 de margen | [architecture.md](architecture.md) §5 |
| WHEP sostenido fuera del navegador | sesión completa desde Python con `aiortc 1.15.0` | [memoria.md](memoria.md) 2026-09-15 |
| Lo que cruza el cable | `Observation(device_id, timestamp, kind, confidence, bbox)` — **cinco campos y una caja, ni un píxel** | [store-readiness.md](store-readiness.md) §1 |
| Inferencia de terceros | **cero**, probado envenenando `socket` | B10 |
| Precisión del carril a bordo | **22 %**, degradado de `PARA` a `CUIDADO` a propósito | [app.md](app.md) §2.2 |
| Suite | **198 passed, 1 skipped** (`python -m pytest -q`, verificado el 2026-09-16) | — |

---

## 1. La referencia de Vimeo — qué se pudo ver y qué no

El enlace entregado fue `https://vimeo.com/1195046947/a1ac9c274c`.

**No se vio el video.** La página de Vimeo respondió con una pantalla de verificación de seguridad
("Verify to continue"), que es un control anti-bot. **No se intentó resolverlo** y no se obtuvo ni un
frame, ni audio, ni transcripción.

**Lo único que sí se obtuvo**, por la API pública de oEmbed de Vimeo
(`https://vimeo.com/api/oembed.json?url=...`, consultada el 2026-09-16), son metadatos:

| Campo | Valor |
|---|---|
| Título | **Ato AI** |
| Descripción | **Launch 2026** |
| Duración | **159 s (2:39)** |
| Publicado | 2026-05-23 |
| Autor | Ato AI |

**Lo que de eso se puede inferir honestamente es el formato, y nada más:** una pieza de lanzamiento
de producto de ~2:39. Eso confirma el objetivo de duración —la pieza de rangyuu debe apuntar a
**2:30–2:45**, cómoda bajo el techo de tres minutos de [video.md](video.md)— y nada más.

⏳ **Pendiente:** ver la referencia. Requiere que alguien la abra en un navegador con sesión y
describa tono, ritmo de corte, si hay presentador en cámara y si la música lleva o no la pieza. Sin
eso, **las decisiones estéticas de este documento son propias, no derivadas de la referencia**, y
están tomadas para que se sostengan solas.

---

## 2. Precio — cuánto cuesta esta pieza en créditos

### 2.a Costos por unidad, publicados

Todos leídos el **2026-09-16**.

| Elemento | Costo en créditos | Precio API equivalente | Fuente |
|---|---|---|---|
| Text to Speech | **1 crédito por carácter** | $0,10 / 1K chars (v3, v2 Multilingual); $0,05 (Flash/Turbo, v3 Conversational) | [elevenlabs.io/pricing](https://elevenlabs.io/pricing), [elevenlabs.io/pricing/api](https://elevenlabs.io/pricing/api) |
| Eleven Music | **900 créditos por minuto** | $0,15 / min | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) |
| Sound Effects | **200 créditos por generación** | $0,12 / min | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) |
| Speech to Text (Scribe) | 330 créditos por minuto | $0,22 / hora | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) |
| Dubbing | 2.000–10.000 créditos por minuto según watermark y studio | $0,33–$2,20 / min | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) |
| **Generación de imagen** | ⏳ **pendiente** | ⏳ | no publicado |
| **Generación de video** | ⏳ **pendiente** | ⏳ | no publicado |
| **Lipsync** | ⏳ **pendiente** | ⏳ | no publicado |

**Por qué tres filas quedan en `⏳ pendiente` y no se rellenan.** La documentación oficial de
ElevenLabs para imagen y video dice explícitamente que *"el costo de generar depende del modelo que
estés usando y de los ajustes que hayas elegido"* y que el costo se muestra **antes de enviar la
generación**, sin publicar tabla alguna
([elevenlabs.io/docs/eleven-creative/playground/image-video](https://elevenlabs.io/docs/eleven-creative/playground/image-video),
consultada 2026-09-16). La página de precios de la API tampoco lista imagen ni video
([elevenlabs.io/pricing/api](https://elevenlabs.io/pricing/api), 2026-09-16). **Un precio inventado
es peor que un hueco admitido**, así que quedan como huecos.

**Referencia de tercero, marcada como tal.** Una guía no oficial
([elevenlabsmagazine.com](https://elevenlabsmagazine.com/elevenlabs-video-generation-guide-2026/),
publicada 2026-05-01, consultada 2026-09-16) da **Sora 2 Pro ≈ 12.000 créditos por generación** y
**Veo 3.1 ≈ 8.000**, con clips de **4, 8 o 12 s**, y admite que sus cifras de Kling y Wan son
estimadas. **No es fuente oficial**: se usa solo para dimensionar el peor caso, y la primera
generación real dentro del Playground reemplaza estos números con el costo que la propia interfaz
muestre antes de confirmar.

### 2.b Estimación para una pieza terminada de ~2:40

**Supuestos declarados:** 160 s de duración; narración en inglés a ~150 palabras por minuto ≈ **400
palabras ≈ 2.300 caracteres**; se presupuestan **retomas**, porque una sola pasada nunca queda.

**Variante completa** (con video generado):

| Elemento | Cálculo | Créditos |
|---|---|---|
| Narración TTS | 2.300 chars × 3 pasadas (2 borradores + máster) | ~7.000 |
| Música | 2,67 min × 900 × 2 tomas | ~4.800 |
| Efectos de sonido | 8 efectos × 2 tomas × 200 | ~3.200 |
| Video generado | ~48 s de pieza = 6 clips de 8 s × 2 tomas × 8.000 (Veo 3.1, cifra no oficial) | ~96.000 |
| Imágenes fijas | ~8 generaciones | ⏳ pendiente |
| Lipsync | no se usa (ver §3.h) | 0 |
| **Total** | | **~111.000 + imágenes ⏳** |

Rango honesto de esa cifra: **110.000–160.000 créditos**, según modelo de video y número de retomas.
Con Sora 2 Pro en lugar de Veo 3.1 el tramo de video sube de ~96.000 a ~144.000 y el total a ~160.000.
**Confianza: baja**, y toda la incertidumbre está en una sola fila —el video— cuyo precio no está
publicado.

**Variante mínima** (recomendada; sin video ni imagen generada, ver §4 y §6):

| Elemento | Cálculo | Créditos |
|---|---|---|
| Narración TTS | ~2.600 chars **con las audio tags incluidas** × 3 pasadas (2 borradores + máster) | ~7.800 |
| Música | 2,7 min × 900 × 2 tomas | ~4.900 |
| Efectos de sonido | 6 × 2 tomas × 200 | ~2.400 |
| Subtítulos con Scribe | 2,7 min × 330 | ~900 |
| **Total** | | **~16.000** |

**Confianza: alta.** Las cuatro filas usan costos oficiales publicados y la aritmética es trivial.

**Qué cambió respecto de la versión anterior de este documento, y por qué.** La estimación previa
daba ~8.000 créditos. Subió al doble por tres razones, todas consecuencia del brief de §3:

1. **Las audio tags se cobran como caracteres.** El guion son ~2.300 caracteres de habla, pero lo
   que se envía a la API son ~2.600 con las etiquetas inline. ⏳ **pendiente:** confirmar en la
   primera generación si ElevenLabs descuenta las etiquetas del conteo; este documento asume que
   **no** lo hace, que es el supuesto caro y por tanto el seguro.
2. **Tres pasadas de narración, no dos.** El brief pide un arco de interpretación que atraviesa la
   pieza entera —curiosidad, luego precisión, luego calma—; eso no sale a la primera y el guion se
   renderiza además **en cinco segmentos** (§3.c), lo que multiplica las retomas parciales.
3. **Un cue de música y un efecto más.** La estructura de §3.f tiene tres movimientos, no dos, y el
   sonido de §3.g suma un tono de sala de respaldo.

Lo que **no** subió: el metraje. Filmar con la cámara que ya existe cuesta cero créditos y es,
además, la opción que mejor cumple la regla del challenge (§5).

### 2.c Qué plan hace falta

| Plan | Precio | Créditos/mes | ¿Alcanza? |
|---|---|---|---|
| Free | $0 | 10.000 | **Ya no alcanza.** La variante mínima subió a ~16.000 créditos (§2.b) y se pasa por 6.000. Antes entraba con 2.000 de margen; con el guion del brief, no entra. |
| Starter | $6 | 30.000 | **El plan que hace falta.** Deja ~14.000 de margen: casi una pieza entera de repuesto. Es la recomendación. |
| Creator | $22 (1er mes 50 % off) | 121.000 | Innecesario para la variante mínima; justo al borde de la completa (~111.000). |
| Pro | $99 | 600.000 | Solo si se genera video, cosa que §3.h recomienda no hacer. |
| Scale | $299 | 1.800.000 | Innecesario para esto. |

Fuente de la tabla: [elevenlabs.io/pricing](https://elevenlabs.io/pricing), consultada 2026-09-16.

⏳ **Pendiente:** el saldo real de la cuenta de quien envía. Este documento no lo conoce. Antes de
empezar hay que mirarlo, porque decide cuál de las dos variantes es viable.

**El premio.** 1er lugar del Challenge 3 = **1.000.000 de créditos** (dato entregado con el encargo;
⏳ **no confirmado contra el portal**, ver §5). Para dimensionarlo: son ~62 piezas de la variante
mínima, o ~9 de la variante completa. Equivale a unos 20 meses de plan Creator.

---

## 3. El film — dirección creativa, guion y prompts

**La dirección creativa de este documento cambió por completo el 2026-09-16.** La versión anterior
era un video técnico con voz en off: milisegundos, homografía y captura de pantalla. Lo que la
sustituye es un **brief humano**, entregado por quien firma la submission y tratado aquí como
dirección canónica: *se cuenta la historia de una persona primero y la tecnología después.*

**Lo que NO cambió:** la investigación. Las tablas de créditos de §2, la estrategia de *un máster,
dos cortes* de §4.c, el análisis de cumplimiento de §5 y —sobre todo— **la regla de honestidad de
§0** siguen vigentes palabra por palabra. Esto reemplaza la dirección estética, no la evidencia.

### 3.a El brief, en once renglones

Es la referencia contra la que se juzga cada plano y cada línea. Si algo de lo que sigue lo
contradice, manda el brief.

1. **Personaje antes que producto.** Se abre sobre un detalle real y específico de la protagonista o
   el protagonista —algo que repara, cocina, colecciona o hace cada día—. El producto todavía no se
   explica. El narrador observa con afecto y humor seco.
2. **Lenguaje visual:** entorno real, luz natural de día, interiores cálidos y verosímiles, detalles
   táctiles, manos sobre objetos familiares, primeros planos de rituales pequeños, algún plano
   general del entorno. Cámara sobria: empujes lentos, handheld suave, encuadres fijos compuestos,
   travelling solo si algo lo motiva. Profundidad de campo selectiva. **Documental íntimo con
   precisión de pieza premium.** Se conservan las imperfecciones; se descartan las reacciones que se
   noten actuadas.
3. **El producto entra como respuesta natural** a algo ya establecido en la vida de la persona. Sin
   cambio de marcha hacia "modo comercial". La propuesta de valor, en lenguaje extremadamente
   simple. Nada de jerga que no venga pegada a algo que se vea.
4. **Demostración:** varias situaciones cortas de vida real, no una demo larga de funcionalidades.
   Cada latido: situación humana → el producto responde → reacción humana pequeña → siguiente
   situación. Interfaz mínima. **"No convertir la mitad del film en una grabación de pantalla."**
5. **Explicación técnica:** contrastar visualmente la simplicidad que vive la persona contra la
   complejidad que ocurre debajo, invisible. Ritmo algo más rápido, gráficos sobrios. Mensaje:
   *algo sofisticado está pasando debajo, y la persona nunca necesita pensar en ello.*
6. **Familia y vínculo:** abrir del individuo a quienes lo quieren. Conexión, tranquilidad, libertad,
   independencia, presencia — sin intrusión. **Dignidad, no dependencia. La persona nunca es
   indefensa y nunca pierde la agencia. La tecnología sostiene la independencia, no la reemplaza.**
7. **Montaje:** empezar lo bastante lento como para observar a la persona, y acelerar de a poco.
   Mezclar planos observacionales de 2–4 s, momentos conversados, interacciones con el producto,
   macros, planos de entorno y momentos de familia. Dejar respirar los latidos emocionales. **No
   cortar cada golpe con la música.** Usar el silencio y el tono de sala. Las transiciones salen de
   una acción, una mirada, un sonido o un significado — nunca de un efecto.
8. **Diseño de sonido:** tono de sala, tela, pasos, pequeños sonidos mecánicos, objetos manipulados,
   puertas, cocina, ambiente de calle, respiración, sonidos sutiles de dispositivo. Los sonidos del
   producto: suaves, reconocibles, elegantes — **nunca sci-fi agresivo**.
9. **Música:** contenida y curiosa al principio —piano mínimo, cuerdas sutiles, texturas orgánicas,
   electrónica sobria—, la calidez entra de a poco, el crecimiento es leve. **Nunca épica. Sin
   percusión de tráiler. Sin crescendo motivacional.**
10. **Acto final:** soltar las funcionalidades, volver del todo a la historia humana, dejar que la
    tecnología se retire. Cerrar sobre lo que el producto protege o habilita —tiempo, vínculo,
    independencia, confianza, familia, curiosidad, dignidad, libertad—. Una sola frase emocional
    corta. Después el nombre y el logo. **Sin lista de funcionalidades al cierre.**
11. **Principio rector:** quien mire debe terminar pensando *"me importa esta persona"*, luego
    *"entiendo por qué este producto debería existir"*, y recién después *"quiero saber más"*.

**Lo que se evita en toda la pieza:** anuncio de startup convencional, demo de software, comercial
futurista de IA, visuales de neón, imaginería genérica de IA, robots, hologramas, interpretaciones
exageradas, clichés de anuncio inspiracional.

### 3.b Tres tensiones reales entre el brief y este proyecto

El brief no se apoya limpiamente sobre el plan anterior. Hay tres choques genuinos. Se nombran y se
resuelven con una recomendación, no con un menú.

#### Tensión 1 — la estructura de demostración contra la regla de honestidad

**El choque.** El brief pide latidos de vida real donde *el producto responde* y *una persona
reacciona*: un momento de asistencia, un momento de independencia. **rangyuu no puede hacer eso
hoy.** rangyuu avisa; no actúa. El detector a bordo acierta **13-20 %** cuando avisa; cableado a una
frenada completa produjo **140 frenadas falsas en 58 segundos** (22 % de acierto) y por eso se
degradó a propósito de `PARA` a `CUIDADO`. Lección 5: **"frenar hay que ganárselo"**. Montar una
escena donde rangyuu asiste a alguien fabricaría una capacidad — exactamente lo que §0 prohíbe, y lo
que peor envejecería si un jurado probara el repositorio.

**Recomendación.** Se conserva **toda** la estructura humana del brief y se cambia una sola cosa: lo
que responde en el segundo acto **no es rangyuu actuando sobre el vehículo, es rangyuu contestando
en pantalla, filmado en vivo**. El latido del brief se instancia así:

| Brief | Instancia honesta en rangyuu |
|---|---|
| Situación humana | La esquina de la calle que no se ve. La caja que alguien dejó en el umbral. |
| El producto responde | La pantalla dice `AVANZA`, `PARA`, `SIN CERTEZA` — respuesta real del núcleo, capturada, no recreada. |
| Reacción humana pequeña | La persona levanta la vista, rodea la caja, sigue. **Decide ella.** |
| Momento de asistencia | **Sustituido por un momento de negativa:** se corta el cable y el sistema dice `HOLD`. Es el plano más fuerte que el proyecto tiene y es literalmente cierto. |
| Momento de independencia | **Se conserva intacto**, y es el que cierra: la persona sale, y nadie la vigila. |

**Y la película lo dice en voz alta.** El guion de §3.c incluye, a los `[2:12]`, la confesión: *no
frena todavía; lo intentamos; se detuvo 140 veces en 58 segundos sobre un piso vacío; le quitamos el
freno*. Eso no es un descargo legal al final en letra chica: **es el giro emocional del tercer
acto**, y funciona dramáticamente porque el brief pide dignidad. Un producto que admite lo que no
sabe hacer es coherente con un protagonista que conserva su agencia.

**Quién es el protagonista.** Una persona real y específica que se mueve con un vehículo de
movilidad motorizado, filmada en su casa y en su calle, con su consentimiento (§6). **Fecha de
decisión: día 3 de los 9** (2026-09-19). Si para entonces no hay persona disponible y consentida, el
plan B **no es recrearla con un actor**: el film pasa a tener como protagonista a quien construye —
misma estructura, mismo arco, misma frase final—, y la primera línea cambia de *"esto es [NOMBRE]"*
a *"esto se está construyendo para alguien"*. Recrear con actor un usuario de vehículo de movilidad
es precisamente la escena que el brief llama *"reacción actuada"* y que §0 llama *afirmación sin
evidencia*.

#### Tensión 2 — "que no sea una grabación de pantalla" contra la recomendación de cumplimiento

**El choque.** §5 recomienda **cero video generado** porque los modelos de imagen y video que
ElevenLabs expone son de terceros (Sora 2, Veo 3.1, FLUX, OmniHuman) y la regla del challenge dice
que no haya otro generador de IA en la cadena. La consecuencia de esa recomendación, en el plan
anterior, era que **todo** el metraje fuera captura de pantalla. El brief ahora exige cinematografía
de acción real, de una persona real, en una casa real.

**Esto no es un problema: es la mejor noticia del documento.** Filmar es *estrictamente más
cumplidor* que generar —una grabación con cámara no es un elemento generado bajo ninguna lectura de
la regla, ni la laxa ni la estricta— y además es gratis en créditos. Lo que cuesta es **tiempo**, y
quedan 9 días.

**Lo que es realista filmar en 9 días** —con un iPhone en 4K, luz natural, sin equipo, sin crew—:

| Día | Qué pasa |
|---|---|
| 1 (09/16) | Bloquear este documento. Pedir consentimiento (§6). Elegir el ritual de apertura: tiene que ser **real**, no inventado para la cámara. |
| 2 (09/17) | Recorrido de localización a la hora exacta del día en que se va a filmar. Lista de planos cerrada contra §3.e. |
| 3 (09/18) | **Fecha límite de casting** (Tensión 1). Rodaje bloque A: casa, rituales, manos, retratos de entorno. Medio día de luz. |
| 4 (09/19) | Rodaje bloque B: umbral, calle, esquina, la caja, el momento de familia. El resto de la luz. |
| 5 (09/20) | **Captura de pantalla**, que es un día aparte y no se mezcla con el rodaje: sesión WHEP viva, mapa llenándose, el corte de red y el `HOLD`, la pantalla de calibración. Grabación de tono de sala. |
| 6 (09/21) | Generación en ElevenLabs: cinco segmentos de narración, dos cues de música, seis efectos. |
| 7 (09/22) | Montaje. Primer corte completo. |
| 8 (09/23) | Mezcla, subtítulos con Scribe, corrección de color. |
| 9 (09/24) | Margen. **Enviar el 09/24, no el 09/25 a las 17:50.** |

**Cuánta captura de pantalla sobrevive sin violar el brief.** El brief prohíbe que la pantalla se
coma la mitad del film, no que aparezca. El reparto que cumple ambas cosas: **de 162 s, no más de
40 s de pantalla (25 %), y ningún tramo continuo de pantalla mayor a 8 s.** Toda pantalla aparece
**dentro del encuadre físico** siempre que se pueda —el teléfono en la mano, el monitor sobre la
mesa del taller, con la habitación alrededor y fuera de foco— y solo se va a pantalla completa en
**dos** momentos, ambos ganados: el `HOLD` al cortar el cable, y la cinta métrica sobre la baldosa.
Eso satisface la frase del brief: la gente interactuando con el producto, no interfaz flotando.

#### Tensión 3 — los números medidos contra "evitar la jerga"

**El choque.** El guion anterior era milisegundos y homografía. El brief quiere lenguaje simple
pegado a algo que se vea. Pero los números medidos **son la credibilidad del proyecto**: sin ellos
esto es otro anuncio de startup, que es justo lo que el brief prohíbe. No se descartan: se traducen.

**Los cuatro que sobreviven, y contra qué se muestra cada uno:**

| Número medido | Cómo suena en el film | Contra qué se ve |
|---|---|---|
| 0,9 cm de error sobre 61 cm | *"menos de un centímetro de error en dos pies de baldosa"* | **Una cinta métrica de verdad, en una mano, sobre una junta de baldosa.** El número más fácil de entender que tiene el repositorio. |
| ~122 fps de capacidad contra 29 fps reales | *"la cámara habla veintinueve veces por segundo; rangyuu puede contestar ciento veintidós"* | La imagen en vivo de la cámara y la respuesta apareciendo antes de que el plano cambie. Se dice "hablar" y "contestar" porque es una conversación, no un presupuesto de latencia. |
| `Observation` = 5 campos y una caja | *"cinco campos y una caja. Ni un píxel."* | El texto literal cruzando el cable, en una terminal, junto al video que **no** cruza. |
| 140 frenadas falsas en 58 s (22 %) | *"acertaba una de cada cinco — y frenó ciento cuarenta veces en cincuenta y ocho segundos, sobre un piso vacío"* | Nada. Cara de la persona y una pantalla quieta. Es el latido de honestidad y no necesita gráfico. |

**Los que se caen, y por qué.** La palabra *homografía*: es jerga y su consecuencia —la cinta y la
baldosa— ya está en pantalla. *WHEP*, *1280x720*, *400 frames*: nomenclatura de infraestructura,
invisible para quien mira. El desglose de 7,48 + 0,58 + 0,10 ms: tres números donde alcanza uno, y
el que alcanza es la comparación 29 contra 122. *"Envenenando el módulo `socket`"*: se convierte en
*"cortamos la red a propósito, para probar que no salía nada"*, que es lo mismo dicho en humano.
*1,6 %*: redundante con los 0,9 cm y menos visible.

**Una precisión que importa.** El film usa **22 % / una de cada cinco**, no el rango 13-20 % del
detector ONNX, porque el 22 % es el número atado al experimento que se cuenta —las 140 frenadas—.
Son dos mediciones distintas de dos implementaciones distintas ([app.md](app.md) §2.2,
[store-readiness.md](store-readiness.md) §2) y **no se promedian ni se mezclan**. El rango 13-20 %
sigue vivo en la documentación; simplemente no es el número de esta escena.

### 3.c Narration script — the master text for Text to Speech

**English on purpose**: it is what will be heard, and the hackathon and its judges are in English.
The bracketed timecodes are edit notes; the `[square-bracket]` words inside the prose are **Eleven
v3 audio tags** and are sent to the API as written. `[NAME]` and `[RITUAL]` are placeholders the
shoot fills in — ⏳ **pendiente**, they depend on who is filmed (§3.b, Tensión 1).

~2.300 characters of speech, ~2.600 with tags, ~2:42 at a documentary pace. **Every number in it is
a number this repository actually measured.**

> **[0:00]** `[curious]`
> This is [NAME].
> [NAME] believes nothing is really broken until you've opened it. `[laughs softly]` And
> technically… he's right. Most of the time.
>
> **[0:14]**
> Thursday mornings, the kitchen table stops being a table.
> Small screws. A lamp that's been dying since March. `[pause]` A coffee that goes cold, every
> single week, in exactly the same spot.
>
> **[0:32]**
> He knows this house by heart.
> `[pause]` The street outside, less so.
>
> **[0:40]**
> [NAME] moves on a machine with a joystick and a camera on the front. The camera sees what's in
> front of it. `[pause]` It does not see around the corner.
>
> **[0:54]**
> But the corner is already being watched.
> There's a camera above his door. One on the porch across the street. They've been looking at that
> sidewalk for years — and telling nobody anything useful.
>
> **[1:08]**
> rangyuu asks them.
> `[pause]` What comes back isn't video. It's a map of what's free.
>
> **[1:18]**
> Hallway. Free.
> Doorway — somebody's box, left where a box shouldn't be. Not free.
> `[pause]`
> And then the part nobody puts in a product film.
>
> **[1:32]**
> Cut the cable, and rangyuu doesn't guess. It says: hold.
> Not a warning. Not a question. A refusal.
> It holds unless everything holds. `[pause]` Absence of evidence is a no.
>
> **[1:48]** `[serious]`
> Underneath that one word there's a lot of arithmetic.
> The floor was measured with a tape — less than a centimetre of error across two feet of tile.
> The camera speaks twenty-nine times a second. rangyuu can answer a hundred and twenty-two.
> And what crosses the wire is five fields and a box. No pixels. We cut the network ourselves, on
> purpose, to prove nothing was leaving.
>
> **[2:06]**
> [NAME] never sees any of that. `[pause]` That's the whole point.
>
> **[2:12]**
> Here's what it doesn't do yet. It doesn't brake.
> That's where this is going — the way a car brakes for you, without asking.
> But we tried it early. Wired to a full stop, it was right about one time in five — and it stopped
> a hundred and forty times in fifty-eight seconds, on an empty floor.
> `[pause]` So we took the brake away from it.
> Braking has to be earned.
>
> **[2:32]** `[warmly]`
> His daughter still calls on Sundays.
> Not to check. `[pause]` She's never had to check.
>
> **[2:40]**
> Nobody should have to give up a street to keep a life.
> `[pause]`
> rangyuu.

**Nota de alcance, y es deliberada.** La línea de apertura del guion anterior decía *"A camera on a
wheelchair"* y estrechaba el producto a sillas de ruedas, contradiciendo la corrección ya hecha:
rangyuu sirve a **todo vehículo de movilidad** —rover, robot, scooter, silla motorizada— y
[plan.md](plan.md) B4 lo registra como **capa espacial reutilizable para dispositivos autónomos y
asistidos**. El guion nuevo resuelve la tensión entre eso y la especificidad que exige el brief
**sin nombrar la categoría**: `[0:40]` dice *"una máquina con un joystick y una cámara adelante"*,
que es verdad de la máquina concreta de una persona concreta y no es una etiqueta de producto. La
generalización no se hace en la narración —donde sonaría a folleto— sino **en la descripción del
post y en la página de la submission**, que es donde corresponde.

### 3.d Cómo se distila la dirección de voz — tags, elección de voz y notas de dirección

La dirección de interpretación entregada son doce párrafos. **No se pega antes del guion**: un
bloque de prosa como prompt de sistema produce una lectura promediada. Se reparte en tres cubetas, y
hay que ser explícito sobre cuál es cuál.

**Lo que sobrevive como ELECCIÓN DE VOZ** (se decide una vez, en la biblioteca, antes de generar):

| Del brief | Por qué es voz y no tag |
|---|---|
| Hombre, entre 35 y 45 años | Es timbre y edad. Ningún tag lo cambia. |
| Inglés americano neutro, natural | Propiedad de la voz. |
| Tono medio-bajo, timbre suave y tranquilizador | Propiedad de la voz. |
| Inteligente, carismático en voz baja, autoridad amable | Se elige; no se pide. |
| Documental premium, no locutor comercial | **La elección más importante de todo el documento.** Descartar cualquier voz etiquetada *narration/commercial/promo*. |

⏳ **Pendiente:** el `voice_id` concreto. Hay que escuchar candidatas con el párrafo `[2:12]` —el de
las 140 frenadas— como texto de prueba, porque es el que más fácil se arruina sonando a anuncio.

**Lo que sobrevive como AUDIO TAGS inline** (van en el texto, se cobran como caracteres, §2.b):

| Punto del guion | Tag | Qué pedazo de la dirección instancia |
|---|---|---|
| `[0:00]` | `[curious]` | *"empezar con curiosidad sutil"* |
| `[0:03]` | `[laughs softly]` | *"un dejo de humor seco y contenido"* — **no** `[laughs]`, que sale a carcajada |
| a lo largo | `[pause]` | *"micro-pausas deliberadas entre ideas"*, colocadas **solo** donde el sentido cambia |
| `[1:48]` | `[serious]` | *"más precisión y ritmo en lo técnico"* |
| `[2:32]` | `[warmly]` | *"desacelerar en lo emocional: familia, independencia, vínculo"* |

Son **cinco tags y siete pausas**, no veinte. El brief pide contención; una narración salpicada de
tags suena manipulada, que es el defecto exacto que el brief prohíbe.

⚠️ **Verdad incómoda sobre los tags:** Eleven v3 los interpreta, no los ejecuta. Un tag que la voz
elegida no entienda **se ignora o, peor, se lee en voz alta**. Por eso la primera generación de cada
segmento se escucha entera antes de gastar las otras dos pasadas. ⏳ **Pendiente:** confirmar el
comportamiento de cada uno de estos cinco tags con la voz elegida. Nada de esto se probó — **no hay
MCP de ElevenLabs conectado en la sesión que escribió este documento** (§0 y §5).

**Lo que NO se puede expresar y es NOTA DE DIRECCIÓN para quien opera** (ni voz ni tag: se consigue
segmentando, ajustando parámetros y editando):

1. **El arco de toda la pieza** —curiosidad → confianza creciente en lo técnico → calma final—. No
   existe un tag de "arco". Se consigue **renderizando en cinco segmentos** con ajustes distintos:
   S1 `[0:00–0:39]`, S2 `[0:40–1:17]`, S3 `[1:18–1:47]`, S4 `[1:48–2:11]`, S5 `[2:12–2:45]`. Subir
   *stability* en S1 y S5 (contención), bajarla un punto en S4 (precisión con algo más de energía).
   Una mala toma cuesta un segmento, no el guion.
2. **"Una leve sonrisa en la voz"**. No es un tag. Es una propiedad de la toma: se elige entre las
   tres pasadas, escuchando.
3. **"Nunca suene a locutor, presentador corporativo o tráiler"**. Es un criterio de **descarte**,
   no una instrucción. Se aplica al elegir voz y al elegir toma.
4. **"No vender. Contar, y dejar que el sentido aterrice"**. Se consigue **en el montaje**, no en la
   generación: dejando aire después de `[1:32]`, de `[2:12]` y de `[2:40]`. El brief ya lo dice —
   *no cortar cada golpe con la música*— y eso es una decisión de editor.
5. **La variación natural de ritmo**. Salió del guion, no de la interpretación: frases cortas,
   fragmentos sin verbo, y un párrafo largo —el técnico— que por contraste suena más rápido sin que
   nadie acelere.

### 3.e Beat sheet y lista de planos

162 s. Origen de cada plano marcado: **LA** = acción real filmada, **SC** = captura de pantalla,
**EL** = generado en ElevenLabs. **No hay una sola fila EL en la columna de imagen** — y ese es
justamente el argumento de cumplimiento de §5.

| # | t | Dur | Latido | Plano | Origen |
|---|---|---|---|---|---|
| 1 | 0:00 | 6 s | Personaje, antes que nada | Macro: manos y un destornillador pequeño sobre [RITUAL]. Fijo, poca profundidad de campo. | LA |
| 2 | 0:06 | 8 s | El chiste seco aterriza | Plano medio de [NAME] en su mesa. Ni mira a cámara. Luz de ventana. | LA |
| 3 | 0:14 | 10 s | El ritual | Tres planos de 3 s: tornillos, la lámpara, la taza en su marca de siempre. Corta por acción. | LA |
| 4 | 0:24 | 8 s | El entorno | Plano general del interior. Él pequeño en su casa. Handheld apenas. | LA |
| 5 | 0:32 | 8 s | Se nombra la calle | Umbral desde adentro: la puerta abierta, la calle fuera de foco. | LA |
| 6 | 0:40 | 14 s | Aparece la máquina, no la categoría | El joystick bajo su mano, en movimiento. La cámara del vehículo, macro. Luego él saliendo. **Nunca un plano que titule "silla de ruedas".** | LA |
| 7 | 0:54 | 14 s | La infraestructura que ya mira | Empuje lento hacia la cámara sobre la puerta. La del porche de enfrente. La acera que ambas ven. | LA |
| 8 | 1:08 | 10 s | **Entra el producto** | El teléfono en su mano, la habitación alrededor. El mapa se llena celda por celda. **Dentro del encuadre físico, no a pantalla completa.** | LA + SC |
| 9 | 1:18 | 14 s | Demostración, tres situaciones | (a) pasillo, `AVANZA`; (b) la caja en el umbral, `PARA`; (c) él **rodea la caja y sigue** — decide él. 2–4 s cada uno. | LA + SC |
| 10 | 1:32 | 16 s | **El clímax: la negativa** | Se tira del cable. Corte a **pantalla completa**: `HOLD`. Único tramo largo de SC de la pieza, y está ganado. Volver a su cara. | SC + LA |
| 11 | 1:48 | 18 s | Lo complejo, debajo | Ritmo más rápido. **Cinta métrica sobre la junta de baldosa** (LA, macro). La imagen viva contestando (SC, 4 s). La terminal con los cinco campos (SC, 4 s). Superposiciones gráficas mínimas o ninguna. | LA + SC |
| 12 | 2:06 | 6 s | *Él nunca ve nada de eso* | Vuelta a un plano quieto de él haciendo algo cotidiano. La tecnología se retira. | LA |
| 13 | 2:12 | 20 s | **El giro de honestidad** | Lo más contenido de la pieza. Un plano largo, casi sin cortar. Taller vacío, o su cara, o la máquina quieta. **Sin gráficos. Sin pantalla.** | LA |
| 14 | 2:32 | 8 s | Familia, sin intrusión | Una llamada de domingo. Ella ríe. **Él no está siendo comprobado.** Corto, de lejos, sin sentimentalismo. | LA |
| 15 | 2:40 | 6 s | Cierre | Él sale a la calle solo. La cámara se queda. Nombre y logo sobre negro. **Sin lista de funcionalidades.** | LA |

**Reparto final:** ~122 s de acción real, ~40 s de pantalla (25 %), 0 s generado. Ningún tramo
continuo de pantalla supera los 8 s salvo el `HOLD`, que es el punto del film.

### 3.f Música — prompts para Eleven Music

Tres movimientos, generados por separado. **Nunca épico**: sin percusión de tráiler, sin crescendo
motivacional. La música entra tarde y sale antes del final.

**Cue A — curiosidad, 0:00 a 1:17, objetivo 78 s, instrumental, sin voces:**

> A restrained, curious opening for an intimate documentary. Solo upright piano, played softly and
> a little sparsely, with the felt and the room audible. A single sustained cello note underneath,
> barely there. Occasional small organic texture — something wooden, something mechanical, like a
> clock in another room. Around 68 BPM, but loose, not locked to a grid. No drums at all. Warm and
> observant, slightly amused, never sentimental. Leave a wide midrange gap for a spoken voice. No
> vocals. No swells. No build.

**Cue B — la calidez entra, 1:18 a 2:11, objetivo 54 s, instrumental, sin voces:**

> A gentle continuation for a documentary scene that is becoming more confident. The same solo
> piano, now joined by a quiet string pad that fades in slowly over twenty seconds. A soft low
> pulse — a muted heartbeat, not a kick drum — enters at the halfway point and stays underneath. It
> grows warmer, never louder. Around 72 BPM. No percussion with attack, no cymbals, no risers, no
> cinematic climax. No vocals. Leave room for speech throughout.

**Cue C — se retira, 2:12 a 2:45, objetivo 34 s, instrumental, sin voces:**

> A quiet withdrawal at the end of an intimate film. Everything thins out: the pulse stops
> completely, the strings fade to a single sustained note, and the piano plays one small figure,
> twice, then stops. Almost silence for the last eight seconds. Honest and calm rather than
> uplifting or triumphant. Ends on an unresolved sustain that simply stops. No vocals, no build, no
> final chord.

**Notas de ejecución.** Generar cada cue dos veces y escoger; a 900 créditos por minuto, dos tomas
de los tres cues son ~4.900 créditos (§2.b). Atenuar 14–18 dB bajo la narración —más que el plan
anterior, porque el brief pide que se oiga el silencio—. **Y `[2:12]`, el latido de honestidad, va
sin música o casi:** que la música se retire justo ahí es la decisión de montaje que vale más que
cualquier prompt.

### 3.g Efectos de sonido — prompts para Sound Effects (200 créditos cada uno)

**El sonido del brief sale mayormente del rodaje, no de ElevenLabs.** Tono de sala, tela, pasos,
puerta, cocina, calle, respiración: eso se graba en la locación y es mejor que cualquier generación.
Hay que grabar **60 s de tono de sala limpio en cada espacio**, sin excepción; es el error que
siempre se paga en montaje.

Se generan **seis** efectos, que son los que la locación no puede dar:

1. **Confirmación de UI** — `A single short soft synthetic interface confirmation tone, warm and low, one note, clean digital decay under 400 milliseconds, no reverb tail.`
2. **Negativa de UI** — `A single short muted synthetic interface tone signalling refusal. Low, dry, slightly detuned downward, no harshness, no alarm quality, no science-fiction character, under 500 milliseconds.`
3. **Celda del mapa asentándose** — `A very short granular digital tick, like a single data cell locking into place on a grid. Dry, tiny, almost subliminal, under 150 milliseconds.`
4. **Corte de red** — `The sound of a live signal dropping out: a brief burst of digital noise collapsing into silence, with a faint low-frequency thump underneath. Under one second, no musical pitch.`
5. **Rodadura** — `Continuous close-mic recording of small rubber wheels rolling steadily over smooth indoor tile, quiet and even, no voices, no room echo, ten seconds, loopable.`
6. **Tono de sala de respaldo** — `Quiet interior room tone of a small domestic kitchen in the morning. Faint refrigerator hum, very distant traffic, no voices, no footsteps, no music, thirty seconds, seamless loop.`

**La regla que gobierna los seis:** *suaves, reconocibles, elegantes — nunca sci-fi agresivo*. Si una
generación suena a nave espacial, se descarta aunque haya costado 200 créditos. Y **no se clona el
chime real de Ring**, que es marca de un tercero.

### 3.h Imagen, video generado y lipsync — la recomendación es no usar ninguno

**Con el brief nuevo la recomendación se endurece, no se ablanda.**

- **Lipsync: no.** No hay presentador ni avatar, y no hace falta ninguno.
- **Video generado: no.** El brief pide una persona real en su casa real, con imperfecciones. Un clip
  generado de un pasillo imaginario es más caro, menos convincente, y **contradice el brief punto por
  punto** —*"conservar las imperfecciones"*, *"evitar imaginería genérica de IA"*—.
- **Imagen generada: no.** Las tarjetas de título del plan anterior sobraban ya entonces. Un tipo
  limpio sobre negro no necesita generarse, y el brief prohíbe explícitamente los visuales de neón y
  la estética futurista que esas tarjetas tenían.

Costo evitado: entre **96.000 y 144.000 créditos** (§2.b, variante completa), con la cifra de video
todavía ⏳ pendiente. **Las tres razones —brief, cumplimiento y precio— apuntan al mismo lado**, que
es la señal de que la decisión es correcta y no una racionalización.

---

## 4. Alineación y estrategia

### 4.a La pieza sirve a los dos objetivos, y no por casualidad

[video.md](video.md) ya fijó un guion de seis bloques para el video del hackathon, y B7 de
[plan.md](plan.md) exige *"Ring aparece funcionando en código y pantalla"*. El guion de §3.c **sigue
cumpliendo los dos contratos**, aunque el orden cambió al reordenarse alrededor de la persona:

| Bloque de video.md | Dónde cae en el guion de §3.c |
|---|---|
| 0:00–0:15 problema | `[0:40]` — la cámara a bordo no ve la esquina. Llega más tarde **a propósito**: el brief pone al personaje antes que al problema. |
| 0:15–0:35 idea | `[0:54]`–`[1:08]` — la infraestructura ya mira; rangyuu la convierte en mapa |
| 0:35–1:20 flujo | `[1:18]` — las tres situaciones, con el mapa contestando en pantalla |
| 1:20–2:15 estados | `[1:32]` — el corte de red y el `HOLD`, que es el clímax |
| 2:15–2:45 privacidad | `[1:48]` — cinco campos, sin píxeles, la red cortada a propósito |
| 2:45–3:00 cierre | `[2:12]`–`[2:40]` — el freno como destino, el 22 % como presente, y la salida a la calle |

**El bloque humano de apertura, `[0:00]`–`[0:32]`, no existía en video.md.** No la contradice:
video.md fija *qué se cuenta* y no prohíbe llegar al problema por una persona. Es el cambio que trae
el brief, y es el que hace que el resto se escuche.

Y cumple el criterio de B7 sin trucos: **los planos 8, 9, 10 y 11 de §3.e son captura de Ring
funcionando**, no narración sobre Ring.

### 4.b El calendario manda

- **Challenge 3 cierra el 2026-09-25 a las 18:00 UTC.** Son **9 días** desde hoy.
- **El hackathon cierra el 2026-10-23.** Son **37 días**, y B7 ya pide enviar con margen, no el 23 a
  las 11:50.
- En medio queda **B11**, abierto: falta grabar el clip y medir con cinta. Si B11 cierra entre las dos
  fechas, el video del hackathon puede mostrar algo que el del Challenge 3 no tenía.

### 4.c Recomendación: **una pieza, dos cortes**

**No dos producciones. Tampoco un único archivo congelado.**

1. **Un solo máster** de ~2:42 en inglés, producido para el 2026-09-24, con todo el audio generado en
   ElevenLabs sobre **metraje filmado y capturado, nada generado**. Ese archivo se envía al
   Challenge 3.
2. **Los stems se guardan sin mezclar** —los cinco segmentos de narración, los cues A, B y C, los
   seis efectos— en la carpeta de artefactos que ya pide video.md, y **fuera del repositorio** (§6).
3. **Para el 2026-10-23 se re-corta**, no se re-produce: si B11 cerró, entra el plano de la
   calibración a bordo medida y se regeneran **solo** los segmentos de narración afectados. Costo
   marginal: unos cientos de créditos, no una pieza entera.

**Y el rodaje no se repite.** Filmar a una persona en su casa es lo caro de esta pieza y solo se
hace una vez: el corte de octubre usa el mismo metraje. Por eso conviene rodar **más de lo que el
guion pide** —planos de entorno, manos, rituales— mientras la cámara ya está puesta.

**Por qué esto y no dos piezas:** con 9 días, producir dos guiones distintos significa dos guiones
mediocres. Y el argumento de rangyuu no cambia entre jurados —los números medidos son los mismos, la
honestidad sobre el 22 % es la misma, y el `HOLD` al cortar la red es el mejor plano que el proyecto
tiene para cualquier audiencia—.

**Por qué tampoco un archivo único congelado:** el video del hackathon se juzga contra el estado del
proyecto el 2026-10-23, y entre las dos fechas el estado puede mejorar. Congelar la pieza el 25 de
septiembre obligaría a enviar en octubre un video que ya quedó corto.

---

## 5. Reglas del challenge y lo que hay que verificar antes de enviar

**La regla dura: todo elemento generado debe salir de ElevenLabs**, sin otra herramienta de IA
generativa en ninguna parte de la cadena.

**Este plan la cumple**, y conviene ser explícito sobre por qué:

- Narración, música y efectos: **generados en ElevenLabs**. ✅
- Metraje: **acción real filmada con cámara (~75 %) y captura de pantalla (~25 %)**, cero generación.
  Ni una grabación de pantalla ni un plano filmado son "elementos generados": son capturas, igual que
  una foto. ✅ **El brief de §3 refuerza esto**: al pedir una persona real en un entorno real,
  elimina la única parte de la pieza que hubiera podido tentar a generar imagen.
- Edición: corte y mezcla en un editor no generativo (DaVinci, Premiere, ffmpeg). Ningún efecto de
  IA generativa del editor —nada de relleno generativo, nada de "AI upscale", nada de subtítulos
  generados por otro modelo—. ✅
- Subtítulos: si se quieren, se transcriben con **Scribe dentro de ElevenLabs** (330 créditos/min,
  ~900 créditos para la pieza), no con la función de subtítulos automáticos del editor. ✅

**Lo que hay que preguntar antes, y es una bandera real.** Los modelos de imagen y video que
ElevenLabs expone no son propios: son **Sora 2, Veo 3.1, Kling, FLUX, Nano Banana, Runway** y otros,
servidos a través de la plataforma
([elevenlabs.io/docs/eleven-creative/playground/image-video](https://elevenlabs.io/docs/eleven-creative/playground/image-video),
consultada 2026-09-16). Lo mismo con el lipsync: **OmniHuman 1.5, Veed, HeyGen, Sync**. La lectura
razonable es que generar *a través de ElevenLabs* cumple la regla —es la plataforma la que lo
ofrece—, pero **"ningún otro generador de IA en la cadena" admite una lectura más estricta**, y en
esa lectura un clip de Sora 2 hecho desde el Playground sería discutible.

**Cómo se desarma el riesgo sin consultar a nadie:** la recomendación de §3.h —cero video generado,
cero imagen generada, cero lipsync— deja la cadena compuesta **solo por modelos propios de
ElevenLabs** (TTS, Eleven Music, Sound Effects, Scribe). Bajo cualquier lectura de la regla, eso
cumple. Es además la variante barata y la más convincente. **Las tres razones apuntan al mismo lado.**

⏳ **Pendientes antes de enviar:**

| Pendiente | Por qué está abierto |
|---|---|
| Texto literal de las reglas, tiers de premio y canal de publicación | `hacks.elevenlabs.io` devolvió **HTTP 403** a la consulta pública el 2026-09-16: el portal exige sesión. La fecha (2026-09-25 18:00 UTC) y el premio (1.000.000 de créditos, 1er lugar) vienen del encargo, **no confirmados contra el portal**. |
| Costo real de imagen, video y lipsync | No publicado; solo visible en el Playground antes de confirmar cada generación. |
| Saldo y plan actual de la cuenta | Este documento no lo conoce; decide qué variante es viable. |
| Ver la referencia de Vimeo | Bloqueada por verificación anti-bot; solo se obtuvieron metadatos. |
| Confirmar que el MCP oficial expone TTS, música y efectos con los nombres esperados | **No hay MCP de ElevenLabs conectado en la sesión que escribió esto.** Nada se probó contra la API. |
| B11 — el clip grabado y medido con cinta | Sigue abierto; decide si el corte de octubre supera al de septiembre. |
| **Quién es el protagonista** — la persona real que se filma | Fecha límite: **día 3, 2026-09-18** (§3.b, Tensión 1). Sin ella el film cambia de protagonista, no de estructura. |
| **Consentimiento escrito** de quien se filma y de quien se oye | Es de quien filma; este documento no puede darlo ni presumirlo (§6). |
| **`voice_id` concreto** para la narración | No se eligió. Hay que escuchar candidatas contra el párrafo `[2:12]`, que es el que peor tolera una voz de locutor (§3.d). |
| **Comportamiento real de los cinco audio tags** con esa voz | Eleven v3 los interpreta, no los ejecuta: un tag no entendido se ignora o se lee en voz alta. Nada se probó — **sin MCP conectado** (§3.d). |
| **Si ElevenLabs cobra las audio tags como caracteres** | §2.b asume que **sí**, que es el supuesto caro. Se confirma en la primera generación. |
| El nombre real en la narración, o un sustituto | Decisión de la persona filmada, no del documento (§6). |
| Los `[RITUAL]` del plano 1 y el momento de familia del plano 14 | Dependen de la vida real de quien se filme; el brief exige que sean **reales**, no inventados para la cámara. |

**Feedback de herramienta.** [video.md](video.md) ya obliga a consignar en la submission qué
funcionó, qué limitó y si se volvería a usar ElevenLabs. Ese registro se lleva **durante** la
producción, no se reconstruye después: cada generación anota modelo, prompt, créditos que la
interfaz mostró y si la toma sirvió. Es el mismo estándar que el resto del repositorio —evidencia
mientras se produce, no memoria a posteriori—.

---

## 6. Privacidad del rodaje — filmar a una persona crea dato personal

**Esto es nuevo y es consecuencia directa del brief.** Hasta ahora la pieza no tenía metraje de
nadie. Ahora tiene una persona identificable, su casa, su calle y la voz de un familiar. Eso es
**dato personal**, y este repositorio ya tiene un antecedente: **un video privado entró al historial
de `main` por un `git add -A`** ([memoria.md](memoria.md), 2026-09-16). No puede volver a pasar.

**Cómo se maneja el metraje:**

1. **Nada de video, foto ni audio de la persona se versiona en este repositorio.** Ni en `fixtures/`,
   ni en una carpeta de artefactos dentro del árbol, ni "temporalmente".
2. El material vive **fuera del repositorio**, en almacenamiento local o privado de quien filma, y el
   proyecto de edición también.
3. **`git add -A` no se usa.** Rutas explícitas, siempre. `.claude/worktrees/` ya está en
   `.gitignore` por el mismo accidente; conviene añadir las extensiones de medios antes de empezar a
   rodar, no después.
4. Lo único que llega al repositorio es **texto**: este documento, los prompts, y el registro de
   generaciones de §5.
5. **Los stems de audio generados en ElevenLabs** (narración, cues, efectos) no contienen dato
   personal y pueden guardarse en la carpeta de artefactos que pide [video.md](video.md) — pero
   **fuera del repositorio igualmente**, por la regla de no versionar medios.
6. **La cara y el nombre de terceros** que aparezcan de fondo en la calle: encuadrar para evitarlos.
   Es más barato que resolverlo en montaje.

**El consentimiento es de quien filma, no de este documento.** Antes de rodar hace falta permiso
explícito, informado y por escrito de la persona filmada y de cualquiera que aparezca o se oiga,
cubriendo específicamente que la pieza se **publica en un canal público** con el tag del challenge y
queda ahí. Este documento no puede darlo ni presumirlo.

⏳ **Pendiente:** el consentimiento firmado, y la decisión de si el nombre real de la persona aparece
en la narración o se sustituye. **Las dos cosas antes del día 3** (2026-09-18), que es la fecha
límite de casting de §3.b.
