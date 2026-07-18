export const brand = {
  canvas: "#f4f2ed",
  surface: "#ffffff",
  surfaceSubtle: "#faf9f6",
  ink: "#171714",
  muted: "#716f68",
  line: "#dedad1",
  indigo: "#5847e8",
  indigoDark: "#4636c9",
  indigoSoft: "#efedff",
  positive: "#18794e",
  negative: "#b84b44",
  warning: "#96651b",
} as const;

export const space = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  10: 40,
  12: 48,
  16: 64,
} as const;

export const radius = {
  control: 7,
  sm: 9,
  md: 12,
  lg: 16,
  pill: 999,
} as const;

export const layout = {
  contentMax: 1396,
  sidebarWidth: 320,
  headerHeight: 68,
} as const;

export const motion = {
  fast: 120,
  default: 160,
  easing: "cubic-bezier(.2, .8, .2, 1)",
} as const;
