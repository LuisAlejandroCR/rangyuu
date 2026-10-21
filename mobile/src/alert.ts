// alert.ts: one haptic and one spoken cue per state CHANGE, never one per frame. Haptics say that
// something changed; the voice says what. Distinguished from voice.ts, which knows how to play a
// cue but not when, and state.ts, which decides nothing about feedback.
import * as Haptics from "expo-haptics";

import type { Lang } from "./i18n";
import { AVANZA, CUIDADO, PARA, SIN_CERTEZA, type ScreenState } from "./state";
import { say, stateCue, type Cue, type VoiceId } from "./voice";

/** Continuous firing is unusable, so the last announced state is remembered and compared. */
let last: ScreenState | null = null;

/** Who speaks, in which language — or null when spoken alerts are off. */
let speaker: { voice: VoiceId; lang: Lang } | null = null;

export function setSpeaker(next: { voice: VoiceId; lang: Lang } | null): void {
  speaker = next;
}

/** Speak a cue outside a state change (start, stop, the test button), if alerts are on. */
export async function speak(cue: Cue): Promise<void> {
  if (speaker) await say(cue, speaker.voice, speaker.lang);
}

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
 * `cue` overrides what is said — a lost link is SIN CERTEZA on screen but says why out loud.
 * Returns true when something actually fired, so the screen can show a change count instead of
 * the user having to trust that it is not buzzing every frame.
 */
export async function announce(state: ScreenState, cue?: Cue): Promise<boolean> {
  if (state === last) return false;
  last = state;
  let fired = false;
  try {
    await fire(state);
    fired = true;
  } catch {
    // A device without a taptic engine is not an error; it just gets the voice and the screen.
  }
  if (speaker && (await say(cue ?? stateCue(state), speaker.voice, speaker.lang)) !== "none") {
    fired = true;
  }
  return fired;
}

/** Forget the last state, so the next reading announces itself. Called when capture stops. */
export function reset(): void {
  last = null;
}
