// app.js: trae el dato del proceso local y lo dibuja. No decide nada: el estado y la razón
// vienen resueltos del núcleo (rangyuu/ui.py). Se distingue de styles.css, que es la identidad
// visual, y de index.html, que es la estructura de las pantallas.

const $ = (id) => document.getElementById(id);
const api = async (path, body) => {
  const options = body
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : {};
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`${path} → ${response.status}`);
  return response.json();
};

const clock = (at) => (at ? new Date(at * 1000).toLocaleTimeString("es") : "—");

// --- navegación entre pantallas ---------------------------------------------

function show(name) {
  document.querySelectorAll(".screen").forEach((s) => { s.hidden = s.dataset.screen !== name; });
  document.querySelectorAll(".tabs button").forEach((b) => {
    b.classList.toggle("active", b.dataset.goto === name);
  });
  refresh(name);
}
document.addEventListener("click", (event) => {
  const target = event.target.closest("[data-goto]");
  if (target) show(target.dataset.goto);
});

// --- 1 · Ahora ---------------------------------------------------------------

function paintVerdict(data) {
  const verdict = $("verdict");
  verdict.dataset.state = data.state;
  $("verdict-state").textContent = data.state;
  $("verdict-reason").textContent = data.reason || "";
  $("verdict-detail").textContent = data.detail || "";
  $("ahora-stamp").textContent = clock(data.at);
  drawMap($("map-now"), data.cells || [], data.route || [], []);
}

// --- mapa ---------------------------------------------------------------------

function drawMap(svg, cells, route, zones) {
  const all = cells.map((c) => c.cell).concat(route);
  if (!all.length) { svg.innerHTML = '<text x="50" y="50" class="zone-label" text-anchor="middle">sin observaciones</text>'; return; }
  const xs = all.map((c) => c[0]), ys = all.map((c) => c[1]);
  const minX = Math.min(...xs) - 1, maxX = Math.max(...xs) + 1;
  const minY = Math.min(...ys) - 1, maxY = Math.max(...ys) + 1;
  const width = maxX - minX + 1, height = maxY - minY + 1;
  const size = 100 / Math.max(width, height);
  const px = (cx) => (cx - minX) * size, py = (cy) => (maxY - cy) * size;

  const parts = cells.map((c) =>
    `<rect class="cell ${c.state.toLowerCase()}" x="${px(c.cell[0])}" y="${py(c.cell[1])}" ` +
    `width="${size}" height="${size}" data-cell="${c.cell}" data-age="${c.age_s}" ` +
    `data-confidence="${c.confidence}" data-source="${c.source}"><title>${c.state}</title></rect>`);

  parts.push(...route.map((c) =>
    `<rect class="route" x="${px(c[0]) + 1}" y="${py(c[1]) + 1}" width="${size - 2}" height="${size - 2}" rx="1"/>`));

  parts.push(...zones.map((z) => {
    const cell = z.cells[0];
    return cell ? `<text class="zone-label" x="${px(cell[0])}" y="${py(cell[1]) - 1}">${z.name}</text>` : "";
  }));

  svg.innerHTML = parts.join("");
}

// --- 3 · Espacio -------------------------------------------------------------

async function loadSpace() {
  const data = await api("/api/space/map");
  $("espacio-stamp").textContent = `celda ${data.cell_size_m} m · ${clock(data.at)}`;
  drawMap($("map-space"), data.cells || [], data.route || [], data.zones || []);
  $("zones").innerHTML = (data.zones || []).map((z) =>
    `<li><strong>${z.name}</strong> · ${z.cells.length} celdas${z.risky ? " · zona de riesgo" : ""}</li>`
  ).join("") || '<li class="hint">Todavía no hay zonas nombradas.</li>';
}

$("map-space").addEventListener("click", (event) => {
  const rect = event.target.closest("rect.cell");
  const panel = $("cell-detail");
  if (!rect) { panel.hidden = true; return; }
  panel.hidden = false;
  panel.innerHTML = `<strong>Celda ${rect.dataset.cell}</strong><br>` +
    `estado: ${rect.classList[1]} · confianza: ${rect.dataset.confidence} · ` +
    `observada hace ${rect.dataset.age} s · fuente: ${rect.dataset.source}`;
});

// --- 4 · Fuentes -------------------------------------------------------------

async function loadSources() {
  const data = await api("/api/sources");
  $("fuentes-stamp").textContent = clock(data.at);
  $("sources").innerHTML = data.sources.map((s) => `
    <li>
      <span><span class="label">${s.label}</span>
        <span class="kind">${s.kind}${s.age_s !== null ? ` · hace ${s.age_s} s` : " · sin observaciones"}</span>
      </span>
      <span class="dot ${s.active ? "on" : "off"}" title="${s.active ? "activa" : "sin señal"}"></span>
    </li>`).join("");

  const cal = data.calibration;
  $("calibration").innerHTML = `<h2>Calibración</h2>
    <div class="row"><span>${cal.reason}</span>
      <span class="${cal.valid ? "good" : "bad"}">${cal.error_cm === null ? "—" : cal.error_cm + " cm"}</span></div>
    <div class="row"><span>${cal.measured ? "medido contra puntos ajenos al ajuste" : "error del ajuste, que no prueba nada"}</span>
      <span>${cal.measured ? "sí" : (cal.fit_error_cm ?? "—") + " cm"}</span></div>
    <div class="row"><span>techo declarado</span><span>${cal.ceiling_cm} cm</span></div>`;

  const b = data.budget_ms;
  $("budget").innerHTML = `<h2>Presupuesto por frame</h2>` + (b.frames
    ? `<div class="row"><span>decodificación</span><span>${b.decode_ms} ms</span></div>
       <div class="row"><span>inferencia local</span><span>${b.inference_ms} ms</span></div>
       <div class="row"><span>decisión</span><span>${b.decision_ms} ms</span></div>
       <div class="row"><span>total · ${b.frames} frames</span><span>${b.total_ms} ms</span></div>`
    : `<div class="row"><span>todavía no llegó ningún frame</span><span>—</span></div>`) +
    `<div class="row"><span>cobertura</span><span>${data.coverage.cells_known}/${data.coverage.cells_seen} celdas</span></div>`;
}

// --- 5 · Configurar ----------------------------------------------------------

const LABELS = ["cercana izquierda", "cercana derecha", "lejana derecha", "lejana izquierda"];
const DEFAULTS = [[95, 818, 0, 0], [697, 841, 0.9, 0], [631, 222, 0.9, 1.5], [247, 208, 0, 1.5]];

$("points").innerHTML = "<tr><th>Esquina</th><th>px x</th><th>px y</th><th>m x</th><th>m y</th></tr>" +
  LABELS.map((label, i) => `<tr><td>${label}</td>` +
    DEFAULTS[i].map((v, j) => `<td><input id="p${i}${j}" type="number" step="0.01" value="${v}"></td>`).join("") +
    "</tr>").join("");

$("calibrate").addEventListener("click", async () => {
  const points = LABELS.map((label, i) => ({
    label,
    pixel: [Number($(`p${i}0`).value), Number($(`p${i}1`).value)],
    floor_m: [Number($(`p${i}2`).value), Number($(`p${i}3`).value)],
  }));
  try {
    const result = await api("/api/space/calibrate", { points });
    const perPoint = Object.entries(result.per_point_cm)
      .map(([k, v]) => `<div class="row"><span>${k}</span><span>${v} cm</span></div>`).join("");
    $("calibration-result").innerHTML = `<h2>${result.accepted ? "Calibración guardada" : "No se guardó"}</h2>
      <div class="row"><span>error medio</span><span class="${result.accepted ? "good" : "bad"}">${result.mean_error_cm} cm</span></div>
      <div class="row"><span>error máximo</span><span class="${result.accepted ? "good" : "bad"}">${result.max_error_cm} cm</span></div>
      <div class="row"><span>techo</span><span>${result.ceiling_cm} cm</span></div>${perPoint}`;
  } catch (error) {
    $("calibration-result").innerHTML = `<h2 class="bad">No se pudo calibrar</h2><div class="row"><span>${error.message}</span></div>`;
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

async function loadDecisions() {
  const data = await api("/api/decisions");
  $("decisions").innerHTML = data.decisions.map((d) => {
    const evidence = d.evidence || {};
    const cells = (evidence.cells || []).map((c) => `[${c}]`).join(" ");
    return `<li><span class="state" data-state="${d.state}">${d.state}</span>
      <span>${d.reason}</span>
      <span class="meta">${clock(d.at)} · ${evidence.device_id || "sin dispositivo"} ${cells}</span></li>`;
  }).join("") || '<li class="hint">Todavía no hay decisiones registradas.</li>';
}

// --- 2 · Caminata ------------------------------------------------------------

let stream = null, walking = false, lastSpoken = "";

async function startWalk() {
  const video = $("camera"), canvas = $("sampler");
  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
  video.srcObject = stream;
  await video.play();
  walking = true;
  $("walk-toggle").textContent = "Pausar";
  $("walk-stamp").textContent = "cámara activa";

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
      paintWalk({ state: "SIN CERTEZA", reason: "se perdió el enlace con el sitio" });
    }
    setTimeout(tick, 400);
  };
  tick();
}

function stopWalk(message) {
  walking = false;
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
  $("walk-toggle").textContent = "Empezar";
  $("walk-stamp").textContent = message || "detenido";
}

function paintWalk(data) {
  const walk = $("walk");
  walk.dataset.state = data.state;
  $("walk-state").textContent = data.state;
  $("walk-reason").textContent = data.reason || "";
  const confidence = data.state === "AVANZA" ? 100 : data.state === "CUIDADO" ? 55 : 15;
  $("walk-confidence").style.width = `${confidence}%`;
  announce(data.state);
}

function announce(state) {
  if (state === lastSpoken) return;
  lastSpoken = state;
  if (navigator.vibrate) navigator.vibrate(state === "AVANZA" ? 40 : state === "CUIDADO" ? [60, 60] : [120, 80, 120]);
  if (window.speechSynthesis) {
    const utterance = new SpeechSynthesisUtterance(state === "SIN CERTEZA" ? "sin certeza" : state.toLowerCase());
    utterance.lang = "es-ES";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }
}

$("walk-toggle").addEventListener("click", () => {
  if (walking) { stopWalk("en pausa"); return; }
  startWalk().catch((error) => { stopWalk("sin acceso a la cámara"); $("walk-reason").textContent = error.message; });
});
$("walk-stop").addEventListener("click", () => { stopWalk("detenido por el usuario"); paintWalk({ state: "PARA", reason: "parada manual" }); });

// --- refresco ----------------------------------------------------------------

async function refresh(name) {
  try {
    if (name === "ahora") paintVerdict(await api("/api/space/now"));
    if (name === "espacio") await loadSpace();
    if (name === "fuentes") await loadSources();
    if (name === "evidencia") await loadDecisions();
  } catch (error) {
    $("verdict-reason").textContent = "sin enlace con el sitio";
  }
}

setInterval(() => {
  const active = document.querySelector(".screen:not([hidden])");
  if (active && active.dataset.screen !== "caminata") refresh(active.dataset.screen);
}, 2000);

show("ahora");
