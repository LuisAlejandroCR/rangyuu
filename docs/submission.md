<!-- docs/submission.md: paquete de entrega de Devpost, en inglés: checklist de una pantalla, campos
     del formulario, feedback por herramienta, friction log, guion de voz verificado, lista de tomas
     con su origen (real, ElevenLabs o compuesta) y prompts de las escenas ilustrativas.
     No es la evidencia (docs/verificacion.md) ni el plan de producción ElevenLabs
     (docs/elevenlabs-challenge.md): aquí solo lo que se pega en Devpost o se graba. -->

# Submission pack — Rangyuu, Ring track

Rules read 2026-10-22 at <https://amazonappdev2026.devpost.com/rules>. Deadline **Fri 2026-10-23,
12:00 PT (14:00 Colombia)**. Drafts can be saved on Devpost before submitting.

## 1. One-screen checklist

| Item | State | Evidence / next action |
|---|---|---|
| Repo has setup + run instructions | ✅ | `README.md` Quickstart; rerun 2026-10-22: `201 passed, 1 skipped` with Playwright, `174 passed, 4 skipped` without, server `200` + `PROCEED`, port freed |
| Ring used at runtime, imported and called | ✅ | `rangyuu/ring_client.py`, `whep.py`, `live.py` (README permalinks at `0cbd264`, reachable from `main`) |
| Secrets in the published history (`origin/main`, 96 commits) | ✅ clean | rescanned 2026-10-22; only variable names; no media except `fixtures/ring/playground_frame_120.png` (Ring Playground output) |
| Commit author emails | ⚠️ will be public | 2 author emails appear in commit metadata once the repo is public |
| Repo access | ⏳ **your call** | Public: set visibility + confirm MIT shows in About. Or private: add `testing@devpost.com` and `knmeiss`, `giolaq`, `anishamalde`, `mosesroth`, `emersonsklar` |
| Old local branches (`codex/rangyuu-rebuild`, …) | ⛔ never push | they still carry the removed home video (docs/memoria.md 2026-10-21) |
| Open Source contribution | ✅ | fork `LuisAlejandroCR/ring-api-helloworld` (public, MIT), branch `add-whep-live-view-script`, `ed293da` 2026-09-15; PR #23 closed, unmerged — allowed |
| Video < 3 min, public on YouTube/Vimeo | ⏳ | script §5, shot list §6 (shot 5A rehearsed 2026-10-22); draft subtitles `docs/video-subtitles.en.srt`, re-sync after the edit |
| App survives a browser's idle connection | ✅ fixed 2026-10-22 | the single-threaded server froze under the in-app browser; now threaded, with a regression test |
| Product feedback per tool | ✅ draft | §3 — confirm the "would build again" answers are yours |
| Friction log (up to +10 %) | ✅ draft | §4 |
| Submit on Devpost | ⏳ manual | you press Submit |
| Illustrative scenes (§7) | ⛔ blocked | needs the full ElevenLabs connector (`https://api.elevenlabs.io/v1/mcp`) and per-scene cost approval |
| GitHub Actions on the recreated repo | ⚠️ never ran | 0 runs ever (`gh api repos/LuisAlejandroCR/rangyuu/actions/runs` → `total_count: 0`) despite push triggers and Actions enabled, 2026-10-22. Likely private-repo minutes or billing. Not required by the rules; local suite is the evidence |

### ElevenLabs credit ledger (cap 25,000)

| Date | What | Model / voice | Credits | Running total |
|---|---|---|---|---|
| 2026-10-22 | Voice test, block 0:00, 1 take (2 takes estimated at 206); tone approved, reused as the master for 0:00 | `eleven_v3` / `XW70ikSsadUbinwLMZ5w` (supplied 2026-10-22) | 102.99 | 102.99 |
| 2026-10-22 | Master, blocks 0:10 → 2:41, 1 take each, every block estimated first. Cap for the master set: 2,500 | same | 135.99 + 249.98 + 132.99 + 254.97 + 350.96 + 172.98 + 178.98 + 247.98 + 147.99 + 56.99 = 1,929.81 | **2,032.80** |
| 2026-10-22 | Scene 1 (§7), 1 take. Estimates for the same clip: Seedance v2.5 14,003 · Seedance v2 mini 4,581 · Wan 2.6 3,030 · Veo 3.1 lite 2,424 · Kling 2.5 Turbo 2,121 · LTX v2 fast 1,454. Cap for this take: 2,200. **Rejected**: the caregiver touches the wheelchair | `kling-2.5-turbo`, flow `xDHFdeM4AHUxuJCN2BNi` | 2,120.79 | **4,153.59** |

All takes live in ElevenLabs flow `3JggnpjaF01ovynn4QfB`; download them from there into the edit
project, outside the repo. Spoken numbers are written out in the prompts ("eight point one six",
"zero point nine", "sixty-one", "twenty-two") so the model reads them as the script says.

## 2. Devpost fields

**Project name:** Rangyuu

**Tagline:** A safe-by-default spatial layer: Ring cameras tell a mobility device whether a path is
clear, and silence never counts as yes.

**Primary track:** Ring · **Mini challenge:** Open Source

**Description**

A wheelchair, a mobility scooter or a small robot sees what is in front of it, not what is around
the corner. The building often already has cameras looking into that space. Rangyuu turns those
observations into a floor-plane occupancy map and answers one question for anything that moves:
*can I traverse this path right now?*

- **Ring as the infrastructure sensor.** Rangyuu calls the Ring API from Python (device discovery,
  status, capabilities), opens a WHEP live-view session without a browser, decodes the H264 media
  with `aiortc`, and verifies Ring webhook signatures (HMAC-SHA256 over the raw body, before parsing).
- **A floor map, not a picture.** A homography projects detections onto floor cells. Each cell
  carries a state, a confidence and an age, and expires.
- **A three-word contract.** `PROCEED` is the only answer that authorizes transit, and only when
  every cell on the path is observed free, fresh and calibrated, with enough confidence. Otherwise
  the answer is `HOLD` (occupied, contradicted, uncovered, uncalibrated, unobserved or expired) or
  `UNKNOWN` (low confidence, or the live feed went silent).
- **Calibration has to be measured.** An uncalibrated or merely fitted camera observes but never
  authorizes. Error is checked on points left out of the fit.
- **An app with three screens** (Now, On board, System) in English and Spanish, plus a thin Expo
  client that speaks state changes in English, Spanish and Portuguese with pre-recorded clips, so
  the "link lost" alert works offline.

Measured (dates and commands in `docs/verificacion.md`):

- Full loop on a live WHEP session from the Ring Developer Playground: 400 frames at 1280x720,
  **8.16 ms per frame** (decode 7.48, inference 0.58, decision 0.10), 2026-09-15.
- Floor calibration: **0.9 cm error over 61 cm**, on a tape-measured floor filmed with a phone,
  checked on points left out of the fit, 2026-09-15.
- On-board camera lane: **22 % precision** against a labeled walk, so it can only warn
  (`CAUTION`); it is never allowed to stop anyone, 2026-09-16.

Rangyuu is meant for supervised use: a parent, caregiver or operator stays responsible, and the
app adds evidence to their judgment. Next on the roadmap is a small unit on the vehicle that
connects to the Ring devices a building already has. It is planned, not built.

What it is not: Rangyuu does not actuate or brake any vehicle, is not a medical device and does not
guarantee physical safety. The Playground live view is a canned clip, so it exercises the
integration; no floor geometry is measured on it. Scenes with people in the video are illustrative
reenactments generated with ElevenLabs; every product screen shown is a real capture. Open items are listed under "Not yet verified" in
the README.

**Built with:** Python, Ring API, Ring Developer Playground, WebRTC/WHEP, aiortc, ONNX Runtime,
Expo / React Native, ElevenLabs (pre-recorded voice clips and demo narration).

**Repository URL:** https://github.com/LuisAlejandroCR/rangyuu

**Open Source mini challenge**

- Contribution URL: https://github.com/LuisAlejandroCR/ring-api-helloworld/tree/add-whep-live-view-script
  (pull request, closed unmerged: https://github.com/AmazonAppDev/ring-api-helloworld/pull/23)
- Project repository URL: https://github.com/LuisAlejandroCR/rangyuu
- GitHub username: LuisAlejandroCR
- What / how / why: `scripts/live_view.py` adds a terminal path to Ring live view in the official
  hello-world sample. It posts the SDP offer to the WHEP endpoint, receives the answer, keeps the
  session `Location` and closes it with `DELETE`; with `--frames` it reports the real resolution and
  frame rate. The sample only showed live view inside a browser. A terminal path lets developers
  confirm their token and device can stream, and measure what they get, before writing any UI or
  computer-vision code. Written and tested against the real API on 2026-09-15.

## 3. Product feedback (per tool)

**Ring API + Ring Developer Playground**

- *Used for:* device discovery, status and capabilities; WHEP live view; webhook signature format.
- *Worked well:* the `ring-api-helloworld` sample was readable enough to derive the full flow.
  WHEP is standard signaling, so a Python client (`aiortc`) worked outside the browser. The
  Playground token gave hardware-free access to real endpoints on day one.
- *Needs work:* the Playground live view is a canned ~40 s clip (1172 frames, H264, no audio). It
  is the same content in every session and has no floor geometry, so you can't calibrate against it.
  The Playground token lasts about 30 minutes. We could not confirm whether the Playground delivers
  webhooks, or the exact refresh-token endpoint path, so ours is configurable.
- *Onboarding:* repo seeded 2026-09-14; first real `/v1/devices` call, WHEP session and decoded
  frame on 2026-09-15.
- *Build again:* Yes. A live view you can get from a server process makes Ring cameras usable as
  infrastructure sensors, not just doorbells. *(Confirm in your own words.)*

**ElevenLabs**

- *Used for:* 42 pre-recorded alert clips (2 voices × en/es/pt × 7 phrases, `eleven_multilingual_v2`,
  about 1,590 credits) bundled in the mobile app, and this video's narration. No ElevenLabs call
  happens at runtime and it makes no decisions.
- *Worked well / needs work / build again:* *(fill after the narration session)*

**aiortc / ONNX Runtime / Expo** — WebRTC media outside the browser; optional local object detector
(24 ms/frame on CPU); thin mobile client. *(Optional: one line each.)*

## 4. Friction log

| Task | Steps | Expected vs actual | Severity | Workaround | Suggestion |
|---|---|---|---|---|---|
| Calibrate a camera from the Playground | Opened two WHEP sessions, decoded frames, compared them | Expected a live or synthetic scene; got the same canned ~40 s clip in both sessions, cut at 1172 frames | Important | Calibrated on our own tape-measured phone footage instead | Offer a Playground scene with known floor markers, or publish the clip's camera intrinsics |
| Keep a long test running | Pasted a Playground access token into `.env.local` | Expected a dev token for a session; it expires in ~30 min | Nice-to-have | Re-paste tokens during measurement runs | A longer-lived sandbox token, or a refresh flow for the Playground |
| Plan webhooks before app approval | Searched sample and docs for Playground webhook delivery | Could not determine whether the Playground emits webhooks | Important | Built and tested the HMAC receiver against fixtures | State in the Playground docs which events it can deliver, and how |
| Refresh-token exchange | Implemented the OAuth refresh path | Exact token endpoint path not confirmed | Important | Made it configurable (`RANGYUU_TOKEN_URL`), no default | Show the token URL in the sample's `.env.example` |

## 5. Voice-over script (verified 2026-10-22)

Direction: documentary, neutral American English, warm but restrained. Eleven v3, generated in
blocks. Timecodes and headings are not spoken. Target 2:20–2:40.

Each claim was checked against code or `docs/verificacion.md`. Changes from the supplied draft are
marked ✎.

```
[0:00 — curious]
A camera on a mobility vehicle can see what is in front of it.
It cannot see around a corner.

[0:10]
The building may already have cameras looking into that space.
Rangyuu asks whether those observations can support one route, right now.

[0:24 — serious]
Ring is the infrastructure source in this demonstration.
The Ring Developer Playground provides the simulator flow we tested.
Its video is a canned clip, so we use it to exercise the integration, not to claim a real-world floor measurement.

[0:45]
Rangyuu turns observations into a floor map.
Cells carry a state, confidence, and age.
Evidence expires. Unknown does not mean clear.

[1:00 — serious]
The route question is simple:
Can this path be traversed?
PROCEED requires evidence for the path that is calibrated, free, and fresh.
When evidence is missing, stale, or contradictory, Rangyuu withdraws permission.
The answer is HOLD or UNKNOWN.

[1:22]
We measured the system, not just described it.
Across four hundred frames from a live WHEP session, decode, inference, and decision took 8.16 milliseconds per frame.
✎ On a tape-measured floor, filmed with a phone, calibration error was 0.9 centimeters across 61 centimeters, checked against points left out of the fit.

[1:48 — serious]
✎ The on-board camera is a different lane.
In a measured walk, its precision was 22 percent.
So it warns. It does not stop anyone.
✎ Stopping has to be earned.

[2:03]
✎ Now we stop the site's server, with the app still open.
GO becomes UNCERTAIN: no link to the site, not clear to proceed.
The screen refuses to keep authorizing from an old answer.

[2:16 — serious]
✎ Rangyuu is meant for supervised use. A parent, a caregiver, or an operator stays responsible.
✎ It adds evidence. It does not replace their judgment.
✎ Next, a small unit on the vehicle will connect to the Ring devices a building already has.

[2:31 — warm, restrained]
✎ ElevenLabs voiced this narration and the app's pre-recorded alerts.
✎ Nothing calls it at runtime, and it makes none of the system's decisions.

[2:41]
When the evidence is there, move.
When it is not —
hold.
```

Why the ✎ lines changed:

- The 0.9 cm calibration was measured with a phone, not a Ring camera (README "Not yet verified").
- The 22 % figure is the on-board lane, which can only warn (`rangyuu/ui.py:60-78`). Rangyuu has no
  brake actuator, so "brake" was replaced.
- The app is not fed by a live WHEP session yet (plan B12), so "cut the feed" can't be filmed in it.
  Shot 5A was chosen on 2026-10-22: stop the server. The line quotes what the screen showed in a
  rehearsal that day.
- The mobile app ships ElevenLabs-generated clips, so "not part of the runtime" needed precision.
- Supervised use and the vehicle unit were added on 2026-10-22. The vehicle unit does not exist
  yet, so it stays in the future tense ("will connect") and is never shown as working.

Spoken length is about 1,900 characters and 326 words (≈2:31 of speech at ~140 wpm; the §6 edit timeline totals 2:40),
counted 2026-10-22, so roughly 1,900 credits at about 1 credit per character on
Eleven v3 before retakes. Check the displayed cost before each generation.

## 6. Shot list (real footage only)

1. **Playground.** Ring Developer Playground in the browser with the simulated device. Hide the token
   field.
2. **Ring call in code.** `rangyuu/ring_client.py` L103–L117 on screen, then the README's
   `RingClient().devices()` one-liner. Crop or blur device IDs and location in the output.
3. **WHEP from the terminal.** Fork's `scripts/live_view.py --frames` showing the session open,
   resolution and fps. This doubles as the Open Source proof.
4. **The app** at `localhost:8080`. Set System → Language → English first; the screens follow the
   browser otherwise. Show Now (decision + map), On board and System (measured calibration error).
   The screen words map to the contract like this: `GO` = `PROCEED`, `CAUTION` = `PROCEED` with a
   thin margin, `STOP` = `HOLD`, `UNCERTAIN` = `UNKNOWN` or no link. Add that as a lower third the
   first time `GO` appears. The seeded zone chips (`entrada`, `pasillo`, `puerta`) stay in Spanish:
   keep them small in frame or crop them.
5. **Withdrawal (option A, chosen 2026-10-22).** Two windows side by side: the app on Now showing
   `GO`, and the terminal running `python -m rangyuu.serve`. Press Ctrl+C in the terminal. In the
   2026-10-22 rehearsal the next poll showed `UNCERTAIN`, "no link to the site", "not clear to
   proceed". Covered by
   `tests/test_app_e2e.py::test_losing_the_link_to_the_site_withdraws_the_authorisation`.
6. **Evidence.** `python -m pytest -q` → `201 passed, 1 skipped`, then the "Measured, with dates"
   table.

### Edit timeline (narration block → picture)

Every visual has one of three origins:

- **REAL** — screen capture of the app, browser, terminal, Ring Developer Playground or test output.
  Everything that proves Ring, the map, a measurement or the withdrawal of permission is REAL.
- **ELEVENLABS** — an illustrative scene with fictional adults, generated with ElevenLabs Image &
  Video (§7). It never shows the Rangyuu UI or vehicle hardware, and is labeled
  "Illustrative reenactment" on screen.
- **COMPOSITE** — an ELEVENLABS scene with a REAL capture inset (picture-in-picture or inside a blank
  device screen), or cut immediately to the matching REAL screen.

Durations are estimated at ~140 wpm plus ~1 s of breath per block (≈151 s of voice); the last row adds a
10 s outro. Each block starts where the previous one ends: no overlaps, no gaps. Total **2:40**,
under the 2:50 target and the 3:00 limit. Re-measure once the approved takes are downloaded. The
§5 cues are script positions, not edit times; re-sync `docs/video-subtitles.en.srt` to this table.

| Start | End | Script cue (§5) | VO block | Visual | Origin | Real capture tied to it | On-screen text | Dur. |
|---|---|---|---|---|---|---|---|---|
| 0:00 | 0:10 | 0:00 | Can't see around a corner | Scene 1: approach to a hallway corner, cut to Now at ~6 s | COMPOSITE | Now (`GO` + map) | Supervised-use card · "Illustrative reenactment" | ~10 s |
| 0:10 | 0:20 | 0:10 | Building may already have cameras | Now: map with the route | REAL | — | — | ~10 s |
| 0:20 | 0:38 | 0:24 | Ring is the infrastructure source | Shot 1 (Playground) → shot 2 (`ring_client.py` + `devices()`) | REAL | — | "Ring Developer Playground — simulator, demo feed" | ~18 s |
| 0:38 | 0:48 | 0:45 | Floor map, cells, expiry | Shot 4: tap a cell (state, confidence, age) | REAL | — | — | ~10 s |
| 0:48 | 1:05 | 1:00 | Route question | Now on `GO` | REAL | — | `GO = PROCEED · STOP = HOLD · UNCERTAIN = UNKNOWN` | ~17 s |
| 1:05 | 1:27 | 1:22 | Measured 8.16 ms, 0.9 cm | Shot 3 (`live_view.py --frames`) → README "Measured, with dates" | REAL | — | "Measured 2026-09-15" | ~22 s |
| 1:27 | 1:40 | 1:48 | On-board lane, 22 % | Scene 2: user with a blank mounted phone | COMPOSITE | On board screen inside the blank phone | "Illustrative reenactment" · "22 % precision → warns only" | ~13 s |
| 1:40 | 1:55 | 2:03 | Stop the server → UNCERTAIN | Shot 5A: app + terminal, Ctrl+C | REAL | — | — | ~15 s |
| 1:55 | 2:14 | 2:16 | Supervised use; vehicle unit planned | Scene 3: caregiver with blank tablet → labeled diagram | COMPOSITE | System screen inside the blank tablet | Supervised-use card · "Illustrative reenactment" · "Vehicle unit: PLANNED, not built" | ~19 s |
| 2:14 | 2:24 | 2:31 | ElevenLabs voiced this | Shot 6 (`pytest` → `201 passed`) | REAL | — | "Narration and illustrative reenactments: ElevenLabs" | ~10 s |
| 2:24 | 2:40 | 2:41 | Evidence there, move | Scene 4: through a doorway → Now on `GO` after restarting the server | COMPOSITE | Now (`GO`) | "Illustrative reenactment" · repo URL once visibility is settled | ~16 s |

If a block runs long, trim the picture, not the claims.

Do not:

- Generate video or imagery for proof shots, or let a generated scene stand alone without its REAL capture.
- Ask ElevenLabs to draw the Rangyuu UI, a Ring device, or vehicle hardware.
- Fake a network failure with graphics.
- Use Ring chimes, or put the Ring logo on title cards or the thumbnail.
- Show raw API JSON or `python -m rangyuu` output: both print Spanish labels (`AVANZA`, `aceptado`).

On-screen card for the first 5 seconds and again under the 2:16 block: **"For supervised use: a
parent, caregiver or operator stays responsible. Rangyuu does not control any vehicle."** If the
vehicle unit appears at all, it is a labeled diagram ("planned"), never footage.

Label any rover drawn on screen as **simulated**. English subtitles: export from the final script.

## 7. Illustrative reenactment prompts (ElevenLabs Image & Video)

Prompts supplied 2026-10-22, checked against §6. Not generated yet: the connector in this session is
voice-only, and each generation needs its displayed cost approved first. One take each, 16:9.

| # | Slot | Length | Real capture composited |
|---|---|---|---|
| 1 | 0:00 | 7 s | cut to Now at ~6 s |
| 2 | 1:27 | 7 s | On board screen in the blank phone |
| 3 | 1:56 | 8 s | System screen in the blank tablet |
| 4 | 2:25 | 6 s | Now (`GO`) as picture-in-picture, right |

**1 — Opening, approach to the hallway**

Revised 2026-10-22 after take 1 was rejected (the caregiver touched the chair): the caregiver is
removed and the user drives alone. Use this version; the original stays below for reference.

```
Create a 7-second, 16:9 cinematic documentary-style video. An adult using a power wheelchair drives it on their own toward a hallway corner at a calm, careful pace. Only one person is in the frame; nobody else is present, and no one touches, pushes or steers the chair. Natural indoor daylight, realistic community building, respectful and matter-of-fact mood. Illustrative reenactment, not a real user testimonial. No distress, accident, near-collision, medical setting, logos, readable text, or visible product branding. Do not show a phone or any interface. Keep the composition uncluttered, with open space on the right for a real app-screen inset to be added in editing.
```

Original:

```
Create a 7-second, 16:9 cinematic documentary-style video. An adult wheelchair user approaches a hallway corner at a calm, careful pace while a caregiver walks nearby, attentive but not touching or steering the chair. Natural indoor daylight, realistic community building, respectful and matter-of-fact mood. Show the situation as an illustrative reenactment, not as a real user testimonial. No distress, accident, near-collision, medical setting, logos, readable text, or visible product branding. Do not show a phone or any interface. Keep the composition uncluttered, with some open space on the right for a real app-screen inset to be added in editing.
```

**2 — On board, user with a mounted phone**

```
Create a 7-second, 16:9 cinematic documentary-style video. An adult wheelchair user pauses safely in a building corridor beside a mounted smartphone, with a caregiver nearby. The phone is clearly visible, facing the camera, but its screen is completely blank, neutral dark gray, and free of reflections, text, icons, or interface. Natural light, realistic setting, calm supervised use. Respectful illustrative reenactment, not a real user testimonial. No logos, readable text, invented hardware, vehicle controls, or dramatic danger. Leave clear space on the left for an editor to composite a real screen recording into the phone display or as a picture-in-picture.
```

**3 — Supervision, caregiver and tablet**

```
Create an 8-second, 16:9 cinematic documentary-style video. An adult caregiver stands beside an adult wheelchair user in a quiet hallway; both calmly look at a tablet held by the caregiver. The tablet screen faces the camera and is completely blank, neutral dark gray, with no reflections, text, icons, or interface. The caregiver remains observant and supportive without operating or steering the wheelchair. Natural indoor daylight, dignified and realistic. Illustrative reenactment only, not a real testimonial. No logos, medical setting, distress, vehicle hardware, or claims of autonomous control. Leave room on the right for a real Rangyuu app capture to be composited during editing.
```

**4 — Closing, through a doorway**

```
Create a 6-second, 16:9 cinematic documentary-style video. An adult wheelchair user calmly passes through a wide interior doorway while a caregiver stays nearby and attentive. Smooth, unhurried movement, realistic community building, natural light, respectful documentary tone. This is an illustrative reenactment, not footage of a real Rangyuu user or product test. No danger, dramatic rescue, logos, readable text, app screens, vehicle hardware, or suggestion that software controls the wheelchair. Compose the subjects on the left and leave open space on the right for a real app-screen capture to appear as a picture-in-picture during editing.
```

Reject a take that shows readable text, a logo, a device screen that isn't blank, distress, or anyone
steering the chair; regenerate only after its cost is approved.
