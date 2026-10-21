// theme.ts: mobile equivalents of the visual tokens in web/styles.css.
// Keep the dark Expo surface while sharing action and semantic state colors across clients.
export const COLORS = {
  background: "#0e1116",
  surface: "#1b222c",
  text: "#d7dde5",
  secondary: "#98a3b0",
  muted: "#7e8a97",
  heading: "#f2f5f8",
  link: "#9cc1ff",
  action: "#0a7499",
  stop: "#c8372d",
  error: "#c8372d",
  // The SIN CERTEZA blue lightened for small text: #4a6fa5 gives 3.70:1 on `background`, this
  // gives 4.94:1 (WCAG AA asks 4.5:1 below 18 px). Same hue, so it still reads as "uncertain".
  uncertainText: "#6084b8",
} as const;
