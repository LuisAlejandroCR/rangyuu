<!-- docs/elevenlabs-challenge.md: el plan de la entrada al Challenge 3 de ElevenLabs — costo en
     créditos, prompts listos para ejecutar y estrategia de calendario. Se distingue de
     docs/video.md, que decide *qué se cuenta* (guion por bloques, criterios de edición, regla de
     que ElevenLabs no toca el runtime): aquello es la política del video; esto es la producción
     —cuánto cuesta, qué se escribe literalmente en cada prompt y cuándo se envía—. -->

# Challenge 3 · Build with ElevenLabs MCP — plan de entrada

**Escrito el 2026-09-16.** Nada de este documento está ejecutado. **No se generó ni un segundo de
audio, imagen o video, y no se gastó ni un crédito.** Es un plan de producción; lo que aquí se llama
"costo" es una estimación citada, no una factura.

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
| Lipsync | no se usa (ver §3.e) | 0 |
| **Total** | | **~111.000 + imágenes ⏳** |

Rango honesto de esa cifra: **110.000–160.000 créditos**, según modelo de video y número de retomas.
Con Sora 2 Pro en lugar de Veo 3.1 el tramo de video sube de ~96.000 a ~144.000 y el total a ~160.000.
**Confianza: baja**, y toda la incertidumbre está en una sola fila —el video— cuyo precio no está
publicado.

**Variante mínima** (recomendada; sin video generado, ver §4):

| Elemento | Cálculo | Créditos |
|---|---|---|
| Narración TTS | 2.300 chars × 2 pasadas | ~4.600 |
| Música | 2,67 min × 900 × 1 toma | ~2.400 |
| Efectos de sonido | 5 × 200 | ~1.000 |
| **Total** | | **~8.000** |

**Confianza: alta.** Las tres filas usan costos oficiales publicados y la aritmética es trivial. El
único riesgo es subestimar las retomas de narración.

### 2.c Qué plan hace falta

| Plan | Precio | Créditos/mes | ¿Alcanza? |
|---|---|---|---|
| Free | $0 | 10.000 | La variante mínima entra por **2.000 créditos de margen** — sin espacio para equivocarse. Además el plan gratuito **no permite generar video** y limita imágenes a 3/día. |
| Starter | $6 | 30.000 | **Cómodo para la variante mínima**: ~3,5 piezas completas. |
| Creator | $22 (1er mes 50 % off) | 121.000 | Justo al borde de la variante completa (~111.000). Demasiado ajustado. |
| Pro | $99 | 600.000 | **El plan necesario si se genera video**, con margen de 4–5 piezas. |
| Scale | $299 | 1.800.000 | Innecesario para esto. |

Fuente de la tabla: [elevenlabs.io/pricing](https://elevenlabs.io/pricing), consultada 2026-09-16.

⏳ **Pendiente:** el saldo real de la cuenta de quien envía. Este documento no lo conoce. Antes de
empezar hay que mirarlo, porque decide cuál de las dos variantes es viable.

**El premio.** 1er lugar del Challenge 3 = **1.000.000 de créditos** (dato entregado con el encargo;
⏳ **no confirmado contra el portal**, ver §5). Para dimensionarlo: son ~125 piezas de la variante
mínima, o ~9 de la variante completa. Equivale a unos 20 meses de plan Creator.

---

## 3. Prompts — listos para ejecutar

**Todo lo de esta sección va en inglés a propósito**, porque es lo que se va a ejecutar y lo que se
va a oír: la submission y los jurados del hackathon son en inglés.

### 3.a Narration script — the master text for Text to Speech

Paste as-is. ~2.300 characters, ~2:40 at a measured pace. Every number in it is a number this
repository actually measured; the bracketed cues are edit notes, **strip them before sending the
text to TTS**.

> **[0:00]**
> A camera on a wheelchair sees what is in front of it. It does not see around the corner.
>
> **[0:10]**
> Rangyuu asks a different question. Not "what can this vehicle see" — but "what does the building
> already see?"
>
> **[0:22]**
> Ring cameras are already mounted, already watching, already pointed at the sidewalk. Rangyuu turns
> what they observe into a spatial map: every cell carries an occupancy value, a confidence, and an
> expiry. A vehicle can then ask one question — is this trajectory traversable?
>
> **[0:45]**
> This is not a mockup. The live view is a real WHEP session, pulled from Ring and decoded outside
> the browser, in Python. Four hundred frames at twelve-eighty by seven-twenty.
>
> **[0:58]**
> Decoding a frame: seven point four eight milliseconds. Local inference: zero point five eight.
> The decision itself: zero point one zero. Eight point one six milliseconds per frame — capacity
> for a hundred and twenty-two frames a second, against the twenty-nine the camera actually
> delivers. A factor of four in headroom.
>
> **[1:18]**
> The floor is measured, not assumed. The homography was calibrated with a tape measure and checked
> against tile joints that were held out of the fit: zero point nine centimetres of error over
> sixty-one. One point six percent.
>
> **[1:35]**
> Nothing leaves the device except a bounding box. Device, timestamp, kind, confidence, box. Five
> fields. No pixels. Inference is local — proven by poisoning the socket module so that any
> third-party call would crash the run.
>
> **[1:52]**
> Now watch what happens when the network is cut.
>
> **[1:58]**
> The feed goes stale, and the answer becomes HOLD. Not a warning. Not a question. A refusal.
> Rangyuu holds unless everything holds — coverage, session, a valid homography, a free cell,
> nothing unknown, nothing stale, nothing contradictory. Absence of evidence is a no.
>
> **[2:15]**
> That is the principle we are building toward: a vehicular emergency brake. The car's camera sees
> the hazard and applies the brakes. It does not ask permission.
>
> **[2:26]**
> Rangyuu does not brake today, and we will not pretend otherwise. The on-board detector is right
> between thirteen and twenty percent of the time. We wired it to a full stop once. It produced a
> hundred and forty false stops in fifty-eight seconds, so we deliberately downgraded it from STOP
> to CAUTION.
>
> **[2:40]**
> Braking has to be earned. The app you just saw is the showcase. The product is the refusal
> underneath it.

**TTS run notes.** Model: Eleven v3 (or v2 Multilingual) for delivery nuance; not Flash — this is a
master, not a draft. Voice: calm, low, unhurried, engineer-reading-results rather than
announcer-selling. The numbers are spelled out in words on purpose so the model reads them as speech
rather than as digits. Generate in **four segments** split at `[0:45]`, `[1:52]` and `[2:26]`, so a
bad take costs one segment, not the whole script.

### 3.b Music direction — prompt for Eleven Music

Two cues, generated separately, because the piece has two halves.

**Cue A — bed, 0:00 to 2:12, target 135 s, instrumental, no vocals:**

> A restrained ambient electronic underscore for a technical product film. Low sustained synth pad
> in a minor key, a slow pulse around 70 BPM, sparse muted piano notes landing on the beat, subtle
> granular texture underneath. No drums until 0:45, then a soft kick and a light hi-hat that keep
> time without pushing. The mood is measured and precise, the sound of careful engineering, not
> triumph. Leave a wide midrange gap for a spoken voiceover. No vocals, no melody that competes
> with speech, no dramatic swells.

**Cue B — resolve, 2:12 to 2:45, target 35 s, instrumental, no vocals:**

> A quiet resolution for the closing of a technical film. The same minor-key pad thins out to a
> single sustained note, the percussion drops away entirely, and one piano figure repeats and then
> stops. Ends on a clean, unresolved sustain rather than a triumphant chord. Sombre and honest, not
> uplifting. No vocals, no build, no cinematic climax.

**Run notes.** Generate each cue twice and pick; at 900 credits per minute a second take of the
135-second bed costs ~2.000 credits. Duck both cues 12 to 15 dB under the narration in the edit.

### 3.c Sound effects — prompts for Sound Effects (200 credits each)

Five effects carry the whole piece. Each prompt is one generation.

1. **UI confirm** — `A single short soft synthetic interface confirmation tone, warm and low, one note, clean digital decay under 400 milliseconds, no reverb tail.`
2. **UI refusal** — `A single short muted synthetic interface tone signalling refusal. Low, dry, slightly detuned downward, no harshness, no alarm quality, under 500 milliseconds.`
3. **Map cell settling** — `A very short granular digital tick, like a single data cell locking into place on a grid. Dry, tiny, almost subliminal, under 150 milliseconds.`
4. **Network cut** — `The sound of a live signal dropping out: a brief burst of digital noise collapsing into silence, with a faint low-frequency thump underneath. Under one second, no musical pitch.`
5. **Wheelchair roll** — `Continuous close-mic recording of small rubber wheels rolling steadily over smooth indoor tile, quiet and even, no voices, no room echo, ten seconds, loopable.`

**Optional three, if the budget allows** (+600 credits): a Ring chime substitute (do **not** clone
Ring's actual branded chime), a keyboard keystroke cluster for the code shots, and a low room tone
bed for the office scenes.

### 3.d Image generation — prompts, only if used

Stills are **not** the recommended visual spine (see §4), but if a title card or two is wanted:

1. **Opening title card** — `A minimal dark editorial title card. Deep near-black background, a thin faint isometric grid receding into the distance, a few grid cells softly lit in pale cyan as if holding data. Wide empty space in the upper two thirds for a title. No text, no logos, no people, no branding. Flat, restrained, technical.`
2. **The spatial map concept** — `A clean abstract diagram of a floor plan seen from above, rendered as a grid of square cells on a dark background. Some cells pale and steady, a few amber, a few dark and empty. Thin precise lines, no glow, no sci-fi ornamentation, no text or labels. The aesthetic of an engineering readout, not a video game HUD.`
3. **Closing card** — `The same minimal dark grid as a closing frame, but nearly all cells dark and unlit, with only one small pale cell remaining at the centre. Deep near-black, thin lines, wide empty space, no text, no logos, no people.`

**Rule baked into every image prompt:** no Ring branding, no recognisable person, no wheelchair user
depicted, no medical imagery. Real people and real branding belong in real footage with real
permission, never in a generated frame.

### 3.e Video generation and lipsync — the recommendation is to skip both

**Lipsync: skip.** It requires a presenter or an avatar. This piece has no face in it and does not
need one, and an AI-generated presenter reading measured numbers is exactly the credibility risk this
project spends every document avoiding. Cost avoided: unknown (⏳ pendiente), plausibly the single
largest line item.

**Generated video: skip for the primary cut.** The most persuasive footage available is footage that
already exists and is free: the live WHEP session on screen, the map filling cell by cell, the
terminal printing `HOLD` when the cable is pulled, the calibration screen showing 0,9 cm. A generated
clip of an imaginary sidewalk is both more expensive and less convincing than the real thing.

**If a generated establishing shot is wanted anyway**, one clip, 8 seconds, at `[0:22]`:

> A slow steady push-in along an empty indoor corridor at dusk, smooth polished floor, soft even
> overhead light, a doorway at the far end. No people, no vehicles, no text, no logos, no cameras
> visible. Calm, still, documentary realism. Shallow depth of field, muted colour, no lens flare,
> no camera shake, no dramatic lighting.

Budget it at **8.000–12.000 créditos** for a single take (unofficial figure, §2.a) and confirm the
real cost in the Playground before pressing generate.

---

## 4. Alineación y estrategia

### 4.a La pieza sirve a los dos objetivos, y no por casualidad

[video.md](video.md) ya fijó un guion de seis bloques para el video del hackathon, y B7 de
[plan.md](plan.md) exige *"Ring aparece funcionando en código y pantalla"*. El guion de §3.a **cumple
los dos contratos a la vez**:

| Bloque de video.md | Dónde cae en el guion de §3.a |
|---|---|
| 0:00–0:15 problema | `[0:00]` — la cámara a bordo no ve el espacio |
| 0:15–0:35 idea | `[0:10]`–`[0:22]` — Ring aporta contexto, rangyuu lo convierte en mapa |
| 0:35–1:20 flujo | `[0:45]`–`[1:18]` — WHEP real, presupuesto medido, homografía medida |
| 1:20–2:15 estados | `[1:52]`–`[2:15]` — el corte de red y el `HOLD` |
| 2:15–2:45 privacidad | `[1:35]` — cinco campos, sin píxeles, inferencia local |
| 2:45–3:00 cierre | `[2:26]`–`[2:40]` — el freno como destino, el 22 % como presente |

El orden de privacidad y estados quedó invertido respecto de video.md, a propósito: el corte de red
es el clímax de la pieza y conviene dejarlo cerca del final, mientras que la privacidad se sostiene
mejor pegada al bloque técnico. **Eso no contradice video.md**, que fija el contenido y no un orden
inmutable.

Y cumple el criterio de B7 sin trucos: **el bloque `[0:45]`–`[1:18]` es todo captura de pantalla de
Ring funcionando**, no narración sobre Ring.

### 4.b El calendario manda

- **Challenge 3 cierra el 2026-09-25 a las 18:00 UTC.** Son **9 días** desde hoy.
- **El hackathon cierra el 2026-10-23.** Son **37 días**, y B7 ya pide enviar con margen, no el 23 a
  las 11:50.
- En medio queda **B11**, abierto: falta grabar el clip y medir con cinta. Si B11 cierra entre las dos
  fechas, el video del hackathon puede mostrar algo que el del Challenge 3 no tenía.

### 4.c Recomendación: **una pieza, dos cortes**

**No dos producciones. Tampoco un único archivo congelado.**

1. **Un solo máster** de ~2:40 en inglés, producido para el 2026-09-25, con todo el audio generado en
   ElevenLabs sobre metraje capturado real. Ese archivo se envía al Challenge 3.
2. **Los stems se guardan sin mezclar** —narración por segmentos, cue A, cue B, los cinco efectos—
   en la carpeta de artefactos que ya pide video.md.
3. **Para el 2026-10-23 se re-corta**, no se re-produce: si B11 cerró, entra el plano de la
   calibración a bordo medida y se regeneran **solo** los segmentos de narración afectados. Costo
   marginal: unos cientos de créditos, no una pieza entera.

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
- Metraje: **captura de pantalla y grabación real**, no generación. Una grabación de pantalla no es
  un "elemento generado", es una captura, igual que una foto. ✅
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

**Cómo se desarma el riesgo sin consultar a nadie:** la recomendación de §3.e —cero video generado,
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

**Feedback de herramienta.** [video.md](video.md) ya obliga a consignar en la submission qué
funcionó, qué limitó y si se volvería a usar ElevenLabs. Ese registro se lleva **durante** la
producción, no se reconstruye después: cada generación anota modelo, prompt, créditos que la
interfaz mostró y si la toma sirvió. Es el mismo estándar que el resto del repositorio —evidencia
mientras se produce, no memoria a posteriori—.
