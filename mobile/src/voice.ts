// voice.ts: the spoken alert — one bundled ElevenLabs clip per cue, voice and language.
// The clips ship inside the app, so speaking needs no key and no network; if a clip fails to
// play, the same words go to the system voice. Distinguished from alert.ts, which decides WHEN
// to speak (once per state change), and i18n.ts, which only words the screen.
import { createAudioPlayer, setAudioModeAsync, type AudioPlayer } from "expo-audio";
import * as Speech from "expo-speech";

import type { Lang } from "./i18n";
import { AVANZA, CUIDADO, PARA, type ScreenState } from "./state";

export type VoiceId = "lumina" | "carlos";
export type Cue = "proceed" | "caution" | "hold" | "unknown" | "linkLost" | "start" | "stop";

export const VOICES: readonly VoiceId[] = ["lumina", "carlos"];
export const VOICE_NAME: Record<VoiceId, string> = { lumina: "Lumina", carlos: "Carlos Andrés" };

/** The words in every clip. Also what the system voice says when a clip cannot play. */
export const PHRASES: Record<Lang, Record<Cue, string>> = {
  es: {
    proceed: "Despejado. Puedes avanzar.",
    caution: "Cuidado. Ve despacio.",
    hold: "Para. No avances.",
    unknown: "Sin certeza. Espera.",
    linkLost: "Se perdió el enlace con el sitio. Espera.",
    start: "Empezando.",
    stop: "Detenido.",
  },
  en: {
    proceed: "Clear ahead. You can go.",
    caution: "Caution. Go slowly.",
    hold: "Stop. Do not go ahead.",
    unknown: "Not certain. Please wait.",
    linkLost: "Lost the link to the site. Please wait.",
    start: "Starting.",
    stop: "Stopped.",
  },
  pt: {
    proceed: "Caminho livre. Pode avançar.",
    caution: "Cuidado. Vá devagar.",
    hold: "Pare. Não avance.",
    unknown: "Sem certeza. Aguarde.",
    linkLost: "Perdemos a conexão com o local. Aguarde.",
    start: "Iniciando.",
    stop: "Parado.",
  },
};

const SPEECH_LOCALE: Record<Lang, string> = { es: "es-ES", en: "en-US", pt: "pt-BR" };

// Metro bundles only static requires, so every clip is spelled out. The Record types make a
// missing clip a compile error rather than a silent gap on the road.
const CLIPS: Record<VoiceId, Record<Lang, Record<Cue, number>>> = {
  lumina: {
    es: {
      proceed: require("../assets/voices/lumina/es/proceed.mp3"),
      caution: require("../assets/voices/lumina/es/caution.mp3"),
      hold: require("../assets/voices/lumina/es/hold.mp3"),
      unknown: require("../assets/voices/lumina/es/unknown.mp3"),
      linkLost: require("../assets/voices/lumina/es/linkLost.mp3"),
      start: require("../assets/voices/lumina/es/start.mp3"),
      stop: require("../assets/voices/lumina/es/stop.mp3"),
    },
    en: {
      proceed: require("../assets/voices/lumina/en/proceed.mp3"),
      caution: require("../assets/voices/lumina/en/caution.mp3"),
      hold: require("../assets/voices/lumina/en/hold.mp3"),
      unknown: require("../assets/voices/lumina/en/unknown.mp3"),
      linkLost: require("../assets/voices/lumina/en/linkLost.mp3"),
      start: require("../assets/voices/lumina/en/start.mp3"),
      stop: require("../assets/voices/lumina/en/stop.mp3"),
    },
    pt: {
      proceed: require("../assets/voices/lumina/pt/proceed.mp3"),
      caution: require("../assets/voices/lumina/pt/caution.mp3"),
      hold: require("../assets/voices/lumina/pt/hold.mp3"),
      unknown: require("../assets/voices/lumina/pt/unknown.mp3"),
      linkLost: require("../assets/voices/lumina/pt/linkLost.mp3"),
      start: require("../assets/voices/lumina/pt/start.mp3"),
      stop: require("../assets/voices/lumina/pt/stop.mp3"),
    },
  },
  carlos: {
    es: {
      proceed: require("../assets/voices/carlos/es/proceed.mp3"),
      caution: require("../assets/voices/carlos/es/caution.mp3"),
      hold: require("../assets/voices/carlos/es/hold.mp3"),
      unknown: require("../assets/voices/carlos/es/unknown.mp3"),
      linkLost: require("../assets/voices/carlos/es/linkLost.mp3"),
      start: require("../assets/voices/carlos/es/start.mp3"),
      stop: require("../assets/voices/carlos/es/stop.mp3"),
    },
    en: {
      proceed: require("../assets/voices/carlos/en/proceed.mp3"),
      caution: require("../assets/voices/carlos/en/caution.mp3"),
      hold: require("../assets/voices/carlos/en/hold.mp3"),
      unknown: require("../assets/voices/carlos/en/unknown.mp3"),
      linkLost: require("../assets/voices/carlos/en/linkLost.mp3"),
      start: require("../assets/voices/carlos/en/start.mp3"),
      stop: require("../assets/voices/carlos/en/stop.mp3"),
    },
    pt: {
      proceed: require("../assets/voices/carlos/pt/proceed.mp3"),
      caution: require("../assets/voices/carlos/pt/caution.mp3"),
      hold: require("../assets/voices/carlos/pt/hold.mp3"),
      unknown: require("../assets/voices/carlos/pt/unknown.mp3"),
      linkLost: require("../assets/voices/carlos/pt/linkLost.mp3"),
      start: require("../assets/voices/carlos/pt/start.mp3"),
      stop: require("../assets/voices/carlos/pt/stop.mp3"),
    },
  },
};

/** The cue for a screen state. SIN CERTEZA is the fallback, matching normalizeState. */
export function stateCue(state: ScreenState): Cue {
  switch (state) {
    case AVANZA:
      return "proceed";
    case CUIDADO:
      return "caution";
    case PARA:
      return "hold";
    default:
      return "unknown";
  }
}

let player: AudioPlayer | null = null;
let audioModeSet = false;

/**
 * Speak a cue. A new cue cuts the one still playing: if PARA arrives while "you can go" is
 * playing, PARA is what the driver must hear.
 *
 * Returns how it was spoken, so a caller can tell a silent failure from a spoken alert.
 */
export async function say(cue: Cue, voice: VoiceId, lang: Lang): Promise<"clip" | "speech" | "none"> {
  try {
    if (!audioModeSet) {
      // A safety alert must sound with the iPhone's silent switch on.
      await setAudioModeAsync({ playsInSilentMode: true });
      audioModeSet = true;
    }
    Speech.stop();
    player?.remove();
    player = createAudioPlayer(CLIPS[voice][lang][cue]);
    player.play();
    return "clip";
  } catch {
    try {
      Speech.stop();
      Speech.speak(PHRASES[lang][cue], { language: SPEECH_LOCALE[lang] });
      return "speech";
    } catch {
      return "none";
    }
  }
}
