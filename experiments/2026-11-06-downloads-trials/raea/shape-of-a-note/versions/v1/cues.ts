export const FPS = 30;
export const DURATION = 64;
export const HARMONICS = [1, 3, 5];
export const SOFT = [1, 0.07, 0.025];
export const RICH = [1, 1 / 3, 1 / 5];
export const PURE = [1, 0, 0];
export const THIRD = [1, 1 / 3, 0];
export const NOTES = [
  { at: 45, hz: 220, name: "A3", length: 0.82 },
  { at: 46, hz: 261.625565, name: "C4", length: 0.82 },
  { at: 47, hz: 329.627557, name: "E4", length: 0.82 },
  { at: 48, hz: 293.664768, name: "D4", length: 0.82 },
  { at: 49, hz: 261.625565, name: "C4", length: 0.82 },
  { at: 50, hz: 220, name: "A3", length: 0.82 },
  { at: 51, hz: 164.813778, name: "E3", length: 0.82 },
  { at: 52, hz: 195.997718, name: "G3", length: 0.82 },
  { at: 53, hz: 220, name: "A3", length: 2.5 },
];

export const EVENTS = [
  ...[1, 2, 3].map((at, i) => ({ at, hz: [220, 261.625565, 329.627557][i], length: 0.75, recipe: "soft" })),
  ...[4, 5, 6].map((at, i) => ({ at, hz: [220, 261.625565, 329.627557][i], length: 0.75, recipe: "rich" })),
  { at: 8, hz: 220, length: 3, recipe: "pure" },
  { at: 12, hz: 220, length: 4.8, recipe: "pure" },
  { at: 18.5, hz: 220, length: 3.1, recipe: "pure" },
  { at: 22, hz: 220, length: 3.1, recipe: "third" },
  { at: 25.5, hz: 220, length: 5.7, recipe: "rich" },
  { at: 32.5, hz: 220, length: 2.5, recipe: "soft" },
  { at: 35.5, hz: 220, length: 2.5, recipe: "rich" },
  { at: 38.5, hz: 220, length: 2.5, recipe: "soft" },
  { at: 41.5, hz: 220, length: 2.5, recipe: "rich" },
  ...NOTES.map(n => ({ ...n, recipe: "rich" })),
  { at: 57, hz: 220, length: 2, recipe: "rich" },
  { at: 60, hz: 220, length: 2.5, recipe: "soft" },
];

export const RECIPES: Record<string, number[]> = { pure: PURE, third: THIRD, soft: SOFT, rich: RICH };

export function eventAt(t: number) {
  return EVENTS.findLast(e => t >= e.at && t < e.at + e.length + 0.24);
}
