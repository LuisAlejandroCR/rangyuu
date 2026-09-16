<!-- README.md (mobile): cómo correr el cliente Expo en un iPhone con Expo Go.
     Contiene los pasos de ejecución y la matriz de versiones del SDK 57.
     Se distingue de docs/mobile.md, que explica qué es la app, qué deliberadamente no hace
     y qué quedó sin verificar; acá solo están los comandos. -->

# rangyuu mobile

A thin Expo client. It captures frames from the on-board camera, posts them to the Python
backend, and shows the decision that comes back. It decides nothing on its own.

**Expo SDK 57** (`expo@~57.0.23`). Runs in **Expo Go** — no Mac, no Apple developer account.

## Run it

1. Start the backend on the machine that will serve the app:

   ```
   python -m rangyuu.serve        # listens on 0.0.0.0:8080
   ```

2. Install and start the client:

   ```
   cd mobile
   npm install
   npm start
   ```

3. Scan the QR with the Camera app on the iPhone and open it in Expo Go. The phone and the
   computer must be on the same network.

By default the app talks to the same host that served the bundle, on port 8080 — in
development that is the machine running Python, so nothing needs configuring. If the backend
lives elsewhere, copy `.env.example` to `.env.local` and set `EXPO_PUBLIC_RANGYUU_API`.

## What it calls

Two routes, both already in the backend — this app added none:

| Route | Where it is defined | Used for |
| --- | --- | --- |
| `POST /api/space/observe` | `rangyuu/webapp.py:104`, body validated at `rangyuu/webapp.py:136` | one 64x36 grayscale frame; answers with `clearance` and a full `now` |
| `GET /api/health` | `rangyuu/webapp.py:67` | telling "backend down" apart from "camera down" |

The `gray` payload is the same shape the web app sends (`web/app.js:257`): `width`, `height`
and a flat array of `width * height` luminance samples, capped at 65 536 by the backend.

## Checks

```
npm run typecheck    # tsc --noEmit, strict
npm run bundle       # expo export --platform ios
npx expo install --check
```

## Not verified

Nothing here has run on a physical iPhone — see `docs/mobile.md` for the full list of what
is proven and what is still `⏳ pendiente`.
