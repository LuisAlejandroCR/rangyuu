<!-- mobile.md: qué es el cliente Expo de mobile/, qué deliberadamente NO hace, cómo se corre,
     contra qué rutas del backend habla y qué quedó sin verificar.
     Se distingue de docs/app.md, que describe la app web de web/ (la demo sin instalación),
     y de docs/plan.md y docs/verificacion.md, que llevan el plan y la evidencia del núcleo. -->

# Cliente móvil (Expo)

## Qué es

Un cliente delgado en React Native, bajo `mobile/`, que hace tres cosas y nada más:

1. Captura frames de la cámara de a bordo.
2. Los manda al backend de Python y muestra la decisión que vuelve.
3. Emite un aviso háptico **por cada cambio de estado**, nunca por frame.

El consumidor es cualquier vehículo de movilidad autónoma o asistida — rover, robot, scooter,
silla motorizada. No es una app para peatones, y la copia visible en inglés no habla de
caminar ni de pasos: habla de la cámara de a bordo y del camino adelante.

## Por qué existe, si ya hay una app web

`web/` sigue siendo la demo sin instalación y no se tocó. Esta app existe por tres cosas que
la web no puede hacer en iOS:

- **Háptica de verdad.** iOS no expone la Vibration API, así que `web/haptics.js:13` detecta
  que no hay vibración y cae a tono y voz. Acá se usa `expo-haptics`.
- **Cámara sin túnel HTTPS.** Safari niega `getUserMedia` sobre HTTP plano. `expo-camera`
  dentro de Expo Go no tiene esa restricción.
- **Correr en un iPhone real sin una Mac.**

## Qué deliberadamente NO hace

- **No porta los tres destinos** (Ahora / Caminata / Sistema). Es una sola pantalla.
- **No reconstruye el mapa** ni las zonas.
- **No reimplementa detección ni decisiones en JavaScript.** El runtime de Python mide
  8,16 ms por frame sin inferencia de terceros, probado envenenando `socket`. Esa evidencia
  es sostenedora y se queda donde está. Esta app es sensor y pantalla; Python decide.
- **No agrega rutas ni cambia el API de Python.** No se agregó código Python en este PR.
- **No agrega una librería de i18n.** La tabla de strings es a mano, en `mobile/src/i18n.ts`.

## Los cuatro estados

La app muestra `AVANZA`, `CUIDADO`, `PARA` y `SIN CERTEZA`, y **no los deriva**: los recibe ya
derivados por `rangyuu/ui.py:45` (`to_screen`), que es donde vive la regla. Duplicar esa
derivación en JavaScript dejaría que las dos versiones se separen con el tiempo.

La única regla de estado del cliente está en `mobile/src/state.ts` (`normalizeState`) y solo
puede mover hacia abajo: cualquier valor que este build no reconozca se muestra como
`SIN CERTEZA`. Nunca puede convertir un `PARA` en un `AVANZA`. Es el mismo invariante que
protege `rangyuu/ui.py:56`: un `HOLD` no se ablanda, y `CUIDADO` solo degrada un `PROCEED`.

Si se pierde el enlace con el backend, la pantalla cae a `SIN CERTEZA`, nunca a `AVANZA`
(`mobile/App.tsx`, rama de error de `tick`).

El aviso se emite una sola vez por cambio: `mobile/src/alert.ts` recuerda el último estado
anunciado y compara. Disparar de forma continua es inusable, y el parpadeo de estado diez
veces por segundo ya fue un bug real acá antes de la histéresis.

## Cómo se corre

Pasos y comandos: `mobile/README.md`. En resumen: `python -m rangyuu.serve` en la máquina,
`npm install && npm start` en `mobile/`, y escanear el QR con Expo Go.

**Expo SDK 57** (`expo@~57.0.23`). Corre en Expo Go: sin Mac y sin cuenta de desarrollador.

La base del backend es configurable con `EXPO_PUBLIC_RANGYUU_API`. Si está vacía, el cliente
usa el host desde el que Expo Go bajó el bundle con el puerto 8080 — en desarrollo, la misma
máquina que corre Python. No hay ninguna IP de nadie escrita en el código.

## Rutas del backend que llama

Las dos ya existían. No se inventó ninguna.

| Ruta | Dónde está definida | Para qué |
| --- | --- | --- |
| `POST /api/space/observe` | `rangyuu/webapp.py:104`; el cuerpo se valida en `rangyuu/webapp.py:136` | manda un frame gris de 64x36; responde `clearance`, `written` y un `now` completo |
| `GET /api/health` | `rangyuu/webapp.py:67` | distinguir "backend caído" de "cámara caída" |

El cuerpo de `observe` es el mismo que manda la app web (`web/app.js:257`): `width`, `height`
y un arreglo plano de `width * height` muestras de luminancia. El tope de 65 536 muestras lo
impone `rangyuu/webapp.py:144`; 64 × 36 = 2304 queda muy por debajo.

Como React Native no tiene canvas, el camino hasta esas muestras es distinto al de la web:
captura fija → `expo-image-manipulator` redimensiona a 64x36 JPEG → `jpeg-js` decodifica en JS
puro → luminancia con los mismos coeficientes que `web/app.js:254`.

## Qué está verificado

- El paquete instala y la matriz de versiones del SDK 57 está limpia: `npx expo install --check`
  responde `Dependencies are up to date`.
- Typecheck estricto en verde: `npx tsc --noEmit`, sin salida.
- El bundle resuelve y compila: `npx expo export --platform ios` produce 609 módulos, 1,5 MB.
- El contrato HTTP es real, ejercido contra el backend de verdad: con
  `python -m rangyuu.serve 8099`, un `POST /api/space/observe` con `width=64`, `height=36` y
  2304 muestras respondió `{clearance, now, reason, written}`, y `now` trajo
  `state='CUIDADO'`, `decision='PROCEED'`, `authorizes=True` — es decir, `CUIDADO` degradando
  un `PROCEED`, exactamente la regla de `ui.py`. `GET /api/health` respondió `{"status":"ok"}`.
- La suite de Python no se movió: 181 passed, 1 skipped, antes y después.

## Qué está sin verificar

- ⏳ **pendiente — no se probó en un iPhone físico.** No hay dispositivo disponible en este
  entorno. Todo lo que sigue depende de eso y no se puede afirmar.
- ⏳ **pendiente — la háptica.** `expo-haptics` no se puede ejercer sin motor táptico. Que
  dispare una vez por cambio está verificado como lógica (`alert.ts` compara contra el último
  estado), no como vibración sentida.
- ⏳ **pendiente — la cámara.** `takePictureAsync` no corre en un simulador sin cámara. La
  orientación del frame capturado no está comprobada contra el suelo real; por eso no se usa
  `skipProcessing`, que según la documentación de expo-camera deja la orientación incierta.
- ⏳ **pendiente — el ritmo real.** `FRAME_INTERVAL_MS` es 700 ms. Una captura fija por frame
  es mucho más cara que `drawImage` sobre un canvas, y cuánto tarda de verdad el ciclo
  captura → redimensionar → decodificar JPEG en un iPhone no está medido.
- ⏳ **pendiente — Expo Go.** Que el QR abra y la app arranque en Expo Go SDK 57 no se
  comprobó; lo que sí se comprobó es que el bundle de iOS exporta sin errores.
- ⏳ **pendiente — el idioma.** La tabla cae a inglés salvo que el dispositivo pida español.
  No se verificó cambiando el idioma de un dispositivo real.
