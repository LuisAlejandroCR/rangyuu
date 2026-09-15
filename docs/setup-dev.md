<!-- docs/setup-dev.md: cómo dejar el entorno corriendo y cómo entregar las credenciales de Ring.
     Es el archivo operativo: pasos ejecutables, no análisis. El análisis de la API vive en
     docs/ring-track.md y el estado de los bloques en docs/plan.md. -->

# Setup — entorno y credenciales

## 1. Entorno, sin credenciales

El núcleo corre sin red y sin tokens. Tres comandos:

```bash
python -m pytest -q
python -m rangyuu
python -m rangyuu tests/fixtures/b0_events.json
```

`python -m pytest -q` debe terminar en `43 passed`. `python -m rangyuu` reproduce el fixture por el
mismo normalizador y el mismo estado espacial que usa el receptor HTTP, e imprime un informe por
paso: `PROCEED` con la celda observada libre, `HOLD` cuando la persona la ocupa, el evento repetido
rechazado por deduplicación, y `HOLD` por `cell stale` cuando la observación caduca. Ese último paso
es la prueba de que el sistema se vuelve conservador solo, sin que nadie lo empuje.

## 2. Dónde van los secretos

`.env.local`, que está en `.gitignore`. `.env.example` se versiona y no lleva valores. El runtime lo
lee por `rangyuu/config.py`, con una regla: **una variable de entorno real siempre gana** sobre el
archivo, para que un secreto de Cloud Run no quede tapado por un `.env.local` viejo dentro de la
imagen. Los nombres que el código espera son los de `.env.example`, `RING_*`. Ningún token
entra en un commit, en un `.md`, en un comentario de código ni en un mensaje de chat pegado al repo.
Si un token se expone, se rota antes de seguir.

## 3. Credenciales de Ring — paso a paso

Hay dos caminos y **no son intercambiables**. El primero desbloquea B3; el segundo desbloquea B2 y
B5, y es trámite, así que arranca el mismo día.

### Camino A — token del Playground (rápido, caduca)

1. Entrá al Ring Developer Playground con la cuenta de Amazon Developer.
2. Generá el **access token corto** y copiá el valor.
3. Pegalo en `.env.local` como `RING_ACCESS_TOKEN=...`.
4. Anotá, en el mismo momento, **a qué hora lo generaste y cuánto dice que dura**. Esa cifra hace
   falta para `docs/verificacion.md`; sin ella no se sabe si una prueba fallida es un bug o un token
   vencido.
5. Dejá también la lista de dispositivos simulados que el Playground muestre (nombre y `device_id`).

Con eso alcanza para `GET /v1/devices` y para abrir una sesión de live view.

### Camino B — app registrada (lento, es el que sirve de verdad)

1. Registrá la app en la consola de Amazon Developer y pedí acceso a las Ring APIs.
2. Cuando emitan `client_id` y `client_secret`, pegalos en `.env.local`.
3. Completá el flujo de OAuth de account linking con tu cuenta de Ring; guardá el
   `RING_REFRESH_TOKEN` que salga.
4. Configurá la URL de webhook (`RING_WEBHOOK_URL`) y guardá el secreto de firma como
   `RING_WEBHOOK_SECRET`.

### Qué dejarme, exactamente

Con esto ya puedo trabajar:

- `.env.local` completo con las variables que tengas, aunque estén a medias.
- La **fecha y hora** de emisión del token corto y su duración declarada.
- Los `device_id` disponibles y qué tipo de evento simula cada uno.
- Si el Playground ofrece o no una sección de webhooks. Es la pregunta que decide el calendario:
  si no los hay, B5 depende enteramente de B2.

No me pegues el token en el chat: dejalo en `.env.local` y decime "listo". El repo lo lee de ahí.

## 4. Mientras no haya credenciales

El fixture de `tests/fixtures/b0_events.json` tiene la misma forma que el payload de un webhook, así
que todo el núcleo —firma, ingesta, rejilla, caducidad, contrato de salida— se desarrolla y se prueba
sin tocar la red.
Lo único que no se puede sustituir con un fixture son las seis mediciones de `docs/perception.md` §7.
