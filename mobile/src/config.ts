// config.ts: where the Python backend lives, resolved at runtime, never hardcoded to a machine.
// Order: EXPO_PUBLIC_RANGYUU_API, then the LAN host that is already serving this bundle, then
// localhost. Distinguished from api.ts, which knows the routes but not the address.
import Constants from "expo-constants";

const DEFAULT_PORT = 8080;

/** The host Expo Go downloaded this bundle from — normally the same machine running Python. */
function devServerHost(): string | null {
  const hostUri =
    Constants.expoConfig?.hostUri ??
    (Constants.expoGoConfig as { debuggerHost?: string } | undefined)?.debuggerHost ??
    null;
  if (!hostUri) return null;
  const host = hostUri.split("/")[0]?.split(":")[0];
  return host && host.length > 0 ? host : null;
}

export function resolveBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_RANGYUU_API;
  if (configured && configured.trim().length > 0) return configured.trim().replace(/\/+$/, "");
  const host = devServerHost();
  if (host) return `http://${host}:${DEFAULT_PORT}`;
  return `http://localhost:${DEFAULT_PORT}`;
}

/** How the base URL was chosen, so the screen can say it instead of the user guessing. */
export function baseUrlOrigin(): "env" | "lan" | "fallback" {
  if (process.env.EXPO_PUBLIC_RANGYUU_API?.trim()) return "env";
  return devServerHost() ? "lan" : "fallback";
}

/** Milliseconds between frames. Slow on purpose: one round trip per frame, not a video stream. */
export const FRAME_INTERVAL_MS = 700;

/** The sampling grid. Matches web/index.html's 64x36 canvas, and 64*36 is far under the
 *  65_536 ceiling that rangyuu/webapp.py:144 enforces on the gray array. */
export const SAMPLE_WIDTH = 64;
export const SAMPLE_HEIGHT = 36;
