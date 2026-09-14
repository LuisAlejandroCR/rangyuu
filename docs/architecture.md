<!-- docs/architecture.md: dónde corre cada cosa y qué pasa cuando se cae la red. Define los tres
     carriles (crítico local, contexto de nube, asíncrono de nube), el presupuesto de latencia por
     tramo y el modo sin nube. La decisión de inferencia local está en §1; la contradicción que esa
     decisión tiene que enfrentar, en §2 — no se esconde, se acota. -->

# Arquitectura — dónde corre cada cosa

**Decisión escogida, 2026-09-14:** la inferencia corre **local**. La nube queda para GPS,
mensajería, alertas y todo lo que no exija un accionar inmediato.

**La regla, en una línea: nada en el camino crítico espera a la red.**

## 1. Qué significa "local" aquí, con precisión

Tres propiedades distintas que conviene no confundir:

| Propiedad | ¿Se cumple? |
|---|---|
| **Ningún frame sale hacia un tercero de inferencia** | Sí. Es una decisión de diseño y se sostiene |
| **Ninguna decisión espera una respuesta remota** | Sí. El lazo de control vive en el sitio |
| **El sensor no depende de la nube** | **No.** Ver §2 |

## 2. La contradicción, dicha de frente

**El frame de Ring ya viajó por la nube de Amazon antes de llegarte.** La sesión de live view se
negocia contra `api.amazonvision.com` y los webhooks los entrega el backend de Ring por internet. Un
dispositivo Ring no expone RTSP ni ONVIF local (confirmar en B1), así que **no hay forma de leer esa
cámara sin pasar por su nube**.

Entonces "el hardware no depende de la nube" no puede afirmarse del sensado de Ring. Lo que sí se
sostiene, y es lo que hay que decir:

> Las imágenes no se mandan a ningún tercero a inferir, y **ninguna decisión espera a la red**.
> Ring es una entrada **degradable**: cuando está, enriquece; cuando no está, el sistema sigue y se
> pone conservador.

Eso no debilita la tesis del escalón previo al LIDAR — **la refuerza**. Precisamente porque el carril
de Ring puede desaparecer, el lazo crítico se diseña desde el día uno para no depender de él; y ese
es exactamente el lazo en el que después entra el LIDAR, por el mismo puerto.

## 3. Los tres carriles

| | **Crítico** | **Contexto** | **Asíncrono** |
|---|---|---|---|
| Dónde corre | En el sitio (LAN) | Nube de Ring | Nube |
| Presupuesto | Milisegundos | Cientos de ms, best-effort | Segundos a minutos |
| Qué lleva | Mapa de ocupación, contrato de degradación, motor de políticas, actuación | Eventos y frames de Ring, inferencia local sobre ellos | GPS, mensajería, alertas, bitácora, dashboard, actualización de modelos |
| Si se cae | **No se cae: es lo que queda** | Cobertura perdida → todo *desconocido* | Se encola y se reintenta. No bloquea nada |

**Dos reglas duras que salen de la tabla:**

1. **El carril de contexto nunca autoriza por sí solo.** Puede aportar a la decisión; su ausencia
   siempre se lee como *desconocido*, nunca como *libre*.
2. **El carril asíncrono no tiene voto.** Si una alerta no sale, el vehículo no cambia de
   comportamiento. Si hiciera falta esperar el acuse de una alerta, esa alerta pertenece al carril
   crítico y hay que moverla al sitio.

## 4. Qué implica en hardware

- Un equipo en el sitio: mini PC, Jetson Orin Nano o Raspberry Pi 5 con acelerador. Ahí viven la
  inferencia, el mapa, el cerrojo y la caducidad.
- Modelo exportado (ONNX o equivalente) corriendo local. El navegador del sample oficial ya es
  inferencia local por construcción —`process(frame: ImageData, …)` corre en el cliente— y sirve para
  el demo; el runtime de producción es un proceso propio.
- Del equipo al vehículo: LAN. MQTT o WebSocket, sin salir a internet.
- **Pendiente de probar (B10):** consumir WHEP desde un proceso que no sea el navegador. WHEP es
  WebRTC con señalización HTTP; en Python `aiortc` puede sostener la sesión, pero el `POST` del SDP
  offer y el manejo de la `Location` hay que escribirlos. No está hecho y no se sabe cuánto cuesta.

## 5. Presupuesto de latencia, por tramo

De estos seis tramos **solo controlas los últimos cuatro**. Medir cada uno en B3 y B10:

```text
cámara → nube de Ring        no controlado
nube de Ring → tu LAN        no controlado, variable
decodificación del frame     controlado
inferencia local             controlado  ← lo que la nube te cobraría en ida y vuelta
decisión (mapa + política)   controlado
actuación por LAN            controlado
```

El argumento de la inferencia local es este: los dos primeros tramos ya se pagaron y no se pueden
evitar; mandar el frame **otra vez** a inferir en la nube pagaría un tercer tramo evitable, encima
del que ya costó. Local no solo es más privado — es el único tramo que se puede recortar.

## 6. Modo sin nube

Si cae internet, **Ring desaparece por completo**: sin eventos y sin video. Lo que queda:

- La última ocupación conocida, **envejeciendo**.
- Los sensores locales del vehículo, si existen.
- El contrato de degradación.

**Caducidad de la ocupación:** cada celda lleva la marca de tiempo de su última observación. Pasada
la ventana declarada, la celda vuelve a *desconocido* — nunca se queda *libre* por inercia. La
ventana se escoge y se escribe; no se deja implícita.

Y la regla que cierra todo: **el sistema arranca en el estado seguro, no en el permisivo.** Al
encender, sin observaciones, todo es desconocido.

## 7. Qué gana el hackathon con esta separación

El mini challenge de **AWS Builder** pide servicios AWS con integraciones documentadas — y encaja
entero en el carril asíncrono, sin meter la nube en el lazo de control: redactar la alerta, entrenar
o exportar el modelo que después corre local, transportar la mensajería. Es un argumento fuerte
frente a jueces de AWS: **la nube donde corresponde, y no donde no.** Un sistema que pone el lazo de
seguridad en la nube es peor ingeniería, aunque use más servicios.
