// haptics.js: el aviso que no exige mirar la pantalla — vibración, tono y voz, uno por estado.
// Se distingue de app.js, que trae el dato y dibuja: acá solo vive cómo se avisa. Cada canal se
// detecta antes de usarse, porque Safari en iOS no tiene API de vibración y no se puede fingir.

const PATTERNS = {
  AVANZA: { vibrate: [35], tone: [660, 0.08], say: "avanza" },
  CUIDADO: { vibrate: [60, 70, 60], tone: [440, 0.12], say: "cuidado" },
  PARA: { vibrate: [140, 80, 140], tone: [220, 0.25], say: "para" },
  "SIN CERTEZA": { vibrate: [25, 120, 25, 120, 25], tone: [330, 0.18], say: "sin certeza" },
};

export const support = {
  vibrate: typeof navigator !== "undefined" && typeof navigator.vibrate === "function",
  audio: typeof window !== "undefined" && !!(window.AudioContext || window.webkitAudioContext),
  speech: typeof window !== "undefined" && "speechSynthesis" in window,
};

let context = null;
let last = "";
let enabled = true;
// El navegador descarta `navigator.vibrate()` mientras no haya habido un gesto del usuario, y
// además lo anota como error en consola. En vez de llamar y fallar, se guarda el patrón del
// estado vigente y se emite en cuanto llega el gesto: el aviso no se pierde y la consola queda
// limpia. Es la misma puerta que ya necesitaba el audio, así que la abre el mismo `unlock()`.
let gestured = false;
let pending = null;

/** Una sola forma de decir el estado por los canales que el dispositivo tenga. */
export function announce(state, { force = false } = {}) {
  const pattern = PATTERNS[state];
  if (!pattern || !enabled) return { skipped: true };
  if (state === last && !force) return { skipped: true };
  last = state;

  const used = [];
  if (support.vibrate) {
    if (gestured) { if (navigator.vibrate(pattern.vibrate)) used.push("vibrate"); }
    else pending = pattern.vibrate;
  }
  if (playTone(pattern.tone)) used.push("tone");
  if (speak(pattern.say)) used.push("speech");
  return { state, used };
}

/** El tono es el respaldo real en iPhone, donde no hay vibración desde el navegador. */
function playTone([frequency, seconds]) {
  // Misma puerta que la vibración: antes del gesto el navegador no deja sonar y avisa por
  // consola. Declarar que no sonó es más honesto que llamar, fallar y contarlo como usado.
  if (!support.audio || !gestured) return false;
  try {
    context = context || new (window.AudioContext || window.webkitAudioContext)();
    if (context.state === "suspended") context.resume();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.type = "sine";
    oscillator.frequency.value = frequency;
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.14, context.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + seconds);
    oscillator.connect(gain).connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + seconds + 0.02);
    return true;
  } catch {
    return false;
  }
}

function speak(text) {
  if (!support.speech) return false;
  try {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    return true;
  } catch {
    return false;
  }
}

/** El audio del navegador necesita un gesto del usuario para arrancar: esto es ese gesto. */
export function unlock() {
  const first = !gestured;
  gestured = true;
  if (first && pending && support.vibrate) { navigator.vibrate(pending); pending = null; }
  if (!support.audio) return false;
  try {
    context = context || new (window.AudioContext || window.webkitAudioContext)();
    if (context.state === "suspended") context.resume();
    return true;
  } catch {
    return false;
  }
}

export function setEnabled(value) {
  enabled = !!value;
  if (!enabled && support.speech) window.speechSynthesis.cancel();
  return enabled;
}

export function reset() {
  last = "";
  pending = null;
}

/** Lo que este dispositivo puede hacer de verdad, para mostrarlo en Fuentes sin prometer de más. */
export function channels() {
  return {
    vibrate: support.vibrate,
    tone: support.audio,
    speech: support.speech,
    note: support.vibrate ? "" : "este navegador no expone vibración: el aviso es tono y voz",
  };
}
