<!-- docs/app.md: la aplicación — qué pantallas tiene, qué muestra cada una y de qué dato vive.
     Es la especificación de producto y de interfaz; el estado de los bloques está en docs/plan.md
     y lo que se hizo, en docs/memoria.md. No repite la arquitectura de carriles, que vive en
     docs/architecture.md. -->

# La app

**Decidido el 2026-09-15.** Cinco pantallas principales y una sexta opcional. Ring ya cubre alertas,
Live View, conversación, historial y control de dispositivos: su app responde *qué está pasando en
casa*. Rangyuu responde otra pregunta, y por eso no se parece.

```text
Ring:      eventos → cámara → alerta
Rangyuu:   observaciones → mapa → decisión segura → movimiento
```

**El momento memorable de la demo es la app diciendo "no sé" y frenando a alguien**, en vez de fingir
una certeza que no tiene. Todo lo demás está subordinado a eso.

## 0. Qué no se copia

- Sin cuadrícula de cámaras. Sin línea de tiempo de clips. Sin rojo permanente de alarma.
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
celdas ocupadas y las desconocidas, distinguidas entre sí. Una línea de razón. Nada más.

Vive de: `GET /api/space/now` — estado, razón, trayectoria, celdas por estado, edad de la observación.

### 2.2 Modo caminata — la experiencia humana

La cámara del iPhone como sensor a bordo. **No es una app de grabación:** no hay botón de grabar, ni
galería, ni vista previa grande. Indicador de dirección, nivel de confianza, aviso háptico o por voz,
y un botón de parar que ocupa el pulgar.

Es también la pantalla de accesibilidad: el estado se anuncia por voz y se siente por vibración, sin
mirar la pantalla.

Vive de: la cámara local del navegador + `POST /api/space/observe` + `GET /api/space/now`.

### 2.3 Espacio — el mapa del sitio

Mapa de ocupación con zonas nombradas: entrada, pasillo, garaje, puerta, zonas de riesgo. Se ve qué
aporta Ring —contexto fijo, de infraestructura— y qué aporta el iPhone —contexto cercano, a bordo—.
**Sin video.** Al tocar una celda se abre su evidencia, y solo ahí puede aparecer una imagen.

Vive de: `GET /api/space/map`.

### 2.4 Fuentes — la honestidad del sistema

Una fila por fuente, con su verdad incómoda a la vista:

- Ring conectado o sin señal, con la hora de la última observación.
- iPhone activo o inactivo.
- Calibración válida o **requiere recalibración**, con el error medido en centímetros.
- Cobertura: qué parte del espacio está siendo observada ahora mismo.

Esta pantalla existe para comunicar límites, no capacidades.

Vive de: `GET /api/sources`.

### 2.5 Configurar espacio — la pantalla "pro"

Flujo de calibración: marcar cuatro puntos del suelo sobre una foto, escribir sus medidas reales,
nombrar zonas, elegir el tamaño de celda y probar una ruta. Muestra el error resultante en
centímetros antes de guardar; si el error supera el techo declarado, no deja guardar en silencio.

Vive de: `POST /api/space/calibrate`.

### 2.6 Evidencia — opcional

Historial corto de **decisiones**, no de videos: qué sensor produjo el dato, cuándo, qué celda afectó
y por qué el sistema decidió detenerse. Una fila por decisión, la más reciente arriba.

Vive de: `GET /api/decisions`.

## 3. Identidad visual

Navegación espacial tranquila, no alarma doméstica. Mapa sobrio, mucho espacio negativo, tipografía
grande para el estado. Colores **semánticos**, nunca decorativos: uno por estado, y ninguno más.
El rojo aparece solo en `PARA`; `SIN CERTEZA` no es rojo, porque no es una alarma: es una ausencia.

## 4. Dónde corre

**Aplicación web servida por el propio proceso de Rangyuu**, no app nativa. El motivo está medido y
escrito en `docs/test-rig.md`: la compilación nativa de iOS exige un Mac, y aquí no hay uno. Safari en
iOS da cámara por `getUserMedia`, vibración limitada y voz, que es lo que la pantalla de caminata
necesita.

**Consecuencia asumida:** la cámara del navegador exige **HTTPS** salvo en `localhost`, así que el
modo caminata en el teléfono necesita un certificado o un túnel. Queda anotado como riesgo de B11.
