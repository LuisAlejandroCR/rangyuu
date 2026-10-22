import { announce, channels, reset as resetHaptics, setEnabled, unlock } from "./haptics.js";
import { LANGUAGES, applyStatic, language_, onLanguageChange, override, s, sList, setLanguage, t }
  from "./i18n.js";

// app.js: trae el dato del proceso local y lo dibuja. No decide nada: el estado y la razón
// vienen resueltos del núcleo (rangyuu/ui.py). Se distingue de styles.css, que es la identidad
// visual, de index.html, que es la estructura, y de i18n.js, que es cómo se dice cada cosa.
// Ni una cadena visible se escribe acá: o sale de `t()`, o viene del servidor y pasa por `s()`.

const $ = (id) => document.getElementById(id);
const api = async (path, body) => {
  const options = body
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : {};
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`${path} → ${response.status}`);
  return response.json();
};

const clock = (at) => (at ? new Date(at * 1000).toLocaleTimeString(language_()) : "—");

// El núcleo habla en constantes; la pantalla habla en el idioma de quien mira. El contrato no
// cambia: acá solo se traduce para mostrar, porque un `RING_INFRASTRUCTURE` en pantalla es una
// fuga del backend. Si la constante no está en la tabla, se muestra cruda antes que esconderla.
const cellWord = (state) => t(`cell.${state}`) === `cell.${state}` ? state : t(`cell.${state}`);
const sourceWord = (kind) => (t(`source.${kind}`) === `source.${kind}` ? kind : t(`source.${kind}`));
const stateWord = (state) => (t(`state.${state}`) === `state.${state}` ? state : t(`state.${state}`));

// --- navegación entre pantallas ---------------------------------------------

function show(name) {
  document.querySelectorAll(".screen").forEach((s) => { s.hidden = s.dataset.screen !== name; });
  document.querySelectorAll(".tabs button").forEach((b) => {
    const active = b.dataset.goto === name;
    b.classList.toggle("active", active);
    if (active) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
  refresh(name);
}
document.addEventListener("click", (event) => {
  unlock();                                   // el audio del navegador necesita un gesto
  const target = event.target.closest("[data-goto]");
  if (target) show(target.dataset.goto);
});

// --- 1 · Ahora ---------------------------------------------------------------

// Lo último que pintó cada tarjeta, para volver a dibujarlo al cambiar de idioma sin esperar
// al siguiente refresco: si no, la pantalla queda medio traducida hasta el próximo tic.
let lastVerdict = null, lastWalk = null;

function paintVerdict(data) {
  lastVerdict = data;
  const verdict = $("verdict");
  verdict.dataset.state = data.state;
  $("verdict-state").textContent = stateWord(data.state);
  $("verdict-reason").textContent = s(data.reason || "");
  $("verdict-detail").textContent = sList(data.detail || "");
  // `authorizes` viene resuelto del núcleo: la pantalla lo muestra, no lo deduce del color.
  $("verdict-gate").textContent = data.authorizes ? t("gate.yes") : t("gate.no");
  $("ahora-stamp").textContent = data.at ? clock(data.at) : t("link.stamp");
  if (data.cells) drawMap($("map-now"), data.cells, data.route || []);
  announce(data.state, { cue: data.cue });
}

/** Perder el enlace con el sitio es quedarse sin evidencia, y sin evidencia no se autoriza.
 *
 * Antes la pantalla dejaba el último estado en grande —un AVANZA verde— y solo cambiaba la
 * razón en letra chica, así que seguía autorizando sobre un dato que ya no tenía. Esto nunca
 * asciende nada: solo retira la autorización, igual que ya hacía la pantalla de caminata. */
function paintLinkLost() {
  paintVerdict({ state: "SIN CERTEZA", reason: t("link.reason"),
                 detail: t("link.detail"), authorizes: false, cue: "linkLost" });
}

// --- mapa ---------------------------------------------------------------------

// Las zonas ya no se dibujan dentro del SVG. Su texto se medía en unidades del viewBox, que
// depende del tamaño de la rejilla, así que el mismo `font-size` salía enorme y desbordando la
// tarjeta en un mapa de 4 celdas e ilegible en uno grande. Ahora son fichas HTML, en px.
function drawMap(svg, cells, route) {
  const all = cells.map((c) => c.cell).concat(route);
  if (!all.length) {
    svg.setAttribute("viewBox", "0 0 100 40");
    svg.style.aspectRatio = "100 / 40";
    svg.style.setProperty("--map-ar", 100 / 40);
    svg.innerHTML = `<text x="50" y="23" class="empty-label" text-anchor="middle">${t("now.noObservations")}</text>`;
    return;
  }
  const xs = all.map((c) => c[0]), ys = all.map((c) => c[1]);
  // Sin margen de celdas vacías: el mapa muestra lo observado, no un marco decorativo.
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const width = maxX - minX + 1, height = maxY - minY + 1;
  const size = 10;
  const box = [width * size, height * size];
  svg.setAttribute("viewBox", `0 0 ${box[0]} ${box[1]}`);
  svg.style.aspectRatio = `${box[0]} / ${box[1]}`;
  svg.style.setProperty("--map-ar", box[0] / box[1]);
  const px = (cx) => (cx - minX) * size, py = (cy) => (maxY - cy) * size;

  const parts = cells.map((c) =>
    `<rect class="cell ${c.state.toLowerCase()}" x="${px(c.cell[0])}" y="${py(c.cell[1])}" ` +
    `width="${size}" height="${size}" data-cell="${c.cell}" data-age="${c.age_s}" ` +
    `data-state="${c.state}" data-confidence="${c.confidence}" data-source="${c.source}">` +
    `<title>${cellWord(c.state)}</title></rect>`);

  parts.push(...route.map((c) =>
    `<rect class="route" x="${px(c[0]) + 1}" y="${py(c[1]) + 1}" width="${size - 2}" height="${size - 2}" rx="1.5"/>`));

  svg.innerHTML = parts.join("");
}

// --- 3 · Espacio -------------------------------------------------------------

let lastZones = [];

async function loadSpace() {
  const data = await api("/api/space/map");
  drawMap($("map-now"), data.cells || [], data.route || []);
  paintZones(data.zones || []);
}

function paintZones(zones) {
  lastZones = zones;
  $("zone-chips").innerHTML = zones.map((z) =>
    `<li class="${z.risky ? "risky" : ""}">${s(z.name)}${z.risky ? ` · ${t("now.risk")}` : ""}</li>`).join("");
  $("zones").innerHTML = zones.map((z) =>
    `<li><span><span class="label">${s(z.name)}</span>
      <span class="meta">${t("now.cells", z.cells.length)}${z.risky ? ` · ${t("now.riskZone")}` : ""}</span></span>
      <span class="chevron">›</span></li>`
  ).join("") || `<li><span class="meta">${t("now.noZones")}</span></li>`;
}

$("map-now").addEventListener("click", (event) => {
  const rect = event.target.closest("rect.cell");
  const panel = $("cell-detail");
  if (!rect) { panel.hidden = true; return; }
  panel.hidden = false;
  panel.innerHTML =
    `<strong>${t("cell.title", rect.dataset.cell, cellWord(rect.dataset.state))}</strong><br>` +
    `<span class="meta">${t("cell.detail", rect.dataset.age, sourceWord(rect.dataset.source),
                            Math.round(rect.dataset.confidence * 100))}</span>`;
});

// --- 4 · Fuentes -------------------------------------------------------------

let lastSources = null;

async function loadSources() {
  lastSources = await api("/api/sources");
  paintSources(lastSources);
}

function paintSources(data) {
  const yes = (ok) => `<span class="${ok ? "good" : "bad"}">${ok ? t("system.available") : t("system.unavailable")}</span>`;
  $("fuentes-stamp").textContent = clock(data.at);
  $("sources").innerHTML = data.sources.map((source) => `
    <li>
      <span><span class="label">${s(source.label)}</span>
        <span class="kind">${s(source.note) || sourceWord(source.kind)}${source.age_s !== null ? ` · ${t("source.ago", source.age_s)}` : ""}</span>
      </span>
      <span><span class="status ${source.active ? "" : "off"}">${source.active ? t("source.on") : t("source.off")}</span>
        <span class="chevron">›</span></span>
    </li>`).join("");

  const cal = data.calibration;
  $("calibration").innerHTML = `<h2>${t("system.calibration")}</h2>
    <div class="row"><span>${cal.measured ? t("system.errorMeasured") : t("system.errorFit")}</span>
      <span class="${cal.valid ? "good" : "bad"}">${cal.error_cm === null ? "—" : cal.error_cm + " cm"}</span></div>
    <div class="row"><span>${t("system.ceiling")}</span><span>${cal.ceiling_cm} cm</span></div>
    <p class="note">${cal.measured ? t("system.measuredNote") : t("system.fitNote")}</p>`;

  const b = data.budget_ms;
  $("budget").innerHTML = `<h2>${t("system.budget")}</h2>` + (b.frames
    ? `<div class="row"><span>${t("system.decode")}</span><span>${b.decode_ms} ms</span></div>
       <div class="row"><span>${t("system.inference")}</span><span>${b.inference_ms} ms</span></div>
       <div class="row"><span>${t("system.decision")}</span><span>${b.decision_ms} ms</span></div>
       <div class="row"><span>${t("system.total", b.frames)}</span><span>${b.total_ms} ms</span></div>`
    : `<div class="row"><span>${t("system.noFrames")}</span><span>—</span></div>`) +
    `<div class="row"><span>${t("system.coverage")}</span><span>${t("system.cellsOf", data.coverage.cells_known, data.coverage.cells_seen)}</span></div>`;

  const h = channels();
  $("haptics").innerHTML = `<h2>${t("system.haptics")}</h2>
    <div class="row"><span>${t("system.vibrate")}</span>${yes(h.vibrate)}</div>
    <div class="row"><span>${t("system.tone")}</span>${yes(h.tone)}</div>
    <div class="row"><span>${t("system.speech")}</span>${yes(h.speech)}</div>` +
    (h.vibrate ? "" : `<div class="row"><span>${t("system.noVibration")}</span><span></span></div>`) +
    `<div class="row"><span>${t("system.alerts")}</span><span><button class="ghost" id="haptics-toggle">${t("system.test")}</button></span></div>`;
  $("haptics-toggle").addEventListener("click", () => {
    unlock(); resetHaptics();
    announce(lastVerdict ? lastVerdict.state : "SIN CERTEZA", { force: true });
  });
}

// --- 5 · Configurar ----------------------------------------------------------

// Las etiquetas viajan al servidor tal cual: son parte del cuerpo del POST y de las claves que
// vuelven en `per_point_cm`. Se traducen al mostrarlas, nunca al mandarlas.
const LABELS = ["cercana izquierda", "cercana derecha", "lejana derecha", "lejana izquierda"];
const DEFAULTS = [[95, 818, 0, 0], [697, 841, 0.9, 0], [631, 222, 0.9, 1.5], [247, 208, 0, 1.5]];

function paintPoints() {
  const values = LABELS.map((_, i) => DEFAULTS[i].map((v, j) => {
    const field = document.getElementById(`p${i}${j}`);
    return field ? field.value : v;
  }));
  $("points").innerHTML =
    `<tr><th>${t("setup.corner")}</th><th>px x</th><th>px y</th><th>m x</th><th>m y</th></tr>` +
    LABELS.map((label, i) => `<tr><td>${s(label)}</td>` +
      values[i].map((v, j) => `<td><input id="p${i}${j}" type="number" step="0.01" value="${v}"></td>`).join("") +
      "</tr>").join("");
}

$("calibrate").addEventListener("click", async () => {
  const points = LABELS.map((label, i) => ({
    label,
    pixel: [Number($(`p${i}0`).value), Number($(`p${i}1`).value)],
    floor_m: [Number($(`p${i}2`).value), Number($(`p${i}3`).value)],
  }));
  try {
    const result = await api("/api/space/calibrate", { points });
    const perPoint = Object.entries(result.per_point_cm)
      .map(([k, v]) => `<div class="row"><span>${s(k)}</span><span>${v} cm</span></div>`).join("");
    $("calibration-result").hidden = false;
    $("calibration-result").innerHTML = `<h2>${result.accepted ? t("setup.saved") : t("setup.notSaved")}</h2>
      <div class="row"><span>${t("setup.meanError")}</span><span class="${result.accepted ? "good" : "bad"}">${result.mean_error_cm} cm</span></div>
      <div class="row"><span>${t("setup.maxError")}</span><span class="${result.accepted ? "good" : "bad"}">${result.max_error_cm} cm</span></div>
      <div class="row"><span>${t("setup.ceiling")}</span><span>${result.ceiling_cm} cm</span></div>${perPoint}`;
  } catch (error) {
    $("calibration-result").hidden = false;
    $("calibration-result").innerHTML = `<h2 class="bad">${t("setup.failed")}</h2><div class="row"><span>${s(error.message)}</span></div>`;
  }
});

$("cell-size").addEventListener("change", async (event) => {
  const value = Number(event.target.value);
  const panel = $("calibration-result");
  panel.hidden = false;
  try {
    const result = await api("/api/space/config", { cell_size_m: value });
    panel.innerHTML = `<h2>${t("setup.gridRedone")}</h2>
      <div class="row"><span>${t("setup.gridSize")}</span><span>${result.cell_size_m} m</span></div>
      <div class="row"><span>${t("setup.dropped")}</span><span>${result.cleared}</span></div>
      <p class="note">${t("setup.gridWarning")}</p>`;
  } catch (error) {
    panel.innerHTML = `<h2 class="bad">${t("setup.gridFailed")}</h2><div class="row"><span>${s(error.message)}</span></div>`;
  }
});

$("save-route").addEventListener("click", async () => {
  const cells = $("route-input").value.trim().split(/\s+/)
    .map((pair) => pair.split(",").map(Number)).filter((c) => c.length === 2 && c.every(Number.isFinite));
  const data = await api("/api/space/route", { cells });
  paintVerdict(data);
  show("ahora");
});

// --- 6 · Evidencia -----------------------------------------------------------

let lastDecisions = null;

async function loadDecisions() {
  lastDecisions = await api("/api/decisions");
  paintDecisions(lastDecisions);
}

function paintDecisions(data) {
  $("decisions").innerHTML = data.decisions.map((d) => {
    const evidence = d.evidence || {};
    const cells = (evidence.cells || []).map((c) => `[${c}]`).join(" ");
    return `<li><span class="state" data-state="${d.state}">${stateWord(d.state)}</span>
      <span>${s(d.reason)}</span>
      <span class="meta">${clock(d.at)} · ${evidence.device_id || t("now.noDevice")} ${cells}</span></li>`;
  }).join("") || `<li class="hint">${t("now.noDecisions")}</li>`;
}

$("evidence-toggle").addEventListener("click", async () => {
  const panel = $("evidence-panel");
  const opening = panel.hidden;
  panel.hidden = !opening;
  $("evidence-toggle").setAttribute("aria-expanded", String(opening));
  if (opening) await loadDecisions();
});

// --- 2 · Caminata ------------------------------------------------------------

// El sello guarda la *clave*, no el texto: así vuelve a decirse en el idioma nuevo sin inventar
// un estado ni volver a pedirle nada al sitio.
let stream = null, walking = false, walkStampKey = "walk.idle";

function setWalkStamp(key) {
  walkStampKey = key;
  $("walk-stamp").textContent = t(key);
}

async function startWalk() {
  const video = $("camera"), canvas = $("sampler");
  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
  video.srcObject = stream;
  await video.play();
  walking = true;
  document.querySelector('[data-screen="caminata"]').classList.add("walking");
  $("walk-toggle").textContent = t("walk.pause");
  $("walk-toggle").dataset.i18n = "walk.pause";
  setWalkStamp("walk.active");

  const context = canvas.getContext("2d", { willReadFrequently: true });
  const tick = async () => {
    if (!walking) return;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
    const gray = new Array(canvas.width * canvas.height);
    for (let i = 0, p = 0; i < data.length; i += 4, p++) {
      gray[p] = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
    }
    try {
      const result = await api("/api/space/observe", { width: canvas.width, height: canvas.height, gray });
      paintWalk(result.now);
    } catch (error) {
      paintWalk({ state: "SIN CERTEZA", reason: t("walk.lostLink") });
    }
    setTimeout(tick, 400);
  };
  tick();
}

function stopWalk(stampKey) {
  walking = false;
  document.querySelector('[data-screen="caminata"]').classList.remove("walking");
  if (stream) { stream.getTracks().forEach((track) => track.stop()); stream = null; }
  resetHaptics();
  $("walk-toggle").textContent = t("walk.start");
  $("walk-toggle").dataset.i18n = "walk.start";
  setWalkStamp(stampKey || "walk.idle");
}

function paintWalk(data) {
  lastWalk = data;
  const walk = $("walk");
  walk.dataset.state = data.state;
  $("walk-state").textContent = stateWord(data.state);
  $("walk-reason").textContent = s(data.reason || "");
  const confidence = data.state === "AVANZA" ? 100 : data.state === "CUIDADO" ? 55 : 15;
  $("walk-confidence").style.width = `${confidence}%`;
  announce(data.state);
}

$("walk-toggle").addEventListener("click", () => {
  if (walking) { stopWalk("walk.paused"); return; }
  startWalk().catch((error) => {
    stopWalk("walk.noCamera");
    $("walk-reason").textContent = error.message;
  });
});
$("walk-stop").addEventListener("click", () => {
  stopWalk("walk.stoppedByUser");
  paintWalk({ state: "PARA", reason: t("walk.manualStop") });
});

// --- idioma -------------------------------------------------------------------
//
// Por defecto se sigue al navegador; el control de Sistema es una anulación explícita que se
// guarda. Cambiarlo vuelve a pintar lo último que ya se tenía, sin pedirle nada al sitio: el
// idioma es presentación y no puede mover ni un estado.

function paintLanguageControl() {
  const select = $("language");
  const current = override() || "";
  select.innerHTML = `<option value="">${t("system.languageAuto")}</option>` +
    Object.entries(LANGUAGES).map(([code, name]) =>
      `<option value="${code}">${name}</option>`).join("");
  select.value = current;
}

$("language").addEventListener("change", (event) => setLanguage(event.target.value || null));

onLanguageChange(() => {
  applyStatic();
  paintLanguageControl();
  paintPoints();
  if (lastVerdict) paintVerdict(lastVerdict);
  if (lastWalk) paintWalk(lastWalk); else applyStatic($("walk"));
  setWalkStamp(walkStampKey);
  paintZones(lastZones);
  if (lastSources) paintSources(lastSources);
  if (lastDecisions) paintDecisions(lastDecisions);
});

// --- refresco ----------------------------------------------------------------

async function refresh(name) {
  try {
    if (name === "ahora") {
      paintVerdict(await api("/api/space/now"));
      await loadSpace();
      if (!$("evidence-panel").hidden) await loadDecisions();
    }
    if (name === "sistema") await loadSources();
  } catch (error) {
    if (name === "ahora") paintLinkLost();
  }
}

setInterval(() => {
  const active = document.querySelector(".screen:not([hidden])");
  if (active && active.dataset.screen !== "caminata") refresh(active.dataset.screen);
}, 2000);

applyStatic();
paintLanguageControl();
paintPoints();

show("ahora");
