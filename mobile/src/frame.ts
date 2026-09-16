// frame.ts: one camera frame turned into the flat grayscale array the backend expects.
// React Native has no canvas, so the path is: still capture -> resize to 64x36 JPEG -> decode in
// pure JS -> luminance. Distinguished from api.ts, which sends the result but never builds it.
import { ImageManipulator, SaveFormat } from "expo-image-manipulator";
import { decode as decodeJpeg } from "jpeg-js";

import { SAMPLE_HEIGHT, SAMPLE_WIDTH } from "./config";

/** base64 -> bytes. Hermes ships atob, so this needs no extra dependency. */
function base64ToBytes(base64: string): Uint8Array {
  const binary = globalThis.atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

/**
 * Downscale a captured image to SAMPLE_WIDTH x SAMPLE_HEIGHT and return its luminance samples.
 *
 * The coefficients are the same ones web/app.js:254 uses, so both clients hand the Python
 * detector the same numbers for the same scene.
 */
export async function toGraySamples(
  uri: string,
): Promise<{ width: number; height: number; gray: number[] }> {
  const context = ImageManipulator.manipulate(uri);
  context.resize({ width: SAMPLE_WIDTH, height: SAMPLE_HEIGHT });
  const image = await context.renderAsync();
  const saved = await image.saveAsync({ format: SaveFormat.JPEG, compress: 1, base64: true });
  if (!saved.base64) throw new Error("the resized frame came back without pixels");

  const decoded = decodeJpeg(base64ToBytes(saved.base64), { useTArray: true });
  const { width, height, data } = decoded;
  const gray = new Array<number>(width * height);
  for (let i = 0, p = 0; p < gray.length; i += 4, p += 1) {
    gray[p] = Math.round(
      0.299 * (data[i] ?? 0) + 0.587 * (data[i + 1] ?? 0) + 0.114 * (data[i + 2] ?? 0),
    );
  }
  return { width, height, gray };
}
