<!-- docs/store-readiness.md: qué falta para publicar rangyuu en App Store y Google Play, y la
     decisión de arquitectura que hay que tomar antes que ninguna otra. Se distingue de
     docs/app.md (la interfaz y su contrato), docs/mobile.md (cómo correr el cliente Expo) y
     docs/plan.md (los bloques del hackathon): esto es lo que cambia al salir del demo. -->

# Publicar en tiendas — lo que cambia al salir del demo

**Escrito el 2026-09-16**, cuando el cliente Expo todavía no existía en `main`. Nada de este
documento está verificado contra una tienda: es el mapa de decisiones, no evidencia. Toda fila
sigue `⏳ pendiente` hasta que alguien la ejecute.

**Regla que no cambia por publicar:** una afirmación sin evidencia repetible no entra. En una tienda
eso además deja de ser higiene interna y pasa a ser lo que se le promete a un desconocido.

## 1. Dónde vive el backend — el dilema era falso

**Corregido el 2026-09-16.** La primera versión de este documento planteaba "alojado contra a bordo"
como un lose-lose. Dos hechos del propio repo lo desarman.

**Alojar no es opcional: ya es obligatorio.** `.env.example:19` describe `RANGYUU_WEBHOOK_URL` como
*"URL pública que recibe los webhooks"*, y `docs/cloud-run.md` ya especifica el despliegue con el
secreto HMAC en Secret Manager. Ring empuja eventos a un endpoint público: no existe una versión de
B2 o B5 que viva en una laptop. El fork nunca fue "alojado o no".

**Por el cable ya viajan observaciones, no frames.** `rangyuu/ring.py:4` define
`Observation(device_id, timestamp, kind, confidence, bbox)`: cinco campos y una caja. Ni un píxel.
El camino de Ring nunca mandó video a ningún lado.

### El diseño que resuelve

- **Cloud Run** sigue haciendo lo que ya hace: recibir los webhooks de Ring, sostener el mapa
  espacial y responder `can_traverse`.
- **El teléfono corre el detector a bordo** y publica `Observation`s — la *misma forma* a la que
  `api.py` normaliza los eventos de Ring. Sin superficie de API nueva, sin contrato nuevo.
- **El video nunca sale del dispositivo.** Solo salen cajas.

**El reclamo de privacidad sobrevive literal, no aproximado.** B10 afirma *cero inferencia a
terceros*, probado envenenando `socket`. Con este diseño la inferencia sigue siendo local —en el
teléfono en vez de la laptop— y lo que cruza el cable es entrada aritmética, no percepción. La
frase se puede seguir diciendo y sigue siendo cierta.

**Lo que cuesta:** portar el detector a `onnxruntime-react-native` —el mismo SSD MobileNet ya medido
en 24 ms/frame en Python— y **volver a medirlo en un teléfono**, porque ese número no se hereda.

**Secuencia:** LAN para el hackathon, que demuestra bien y no cuesta nada. El port a bordo después
del 10/23, como primera tarea del proyecto de publicación.

⏳ **Pendiente:** el port a bordo y su medición en teléfono.

## 1.b El producto real es pasivo: freno de emergencia, no asistente

**Anotado el 2026-09-16.** La app es la superficie de demostración. En uso real rangyuu es
tecnología pasiva: corre de fondo y **actúa**, no pregunta. El modelo es el freno de emergencia —si
hay obstáculo, frena; no pide permiso.

**La buena noticia: el núcleo ya está diseñado así.** `policy.py:34` devuelve `HOLD` salvo que se
cumpla *todo* —cobertura, sesión, homografía válida, celda libre, sin `unknown`, sin `stale`, sin
contradicción—. La ausencia de evidencia positiva es una negativa, no una duda. Feed cortado →
`HOLD` por `feed stale`. Calibración sin medir → `HOLD`. Eso **es** semántica de freno: seguro por
defecto, y `authorizes` solo se enciende cuando algo se lo ganó.

Que el vehículo consulte `POST /api/rover/can-traverse` (plan, línea 134) en un lazo no contradice
el modelo pasivo: es cómo se implementa. Quien decide frenar es la respuesta, no una persona
mirando una pantalla.

**La mala noticia, y es la que manda:** *actuar* exige una precisión que hoy no existe. Esto ya se
intentó. Lección 5, textual: el carril a bordo se cableó a `PARA`, resultó **22 %** preciso —catorce
frenadas falsas por minuto— y se degradó a aviso. **"Frenar hay que ganárselo."**

En un vehículo de movilidad el error es peligroso en las dos direcciones: un falso negativo no
frena ante un obstáculo real; un falso positivo frena solo y puede lanzar hacia adelante a quien
viaja. Un freno automático no tolera 13-20 % de acierto en ninguna de las dos.

**Conclusión:** el destino pasivo es correcto y el núcleo ya lo soporta. Lo que falta no es
arquitectura, es **B11**: sin calibración a bordo no hay distancia, sin distancia no hay obstrucción,
y sin obstrucción medida frenar automáticamente sería inventar una certeza que no se tiene.

⏳ **Pendiente:** B11, y una medición de precisión que justifique pasar de avisar a actuar.

## 2. La puerta técnica: B11

Sin calibración a bordo no hay distancia, y sin distancia **no se puede decidir si un objeto
obstruye**. Por eso hoy el carril a bordo avisa pero no frena.

Los números que hay, medidos, no los de un folleto:

- Heurística de texturas: **22 %** de acierto, 140 frenadas falsas en 58 s.
- Detector ONNX local: **13-20 %** de acierto en sus avisos. Encuentra objetos que sí están; lo que
  no puede es ubicarlos.
- Por eso el carril se degradó de `PARA` a `CUIDADO` (Lección 5).

**Publicar con esos números es distinto que demostrar con ellos.** Un jurado entiende un prototipo
medido y honesto; alguien que instala desde una tienda entiende lo que dice la ficha. Una app que
le dice a un vehículo de movilidad si un trayecto es transitable es adyacente a seguridad, y la
revisión de Apple trata con cuidado lo asistivo. **La ficha no puede prometer detección de
obstáculos mientras el acierto siga en 13-20 %.**

B11 es lo que convierte esto de demo en producto publicable. Es una puerta, no una tarea más.

## 3. El camino de distribución

La cuenta de Apple Developer ya existe, así que esta parte es trámite y no incógnita.

1. **EAS Build** compila iOS en la nube: no hace falta un Mac.
2. **TestFlight** distribuye a dispositivos reales — 100 probadores internos sin revisión, hasta
   10 000 externos con una revisión ligera en la primera subida. Esta es la respuesta a "conseguir
   gente que pruebe la app": no se busca una plataforma, se los invita a un build.
3. **EAS Submit** sube a App Store Connect.
4. Google Play: alta única de 25 USD, aparte.

**Hacer un build de TestFlight antes del 10/23, no después.** El primero siempre sorprende:
identificador de bundle, aprovisionamiento, entitlements, cadenas de privacidad en `Info.plist`.
Descubrirlo en semana uno no es nada; descubrirlo el 22/10 sí.

## 4. Lo que la tienda va a pedir y hoy no existe

- **Política de privacidad publicada.** Obligatoria: la app usa cámara y datos de una cuenta Ring.
- **App Privacy (las etiquetas de datos).** Tienen que describir lo que de verdad cruza el cable.
  Con el diseño del punto 1 el video no sale del dispositivo, pero las observaciones —caja,
  confianza, marca de tiempo, identificador de dispositivo— **sí**. "No se recolectan datos" sería
  falso; lo cierto y defendible es "no sale video".
- **Cadenas de uso en `Info.plist`**: cámara como mínimo, y las que sume el cliente Expo.
- **Capturas de pantalla** por tamaño de dispositivo.
- **Cuenta de demostración o video** para revisión, porque la app no se puede evaluar sin una fuente
  de datos: el revisor no tiene una cámara Ring.
- **Vínculo con Ring**: falta B2 —`client_id`, `client_secret` y `RANGYUU_TOKEN_URL`—. Sin eso nadie
  que instale desde la tienda puede conectar su propia cámara.

⏳ Ninguno de estos seis está hecho.

## 5. Qué NO hacer antes del 10/23

Nada de esto mejora la entrega del hackathon. App Store Connect, capturas, fichas y política de
privacidad **no suman un punto** y compiten directamente con B11, B7 y el video.

El orden sano: entregar el hackathon, después tratar la publicación como un proyecto aparte que
**arranca por la decisión del punto 1**, no por el trámite.

## 6. Estado

| Ítem | Estado |
|---|---|
| Cuenta Apple Developer | ✅ existe |
| Diseño de backend | ✅ resuelto: Cloud Run + detección a bordo, solo observaciones por el cable |
| Port del detector a `onnxruntime-react-native` | ⏳ sin hacer, y sin medir en teléfono |
| Actuación pasiva (freno automático) | ⏳ bloqueada por B11 y por la precisión |
| B11 calibración a bordo | ⏳ falta la medida de la baldosa |
| B2 vínculo de cuenta Ring | ⏳ faltan credenciales |
| Primer build de TestFlight | ⏳ sin hacer |
| Política de privacidad | ⏳ no existe |
| Etiquetas de App Privacy | ⏳ dependen del punto 1 |
