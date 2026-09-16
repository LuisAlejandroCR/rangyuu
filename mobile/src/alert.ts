// alert.ts: one haptic per state CHANGE, never one per frame. This is the reason the app exists:
// iOS Safari has no Vibration API, so web/haptics.js falls back to tone and voice on iPhone.
// Distinguished from state.ts, which decides nothing about feedback, only which states are legal.
import * as Haptics from "expo-haptics";

import { AVANZA, CUIDADO, PARA, SIN_CERTEZA, type ScreenState } from "./state";

/** Continuous firing is unusable, so the last announced state is remembered and compared. */
let last: ScreenState | null = null;

async function fire(state: ScreenState): Promise<void> {
  switch (state) {
    case AVANZA:
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      return;
    case CUIDADO:
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      return;
    case PARA:
      // Two heavy taps: the only pattern that must be distinguishable without looking.
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      return;
    case SIN_CERTEZA:
    default:
      await Haptics.selectionAsync();
  }
}

/**
 * Announce a state if — and only if — it differs from the last one announced.
 *
 * Returns true when something actually fired, so the screen can show a change count instead of
 * the user having to trust that it is not buzzing every frame.
 */
export async function announce(state: ScreenState): Promise<boolean> {
  if (state === last) return false;
  last = state;
  try {
    await fire(state);
  } catch {
    // A device without a taptic engine is not an error; it just gets the visual state.
    return false;
  }
  return true;
}

/** Forget the last state, so the next reading announces itself. Called when capture stops. */
export function reset(): void {
  last = null;
}
