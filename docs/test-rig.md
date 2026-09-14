# Montaje de pruebas sin hardware dedicado

## Configuración recomendada

- **iPhone con USB-C → portátil:** transferir videos MP4, cargar el teléfono y copiar capturas de la
  app. Es el camino base y reproducible.
- **iPhone USB-C → adaptador HDMI → capturadora USB (UVC) → portátil:** mostrar la pantalla o cámara
  en vivo durante una grabación de demo. La capturadora aparece como webcam estándar.
- **iPhone USB-C → Mac con Xcode:** depuración nativa y ejecución directa de una app iOS. Es necesario
  un Mac para el flujo Xcode; USB-C por sí solo no permite depurar una app nativa desde Windows.

## Orden de implementación

1. MP4 grabado del iPhone como fixture en `fixtures/iphone/`.
2. App iOS en primer plano con cámara local y procesamiento Core ML/Vision.
3. Captura HDMI únicamente si mejora la grabación de la demo.
4. WebRTC desde Safari como extensión, no como dependencia de la entrega.

El iPhone es `IPHONE_ONBOARD`; nunca reemplaza la llamada real al Ring Playground. Rangyuu debe seguir
funcionando con fixtures cuando no haya cable, capturadora o dispositivo físico.
