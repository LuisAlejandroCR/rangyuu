# Video de demo — Rangyuu

## Herramienta escogida

**ElevenLabs MCP** se usará únicamente para producir la narración, audio y, si resulta útil, recursos
del video de demostración. No forma parte del runtime de Rangyuu ni del motor de riesgo. El producto
debe funcionar sin ElevenLabs.

La integración oficial es el MCP alojado en `https://api.elevenlabs.io/v1/mcp`, con autenticación OAuth;
no se debe guardar una API key en este repositorio. El MCP puede gestionar agentes y generar voz,
música, imágenes y video desde un asistente. Fuente: https://elevenlabs.io/mcp (consultada 2026-09-14).

## Guion objetivo (menos de tres minutos)

1. **0:00–0:15 — Problema:** la cámara a bordo no ve todo el espacio.
2. **0:15–0:35 — Idea:** Ring aporta contexto desde la infraestructura; Rangyuu lo convierte en un
   mapa espacial abierto.
3. **0:35–1:20 — Flujo:** iPhone/rover digital, observación Ring, mapa, consulta `can-traverse()`.
4. **1:20–2:15 — Tres estados:** `PROCEED`, `CUIDADO/PRECAUCIÓN`, `PARA` y `UNKNOWN` cuando la
   evidencia es insuficiente o vencida.
5. **2:15–2:45 — Privacidad:** inferencia local, mínima retención y proveedores intercambiables.
6. **2:45–3:00 — Cierre:** “The iPhone sees where you are going. Ring helps Rangyuu understand
   what you cannot see.”

El video debe estar en inglés, ser público y no usar música, marcas o material de terceros sin permiso.
ElevenLabs se consignará en el feedback de herramientas de la submission, incluyendo qué funcionó,
qué limitaciones tuvo y si se volvería a utilizar.

## Criterios de edición

- Mostrar código o UI que invoque Ring; no basta con mencionarlo en la narración.
- Etiquetar claramente `RING_INFRASTRUCTURE`, `IPHONE_ONBOARD` y `SIMULATED_ROVER`.
- No presentar el sistema como dispositivo médico ni como garantía de seguridad física.
- Conservar el proyecto editable y los archivos de audio generados en una carpeta de artefactos fuera
  del código sensible; nunca incluir credenciales.
