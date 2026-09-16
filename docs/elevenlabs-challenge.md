<!-- docs/elevenlabs-challenge.md: el plan de la entrada al Challenge 3 de ElevenLabs — dirección
     creativa del film, guion narrado en inglés, prompts listos para ejecutar y costo en créditos.
     Se distingue de docs/video.md, que decide *qué se cuenta* y fija la política del video:
     aquello es la política; esto es la producción —cómo se filma, qué se dice literalmente,
     cuánto cuesta y cuándo se envía—. -->

# Challenge 3 · Build with ElevenLabs MCP — plan de entrada

**Escrito el 2026-09-16. Dirección creativa reescrita dos veces el mismo día.** La segunda reescritura
reemplaza casi por completo el guion y la lista de planos de la primera, alrededor de un segundo brief
—más detallado, arquitectónico y explícito sobre el motivo `HOLD`— entregado por quien firma la
submission y tratado aquí como dirección canónica (§3). **Lo que sigue sin tocarse es la
investigación:** las tablas de créditos (§2), la estrategia de *un máster, dos cortes* (§4.c), el
análisis de cumplimiento (§5) y la nota de privacidad (§6) siguen en pie, con ajustes menores donde el
nuevo guion cambia el reparto de plano o el conteo de caracteres.

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
| Narración TTS | ~2.550 chars **con las audio tags incluidas** × 3 pasadas (2 borradores + máster) | ~7.650 |
| Música | ~1,8 min efectivos de cue (63 s + 11 s + 33 s) × 900 × 2 tomas | ~3.200 |
| Efectos de sonido | 5 × 2 tomas × 200 | ~2.000 |
| Subtítulos con Scribe | ~2,7 min × 330 | ~900 |
| **Total** | | **~13.800** |

**Confianza: alta.** Las cuatro filas usan costos oficiales publicados y la aritmética es trivial.

**Qué cambió respecto de la versión anterior de este documento, y por qué.** La estimación anterior
—ya con el primer brief humano— daba ~16.000 créditos. Bajó a ~13.800 con el segundo brief, por dos
razones puntuales, no por una relajación general:

1. **El guion es más corto y tiene más silencio, no menos.** El nuevo guion mide ~2.550 caracteres
   contra ~2.600 antes, y **el cambio real está en la música**: el brief pide silencio explícito antes
   de `HOLD` y antes de "rangyuu does not brake today" (§3.f), así que los tres cues de música ocupan
   ~1,8 minutos de audio en total en vez de los ~2,7 minutos que cubría la música anterior de punta a
   punta. Menos minutos de Eleven Music generados es menos créditos, no una toma menos.
2. **Cinco efectos de sonido, no seis.** "Confirmación de UI" y "celda asentándose" se fusionan en un
   solo prompt (§3.g), porque en este guion ambos sonidos ocurren en el mismo plano (la revelación del
   producto).

Lo que **no** cambió: sigue habiendo **tres** pasadas de narración (el arco documental-preciso →
temor contenido → resolución sigue exigiendo tomas distintas por segmento, §3.d) y las audio tags
siguen contándose como caracteres bajo el mismo supuesto caro-y-seguro de antes. ⏳ **pendiente:**
confirmar en la primera generación si ElevenLabs descuenta las etiquetas del conteo.

Lo que **no** subió ni bajó: el metraje. Filmar con la cámara que ya existe cuesta cero créditos y es,
además, la opción que mejor cumple la regla del challenge (§5).

### 2.c Qué plan hace falta

| Plan | Precio | Créditos/mes | ¿Alcanza? |
|---|---|---|---|
| Free | $0 | 10.000 | **No alcanza.** La variante mínima es ~13.800 créditos (§2.b); se pasa por ~3.800. |
| Starter | $6 | 30.000 | **El plan que hace falta.** Deja ~16.200 de margen: casi una pieza entera de repuesto. Es la recomendación. |
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

**La dirección creativa cambió por segunda vez el 2026-09-16, en el mismo día.** La primera reescritura
había puesto a la persona antes que al producto pero seguía organizada alrededor de un ritual doméstico
genérico. El segundo brief —el que gobierna esta versión— es más estricto y más arquitectónico:
*"el video debería sentirse menos como 'AI product launch' y más como una historia humana sostenida
por una arquitectura extremadamente rigurosa por debajo. El protagonista es la persona; rangyuu es la
capa invisible que se niega a fingir certeza."* Esa frase, citada tal cual la entregó quien firma la
submission, es la vara contra la que se mide cada plano de este documento.

**La idea central, en una frase.** Un vehículo de movilidad ve lo que tiene directamente enfrente; no
puede ver alrededor de una esquina; el edificio ya puede. rangyuu convierte las observaciones de Ring en
un mapa espacial al que el vehículo le hace **una sola pregunta**: *¿esta trayectoria es transitable?*
Y cada respuesta incierta se convierte en **HOLD**. La tesis del film: **rangyuu es confiable no porque
prediga todo, sino porque se niega a fingir que sabe cuando no sabe.**

**Lo que NO cambió respecto de la versión anterior:** la investigación de §2 (créditos), §4.c (un
máster, dos cortes), §5 (cumplimiento) y §6 (privacidad) sigue vigente palabra por palabra, salvo el
ajuste de conteo de caracteres y de reparto de plano que trae este guion (§3.c, §3.e). **Y sobre todo,
la regla de honestidad de §0 no se negoció ni una línea:** ninguna frase de este guion dice que rangyuu
frena hoy.

### 3.a El brief, en sus propios términos

Estructura obligatoria, tomada literalmente del brief entregado y usada como el orden del guion de
§3.c: **Apertura → revelación del producto → la pregunta → el principio (regla HOLD) → prueba, no
afirmaciones → el fallo → por qué no frena → retorno humano → posicionamiento de ElevenLabs → acto
final.**

1. **Apertura.** La persona antes que el producto. Un plano sostenido sobre una esquina ocluida.
   Narración: *"a camera on a mobility vehicle can see what's ahead — it can't see around the corner —
   but the building already can."*
2. **Revelación del producto.** Infraestructura, no app. Visualización física restringida: piso,
   celdas, confianza, ocupación, vencimiento. **Sin hologramas, sin IA brillante flotando.**
3. **La pregunta.** Se muestra la trayectoria y el razonamiento en pantalla: cobertura, sesión, piso
   verificado, celdas libres, frescura, contradicciones.
4. **El principio.** Analogía del freno de emergencia, y luego la regla *HOLD-salvo-que-todo-sostenga*
   mostrada condición por condición, colapsando a un solo estado.
5. **Prueba, no afirmaciones.** Solo metraje real: cinta métrica sobre las juntas de la baldosa, 0,9 cm
   de error sobre 61 cm, 8,16 ms/frame, cinco campos y una caja sin píxeles, corte de red que prueba
   inferencia local, API/WHEP real de Ring.
6. **El fallo.** 140 frenadas falsas en 58 segundos — **la mejor escena del film, no un descargo**:
   *"we took the brake away, and left it a warning"*, dicho como decisión de ingeniería, no como
   disculpa.
7. **Por qué no frena.** Distancia → obstrucción → autoridad, y la calibración que falta.
8. **Retorno humano.** Las interfaces desaparecen; la persona sigue por el espacio.
9. **Posicionamiento de ElevenLabs.** Solo producción, nunca el runtime: *"ElevenLabs tells the story.
   It never makes the decision."*
10. **Acto final.** *"The app is the showcase. The product is the refusal underneath it."* /
    *"When the evidence is there, move. When it isn't — HOLD."*

**Lo que el brief prohíbe explícitamente**, y que este guion no contiene en ninguna toma: demo de
startup, montaje de hackathon, comercial de autos autónomos, film futurista de IA, hologramas, redes
neuronales brillantes, partículas de IA flotando, beeps de ciencia ficción, retratar a la persona como
indefensa, retratar la tecnología como heroica, lenguaje *"AI-powered" / "revolutionary" / "smart
mobility"*, música épica, percusión de tráiler, crescendo motivacional, montaje frenético, transiciones
con glitch, cortar cada golpe a la música.

### 3.b `HOLD` como motivo estructural — tres apariciones, tres tratamientos distintos

**Nota del usuario, ejecutada aquí, no solo reconocida:** *"140 false stops in 58 seconds" no es un
descargo — es la mejor escena del film, la prueba del carácter del producto.* Y **`HOLD` es el motivo
recurrente del film** — visual, verbal y sonoro —, leído primero como una respuesta de sistema y
entendido al final como la filosofía entera del producto. Se especifican **cuatro** apariciones (el
brief pedía al menos tres) para que el arco sea inequívoco en el montaje.

| # | Momento del guion | Qué dispara `HOLD` | Tratamiento visual | Tratamiento de narración | Tratamiento de sonido | Cómo difiere de la anterior |
|---|---|---|---|---|---|---|
| 1 | `[0:22]` — apertura, sobre la esquina ocluida | Nadie corta nada todavía; es la condición por defecto del sistema, mostrada antes de explicarla | Un HUD mínimo en la esquina del encuadre físico (dentro de la pantalla del teléfono, no a pantalla completa) muestra `HOLD` en gris, sin urgencia | El narrador **no dice la palabra todavía** — la cámara la deja leerse sola, sin comentario | Silencio casi total; un solo tick de UI apenas audible | **Primera lectura: clínica y silenciosa.** Es un estado del sistema, no un evento dramático. |
| 2 | `[1:04]` — el principio, la regla mostrada condición por condición | Se listan en pantalla, una por una, cobertura / sesión / piso verificado / celdas libres / frescura / sin contradicción, y colapsan a un único estado cuando cualquiera falla | Cada condición aparece y se apaga como un interruptor; la última que se apaga deja `HOLD` solo, en el centro, más grande | El narrador dice la regla completa: *"it holds unless everything holds. Absence of evidence is a no."* | Un tono de UI seco y sin reverberación marca cada condición que se apaga; silencio total antes de la palabra `HOLD` | **Segunda lectura: mecánica y explicada.** Deja de ser un misterio visual y se vuelve una regla que se entiende. |
| 3 | `[1:34]` — se corta el cable de red en vivo | Pérdida de señal real, filmada, no recreada en post | Pantalla completa por primera y única vez en el film; caída de señal real, luego `HOLD` sostenido varios segundos sin cortar | Silencio de narración total durante el corte; el narrador vuelve recién después: *"It says: hold. Not a warning. Not a question. A refusal."* | El sonido de corte de red real (o el generado en §3.g si el corte de cable no suena) y después silencio de sala, sin música | **Tercera lectura: el clímax dramático.** Es la prueba física de que la negativa es real, no una animación. |
| 4 | `[2:38]` — última línea del guion, acto final | Ninguna condición nueva: es la síntesis de las tres anteriores | Plano quieto, sin gráficos, sin pantalla; corte a negro con el nombre | El narrador cierra con la línea del brief casi textual: *"When the evidence is there, move. When it isn't — hold."* | Música casi apagada (Cue C, §3.f), sin percusión, terminando en un sostenido que se corta | **Cuarta lectura: la respuesta se convierte en filosofía.** La misma palabra que abrió como estado de sistema cierra como principio de producto. |

**Por qué cuatro y no una.** Repetir `HOLD` sin variar el tratamiento sería el "cortar cada golpe a la
música" que el brief prohíbe en otro plano: aquí el riesgo es prohibir la repetición monótona de una
palabra. Cada aparición cambia al menos dos de tres ejes —visual, verbal, sonoro— respecto de la
anterior, y la cuarta no introduce evidencia nueva a propósito: es pura síntesis.

### 3.c Narration script — the master text for Text to Speech

**English on purpose**: it is what will be heard, and the hackathon and its judges are in English.
Bracketed timecodes are edit notes; `[square-bracket]` words inside the prose are **Eleven v3 audio
tags**, sent to the API as written. `[NAME]` is a placeholder the shoot fills in — ⏳ **pendiente**,
depends on who is filmed (§3.d, casting note carried over unchanged from the prior draft).

Target: **~2:35**, comfortably inside 2:30–2:45 and under video.md's three-minute ceiling.
~2.250 characters of speech, ~2.550 with tags — slightly **shorter** than the previous draft (~2.300 /
~2.600), because this brief's beats are tighter and the technical block compresses to one paragraph
instead of two. **Every number in it is a number this repository actually measured** — see the table
in §0.

> **[0:00]** `[curious]`
> A camera on a mobility vehicle can see what's ahead.
> `[pause]` It can't see around the corner.
>
> **[0:10]**
> [NAME] knows that corner by heart. The vehicle doesn't — not yet.
>
> **[0:16]**
> But the building already can. A camera above the door. One on the porch across the street. They've
> watched that sidewalk for years, and told nobody anything useful. `[pause]` Until now.
>
> **[0:30]** `[serious]`
> This isn't an app. It's a floor.
> A grid of cells — free, occupied, uncertain — each one timestamped, each one expiring. No pixels
> leave this room. Five fields and a box. `[pause]` That's the whole shape of what crosses the wire.
>
> **[0:46]**
> rangyuu asks it one question: is this trajectory traversable?
> `[pause]` And it shows its work. Coverage. Session. A floor that was actually measured. Free cells.
> How fresh the evidence is. Whether anything contradicts anything else.
>
> **[1:04]** `[serious]`
> Here's the rule, and it doesn't bend: it holds unless everything holds.
> `[pause]` Coverage — session — a verified floor — free cells — fresh evidence — no contradiction.
> Any one goes dark, and the answer collapses to the same word.
> `[pause]` Hold. Absence of evidence is a no.
>
> **[1:22]**
> Think of the emergency brake in a car. It doesn't ask permission. `[pause]` This is that instinct,
> built for a building instead of a bumper.
>
> **[1:30]**
> We don't ask you to believe it. We measured it.
> A tape, on a tile joint — less than a centimetre of error across two feet.
> Eight milliseconds to decode, think, and decide, frame after frame.
> `[pause]` We cut the network ourselves, on purpose. Nothing left this room. `[laughs softly]`
> We checked.
>
> **[1:34]**
> `[pause, five seconds]`
>
> **[1:39]** `[serious]`
> Here's what it doesn't do. It doesn't brake.
> We tried. Wired straight to a stop, it was right about one time in five — and it stopped a hundred
> and forty times in fifty-eight seconds, on an empty floor.
> `[pause]` Distance isn't obstruction. Obstruction isn't authority. We don't have the calibration to
> tell them apart yet. `[pause]` So we took the brake away, and left it a warning.
> Braking has to be earned.
>
> **[2:02]** `[warmly]`
> [NAME] never sees any of this. The floor, the cells, the arithmetic underneath — it disappears, and
> he just… goes.
>
> **[2:12]**
> His daughter still calls on Sundays. `[pause]` Not to check. She's never had to.
>
> **[2:20]**
> ElevenLabs told you this story. `[pause]` It never made a single decision in it. It never will.
>
> **[2:28]** `[warmly]`
> The app is the showcase. `[pause]` The product is the refusal underneath it.
>
> **[2:35]**
> When the evidence is there, move.
> `[pause]` When it isn't —
> hold.

**Nota de alcance.** Como en el borrador anterior, `[0:00]` evita nombrar la categoría del vehículo
—"silla de ruedas", "scooter"— y en cambio dice *"a mobility vehicle"*, que es genérico y verdadero
para el rango completo que [plan.md](plan.md) B4 registra: rover, robot, scooter, silla motorizada. La
especificidad la aporta `[NAME]` y el metraje, no una etiqueta de producto en la narración.

**Qué se dejó afuera del guion anterior y por qué.** El ritual doméstico del jueves ([RITUAL], la
lámpara, el café frío) desaparece: el segundo brief no lo pide y competía con el tiempo que ahora exige
"la pregunta" (§3.a punto 3) y "el principio" (punto 4), que en la versión anterior estaban comprimidos
en una sola frase. Se conserva el llamado del domingo de la hija —es el latido de familia que el brief
sigue pidiendo en "retorno humano"— pero se acorta de dos frases a dos líneas.

### 3.d Voz — elección, audio tags y notas de dirección

Mismo esquema de tres cubetas que el borrador anterior; se reconstruye para el arco emocional de este
guion, que ya no es *curiosidad → calidez → calma* sino **documental-preciso → temor contenido durante
el fallo → resolución contenida al final.**

**ELECCIÓN DE VOZ** (se decide una vez, sin cambios respecto del borrador anterior — el brief no tocó
esto): hombre, 35–45, inglés americano neutro, tono medio-bajo, autoridad amable, **documental premium,
nunca locutor comercial**. ⏳ Pendiente el `voice_id` concreto; se prueba contra el párrafo `[1:39]`
—el del fallo— porque es el que peor tolera sonar a anuncio.

**AUDIO TAGS inline** (se cobran como caracteres, §2.b):

| Punto | Tag | Función en el nuevo arco |
|---|---|---|
| `[0:00]` | `[curious]` | Abre en curiosidad documental, igual que antes |
| `[0:30]`, `[1:04]`, `[1:39]` | `[serious]` | Marca las tres zonas de mayor precisión técnica: la revelación del producto, el principio, y el fallo — **tres usos, no uno**, porque el brief pide que "el fallo" suene a decisión de ingeniería y eso exige el mismo registro que la explicación técnica, no un registro distinto |
| `[1:30]` | `[laughs softly]` | Único momento de alivio antes del silencio de `[1:34]` — humor seco, nunca carcajada |
| `[2:02]`, `[2:28]` | `[warmly]` | El retorno humano y el acto final se desaceleran, igual que el borrador anterior marcaba lo emocional |
| a lo largo | `[pause]` | Micro-pausas donde cambia el sentido; una sola pausa larga marcada explícitamente, `[pause, five seconds]` en `[1:34]`, que es el silencio antes de "the failure" — la pausa más importante del guion, y la única con duración explícita |

Siete tags de contenido más ocho pausas — algo más denso que el borrador anterior (cinco tags, siete
pausas), porque este guion tiene **tres** zonas técnicas distintas (revelación, principio, fallo) en
vez de una sola.

**NOTAS DE DIRECCIÓN que ni voz ni tag expresan:**

1. **El silencio de `[1:34]` es el gesto dramático central del guion**, no un espacio en blanco entre
   frases. Se renderiza como un segmento de audio separado —silencio real, no un corte de edición— para
   que la ausencia de narración quede intencional y no accidental si se re-edita el master.
2. **El registro de `[1:39]` no es una disculpa.** Es la instrucción de dirección más importante del
   documento: la misma cadencia firme del principio (`[1:04]`), nunca una caída de energía ni un tono
   de descargo legal. Se elige la toma que suena más a "esto es lo que decidimos" y se descarta
   cualquier toma que suene a "lamentamos informar".
3. **Arco por segmentos**, igual que antes pero renumerado sobre este guion: S1 `[0:00–0:29]`
   (curiosidad), S2 `[0:30–1:21]` (revelación + pregunta + principio, la zona más densa), S3
   `[1:22–1:38]` (prueba, hasta el silencio), S4 `[1:39–2:01]` (el fallo), S5 `[2:02–2:35]` (retorno,
   ElevenLabs, cierre). Cinco segmentos, como antes; los límites se movieron porque los latidos se
   movieron.
4. **`[2:20]`, la línea de ElevenLabs, se graba y se escucha aislada del resto.** Es la línea de
   cumplimiento más sensible del documento (§5): tiene que sonar a hecho, no a nota legal susurrada.

### 3.e Beat sheet y lista de planos

~155 s de guion hablado más aire de montaje, apuntando a **2:35–2:40** final. **LA** = acción real
filmada, **SC** = captura de pantalla, **EL** = generado en ElevenLabs. **Ninguna fila EL en la columna
de imagen**, igual que en el borrador anterior — es el argumento de cumplimiento de §5.

| # | t | Dur | Latido (§3.a) | Plano | Origen |
|---|---|---|---|---|---|
| 1 | 0:00 | 10 s | Apertura | Plano fijo, cámara del vehículo mirando al frente; la esquina fuera de campo. Handheld apenas. | LA |
| 2 | 0:10 | 6 s | Apertura, `HOLD` #1 (§3.b) | Encuadre físico del teléfono en su mano: HUD mínimo, `HOLD` en gris, sin urgencia. Habitación alrededor, fuera de foco. | LA + SC |
| 3 | 0:16 | 14 s | Apertura → transición | Cámaras de terceros: sobre la puerta, en el porche de enfrente. Empujes lentos. | LA |
| 4 | 0:30 | 16 s | **Revelación del producto** | Visualización física restringida: el mapa de celdas llenándose sobre la mesa del taller (monitor, no pantalla completa), confianza y vencimiento visibles como texto simple. **Sin hologramas, sin partículas.** | SC (dentro de encuadre físico) |
| 5 | 0:46 | 18 s | **La pregunta** | Terminal simple: coverage / session / floor verified / free cells / freshness / contradiction, apareciendo en el orden en que se nombran. | SC (dentro de encuadre físico) |
| 6 | 1:04 | 18 s | **El principio — `HOLD` #2** | Cada condición se apaga una por una en pantalla; la última deja `HOLD` solo, centrado, agrandándose. | SC (pantalla completa breve, ≤4 s) |
| 7 | 1:22 | 8 s | Analogía del freno | Plano de la mano sobre el joystick, corte a un plano genérico de un auto frenando en la calle (metraje propio, no de archivo con marca visible). | LA |
| 8 | 1:30 | 4 s | Prueba — cinta métrica | **Cinta métrica real, en una mano, sobre una junta de baldosa.** Macro. | LA |
| 9 | 1:34 | 5 s | **`HOLD` #3 — el clímax** | Se corta el cable. Pantalla completa, caída de señal real, `HOLD` sostenido. Único tramo largo de SC del film. | SC |
| 10 | 1:39 | 20 s | **El fallo** | Plano largo, casi sin cortar, cara de la persona o la máquina quieta sobre piso vacío. **Sin gráficos. Sin pantalla.** Es la escena, no el descargo. | LA |
| 11 | 1:59 | 4 s | Por qué no frena | Insert breve: distancia medida, obstrucción no confirmada, autoridad apagada — tres palabras simples en pantalla, sin jerga. | SC |
| 12 | 2:02 | 10 s | Retorno humano | Él sale a la calle. Nadie lo vigila. Plano general, luz natural. | LA |
| 13 | 2:12 | 8 s | Familia | Llamada de domingo. Corto, de lejos, sin sentimentalismo. | LA |
| 14 | 2:20 | 8 s | Posicionamiento ElevenLabs | Plano quieto de la persona o del taller; ningún elemento de interfaz en cámara — la línea se sostiene sola, sin ilustrarse con un logo de ElevenLabs superpuesto a una decisión del sistema. | LA |
| 15 | 2:28 | 7 s | Acto final — `HOLD` #4 | Plano fijo, corte a negro, nombre y logo. **Sin lista de funcionalidades.** | LA |

**Reparto final y su cambio respecto del borrador anterior.** Suma de columna SC: planos 2 (parcial),
4, 5, 6, 9, 11 ≈ **35 s sobre ~148 s de guion visible**, es decir **~24 %** — prácticamente el mismo
techo del 25 % que fijaba el borrador anterior (40 s sobre 162 s), y por la misma razón: el reparto es
una decisión de cumplimiento y de ritmo, no del guion. **Lo que sí cambió es la distribución dentro de
ese 24 %:** el borrador anterior concentraba la pantalla en una demostración de tres situaciones de
uso; este guion la reparte en tres momentos más cortos y más densos —la revelación del producto, la
pregunta razonada, y el colapso a `HOLD`— porque el brief pide explícitamente mostrar el razonamiento
en pantalla como parte de "la pregunta" y "el principio". Ningún tramo continuo de pantalla supera los
8 s salvo el plano 9 (`HOLD` #3), que sigue siendo, como en el borrador anterior, el único ganado.

### 3.f Música — prompts para Eleven Music

Estructura de tres movimientos, ajustada al nuevo arco (documental-preciso → temor contenido →
resolución contenida), no una copia del borrador anterior. **Silencio explícito antes de `HOLD` (plano
9) y antes de la línea "rangyuu does not brake today" (`[1:39]`)** — ambos exigidos por el usuario como
tratamiento sonoro del motivo.

**Cue A — curiosidad documental, 0:00 a 1:03, objetivo ~63 s, instrumental, sin voces:**

> A restrained, observational documentary opening. Solo upright piano, sparse and dry, room tone
> audible around it. A single low sustained string note underneath, barely present. No drums. Around
> 66 BPM, loose, not gridded. Curious and precise, never sentimental. Wide midrange gap for spoken
> voice throughout. No vocals, no swells.

**Cue B — precisión técnica con calidez naciente, 1:22 a 1:33, objetivo ~11 s, instrumental, sin
voces:**

> A brief, focused continuation. The same piano, slightly more rhythmic and even, like a steady
> pulse of measurement rather than emotion. No percussion with attack. Quiet and exact. Fades to
> near-silence by the end of the cue. No vocals.

*(Nota: este cue es corto a propósito — termina justo antes del silencio de cinco segundos en `[1:34]`,
que va **sin música**, ver más abajo.)*

**Cue C — resolución contenida, 2:02 a 2:35, objetivo ~33 s, instrumental, sin voces:**

> A quiet return at the end of an intimate, precise documentary. The piano returns alone after an
> absence, plays one small figure, and a single string note joins late and briefly. No pulse, no
> percussion, no rise, no triumphant chord. Ends on an unresolved sustain that simply stops. Honest
> and calm, never uplifting. No vocals.

**Silencios explícitos, sin música:** `[1:34]–[1:38]` (el corte de cable y el silencio de cinco
segundos que precede al fallo) y el instante inmediatamente anterior a *"So we took the brake away"* en
`[1:39]`. Es la instrucción del usuario aplicada literalmente: silencio específico antes de `HOLD` y
antes de la confesión de que rangyuu no frena hoy.

**Notas de ejecución.** Dos tomas de cada cue, igual que el borrador anterior: a 900 créditos/min, tres
cues cortos (63 + 11 + 33 ≈ 107 s ≈ 1,8 min) generan **~3.200 créditos** con dos tomas — **menos** que
el estimado anterior de ~4.900, porque este guion tiene más silencio, no más música. Ver §2.b para el
ajuste del total.

### 3.g Efectos de sonido — prompts para Sound Effects (200 créditos cada uno)

**El sonido sale mayormente del rodaje**, igual que en el borrador anterior: tono de sala, pasos,
puerta, calle, respiración. Se generan **cinco** efectos —uno menos que antes, porque "celda del mapa
asentándose" y "confirmación de UI" se fusionan en uno solo dado que la revelación del producto (plano
4) ahora es la escena que más los necesita juntos—:

1. **Confirmación de UI / celda asentándose** — `A single short soft synthetic interface confirmation tone with a subtle granular tick layered underneath, like a data cell locking into a grid. Warm, low, clean digital decay under 400 milliseconds, no reverb tail, no alarm quality.`
2. **Negativa de UI (`HOLD` aparece)** — `A single short muted synthetic interface tone signalling refusal. Low, dry, slightly detuned downward, no harshness, no science-fiction character, under 500 milliseconds.` — usado en las apariciones 1 y 2 de `HOLD` (§3.b), nunca en la 3, que usa el corte de red real.
3. **Corte de red** — `The sound of a live signal dropping out: a brief burst of digital noise collapsing into silence, with a faint low-frequency thump underneath. Under one second, no musical pitch.` — usado en `HOLD` #3, el clímax.
4. **Rodadura** — `Continuous close-mic recording of small rubber wheels rolling steadily over smooth indoor tile, quiet and even, no voices, no room echo, ten seconds, loopable.`
5. **Tono de sala de respaldo** — `Quiet interior room tone of a small domestic space in the morning. Faint distant hum, no voices, no footsteps, no music, thirty seconds, seamless loop.`

**La regla que gobierna los cinco, sin cambios:** *suaves, reconocibles, elegantes — nunca sci-fi
agresivo*. No se clona el chime real de Ring, que es marca de un tercero.

### 3.h Imagen, video generado y lipsync — la recomendación sigue siendo no usar ninguno

Sin cambios respecto del borrador anterior, y el nuevo brief la refuerza en el mismo sentido:
**lipsync no** (no hay presentador ni avatar), **video generado no** (el brief pide metraje real,
"proof not claims", que es precisamente lo opuesto a un clip sintético), **imagen generada no** (la
"visualización física restringida" del plano 4 se filma sobre una pantalla real, no se genera). Costo
evitado: el mismo rango de §2.b, ~96.000–144.000 créditos.

---

## 4. Alineación y estrategia

### 4.a La pieza sirve a los dos objetivos, y no por casualidad

[video.md](video.md) ya fijó un guion de seis bloques para el video del hackathon, y B7 de
[plan.md](plan.md) exige *"Ring aparece funcionando en código y pantalla"*. El guion de §3.c **sigue
cumpliendo los dos contratos**, aunque el orden cambió al reordenarse alrededor de la persona:

| Bloque de video.md | Dónde cae en el guion de §3.c |
|---|---|
| 0:00–0:15 problema | `[0:00]`–`[0:16]` — la cámara a bordo no ve la esquina; el brief pone la esquina y a la persona antes que la explicación de producto, no después |
| 0:15–0:35 idea | `[0:16]`–`[0:46]` — la infraestructura ya mira; rangyuu la convierte en mapa (revelación del producto) |
| 0:35–1:20 flujo | `[0:46]`–`[1:21]` — la pregunta razonada y el principio, con `HOLD` #1 y #2 (§3.b) contestando en pantalla |
| 1:20–2:15 estados | `[1:22]`–`[2:01]` — la prueba, el corte de red (`HOLD` #3, el clímax) y el fallo |
| 2:15–2:45 privacidad | `[1:30]`–`[1:38]` — cinco campos, sin píxeles, la red cortada a propósito |
| 2:45–3:00 cierre | `[2:02]`–`[2:35]` — el retorno humano, el posicionamiento de ElevenLabs y `HOLD` #4 como cierre filosófico |

**El bloque de apertura sobre la esquina, `[0:00]`–`[0:16]`, no existía en video.md.** No la
contradice: video.md fija *qué se cuenta* y no prohíbe llegar al problema por una persona y una esquina
ocluida en vez de una lista de funcionalidades. Es el cambio que trae el brief, y es el que hace que el
resto se escuche.

Y cumple el criterio de B7 sin trucos: **los planos 4, 5, 6 y 9 de §3.e son captura de Ring
funcionando**, no narración sobre Ring.

### 4.b El calendario manda

- **Challenge 3 cierra el 2026-09-25 a las 18:00 UTC.** Son **9 días** desde hoy.
- **El hackathon cierra el 2026-10-23.** Son **37 días**, y B7 ya pide enviar con margen, no el 23 a
  las 11:50.
- En medio queda **B11**, abierto: falta grabar el clip y medir con cinta. Si B11 cierra entre las dos
  fechas, el video del hackathon puede mostrar algo que el del Challenge 3 no tenía.

**El calendario de 9 días del borrador anterior sigue en pie**, reconciliado contra el guion de §3.c y
§3.e — cambia qué se filma cada día, no cuándo:

| Día | Qué pasa |
|---|---|
| 1 (09/16) | Bloquear este documento. Pedir consentimiento (§6). Confirmar quién es el protagonista real. |
| 2 (09/17) | Recorrido de localización: la esquina ocluida, la calle, las cámaras de terceros visibles desde afuera. Lista de planos cerrada contra §3.e. |
| 3 (09/18) | **Fecha límite de casting.** Sin protagonista consentido para esta fecha, el film pasa a tener como protagonista a quien construye rangyuu, misma estructura, mismo guion salvo `[NAME]`. Rodaje bloque A: interior, la máquina, el joystick, manos. |
| 4 (09/19) | Rodaje bloque B: la esquina, la calle, el umbral, la llamada de domingo (o su reconstrucción honesta si no coincide con el rodaje). |
| 5 (09/20) | **Captura de pantalla**, día aparte: sesión WHEP viva, el mapa de celdas llenándose (plano 4), la terminal con los seis campos de la pregunta (plano 5), el colapso a `HOLD` (plano 6), el corte de red en vivo (plano 9). Grabación de tono de sala. |
| 6 (09/21) | Generación en ElevenLabs: cinco segmentos de narración, tres cues de música, cinco efectos (§3.c–§3.g). |
| 7 (09/22) | Montaje. Primer corte completo. |
| 8 (09/23) | Mezcla, silencios de §3.f colocados a mano, subtítulos con Scribe, corrección de color. |
| 9 (09/24) | Margen. **Enviar el 09/24, no el 09/25 a las 17:50.** |

### 4.c Recomendación: **una pieza, dos cortes**

**No dos producciones. Tampoco un único archivo congelado.**

1. **Un solo máster** de ~2:35–2:40 en inglés, producido para el 2026-09-24, con todo el audio
   generado en ElevenLabs sobre **metraje filmado y capturado, nada generado**. Ese archivo se envía
   al Challenge 3.
2. **Los stems se guardan sin mezclar** —los cinco segmentos de narración, los cues A, B y C, los
   cinco efectos— en la carpeta de artefactos que ya pide video.md, y **fuera del repositorio** (§6).
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
| **Quién es el protagonista** — la persona real que se filma | Fecha límite: **día 3, 2026-09-18** (§4.b). Sin ella el film cambia de protagonista, no de estructura. |
| **Consentimiento escrito** de quien se filma y de quien se oye | Es de quien filma; este documento no puede darlo ni presumirlo (§6). |
| **`voice_id` concreto** para la narración | No se eligió. Hay que escuchar candidatas contra el párrafo `[1:39]` — el del fallo —, que es el que peor tolera una voz de locutor o de descargo legal (§3.d). |
| **Comportamiento real de los siete audio tags** con esa voz | Eleven v3 los interpreta, no los ejecuta: un tag no entendido se ignora o se lee en voz alta. Nada se probó — **sin MCP conectado** (§3.d). |
| **Si ElevenLabs cobra las audio tags como caracteres** | §2.b asume que **sí**, que es el supuesto caro. Se confirma en la primera generación. |
| El nombre real ([NAME]) en la narración, o un sustituto | Decisión de la persona filmada, no del documento (§6). |
| El momento de familia del plano 13 (§3.e) | Depende de la vida real de quien se filme; el brief exige que sea **real**, no inventado para la cámara. |

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
límite de casting de §4.b.
