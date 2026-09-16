// i18n.ts: the small hand-rolled string table, device language first, English as fallback.
// Same rule as the web app, and deliberately no i18n library for a screen with a dozen strings.
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
  | "backendUnreachable"
  | "framesLabel"
  | "alertsLabel"
  | "decisionLabel"
  | "onboardLabel"
  | "authorized"
  | "notAuthorized"
  | "linkLost"
  | "capturing"
  | "idle";

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
  backendUnreachable: "Backend unreachable",
  framesLabel: "Frames sent",
  alertsLabel: "Alerts fired",
  decisionLabel: "Core decision",
  onboardLabel: "On-board camera",
  authorized: "Route authorized",
  notAuthorized: "Route not authorized",
  linkLost: "lost the link to the site",
  capturing: "capturing",
  idle: "stopped",
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
  backendUnreachable: "Backend inalcanzable",
  framesLabel: "Frames enviados",
  alertsLabel: "Avisos emitidos",
  decisionLabel: "Decisión del núcleo",
  onboardLabel: "Cámara de a bordo",
  authorized: "Ruta autorizada",
  notAuthorized: "Ruta no autorizada",
  linkLost: "se perdió el enlace con el sitio",
  capturing: "capturando",
  idle: "detenido",
};

/** Spanish only when the device asks for it; anything else falls back to English. */
function pickTable(): Record<Key, string> {
  try {
    const code = getLocales()[0]?.languageCode;
    return code === "es" ? ES : EN;
  } catch {
    return EN;
  }
}

const TABLE = pickTable();

export function t(key: Key): string {
  return TABLE[key];
}

/** The reason strings arrive already worded by rangyuu/ui.py:15 (REASONS) and are shown as-is. */
export function reasonAsGiven(reason: string): string {
  return reason;
}
