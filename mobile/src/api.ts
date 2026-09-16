// api.ts: the only two backend routes this client knows, both read straight out of the Python.
// POST /api/space/observe  (rangyuu/webapp.py:104) and GET /api/health (rangyuu/webapp.py:67).
// Distinguished from config.ts, which resolves the address but knows no routes.
import { resolveBaseUrl } from "./config";
import { normalizeState, type ScreenState } from "./state";

/** The screen payload rangyuu/site.py:83 (`now`) returns, narrowed to what this app shows. */
export type NowPayload = {
  state: ScreenState;
  reason: string;
  detail: string;
  authorizes: boolean;
  decision: string;
  at: number | null;
};

/** What POST /api/space/observe answers: the onboard reading plus a full `now` (webapp.py:148). */
export type ObserveResult = {
  now: NowPayload;
  written: number;
  clearanceState: string | null;
  clearanceNote: string | null;
};

const REQUEST_TIMEOUT_MS = 6000;

async function postJson(path: string, body: unknown): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${resolveBaseUrl()}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`${path} -> ${response.status}`);
    return (await response.json()) as unknown;
  } finally {
    clearTimeout(timer);
  }
}

function readNow(value: unknown): NowPayload {
  const now = (value ?? {}) as Record<string, unknown>;
  return {
    state: normalizeState(now.state),
    reason: typeof now.reason === "string" ? now.reason : "",
    detail: typeof now.detail === "string" ? now.detail : "",
    // A missing `authorizes` is never read as permission.
    authorizes: now.authorizes === true,
    decision: typeof now.decision === "string" ? now.decision : "UNKNOWN",
    at: typeof now.at === "number" ? now.at : null,
  };
}

/**
 * Send one downscaled grayscale frame and return the decision the core made.
 *
 * The body shape is exactly what rangyuu/webapp.py:136 (`_observe`) validates: `width`,
 * `height` and a flat `gray` list of width*height samples, at most 65_536 of them.
 */
export async function observe(
  width: number,
  height: number,
  gray: number[],
): Promise<ObserveResult> {
  const payload = (await postJson("/api/space/observe", { width, height, gray })) as Record<
    string,
    unknown
  >;
  const clearance = (payload.clearance ?? {}) as Record<string, unknown>;
  return {
    now: readNow(payload.now),
    written: typeof payload.written === "number" ? payload.written : 0,
    clearanceState: typeof clearance.state === "string" ? clearance.state : null,
    clearanceNote: typeof payload.reason === "string" ? payload.reason : null,
  };
}

/** GET /api/health (rangyuu/webapp.py:67). Used once, to tell "backend down" from "camera down". */
export async function health(): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${resolveBaseUrl()}/api/health`, { signal: controller.signal });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}
