// i18n.js: la tabla de idiomas y cómo se elige uno. Sin dependencias y sin build: un objeto por
// idioma y una función de búsqueda. Se distingue de app.js —que trae el dato y dibuja— y de
// styles.css: acá no hay ni una decisión de producto, solo cómo se dicen las cosas.
//
// Dos tablas, porque hay dos orígenes de texto:
//   UI      — lo que escribe la propia pantalla, por clave.
//   SERVER  — lo que llega ya resuelto del núcleo (estado, razón, detalle, etiquetas de fuente).
//             El contrato manda esos valores en castellano y no se tocan en el servidor: se
//             traducen acá, indexados por el valor que de verdad llega, y si no está en la tabla
//             se muestra tal cual en vez de esconderlo.

export const LANGUAGES = { en: "English", es: "Español" };
const FALLBACK = "en";
const KEY = "rangyuu.lang";

const UI = {
  en: {
    "nav.now": "Now",
    "nav.onboard": "On board",
    "nav.system": "System",

    "state.AVANZA": "GO",
    "state.CUIDADO": "CAUTION",
    "state.PARA": "STOP",
    "state.SIN CERTEZA": "UNCERTAIN",

    "now.eyebrow": "Current route",
    "now.waiting": "waiting for the site",
    "now.map": "Site plan",
    "now.mapAria": "Site map with the proposed route",
    "now.evidence": "Evidence",
    "now.zones": "Zones of the site",
    "now.decisions": "Latest decisions",
    "now.noZones": "No zones have been named yet.",
    "now.noDecisions": "No decisions recorded yet.",
    "now.noObservations": "no observations yet",
    "now.cells": (n) => `${n} cells`,
    "now.riskZone": "risk zone",
    "now.risk": "risk",
    "now.noDevice": "no device",

    "gate.yes": "clear to proceed",
    "gate.no": "not clear to proceed",

    "link.stamp": "no link",
    "link.reason": "no link to the site",
    "link.detail": "the last reading on screen can no longer be confirmed",

    "legend.free": "clear",
    "legend.occupied": "occupied",
    "legend.unknown": "no data",
    "legend.route": "route",

    "cell.FREE": "clear",
    "cell.OCCUPIED": "occupied",
    "cell.UNKNOWN": "no data",
    "cell.title": (id, state) => `Cell ${id} · ${state}`,
    "cell.detail": (age, source, confidence) =>
      `Seen ${age} s ago by the ${source}, with ${confidence} % confidence.`,

    "source.RING_INFRASTRUCTURE": "fixed site camera",
    "source.IPHONE_ONBOARD": "on-board camera",
    "source.ago": (s) => `${s} s ago`,
    "source.on": "Connected",
    "source.off": "No signal",

    "walk.eyebrow": "The way ahead",
    "walk.idle": "stopped",
    "walk.cameraOff": "the camera is off",
    "walk.note": "The camera is a sensor, not a recorder: no video is stored.",
    "walk.start": "Start",
    "walk.pause": "Pause",
    "walk.stop": "STOP",
    "walk.active": "camera on",
    "walk.paused": "paused",
    "walk.noCamera": "no access to the camera",
    "walk.stoppedByUser": "stopped by the operator",
    "walk.manualStop": "stopped by hand",
    "walk.lostLink": "lost the link to the site",

    "system.sources": "Observation sources",
    "system.language": "Language",
    "system.languageAuto": "Match the browser",
    "system.calibration": "Calibration",
    "system.errorMeasured": "measured error",
    "system.errorFit": "fit error",
    "system.ceiling": "declared ceiling",
    "system.measuredNote":
      "Measured against points that were not part of the fit: the number proves something.",
    "system.fitNote": "This is the fit's own error, which is always near zero and proves nothing.",
    "system.budget": "Per-frame budget",
    "system.decode": "decoding",
    "system.inference": "local inference",
    "system.decision": "decision",
    "system.total": (frames) => `total · ${frames} frames`,
    "system.noFrames": "no frame has arrived yet",
    "system.coverage": "coverage",
    "system.cellsOf": (known, seen) => `${known}/${seen} cells`,
    "system.haptics": "Alerts without looking at the screen",
    "system.vibrate": "vibration",
    "system.tone": "tone",
    "system.speech": "speech",
    "system.available": "available",
    "system.unavailable": "unavailable",
    "system.alerts": "alerts",
    "system.test": "Test",
    "system.noVibration": "this browser exposes no vibration: the alert is tone and speech",

    "setup.title": "Configure the space",
    "setup.hint": "Mark four points on the floor and type their real measurements. The error is " +
      "shown before saving; if it is over the declared ceiling, it is not saved.",
    "setup.corner": "Corner",
    "setup.cellSize": "Cell size (m)",
    "setup.testRoute": "Route to test (cells)",
    "setup.calibrate": "Calibrate and measure",
    "setup.runRoute": "Test route",
    "setup.saved": "Calibration saved",
    "setup.notSaved": "Not saved",
    "setup.meanError": "mean error",
    "setup.maxError": "max error",
    "setup.ceiling": "ceiling",
    "setup.failed": "Could not calibrate",
    "setup.gridRedone": "Grid rebuilt",
    "setup.gridSize": "cell size",
    "setup.dropped": "observations discarded",
    "setup.gridWarning": "changing the grid invalidates what was observed",
    "setup.gridFailed": "Could not change the grid",

    "say.AVANZA": "go",
    "say.CUIDADO": "caution",
    "say.PARA": "stop",
    "say.SIN CERTEZA": "uncertain",
  },

  es: {
    "nav.now": "Ahora",
    "nav.onboard": "Caminata",
    "nav.system": "Sistema",

    "state.AVANZA": "AVANZA",
    "state.CUIDADO": "CUIDADO",
    "state.PARA": "PARA",
    "state.SIN CERTEZA": "SIN CERTEZA",

    "now.eyebrow": "Ruta actual",
    "now.waiting": "esperando al sitio",
    "now.map": "Plano del espacio",
    "now.mapAria": "Mapa espacial con la trayectoria propuesta",
    "now.evidence": "Evidencia",
    "now.zones": "Zonas del sitio",
    "now.decisions": "Últimas decisiones",
    "now.noZones": "Todavía no hay zonas nombradas.",
    "now.noDecisions": "Todavía no hay decisiones registradas.",
    "now.noObservations": "todavía no hay observaciones",
    "now.cells": (n) => `${n} celdas`,
    "now.riskZone": "zona de riesgo",
    "now.risk": "riesgo",
    "now.noDevice": "sin dispositivo",

    "gate.yes": "autoriza el paso",
    "gate.no": "no autoriza el paso",

    "link.stamp": "sin enlace",
    "link.reason": "sin enlace con el sitio",
    "link.detail": "el último dato en pantalla ya no se puede confirmar",

    "legend.free": "libre",
    "legend.occupied": "ocupado",
    "legend.unknown": "sin datos",
    "legend.route": "ruta",

    "cell.FREE": "libre",
    "cell.OCCUPIED": "ocupado",
    "cell.UNKNOWN": "sin datos",
    "cell.title": (id, state) => `Celda ${id} · ${state}`,
    "cell.detail": (age, source, confidence) =>
      `Observada hace ${age} s por la ${source}, con ${confidence} % de confianza.`,

    "source.RING_INFRASTRUCTURE": "cámara fija del sitio",
    "source.IPHONE_ONBOARD": "cámara a bordo",
    "source.ago": (s) => `hace ${s} s`,
    "source.on": "Conectado",
    "source.off": "Sin señal",

    "walk.eyebrow": "Frente a vos",
    "walk.idle": "detenido",
    "walk.cameraOff": "la cámara está apagada",
    "walk.note": "La cámara es un sensor, no una grabadora: no se guarda video.",
    "walk.start": "Empezar",
    "walk.pause": "Pausar",
    "walk.stop": "PARAR",
    "walk.active": "cámara activa",
    "walk.paused": "en pausa",
    "walk.noCamera": "sin acceso a la cámara",
    "walk.stoppedByUser": "detenido por quien opera",
    "walk.manualStop": "parada manual",
    "walk.lostLink": "se perdió el enlace con el sitio",

    "system.sources": "Fuentes de observación",
    "system.language": "Idioma",
    "system.languageAuto": "El del navegador",
    "system.calibration": "Calibración",
    "system.errorMeasured": "error medido",
    "system.errorFit": "error del ajuste",
    "system.ceiling": "techo declarado",
    "system.measuredNote":
      "Medido contra puntos que no entraron en el ajuste: el número prueba algo.",
    "system.fitNote": "Es el error del propio ajuste, que siempre da casi cero y no prueba nada.",
    "system.budget": "Presupuesto por frame",
    "system.decode": "decodificación",
    "system.inference": "inferencia local",
    "system.decision": "decisión",
    "system.total": (frames) => `total · ${frames} frames`,
    "system.noFrames": "todavía no llegó ningún frame",
    "system.coverage": "cobertura",
    "system.cellsOf": (known, seen) => `${known}/${seen} celdas`,
    "system.haptics": "Aviso sin mirar la pantalla",
    "system.vibrate": "vibración",
    "system.tone": "tono",
    "system.speech": "voz",
    "system.available": "disponible",
    "system.unavailable": "no disponible",
    "system.alerts": "avisos",
    "system.test": "Probar",
    "system.noVibration": "este navegador no expone vibración: el aviso es tono y voz",

    "setup.title": "Configurar espacio",
    "setup.hint": "Marcá cuatro puntos del suelo y escribí sus medidas reales. El error se " +
      "muestra antes de guardar; si supera el techo declarado, no se guarda.",
    "setup.corner": "Esquina",
    "setup.cellSize": "Tamaño de celda (m)",
    "setup.testRoute": "Trayectoria a probar (celdas)",
    "setup.calibrate": "Calibrar y medir",
    "setup.runRoute": "Probar ruta",
    "setup.saved": "Calibración guardada",
    "setup.notSaved": "No se guardó",
    "setup.meanError": "error medio",
    "setup.maxError": "error máximo",
    "setup.ceiling": "techo",
    "setup.failed": "No se pudo calibrar",
    "setup.gridRedone": "Rejilla rehecha",
    "setup.gridSize": "tamaño de celda",
    "setup.dropped": "observaciones descartadas",
    "setup.gridWarning": "cambiar la rejilla invalida lo observado",
    "setup.gridFailed": "No se pudo cambiar la rejilla",

    "say.AVANZA": "avanza",
    "say.CUIDADO": "cuidado",
    "say.PARA": "para",
    "say.SIN CERTEZA": "sin certeza",
  },
};

// Lo que el núcleo ya resolvió y manda en castellano. La clave es el valor que llega; el
// castellano no necesita tabla porque ya está en su idioma.
const SERVER = {
  en: {
    // razones de `rangyuu/ui.py`
    "camino libre": "clear path",
    "algo ocupa el camino": "something is on the path",
    "zona sin cobertura": "area with no coverage",
    "la observación caducó": "the observation expired",
    "cámara sin conexión": "camera offline",
    "sesión de video caída": "video session down",
    "calibración no válida": "calibration not valid",
    "confianza baja": "low confidence",
    "sin confianza declarada": "no confidence declared",
    "sin evidencia que anclar": "no evidence to anchor to",
    "el evento contradice el frame": "the event contradicts the frame",
    "hace rato que no llega imagen": "no image has arrived for a while",
    // detalles de CUIDADO, que llegan unidos por "; "
    "la cámara a bordo ve algo distinto al suelo adelante":
      "the on-board camera sees something other than floor ahead",
    "la cámara a bordo no puede afirmar qué hay al frente":
      "the on-board camera cannot state what is ahead",
    "hay algo ocupado al lado del camino": "something is occupied beside the path",
    "la confianza está cerca del umbral": "confidence is close to the threshold",
    "la observación está por caducar": "the observation is about to expire",
    // etiquetas y notas de fuentes
    "Ring (infraestructura)": "Ring (infrastructure)",
    "iPhone (a bordo)": "iPhone (on board)",
    "camino despejado al frente": "clear ahead",
    "algo al frente que no es el suelo": "something ahead that is not the floor",
    "no puede afirmar qué hay al frente": "cannot state what is ahead",
    "el iPhone no está calibrado contra este suelo: observa, no escribe":
      "the iPhone is not calibrated against this floor: it observes, it does not write",
    // razones de calibración
    "calibración válida": "calibration valid",
    "sin calibrar": "not calibrated",
    "ajustada pero sin medir contra un punto conocido":
      "fitted but never measured against a known point",
    "requiere recalibración": "needs recalibration",
    // etiquetas de las cuatro esquinas: viajan al servidor en castellano y vuelven como claves de
    // `per_point_cm`, así que se traducen solo al mostrarlas y el cuerpo del POST no cambia.
    "cercana izquierda": "near left",
    "cercana derecha": "near right",
    "lejana derecha": "far right",
    "lejana izquierda": "far left",
    // nombres de las zonas sembradas en `rangyuu/serve.py`: son dato, viajan en castellano y se
    // traducen solo al mostrarlos. Una zona que nombre el usuario se muestra tal cual.
    "entrada": "entrance",
    "pasillo": "hallway",
    "puerta": "door",
    // errores del servidor que la pantalla de Sistema muestra
    "se necesitan cuatro puntos medidos": "four measured points are needed",
    "el tamaño de celda debe estar entre 0,05 y 5 m": "cell size must be between 0.05 and 5 m",
  },
  // el núcleo geométrico falla en inglés; en castellano se traduce lo que Sistema puede mostrar
  es: {
    "need at least four measured correspondences": "se necesitan al menos cuatro puntos medidos",
    "need at least four matching points": "se necesitan al menos cuatro puntos que coincidan",
    "degenerate correspondences": "los puntos no forman un cuadrilátero válido",
    "degenerate homography": "la homografía es degenerada",
    "point projects to infinity": "un punto se proyecta al infinito",
    "rectangle sides must be positive": "los lados del rectángulo deben ser positivos",
  },
};

let language = FALLBACK;
const listeners = new Set();

/** El idioma guardado, o null. El almacenamiento tira en ventanas privadas: nunca sin `try`. */
export function storedLanguage() {
  try {
    const value = window.localStorage.getItem(KEY);
    return value && UI[value] ? value : null;
  } catch {
    return null;
  }
}

function store(value) {
  try {
    if (value) window.localStorage.setItem(KEY, value);
    else window.localStorage.removeItem(KEY);
    return true;
  } catch {
    return false;                       // la app sigue andando, solo no recuerda la elección
  }
}

/** El primero de los idiomas pedidos que existe en la tabla; si ninguno, inglés. */
export function matchLanguage(tags) {
  for (const tag of tags || []) {
    const base = String(tag).toLowerCase().split("-")[0];
    if (UI[base]) return base;
  }
  return FALLBACK;
}

function browserLanguage() {
  const tags = (typeof navigator === "undefined" ? [] : navigator.languages)
    || [typeof navigator === "undefined" ? "" : navigator.language];
  return matchLanguage(tags);
}

export function language_() { return language; }
export function override() { return storedLanguage(); }

/** Fija el idioma. `null` vuelve a seguir al navegador. Sincroniza `<html lang>`. */
export function setLanguage(value) {
  store(value && UI[value] ? value : null);
  language = (value && UI[value]) ? value : browserLanguage();
  if (typeof document !== "undefined") document.documentElement.lang = language;
  listeners.forEach((fn) => fn(language));
  return language;
}

export function onLanguageChange(fn) { listeners.add(fn); }

/** Un texto de la interfaz. Si la clave falta cae al inglés, y si falta ahí devuelve la clave. */
export function t(key, ...args) {
  const value = UI[language]?.[key] ?? UI[FALLBACK]?.[key];
  if (value === undefined) return key;
  return typeof value === "function" ? value(...args) : value;
}

/** Un texto que ya venía resuelto del núcleo. Sin traducción conocida, se muestra tal cual. */
export function s(text) {
  if (!text) return "";
  return SERVER[language]?.[text] ?? text;
}

/** Los detalles de CUIDADO llegan unidos por "; ": se traduce cada uno y se vuelven a unir. */
export function sList(text) {
  if (!text) return "";
  return String(text).split("; ").map(s).join("; ");
}

/** Rellena el marcado estático marcado con `data-i18n`, `data-i18n-aria` y `data-i18n-title`. */
export function applyStatic(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  root.querySelectorAll("[data-i18n-aria]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nAria));
  });
  root.querySelectorAll("[data-i18n-title]").forEach((node) => {
    node.title = t(node.dataset.i18nTitle);
  });
}

setLanguage(storedLanguage());
