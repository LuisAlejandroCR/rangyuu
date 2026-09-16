// state.ts: the four states the screen may show, and the one rule this client is allowed to apply.
// It does NOT re-derive anything: rangyuu/ui.py:45 (to_screen) already turned the core decision
// into a state, and duplicating that logic in JavaScript would let the two drift apart.
// Distinguished from api.ts, which fetches, and i18n.ts, which only translates labels.

export const AVANZA = "AVANZA";
export const CUIDADO = "CUIDADO";
export const PARA = "PARA";
export const SIN_CERTEZA = "SIN CERTEZA";

export type ScreenState =
  | typeof AVANZA
  | typeof CUIDADO
  | typeof PARA
  | typeof SIN_CERTEZA;

const KNOWN: readonly string[] = [AVANZA, CUIDADO, PARA, SIN_CERTEZA];

/**
 * Accept the state the core derived, or fall back to SIN CERTEZA.
 *
 * This is the only state rule on the client, and it can only move downward: anything this
 * build does not recognise becomes SIN CERTEZA. It can never turn a PARA into an AVANZA,
 * which is the invariant rangyuu/ui.py:56 protects (a HOLD is never softened, and CUIDADO
 * only ever degrades a PROCEED).
 */
export function normalizeState(value: unknown): ScreenState {
  return typeof value === "string" && KNOWN.includes(value)
    ? (value as ScreenState)
    : SIN_CERTEZA;
}

/** Whether a state authorizes movement. Display only — the core answers this in `authorizes`. */
export function isRejection(state: ScreenState): boolean {
  return state === PARA || state === SIN_CERTEZA;
}

export const STATE_COLOR: Record<ScreenState, string> = {
  [AVANZA]: "#2ecc71",
  [CUIDADO]: "#f1c40f",
  [PARA]: "#e74c3c",
  [SIN_CERTEZA]: "#8e9aa6",
};
