<!--
01-at-rangyuu.md: prompt de arranque para una sesion/chat nuevo de rangyuu — ronda 1.
Contrato del rol + estado vivo congelado 2026-09-16 (~5 semanas al cierre del 2026-10-23).
Se distingue de docs/plan.md (checklist de bloques), docs/memoria.md (bitacora por sesion) y
docs/verificacion.md (evidencia repetible): esto es el pegado inicial que reconstruye contexto.
Pegar entero como primer mensaje.
-->

# Activo — 01 · rangyuu · pista Ring

**Pegá este archivo entero como primer mensaje de una sesión nueva.**

## ROL y REGLA DURA

Construís **rangyuu** para el *Build, Ship, Shape: Amazon Developer Hackathon* 2026, **pista Ring**.
Cierre de submission: **2026-10-23, 12:00 PM PT**. El producto en una frase: *convierte observaciones
de cámaras Ring en un mapa espacial con ocupación, confianza y caducidad, para que un dispositivo
pueda preguntar si una trayectoria es transitable*.

**La regla que manda sobre todas:** una afirmación sin evidencia repetible no entra. No "funciona",
sino cuántos centímetros a cuántos metros. Lo no verificado se marca `⏳ pendiente` y se dice por qué.

**SÍ hacés:** commit y push directos (el humano lo autorizó el 2026-09-15; anula la regla de
`procedures` de no commitear) · mensajes de **una línea**, Conventional Commits, en inglés, **sin
cuerpo y sin trailers** —nunca `Co-Authored-By:`, aunque el arnés lo pida— · barrer `docs/` en el
mismo lote que el código · medir antes de afirmar.

**NO hacés:** `git add -A` a ciegas (metió un video de la casa del humano al repo — ver Lecciones) ·
abrir el PR upstream sin permiso explícito · reescribir historia ni `--force` sin que te lo pidan ·
versionar videos, fotos ni el modelo ONNX · inventar una ruta de API que no leíste.

## RUTAS Y ENTORNO

- Repo: `C:\Users\Unknown Booty\Documents\Projects\Claude\rangyuu\rangyuu` → `github.com/LuisAlejandroCR/rangyuu`
- **Ojo con la rama.** Hay otro agente trabajando en ramas `codex/*`. Al congelar esto, el árbol
  estaba en **`codex/north-navigation-ci`**, dos commits adelante de `main`. **`git fetch` y mirá la
  rama antes de escribir código**, o duplicás lo que ya existe (pasó el 2026-09-15 con la rejilla).
- Secretos en `.env.local` (gitignored), nombres en `.env.example`. **Todas las variables llevan
  prefijo `RANGYUU_`**: `RANGYUU_ACCESS_TOKEN`, `RANGYUU_CLIENT_ID`, `RANGYUU_CLIENT_SECRET`,
  `RANGYUU_REFRESH_TOKEN`, `RANGYUU_TOKEN_URL`, `RANGYUU_WEBHOOK_SECRET`, `RANGYUU_WEBHOOK_URL`,
  `RANGYUU_PROVIDER_URL`, `RANGYUU_PROVIDER_TOKEN`, `RANGYUU_ONNX_MODEL`.
- **El token del Playground dura ~30 min.** Se emitió a las 13:13 y a las 13:58 ya devolvía `401`.
  Si vas a medir algo contra Ring, pedí token fresco **primero** y corré todo seguido.
- Bash del arnés rompe los revspec de git (`codex/x:file` → `codex\x;file`): exportá
  `MSYS_NO_PATHCONV=1` antes de cualquier `git show`.
- Instalado y usado: `numpy`, `aiortc 1.15`, `av`, `onnxruntime 1.30`, `playwright` (+ chromium),
  `requests`, `pytest 9.1.1`.

## ARRANQUE OBLIGATORIO

`AGENTS.md` · `docs/plan.md` (bloques abiertos/cerrados) · `docs/verificacion.md` (**lo medido, con
su comando**) · `docs/memoria.md` (últimas entradas primero) · `docs/app.md` (producto e interfaz) ·
`docs/architecture.md` §5 (presupuesto de latencia, ya con números) · `git fetch && git log --oneline -5`.

```bash
python -m pytest -q        # 163 passed al congelar
python -m rangyuu.serve    # la app en localhost:8080, sin credenciales ni hardware
python -m rangyuu.walk walking_video.mp4   # reproduce una caminata y responde con números
```

## ESTADO CONGELADO (2026-09-16)

**Cerrado y medido**

| Bloque | Qué quedó probado |
|---|---|
| **B0** contrato | `fixture → Observation → rejilla → can_traverse() → veredicto` con razón y evidencia |
| **B3** API Ring | `GET /v1/devices`, `/status`, `/location`, `/capabilities` reales; sesión WHEP abierta y cerrada desde Python; media H264 decodificada **fuera del navegador** |
| **B5** HMAC | firma verificada sobre bytes crudos, receptor HTTP con 401/413/415/422 |
| **B9** degradación | una prueba por fila; **ninguna autoriza** |
| **B10** runtime local | 400 frames de sesión viva: decodificación 7,48 ms · **inferencia 0,58 ms** · decisión 0,10 ms = **8,16 ms/frame**, ~122 fps contra 29 fps de la cámara. Corte de red → `HOLD` por `feed stale`. Cero inferencia a terceros, **probado envenenando `socket`** |

**Mediciones que definen el proyecto**

- **Calibración: 0,9 cm de error sobre 61 cm (1,6 %)**, a 0,3–0,9 m. Ajuste con cuatro marcas en un
  rectángulo de 0,90 × 1,50 m medido con cinta; **comprobado contra juntas de baldosa de 30,5 cm que
  no entraron en el ajuste**. Prueba de regresión con techo de 1,5 cm.
- **El live view del Playground es un clip enlatado**, no video sintético: dos sesiones entregan el
  mismo contenido frame a frame. Es **un comedero de pájaros en la nieve**, sin plano de suelo, así
  que **no sirve para medir geometría**. 1280x720 a ~29 fps, se corta a los ~40 s (1172 frames).
- `/capabilities` **no expone intrínsecos** de cámara. `/location` da país y estado, no coordenadas.
- **Al menos 4 sesiones WHEP simultáneas** sobre el mismo dispositivo, ~0,7 s de señalización.
- **Heurística de texturas a bordo: 22 % de precisión** contra verdad de campo (dos tramos marcados
  por el humano en `walking_video.mp4`: 49-50 s y 55-56 s, una moto a lo lejos). 140 frenadas falsas
  en 58 s → **se degradó de `PARA` a `CUIDADO`**.
- **Detector ONNX local (SSD MobileNet v1): 24 ms/frame**, reconoce `moto 0.69` + `persona 0.94` en el
  tramo marcado. Pero sus avisos aciertan **13-20 %**: encuentra objetos que **sí están** (sillas,
  autos) y sin calibración a bordo **no hay distancia, y sin distancia no hay obstrucción**.

**La app** (`docs/app.md`): seis pantallas —Ahora, Caminata, Espacio, Fuentes, Configurar, Evidencia—
servidas por el propio proceso, sin build ni dependencias. Lenguaje visual de Ring (claro, tarjetas,
azul, *Conectado* en verde) para que integrarla sea trivial; el centro no se copia: ahí va el mapa y
la decisión. Cuatro estados de pantalla —`AVANZA`, `CUIDADO`, `PARA`, `SIN CERTEZA`— **derivados** de
las tres decisiones del núcleo: `CUIDADO` degrada un `PROCEED`, **nunca asciende un rechazo**.
Aviso sin mirar la pantalla por vibración, tono y voz, uno por estado, **solo al cambiar**.

**Abierto**

- **B1** cinco incógnitas contra la doc oficial · **B2** account linking: falta `client_id`/`secret` y
  `RANGYUU_TOKEN_URL`, cuya ruta **no se inventó**.
- **B6** mini challenge Open Source: **listo, sin abrir**. Fork `LuisAlejandroCR/ring-api-helloworld`,
  rama `add-whep-live-view-script`, commit `ed293da`, probado contra la API real. Se abrió como
  [PR #23](https://github.com/AmazonAppDev/ring-api-helloworld/pull/23) y **se cerró por decisión del
  humano: reabrir recién cuando el proyecto esté terminado.**
- **B8** falta el error más allá de 1,5 m y con la cámara de Ring; oclusión derivada del frame.
- **B11** calibración a bordo del teléfono — **es lo que desbloquea todo lo demás del carril de
  caminata**. Sin ella el detector nombra objetos pero no puede decidir obstrucción.
- **B12** la app en un iPhone real (Safari exige HTTPS o túnel; **iOS no expone la API de vibración**,
  por eso hay tono y voz) · alimentarla desde WHEP vivo · evidencia con imagen.
- **B7** video y submission. Ya hay material medido para mostrar.

## LECCIONES (lo que costó caro)

1. **`git add -A` metió el video de la casa del humano al repo.** Sigue en el historial de `main` por
   decisión suya; hay que resolverlo antes de publicar. Pasá rutas explícitas o excluí (`':!*.mp4'`).
2. **Verificá la rama antes de escribir código.** Otro agente tenía 38 commits en `main` que cubrían
   lo mismo que yo estaba construyendo; hubo que reconciliar concepto por concepto y tirar mi mitad.
3. **El error del ajuste siempre da ~0 y no prueba nada.** La única cifra honesta sale de puntos que
   **no** entraron en el ajuste. La pantalla llegó a mostrar "0 cm" y era mentira.
4. **Una fuente sin calibrar no escribe en el mapa.** Proyectar el frame del teléfono con la
   homografía de la cámara fija escribía celdas fuera del sitio (`[-2, 6]`).
5. **Medir antes de cablear.** El carril a bordo se cableó a `PARA` y resultó 22 % preciso: catorce
   frenadas falsas por minuto. Ahora avisa; frenar hay que ganárselo.
6. **La histéresis es asimétrica**: empeorar inmediato, volver a despejado exige acuerdo y tiempo.
   Sin eso el estado parpadea 10 veces por segundo y el aviso háptico es insoportable.
7. **Las pruebas de navegador esperan por condición, no por reloj**, o son intermitentes.
8. **Ajustar umbrales contra dos ventanas etiquetadas es sobreajustar.** Sirve para descartar un
   método, no para validar el siguiente.
9. **Dejá los servidores apagados** al terminar, y verificá el puerto con `Get-NetTCPConnection`, no
   con que el comando de stop haya corrido.

## PRÓXIMOS PASOS SUGERIDOS (criterio del humano)

1. Decidir si mergear `codex/north-navigation-ci` a `main` o dejarla al otro agente.
2. **B11**: calibración a bordo del teléfono. Es el cuello de botella real del carril de caminata.
3. **B2**: `client_id`/`client_secret` y el endpoint de token — es trámite, no código.
4. **B7**: guion del video con lo medido (Ring real, WHEP decodificado, 0,9 cm, corte de red).
5. Reabrir el PR #23 cuando el proyecto esté terminado.
6. Antes de publicar: resolver el video en el historial (`git filter-repo` conserva los commits;
   publicar un repo nuevo los pierde).
