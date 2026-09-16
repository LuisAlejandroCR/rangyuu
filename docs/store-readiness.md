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

## 1. La decisión que bloquea a todas las demás: dónde vive el backend

Hoy la app apunta a `python -m rangyuu.serve` por LAN. **Eso no se puede publicar.** Ninguna app de
tienda puede exigirle a quien la instala que corra un proceso de Python en una máquina de su casa.
En cuanto esa laptop se suspende, quien probó desde TestFlight no ve nada.

Hay dos salidas y **no son equivalentes**:

| Salida | Qué gana | Qué cuesta |
|---|---|---|
| **Backend alojado** | Camino corto: el runtime medido de Python sigue siendo el que decide, tal cual está | **Se pierde el argumento de privacidad.** Los frames salen del dispositivo. B10 afirma *cero inferencia a terceros, probado envenenando `socket`*: alojado, esa frase deja de describir lo que se publica |
| **Inferencia a bordo** | Conserva la privacidad, que es el diferenciador más fuerte | Hay que reconstruir la detección en el dispositivo. Se pierden los **8,16 ms/frame** ya medidos en Python y hay que volver a medir desde cero |

**Lo que no se puede hacer es no decidir.** Si nadie elige, se elige alojado por inercia —es el
camino de menor fricción— y el reclamo de privacidad se queda en el material de promoción
describiendo algo que el producto ya no hace. Eso no es un detalle de marketing: es una afirmación
sin evidencia, publicada.

⏳ **Pendiente:** decidir, y anotar la decisión aquí con fecha.

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
- **App Privacy (las etiquetas de datos).** Lo que se declare ahí tiene que coincidir con la
  decisión del punto 1. Declarar "no se recolectan datos" con un backend alojado es falso.
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
| Decisión de backend (alojado vs a bordo) | ⏳ sin decidir — **bloquea el resto** |
| B11 calibración a bordo | ⏳ falta la medida de la baldosa |
| B2 vínculo de cuenta Ring | ⏳ faltan credenciales |
| Primer build de TestFlight | ⏳ sin hacer |
| Política de privacidad | ⏳ no existe |
| Etiquetas de App Privacy | ⏳ dependen del punto 1 |
