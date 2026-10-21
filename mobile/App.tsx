// App.tsx: the whole app — one screen, one capture loop, one state readout.
// It captures, posts and displays. It decides nothing: rangyuu/ui.py derives the state and this
// file renders it. Distinguished from src/, which holds the pieces this screen wires together.
import { CameraView, useCameraPermissions } from "expo-camera";
import { StatusBar } from "expo-status-bar";
import { useCallback, useEffect, useRef, useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

import { health, observe, type NowPayload } from "./src/api";
import { announce, reset as resetAlerts } from "./src/alert";
import { baseUrlOrigin, FRAME_INTERVAL_MS, resolveBaseUrl } from "./src/config";
import { toGraySamples } from "./src/frame";
import { t } from "./src/i18n";
import { SIN_CERTEZA, STATE_COLOR, type ScreenState } from "./src/state";
import { COLORS } from "./src/theme";

const OFFLINE: NowPayload = {
  state: SIN_CERTEZA,
  reason: "",
  detail: "",
  authorizes: false,
  decision: "UNKNOWN",
  at: null,
};

export default function App() {
  const [permission, requestPermission] = useCameraPermissions();
  const [running, setRunning] = useState(false);
  const [now, setNow] = useState<NowPayload | null>(null);
  const [frames, setFrames] = useState(0);
  const [alerts, setAlerts] = useState(0);
  const [onboard, setOnboard] = useState<string | null>(null);
  const [backendUp, setBackendUp] = useState<boolean | null>(null);

  const camera = useRef<CameraView | null>(null);
  // A ref, not state: the loop must read the live value without being re-created each tick.
  const runningRef = useRef(false);
  const busy = useRef(false);

  useEffect(() => {
    health().then(setBackendUp).catch(() => setBackendUp(false));
  }, []);

  const applyState = useCallback(async (next: NowPayload, onboardState: string | null) => {
    setNow(next);
    setOnboard(onboardState);
    // One alert per state change: `announce` returns false when the state did not move.
    if (await announce(next.state)) setAlerts((n) => n + 1);
  }, []);

  const tick = useCallback(async () => {
    if (!runningRef.current || busy.current || !camera.current) return;
    busy.current = true;
    try {
      const shot = await camera.current.takePictureAsync({
        quality: 0.3,
        // `skipProcessing` is faster but, per the expo-camera docs, leaves the orientation
        // uncertain. A floor-ahead reading that may be rotated is worse than a slower one.
        shutterSound: false,
        base64: false,
      });
      if (!shot?.uri) throw new Error("the camera returned no frame");
      const { width, height, gray } = await toGraySamples(shot.uri);
      const result = await observe(width, height, gray);
      setFrames((n) => n + 1);
      setBackendUp(true);
      await applyState(result.now, result.clearanceState);
    } catch (caught) {
      setBackendUp(false);
      // A lost link is not permission to move: it degrades to SIN CERTEZA, never to AVANZA.
      await applyState({ ...OFFLINE, reason: t("linkLost") }, null);
    } finally {
      busy.current = false;
    }
  }, [applyState]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      void tick();
    }, FRAME_INTERVAL_MS);
    return () => clearInterval(id);
  }, [running, tick]);

  const toggle = useCallback(() => {
    setRunning((was) => {
      const next = !was;
      runningRef.current = next;
      if (!next) {
        resetAlerts();
      }
      return next;
    });
  }, []);

  if (!permission) return <View style={styles.root} />;

  if (!permission.granted) {
    return (
      <SafeAreaView style={styles.root}>
        <StatusBar style="light" />
        <View style={styles.centered}>
          <Text style={styles.heading}>{t("permissionTitle")}</Text>
          <Text style={styles.body}>{t("permissionBody")}</Text>
          <Pressable style={styles.button} onPress={() => void requestPermission()}>
            <Text style={styles.buttonText}>{t("permissionGrant")}</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const state: ScreenState = now?.state ?? SIN_CERTEZA;

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" />

      <View style={styles.preview}>
        <CameraView ref={camera} style={StyleSheet.absoluteFill} facing="back" />
      </View>

      <View style={[styles.banner, { borderColor: STATE_COLOR[state] }]}>
        <Text style={[styles.state, { color: STATE_COLOR[state] }]}>{state}</Text>
        <Text style={styles.reason}>{now?.reason || t("waiting")}</Text>
        {now?.detail ? <Text style={styles.detail}>{now.detail}</Text> : null}
        <Text style={styles.authorizes}>
          {now?.authorizes ? t("authorized") : t("notAuthorized")}
        </Text>
      </View>

      <View style={styles.meta}>
        <Row label={t("backendLabel")} value={`${resolveBaseUrl()} (${baseUrlOrigin()})`} />
        <Row label={t("decisionLabel")} value={now?.decision ?? "—"} />
        <Row label={t("onboardLabel")} value={onboard ?? "—"} />
        <Row label={t("framesLabel")} value={String(frames)} />
        <Row label={t("alertsLabel")} value={String(alerts)} />
      </View>

      <View style={styles.actionWrap}>
        {backendUp === false ? (
          <Text style={styles.backendDown} accessibilityLiveRegion="polite">
            {running ? t("backendLostWhileRunning") : t("backendDown")}
          </Text>
        ) : null}
        <Pressable style={[styles.button, running && styles.buttonStop]} onPress={toggle}>
          <Text style={styles.buttonText}>{running ? t("stop") : t("start")}</Text>
        </Pressable>
      </View>
      <Text style={styles.status}>{running ? t("capturing") : t("idle")}</Text>
    </SafeAreaView>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue} numberOfLines={1}>
        {value}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: COLORS.background, paddingHorizontal: 16 },
  centered: { flex: 1, justifyContent: "center", gap: 16 },
  preview: { height: 200, borderRadius: 12, overflow: "hidden", marginTop: 8, backgroundColor: COLORS.surface },
  banner: { borderWidth: 2, borderRadius: 12, padding: 16, marginTop: 12, gap: 4 },
  state: { fontSize: 38, fontWeight: "800", letterSpacing: 1 },
  reason: { color: COLORS.text, fontSize: 16 },
  detail: { color: COLORS.secondary, fontSize: 13 },
  authorizes: { color: COLORS.secondary, fontSize: 13, marginTop: 4 },
  meta: { marginTop: 12, gap: 6 },
  row: { flexDirection: "row", justifyContent: "space-between", gap: 12 },
  rowLabel: { color: COLORS.muted, fontSize: 13 },
  rowValue: { color: COLORS.text, fontSize: 13, flexShrink: 1 },
  heading: { color: COLORS.heading, fontSize: 24, fontWeight: "700" },
  body: { color: COLORS.secondary, fontSize: 15, lineHeight: 21 },
  actionWrap: { marginTop: "auto" },
  backendDown: {
    color: STATE_COLOR[SIN_CERTEZA],
    fontSize: 13,
    textAlign: "center",
    marginBottom: 8,
  },
  button: {
    backgroundColor: COLORS.action,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 8,
  },
  buttonStop: { backgroundColor: COLORS.stop },
  buttonText: { color: "#fff", fontSize: 17, fontWeight: "700" },
  status: { color: COLORS.muted, fontSize: 12, textAlign: "center", paddingVertical: 8 },
});
