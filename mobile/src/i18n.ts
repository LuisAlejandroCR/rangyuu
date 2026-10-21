// i18n.ts: the small hand-rolled string table in Spanish, English and Portuguese. The device
// language is the default; a choice saved in settings.ts overrides it. No i18n library for a
// screen with a couple of dozen strings.
// Distinguished from state.ts: the four state names are NOT translated — they are core values.
import { getLocales } from "expo-localization";

type Key =
  | "title"
  | "start"
  | "stop"
  | "waiting"
  | "permissionTitle"
  | "permissionBody"
  | "permissionGrant"
  | "backendLabel"
  | "backendDown"
  | "backendLostWhileRunning"
  | "framesLabel"
  | "alertsLabel"
  | "decisionLabel"
  | "onboardLabel"
  | "authorized"
  | "notAuthorized"
  | "linkLost"
  | "capturing"
  | "idle"
  | "settings"
  | "languageLabel"
  | "languageAuto"
  | "voiceLabel"
  | "spokenLabel"
  | "on"
  | "off"
  | "test";

export type Lang = "es" | "en" | "pt";

const EN: Record<Key, string> = {
  title: "rangyuu",
  start: "Start",
  stop: "Stop",
  waiting: "Waiting for the first decision",
  permissionTitle: "Camera access needed",
  permissionBody:
    "rangyuu reads the way ahead from the on-board camera. Frames are sent to your own backend and nowhere else.",
  permissionGrant: "Allow camera",
  backendLabel: "Backend",
  backendDown: "Backend connection unavailable. Starting won’t send frames.",
  backendLostWhileRunning: "Backend connection lost. Stop until it is restored.",
  framesLabel: "Frames sent",
  alertsLabel: "Alerts fired",
  decisionLabel: "Core decision",
  onboardLabel: "On-board camera",
  authorized: "Route authorized",
  notAuthorized: "Route not authorized",
  linkLost: "lost the link to the site",
  capturing: "capturing",
  idle: "stopped",
  settings: "Voice and language",
  languageLabel: "Language",
  languageAuto: "Device",
  voiceLabel: "Voice",
  spokenLabel: "Spoken alerts",
  on: "On",
  off: "Off",
  test: "Test voice",
};

const ES: Record<Key, string> = {
  title: "rangyuu",
  start: "Empezar",
  stop: "Detener",
  waiting: "Esperando la primera decisión",
  permissionTitle: "Hace falta la cámara",
  permissionBody:
    "rangyuu lee el camino adelante con la cámara de a bordo. Los frames van a tu propio backend y a ningún otro lado.",
  permissionGrant: "Permitir cámara",
  backendLabel: "Backend",
  backendDown: "Sin conexión con el backend. Empezar no enviará frames",
  backendLostWhileRunning: "Se perdió la conexión con el backend. Detén la captura hasta que vuelva.",
  framesLabel: "Frames enviados",
  alertsLabel: "Avisos emitidos",
  decisionLabel: "Decisión del núcleo",
  onboardLabel: "Cámara de a bordo",
  authorized: "Ruta autorizada",
  notAuthorized: "Ruta no autorizada",
  linkLost: "se perdió el enlace con el sitio",
  capturing: "capturando",
  idle: "detenido",
  settings: "Voz e idioma",
  languageLabel: "Idioma",
  languageAuto: "Del teléfono",
  voiceLabel: "Voz",
  spokenLabel: "Avisos hablados",
  on: "Sí",
  off: "No",
  test: "Probar voz",
};

const PT: Record<Key, string> = {
  title: "rangyuu",
  start: "Iniciar",
  stop: "Parar",
  waiting: "Aguardando a primeira decisão",
  permissionTitle: "É preciso acesso à câmera",
  permissionBody:
    "rangyuu lê o caminho à frente com a câmera de bordo. Os quadros vão para o seu próprio backend e para nenhum outro lugar.",
  permissionGrant: "Permitir câmera",
  backendLabel: "Backend",
  backendDown: "Sem conexão com o backend. Iniciar não enviará quadros.",
  backendLostWhileRunning: "A conexão com o backend caiu. Pare até que volte.",
  framesLabel: "Quadros enviados",
  alertsLabel: "Avisos emitidos",
  decisionLabel: "Decisão do núcleo",
  onboardLabel: "Câmera de bordo",
  authorized: "Rota autorizada",
  notAuthorized: "Rota não autorizada",
  linkLost: "perdemos a conexão com o local",
  capturing: "capturando",
  idle: "parado",
  settings: "Voz e idioma",
  languageLabel: "Idioma",
  languageAuto: "Do telefone",
  voiceLabel: "Voz",
  spokenLabel: "Avisos falados",
  on: "Sim",
  off: "Não",
  test: "Testar voz",
};

const TABLES: Record<Lang, Record<Key, string>> = { es: ES, en: EN, pt: PT };

/** The device language when it is one of ours; anything else falls back to English. */
export function deviceLanguage(): Lang {
  try {
    const code = getLocales()[0]?.languageCode;
    return code === "es" || code === "pt" ? code : "en";
  } catch {
    return "en";
  }
}

let current: Lang = deviceLanguage();

/** Switch the strings t() returns. The screen re-renders from its own settings state. */
export function setLanguage(lang: Lang): void {
  current = lang;
}

export function t(key: Key): string {
  return TABLES[current][key];
}

/** The reason strings arrive already worded by rangyuu/ui.py:15 (REASONS) and are shown as-is. */
export function reasonAsGiven(reason: string): string {
  return reason;
}
