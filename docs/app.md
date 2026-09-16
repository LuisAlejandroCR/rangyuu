<!-- docs/app.md: la aplicación — qué pantallas tiene, qué muestra cada una y de qué dato vive.
     Es la especificación de producto y de interfaz; el estado de los bloques está en docs/plan.md
     y lo que se hizo, en docs/memoria.md. No repite la arquitectura de carriles, que vive en
     docs/architecture.md. -->

# La app

**Decidido el 2026-09-16.** Tres destinos principales: Ahora, Caminata y Sistema. Ring ya cubre alertas,
Live View, conversación, historial y control de dispositivos: su app responde *qué está pasando en
casa*. Rangyuu responde otra pregunta, y por eso no se parece.

```text
Ring:      eventos → cámara → alerta
Rangyuu:   observaciones → mapa → decisión segura → movimiento
```

**El momento memorable de la demo es la app diciendo "no sé" y frenando a alguien**, en vez de fingir
una certeza que no tiene. Todo lo demás está subordinado a eso.

## 0. Qué no se copia

- Sin cuadrícula de cámaras. Sin línea de tiempo de clips. Sin rojo permanente de alarma —el botón
  de parar solo se enciende cuando hay algo que parar.
- **El video no se muestra por defecto.** Aparece solo al tocar una evidencia concreta.
- Nada en pantalla que no se pueda señalar en el dato de origen: dispositivo, timestamp, celda.

## 1. Los cuatro estados, y de dónde salen

El contrato del núcleo tiene tres decisiones —`PROCEED`, `HOLD`, `UNKNOWN`— y la interfaz muestra
cuatro. La cuarta no se inventa en la pantalla: se deriva con una regla explícita y probada.

| En pantalla | Sale de | Regla |
|---|---|---|
| **AVANZA** | `PROCEED` | Toda la trayectoria observada libre, fresca y con confianza sobre el umbral |
| **CUIDADO** | `PROCEED` degradado | Autoriza, pero con margen escaso: confianza cerca del umbral, observación cerca de caducar, o celda ocupada **adyacente** a la trayectoria |
| **PARA** | `HOLD` | Algo observado bloquea o contradice |
| **SIN CERTEZA** | `UNKNOWN` | Evidencia ausente, caducada o insuficiente |

**AVANZA y CUIDADO autorizan; PARA y SIN CERTEZA no.** CUIDADO nunca se usa para suavizar un `HOLD`:
degrada un `PROCEED`, jamás asciende una negativa.

Cada estado va acompañado de **una razón corta y humana** —"pasillo libre", "cámara sin conexión",
"zona sin cobertura"— y de la evidencia que la sostiene.

## 2. Las pantallas

### 2.1 Ahora / Ruta segura — la principal

Mapa espacial sobrio del sitio y un estado grande. Encima, la trayectoria propuesta; debajo, las
celdas ocupadas y las desconocidas, distinguidas entre sí. Las zonas, el detalle de una celda y el
historial corto de decisiones se abren dentro del mapa: son evidencia de la decisión, no destinos.

Vive de: `GET /api/space/now` — estado, razón, trayectoria, celdas por estado, edad de la observación.

### 2.2 Modo caminata — la experiencia humana

La cámara del iPhone como sensor a bordo. **No es una app de grabación:** no hay botón de grabar, ni
galería, ni vista previa grande. Indicador de dirección, nivel de confianza, aviso háptico o por voz,
y un botón de parar que ocupa el pulgar.

Es también la pantalla de accesibilidad: el estado se anuncia **sin mirar la pantalla**, por tres
canales con un patrón propio cada uno (`web/haptics.js`):

| Estado | Vibración | Tono | Voz |
|---|---|---|---|
| **AVANZA** | un toque corto | 660 Hz, 0,08 s | "avanza" |
| **CUIDADO** | dos toques | 440 Hz, 0,12 s | "cuidado" |
| **PARA** | dos golpes largos | 220 Hz, 0,25 s | "para" |
| **SIN CERTEZA** | tres toques espaciados | 330 Hz, 0,18 s | "sin certeza" |

Solo avisa **cuando el estado cambia**: un aviso que se repite deja de leerse como aviso. El aviso
también corre en la pantalla principal, no solo en caminata.

**Límite dicho de frente:** Safari en iOS **no expone la API de vibración**, así que en iPhone el
aviso es tono y voz. Por eso hay tres canales y no uno, y por eso Fuentes muestra cuáles existen de
verdad en el dispositivo que se está usando en vez de prometerlos. El tono necesita un gesto previo
del usuario para que el navegador habilite audio; el primer toque en cualquier parte sirve.

Vive de: la cámara local del navegador + `POST /api/space/observe` + `GET /api/space/now`.

**Regla dura, aprendida el 2026-09-15:** el teléfono no tiene calibración propia contra este suelo, y
proyectar su frame con la homografía de la cámara fija escribe celdas que nadie observó. Mientras no
haya calibración a bordo, la caminata **observa pero no escribe en el mapa**, y lo dice en Fuentes.

Lo que sí puede afirmar sin calibración es si la franja de suelo de unos pasos adelante **sigue
pareciéndose al suelo que tiene bajo los pies** (`rangyuu/onboard.py`). Eso alcanza para **avisar**, no para frenar: medido contra
una caminata real etiquetada el 2026-09-16, acierta el **22 %** de las veces que dice "obstáculo".
Por eso `OBSTACLE` y `UNCERTAIN` bajan la pantalla a `CUIDADO` y **nunca a `PARA`**: detener a una
persona catorce veces por minuto sin motivo es peor que no avisar. **Nunca autoriza por sí solo.** La lectura cruda parpadea varias veces por segundo, así que se
suaviza con histéresis asimétrica: empeorar es inmediato, volver a despejado exige acuerdo y 1,2 s.

### 2.3 Sistema — honestidad y configuración

Una fila por fuente, con su verdad incómoda a la vista:

- Ring conectado o sin señal, con la hora de la última observación.
- iPhone activo o inactivo.
- Calibración válida o **requiere recalibración**, con el error medido en centímetros.
- Cobertura: qué parte del espacio está siendo observada ahora mismo.

Esta pantalla existe para comunicar límites, no capacidades. El flujo infrecuente de calibración,
tamaño de celda y ruta de prueba vive plegado aquí; no ocupa una pestaña de uso diario.

Vive de: `GET /api/sources`, `POST /api/space/calibrate` y `POST /api/space/route`.

## 3. Identidad visual

**Decisión escogida el 2026-09-15: se adopta el lenguaje visual de la app de Ring**, para que
integrarla del lado de ellos sea trivial y para que un usuario de Ring no tenga que aprender nada
nuevo. De ahí salen el fondo claro, las tarjetas blancas con secciones agrupadas, el azul de acción,
el verde de *Conectado* y la navegación inferior.

**Lo que no se copia es el centro.** Donde Ring pone una cuadrícula de cámaras y una línea de tiempo
de clips, Rangyuu pone el mapa y la decisión. Los colores de estado siguen siendo **semánticos**, uno
por estado y ninguno más: el rojo aparece solo en `PARA`, y `SIN CERTEZA` no es rojo, porque no es una
alarma sino una ausencia.

## 4. Dónde corre

**Aplicación web servida por el propio proceso de Rangyuu**, no app nativa. El motivo está medido y
escrito en `docs/test-rig.md`: la compilación nativa de iOS exige un Mac, y aquí no hay uno. Safari en
iOS da cámara por `getUserMedia`, vibración limitada y voz, que es lo que la pantalla de caminata
necesita.

**Consecuencia asumida:** la cámara del navegador exige **HTTPS** salvo en `localhost`, así que el
modo caminata en el teléfono necesita un certificado o un túnel. Queda anotado como riesgo de B11.
