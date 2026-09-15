<!-- docs/perception.md: la tesis de percepción del proyecto — usar cámaras Ring como capa de
     sensado previa a un LIDAR. Qué da la API de verdad (verificado contra el sample oficial), qué
     no da, el puente geométrico que sí cabe en cinco semanas, y dónde se rompe.
     Las mediciones que faltan están listadas en §7 y atadas al bloque B3 de docs/plan.md. -->

# Percepción con cámaras Ring — el sensor que ya está instalado

**Decisión escogida, 2026-09-14:** el eje del proyecto es usar las cámaras Ring como **capa de
percepción de infraestructura**, el escalón anterior a instalar LIDAR.

## 1. La distinción que sostiene todo

Hay dos maneras de que una máquina sepa dónde está lo que la rodea:

| | **A bordo** | **De infraestructura** |
|---|---|---|
| Dónde vive el sensor | En el vehículo | Fijo en el sitio |
| Qué resuelve | Navegación, evasión a velocidad | Contexto previo: qué hay, dónde, desde cuándo |
| Sensor típico | LIDAR, radar, cámaras estéreo, IMU | Cámaras fijas calibradas |
| Latencia tolerable | Milisegundos | Cientos de milisegundos |

**Ring no puede ser el ojo del vehículo.** Es fijo, monocular, con latencia de red y sin sincronía
con nada. Pero es el sensor de infraestructura **que ya está instalado y apuntando a la entrada, al
garaje y al patio** — en millones de casas y negocios, comprado y montado por otra razón. Esa es la
tesis: no compites con el LIDAR, ocupas el escalón que va antes, donde el costo marginal de sensar
es cero porque el hardware ya está ahí.

Dicho como producto: **el vehículo todavía no ve, pero el sitio sí.**

## 2. Lo que la API da de verdad

Verificado leyendo `AmazonAppDev/ring-api-helloworld` (MIT), no de la documentación:

- **Video en vivo real por WHEP.** `POST /v1/devices/{id}/media/streaming/whep/sessions` con un SDP
  offer; devuelve el SDP answer y una `Location` de sesión que se cierra con `DELETE`. Es WebRTC
  estándar: los frames llegan a un `<video>` del navegador.
- **Frames procesables, cuadro por cuadro.** El sample trae un sistema de plugins cuya interfaz es
  `process(frame: ImageData, canvas, video) → { boundingBoxes, data }`. Es decir: **acceso a píxeles
  crudos y overlay sobre el video**, con ejemplos que ya corren (heatmap de movimiento, MediaPipe
  para manos). El camino de visión por computador está abierto y demostrado.
- **Detecciones que no tienes que construir.** Los webhooks traen `person_detected`,
  `motion_detected`, y el Playground simula **Package, Vehicle y Motion**. El payload incluye
  `confidence`, `bounding_box` y `thumbnail_url`.
- **Geometría declarada por el dueño.** `/v1/devices/{id}/configurations` expone **zonas de
  movimiento y zonas de privacidad** — información espacial que alguien ya dibujó a mano.

## 3. Lo que NO da, y hay que decirlo antes de escribir código

1. **Sin profundidad.** Una cámara monocular fija. No hay rango, no hay nube de puntos.
2. **Sin parámetros intrínsecos publicados** —confirmado contra la API el 2026-09-15, no ya un
   supuesto—. Sin ellos hay que calibrar a mano.
3. **Sin sincronía ni IMU.** No hay reloj común entre cámaras ni entre cámara y vehículo.
4. **Latencia de red.** WebRTC sobre internet: cientos de milisegundos, variables. Sirve para
   "hay alguien en la rampa, no salgas"; **no** para evadir un obstáculo en movimiento.
5. **Streaming bajo demanda.** Es una sesión que se abre y se cierra, no un feed perpetuo; los
   dispositivos a batería lo limitan aún más. La percepción continua 24/7 probablemente no existe.
6. **`/location` es país y estado, para cumplimiento** — no son coordenadas. **La pose de cada
   cámara la pones tú.**
7. **No hay API para mover nada.** Ring sensa; el actuador lo pones tú.

## 4. El puente geométrico que sí cabe en cinco semanas

De píxeles a metros, sin profundidad, hay un camino clásico y honesto: **homografía al plano del
suelo**.

1. Se miden con cinta métrica cuatro puntos del piso visibles en la imagen (esquinas del garaje, dos
   marcas en la rampa).
2. Esas cuatro correspondencias píxel ↔ metro definen una homografía 3×3.
3. Cualquier objeto **que toque el suelo** se ubica por el **punto medio del borde inferior de su
   bounding box**: ese píxel, pasado por la homografía, da su posición métrica en el plano.
4. Con eso se llena una **rejilla de ocupación 2D** del sitio: libre, ocupado, desconocido.
5. Con varias cámaras, cada una con su homografía al mismo marco del sitio, la ocupación se fusiona.

Es LIDAR de pobre, limitado al plano del suelo — y para "¿está libre la entrada?" alcanza de sobra.
El `bounding_box` que ya viene en los eventos alimenta el paso 3 **sin procesar un solo píxel**; el
video queda para lo que el evento no cubre.

## 5. Dónde se rompe (escribirlo en la UI, no esconderlo)

- **Lo que no toca el suelo** rompe el supuesto: una rama, un objeto colgante, alguien en una
  escalera. La homografía los proyecta lejísimos.
- **El error crece con la distancia.** Los píxeles por metro caen; a 15 m un píxel vale decenas de
  centímetros. La rejilla necesita **incertidumbre por celda**, no un booleano.
- **Oclusión.** Un carro parqueado tapa media rampa y esa zona pasa a *desconocido*, que no es
  *libre*. La distinción es la diferencia entre un sistema honesto y uno peligroso.
- **Noche, lluvia, contraluz, lente sucio.** La confianza cae y hay que notarlo.
- **Cámara movida.** Si alguien la reorienta, la homografía queda inválida y todo el mapa miente en
  silencio. Hace falta detectar la deriva contra puntos fijos de referencia.
- **Cámara offline** (`device_offline`) o sesión caída: cobertura perdida.

## 6. La consecuencia de diseño: percepción propone, política dispone

Todo lo de §5 lleva al mismo sitio: **un sistema que se mueve no puede confiar en un sensor que no
controla.** Por eso la arquitectura se parte en dos y el motor de políticas vuelve a ser el centro:

```text
Ring (eventos + frames)  →  capa de percepción  →  ocupación + confianza + cobertura
                                                          ↓
                                              motor de políticas (el cerrojo)
                                                          ↓
                                        avanzar · esperar · detenerse · pedir a un humano
```

**Contrato de degradación**, explícito y probado con tests:

| Estado | Acción segura |
|---|---|
| Cobertura completa, confianza alta, zona libre | Avanzar |
| Celda *desconocida* en la trayectoria | Esperar, no avanzar |
| Confianza baja (noche, lluvia) | Velocidad reducida o esperar |
| Cámara offline, sesión caída o homografía derivada | **Detener y avisar** |
| El evento contradice el frame | Gana el más restrictivo |

"Desconocido" nunca se trata como "libre". Esa sola regla es la diferencia entre una demo bonita y
algo que alguien podría encender.

## 7. Lo que hay que medir antes de comprometerse (→ B3)

Ninguna de estas cifras está en la documentación pública, y todas cambian el diseño:

- **Resolución y fps reales** del stream WHEP. Define el tamaño mínimo detectable a X metros.
- **Latencia glass-to-glass.** Define a qué velocidad puede moverse lo que gobiernas.
- **Duración máxima de sesión** y si se puede reabrir sin fricción.
- **Cuántas sesiones simultáneas** permite una cuenta — decide si el multi-cámara de §4 es viable.
- **Si el live view simulado del Playground entrega video sintético o un clip enlatado.** **Es la
  medición que más pesa:** si es enlatado, la calibración contra él no es real y el demo necesita un
  dispositivo físico o un clip propio grabado. Todo §4 depende de esto.
- ~~Si los intrínsecos de la cámara se exponen en `/capabilities`~~ — **medido el 2026-09-15: no se
  exponen.** `/capabilities` da códecs (`AVC`), relación `16:9`, `max_resolution: 1080` y las
  configuraciones de `motion_zones` y `privacy_zones`; ni distancia focal ni distorsión. La
  calibración es manual por homografía, como se asumió. Evidencia en
  [verificacion.md](verificacion.md).

## 8. Por qué esto no se tira cuando llegue el LIDAR

La capa de percepción se define **por interfaz**, no por sensor: entrega ocupación, confianza y
cobertura en el marco del sitio. Ring es la primera implementación de ese puerto; un LIDAR es otra;
una fusión de ambas es una tercera. El mismo patrón de puertos con implementación intercambiable que
ya se usó en `creva-zk` para las pruebas.

Eso es lo que hace honesta la frase "el hardware anterior al LIDAR": solo es cierta si el software
sobrevive al cambio de sensor. Si hay que reescribirlo, no era un escalón — era un desvío.
