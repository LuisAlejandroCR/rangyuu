// settings.ts: the three personal choices — language, voice, spoken alerts — kept on the phone.
// Anything unreadable falls back to the defaults, so a corrupt value can never silence alerts.
// Distinguished from voice.ts, which plays a cue, and i18n.ts, which holds the screen strings.
import AsyncStorage from "@react-native-async-storage/async-storage";

import type { Lang } from "./i18n";
import { VOICES, type VoiceId } from "./voice";

export type LanguageChoice = "auto" | Lang;

export interface Settings {
  language: LanguageChoice;
  voice: VoiceId;
  spoken: boolean;
}

export const DEFAULT_SETTINGS: Settings = { language: "auto", voice: "lumina", spoken: true };

const KEY = "rangyuu.settings.v1";
const LANGUAGES: readonly LanguageChoice[] = ["auto", "es", "en", "pt"];

/** Keep only fields that are well-formed; everything else takes its default. */
export function parseSettings(raw: string | null): Settings {
  if (!raw) return DEFAULT_SETTINGS;
  try {
    const value = JSON.parse(raw) as Partial<Record<keyof Settings, unknown>>;
    return {
      language: LANGUAGES.includes(value.language as LanguageChoice)
        ? (value.language as LanguageChoice)
        : DEFAULT_SETTINGS.language,
      voice: VOICES.includes(value.voice as VoiceId) ? (value.voice as VoiceId) : DEFAULT_SETTINGS.voice,
      spoken: typeof value.spoken === "boolean" ? value.spoken : DEFAULT_SETTINGS.spoken,
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export async function loadSettings(): Promise<Settings> {
  try {
    return parseSettings(await AsyncStorage.getItem(KEY));
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export async function saveSettings(settings: Settings): Promise<void> {
  try {
    await AsyncStorage.setItem(KEY, JSON.stringify(settings));
  } catch {
    // Not persisting is an inconvenience, not a safety issue: the choice still applies now.
  }
}
