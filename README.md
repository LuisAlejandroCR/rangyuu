<!-- README.md: portada pública del repo, en inglés, para el jurado de la pista Ring.
     Dice qué hace el código, dónde se usa Ring (permalinks), cómo correrlo desde un clon limpio y
     qué sigue sin verificar. No es el checklist (docs/plan.md) ni la evidencia fechada
     (docs/verificacion.md) ni la bitácora (docs/memoria.md), que siguen en castellano. -->

# rangyuu

**A safe-by-default spatial layer for assisted mobility.** Rangyuu turns Ring camera observations
into a floor-plane occupancy map with confidence and expiry, and answers one question for anything
that moves: *can I traverse this path right now?*

The answer is always one of three:

| Decision | Meaning | Authorizes transit |
|---|---|---|
| `PROCEED` | Every cell on the path was observed free, recently, by a calibrated camera | **yes — the only one** |
| `HOLD` | The path is occupied or contradicted, or a precondition fails: no coverage, no valid calibration, a cell never observed or already expired | no |
| `UNKNOWN` | Cells were observed but confidence is missing or below 0.5, or the live feed went silent (`feed stale`) | no |

Absence of evidence is never a yes. Cut the feed and the answer drops from `PROCEED` to `UNKNOWN`
(`feed stale`) without anything else changing.

Built for **Build, Ship, Shape: Amazon Developer Hackathon 2026 — Ring track**. Priority category:
**accessibility** (assisted mobility: a wheelchair, a mobility scooter or a robot crossing a space
its own camera cannot fully see). The visible consumer in the demo is a digital rover; no physical
hardware is required.

## Where Ring is used

Ring is the infrastructure sensor. Remove it and the map has no evidence, so every answer is
`HOLD`/`UNKNOWN`. Permalinks point at the exact lines:

| What | Where |
|---|---|
| Ring REST client: Playground access token or refresh-token exchange, HTTPS-only | [`rangyuu/ring_client.py` L61–L99](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/ring_client.py#L61-L99) |
| Device discovery: `/v1/devices`, `/status`, `/capabilities`, `/location`, `/v1/users/me` (JSON:API unwrapped) | [`rangyuu/ring_client.py` L103–L117](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/ring_client.py#L103-L117) |
| WHEP live view signaling from Python, no browser: `POST` SDP offer, `DELETE` to close | [`rangyuu/whep.py` L12–L60](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/whep.py#L12-L60) |
| H264 media received and decoded outside the browser (`aiortc`) | [`rangyuu/live.py` L38–L84](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/live.py#L38-L84) |
| Webhook HMAC-SHA256 over the raw body bytes, constant-time compare | [`rangyuu/ring.py` L6–L11](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/ring.py#L6-L11) |
| Signature checked **before** JSON is parsed, with a body size cap | [`rangyuu/api.py` L56–L67](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/api.py#L56-L67) |
| Ring event (`confidence`, `bounding_box`) → observation → floor cell through a homography | [`rangyuu/ring.py` L12–L18](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/ring.py#L12-L18), [`rangyuu/spatial.py` L26–L44](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/spatial.py#L26-L44) |
| The decision contract: `PROCEED` only when everything holds | [`rangyuu/policy.py` L33–L36](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/policy.py#L33-L36) |
| `POST /api/rover/can-traverse`: `authorizes` is true only for `PROCEED` | [`rangyuu/api.py` L89–L94](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/api.py#L89-L94) |
| An unmeasured calibration observes but never authorizes | [`rangyuu/site.py` L253–L275](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/site.py#L253-L275) |

## Where AWS is used: Amazon Bedrock, outside the control loop

[`rangyuu/briefing.py`](rangyuu/briefing.py) calls the **Amazon Bedrock Converse API**
(`bedrock-runtime`, boto3) to turn a decision the core already made into one or two plain sentences
for the supervising caregiver, in English or Spanish. The cloud belongs where it helps, not where it
could hurt:

- **It never decides.** `decision` and `authorizes` are copied from the core; the model only writes
  words.
- **It can't say "go" on a stop.** On `HOLD` or `UNKNOWN`, a reply containing a permission word
  (`proceed`, `clear`, `safe to`, `avanza`, …) is rejected and the fixed template is used instead.
- **It fails closed and stays fast.** Timeouts of 3 s connect / 10 s read, `maxTokens` 120, two
  retries; any error, empty or over-long reply falls back to the template. Unset
  `RANGYUU_BEDROCK_MODEL` and no network call is made at all.

```sh
pip install -e ".[bedrock]"
aws login                                   # or any standard AWS credential source
RANGYUU_BEDROCK_MODEL=<model or inference profile id> python -m rangyuu.briefing   # add --es for Spanish
```

Tests use a stub client and need no AWS account: `tests/test_briefing.py`.

## Quickstart from a clean clone

Requires Python 3.11+. No Ring credentials and no hardware are needed for the steps below.

```sh
git clone https://github.com/LuisAlejandroCR/rangyuu.git
cd rangyuu
python -m pip install -e . pytest
python -m pytest -q          # 174 passed, 4 skipped
python -m rangyuu            # terminal demo: free -> occupied -> duplicate rejected -> expired
python -m rangyuu.serve      # the app at http://localhost:8080
```

Three of the four skips are the browser end-to-end modules, which skip cleanly unless Playwright is
installed (`pip install playwright && python -m playwright install chromium`); with it the suite is
201 passed, 1 skipped. The remaining skip is the on-board calibration clip (see "Not yet verified").

**Against the real Ring API.** Copy `.env.example` to `.env.local` and set
`RANGYUU_ACCESS_TOKEN` to a [Ring Developer Playground](https://developer.amazon.com/ring/console/playground)
token (it lasts about 30 minutes). Then:

```sh
python -c "from rangyuu.ring_client import RingClient; print(RingClient().devices())"
```

Live media needs `pip install aiortc`. The on-board object detector is optional and needs
`onnxruntime` plus the model path in `RANGYUU_ONNX_MODEL`; without it the lane falls back to a
texture heuristic and says so on the Sources screen. `.env.local` is gitignored and never committed.

## What the app shows

Three destinations, served by the same process, in English or Spanish following the browser:

- **Now** — the dominant decision for the current route, the reason, and the map cells behind it.
- **On board** — the phone camera as the vehicle's own sensor. It can warn; it does not write to the
  map until its calibration is measured.
- **System** — sources, calibration (with the measured error, not the fit residual) and language.

## Measured, with dates

Every number below has a repeatable command in [`docs/verificacion.md`](docs/verificacion.md).

| Measurement | Value | Date |
|---|---|---|
| Live WHEP session against the Playground device, full loop | 400 frames at 1280x720: decode 7.48 ms, **inference 0.58 ms**, decision 0.10 ms → **8.16 ms/frame** (~122 fps capacity vs ~29 fps delivered) | 2026-09-15 |
| No third-party inference | the loop keeps working with `socket` poisoned while a frame is processed | 2026-09-15 |
| Floor calibration error, measured on points **left out of the fit** | **0.9 cm over 61 cm (1.6 %)** | 2026-09-15 |
| Playground live view | a canned ~40 s clip (1172 frames), H264 only, no audio — so nothing geometric is measured on it | 2026-09-15 |
| On-board detector precision vs ground truth | **22 %** — so it only warns ("caution"); it is not allowed to brake | 2026-09-16 |

## Not yet verified

Stated plainly so nobody has to discover it:

- **On-board phone calibration (B11).** The gate and wiring are done and tested; the physical tape
  measurement has not been recorded, so that test is the one skipped.
- **The webhook path is gated by a fitted homography, not a measured one**
  ([`spatial.py` L67](https://github.com/LuisAlejandroCR/rangyuu/blob/0cbd2640df36f6b4b251646ab459aa16a866c00c/rangyuu/spatial.py#L67)).
  The app path is gated by a measured error; the webhook path still needs a per-device measurement.
- **OAuth app linking (B2).** Webhooks from Ring need a registered app; the token endpoint is
  configurable (`RANGYUU_TOKEN_URL`) because its exact path was not verified.
- **Glass-to-glass latency** needs a physical Ring camera; the Playground clip carries its own clock.
- **Error beyond 1.5 m** and with a Ring camera instead of a phone.

## Repository map

| Path | What it does |
|---|---|
| `rangyuu/geometry.py`, `calibrate.py` | Normalized DLT homography; calibration with error in centimetres |
| `rangyuu/spatial.py`, `policy.py` | Occupancy cells with confidence, expiry, occlusion, dedup; the decision contract |
| `rangyuu/ring_client.py`, `whep.py`, `live.py`, `ring.py` | Ring REST, WHEP, media, webhook signature |
| `rangyuu/api.py` | `POST /api/webhook/ring` and `POST /api/rover/can-traverse` |
| `rangyuu/runtime.py`, `detect.py` | Local loop with per-stage budget and feed watchdog |
| `rangyuu/briefing.py` | Amazon Bedrock operator briefing; never decides, falls back to a template |
| `rangyuu/site.py`, `ui.py`, `webapp.py`, `serve.py`, `web/` | The app and its four screen states |
| `rangyuu/onboard.py`, `onboard_calibration.py`, `vision.py`, `walk.py` | The on-board lane and its calibration gate |
| `mobile/` | Thin Expo client that sends on-board frames to the core |
| `docs/` | Plan, architecture, perception analysis, verification log (in Spanish) |

## License

[MIT](LICENSE).
