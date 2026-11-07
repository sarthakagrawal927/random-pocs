import { AbsoluteFill, Composition, Mix, registerRoot, useCurrentFrame } from "raea";
import * as Tone from "raea/tone";
import { DURATION, EVENTS, FPS, HARMONICS, NOTES, PURE, RECIPES, RICH, SOFT, THIRD, eventAt } from "./cues";

const C = { paper: "#f3efe5", ink: "#18323a", quiet: "#58686b", rule: "#c9cec5", orange: "#b44e24", teal: "#216e66", blue: "#4e6493" };
const COLORS = [C.orange, C.teal, C.blue];
const TAU = Math.PI * 2;
const clamp = (x: number) => Math.max(0, Math.min(1, x));
const smooth = (x: number) => { const p = clamp(x); return p * p * (3 - 2 * p); };
const out = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const mix = (a: number[], b: number[], p: number) => a.map((v, i) => lerp(v, b[i], smooth(p)));

Object.entries(RECIPES).forEach(([name, recipe]) => {
  const rms = Math.sqrt(recipe.reduce((s, a) => s + a * a, 0));
  recipe.forEach((a, i) => {
    if (!a) return;
    const synth = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "sine" },
      envelope: { attack: 0.035, decay: 0.08, sustain: 0.92, release: 0.22 },
      volume: -18 + 20 * Math.log10(a / rms),
      maxPolyphony: 4,
    }).connect(Tone.buses.music);
    EVENTS.filter(e => e.recipe === name).forEach(e => synth.triggerAttackRelease(e.hz * HARMONICS[i], e.length, e.at));
  });
});

function Label({ x, y, children, size = 34, color = C.quiet, width = 1700, family = "Arial", weight = 400, opacity = 1 }: any) {
  return <div style={{ position: "absolute", left: x, top: y, width, color, fontFamily: family, fontSize: size, fontWeight: weight, lineHeight: 1.15, opacity, whiteSpace: "pre-line" }}>{children}</div>;
}

function Fade({ t, start, end, children }: any) {
  const a = out((t - start) / 0.7) * (1 - smooth((t - end + 0.4) / 0.4));
  return a > 0 ? <AbsoluteFill style={{ opacity: a, transform: `translateY(${(1 - out((t - start) / 0.7)) * 18}px)` }}>{children}</AbsoluteFill> : null;
}

function Chapter({ number, title, detail }: any) {
  return <>
    <Label x={120} y={120} size={30} color={C.orange} weight={700}>{number}</Label>
    <Label x={120} y={176} size={88} color={C.ink} family="Georgia">{title}</Label>
    <Label x={124} y={292} size={39}>{detail}</Label>
  </>;
}

function wave(u: number, a: number[], phase = 0) {
  return a.reduce((s, v, i) => s + v * Math.sin(TAU * HARMONICS[i] * u + HARMONICS[i] * phase), 0);
}

function path(x: number, y: number, w: number, h: number, a: number[], phase = 0, cycles = 2, reveal = 1) {
  const n = Math.max(2, Math.round(500 * clamp(reveal)));
  return Array.from({ length: n + 1 }, (_, i) => {
    const u = i / 500;
    return `${i ? "L" : "M"}${(x + u * w).toFixed(2)},${(y - h * wave(u * cycles, a, phase)).toFixed(2)}`;
  }).join(" ");
}

function Svg({ children, opacity = 1 }: any) {
  return <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", left: 0, top: 0, opacity }}>{children}</svg>;
}

function Line({ x1, y1, x2, y2, color = C.rule, width = 2, dash }: any) {
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeDasharray={dash} />;
}

function Trace({ d, color = C.ink, width = 5, opacity = 1 }: any) {
  return <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" opacity={opacity} />;
}

function Grid({ x, y, w, h }: any) {
  return <>
    {[0, 0.25, 0.5, 0.75, 1].map((p, i) => <Line key={i} x1={x + p * w} y1={y - h} x2={x + p * w} y2={y + h} width={1} />)}
    <Line x1={x} y1={y} x2={x + w} y2={y} />
  </>;
}

function Scope({ a, phase, x = 760, y = 585, w = 1040, h = 160, color = C.ink, reveal = 1 }: any) {
  return <>
    <Grid x={x} y={y} w={w} h={h + 30} />
    <Trace d={path(x, y, w, h, a, phase, 2, reveal)} color={color} width={6} />
  </>;
}

function Spectrum({ a, x = 130, y = 750, scale = 220, gap = 145 }: any) {
  return <>
    {[0, 1, 2].map(i => <g key={i}>
      <rect x={x + i * gap} y={y - scale} width={44} height={scale} rx={8} fill={C.rule} opacity={0.3} />
      <rect x={x + i * gap} y={y - a[i] * scale} width={44} height={Math.max(0.1, a[i] * scale)} rx={8} fill={COLORS[i]} />
    </g>)}
  </>;
}

function Epicycles({ a, phase, x = 410, y = 580, scale = 152, connect = true }: any) {
  let px = x, py = y;
  const parts = a.map((amplitude, i) => {
    const r = amplitude * scale;
    const nx = px + r * Math.cos(HARMONICS[i] * phase);
    const ny = py - r * Math.sin(HARMONICS[i] * phase);
    const element = <g key={i}>
      <circle cx={px} cy={py} r={Math.max(0.1, r)} stroke={COLORS[i]} fill="none" strokeWidth={2} opacity={amplitude > 0.005 ? 0.45 : 0} />
      <Line x1={px} y1={py} x2={nx} y2={ny} color={COLORS[i]} width={5} />
      <circle cx={nx} cy={ny} r={i === 2 ? 8 : 6} fill={COLORS[i]} />
    </g>;
    px = nx; py = ny;
    return element;
  });
  return <>{parts}{connect && <Line x1={px} y1={py} x2={760} y2={py} color={C.quiet} dash="5 9" width={1.5} />}</>;
}

function Opening({ t }: { t: number }) {
  const rich = smooth((t - 3.7) / 0.5);
  const a = mix(SOFT, RICH, rich);
  const phase = -t * TAU * 0.32;
  return <Fade t={t} start={-0.7} end={7}>
    <Label x={120} y={128} size={30} color={C.orange} weight={700}>A SMALL LESSON IN LISTENING</Label>
    <Label x={112} y={218} size={124} color={C.ink} family="Georgia" width={1600}>{"The shape\nof a note."}</Label>
    <Label x={124} y={600} size={48} color={C.ink} width={720}>{"Same notes.\nA different color."}</Label>
    <Label x={124} y={826} size={32}>Listen to the phrase twice.</Label>
    <Svg>
      <Line x1={940} y1={570} x2={1800} y2={570} />
      <Trace d={path(940, 570, 860, 155, a, phase, 1.6)} width={7} color={rich > 0.5 ? C.teal : C.orange} />
      {[0, 1, 2].map(i => <circle key={i} cx={1110 + i * 230} cy={790} r={8 + a[i] * 26} fill={COLORS[i]} />)}
    </Svg>
    <Label x={1055} y={860} size={30} width={700} color={C.ink}>{rich > 0.5 ? "02 / More upper harmonics" : "01 / Fewer upper harmonics"}</Label>
  </Fade>;
}

function PureTone({ t }: { t: number }) {
  const s = t - 7;
  const phase = -s * TAU * 0.35;
  return <Fade t={t} start={7} end={18}>
    <Chapter number="01 / THE FUNDAMENTAL" title="Start with one wave." detail="A pure tone carries one frequency." />
    <Svg>
      <Epicycles a={PURE} phase={phase} y={585} scale={160} />
      <Scope a={PURE} phase={phase} color={C.orange} reveal={out(s / 1.5)} />
      <Line x1={760} y1={827} x2={1280} y2={827} color={C.orange} />
      <Line x1={760} y1={818} x2={760} y2={836} color={C.orange} />
      <Line x1={1280} y1={818} x2={1280} y2={836} color={C.orange} />
    </Svg>
    <Label x={252} y={790} size={58} color={C.orange} width={450}>220 Hz</Label>
    <Label x={270} y={862} size={30} width={450}>one frequency</Label>
    <Label x={830} y={853} size={30} width={600}>one cycle = 1 / 220 second</Label>
    <Label x={1295} y={916} size={28} width={550}>Motion slowed for visibility.</Label>
  </Fade>;
}

function Addition({ t }: { t: number }) {
  const a = t < 22 ? PURE : t < 25.5 ? mix(PURE, THIRD, (t - 22) / 0.4) : mix(THIRD, RICH, (t - 25.5) / 0.4);
  const phase = -(t - 18) * TAU * 0.28;
  const active = t < 22 ? 0 : t < 25.5 ? 1 : 2;
  const centers = [453, 573, 693];
  return <Fade t={t} start={18} end={32}>
    <Chapter number="02 / ADDITIVE SYNTHESIS" title="Simple waves. A richer sound." detail="Add selected harmonics: 1, 3 and 5 times the fundamental." />
    <Svg>
      {centers.map((cy, i) => <g key={i} opacity={i > active ? 0.18 : 1}>
        <Line x1={350} y1={cy} x2={880} y2={cy} width={1} />
        <Trace d={path(350, cy, 530, 80, a.map((v, k) => k === i ? v : 0), phase, 1)} color={COLORS[i]} width={4} />
        <Line x1={910} y1={cy} x2={1000} y2={573} color={COLORS[i]} width={2} />
      </g>)}
      <circle cx={1030} cy={573} r={35} fill={C.ink} />
      <Line x1={1015} y1={573} x2={1045} y2={573} color={C.paper} width={3} />
      <Line x1={1030} y1={558} x2={1030} y2={588} color={C.paper} width={3} />
      <Line x1={1080} y1={573} x2={1800} y2={573} />
      <Trace d={path(1080, 573, 720, 120, a, phase, 1.5)} color={C.ink} width={6} />
    </Svg>
    {centers.map((cy, i) => <Label key={i} x={120} y={cy - 24} size={42} color={COLORS[i]} width={250} opacity={i > active ? 0.25 : 1}>{["220 Hz", "660 Hz", "1100 Hz"][i]}</Label>)}
    <Label x={123} y={818} size={44} color={C.ink} width={1600}>{active === 0 ? "Hear the fundamental alone." : active === 1 ? "The third harmonic adds a new contour." : "The fifth adds another layer of detail."}</Label>
    <Label x={123} y={894} size={30} width={1600}>Each curve is a sine wave. Add their heights to get the dark curve.</Label>
  </Fade>;
}

function Recipe({ t }: { t: number }) {
  const rich = (t >= 35.5 && t < 38.5) || t >= 41.5;
  const change = t >= 41.5 ? 41.5 : t >= 38.5 ? 38.5 : t >= 35.5 ? 35.5 : 32;
  const a = mix(rich ? SOFT : RICH, rich ? RICH : SOFT, (t - change) / 0.3);
  const phase = -(t - 32) * TAU * 0.28;
  return <Fade t={t} start={32} end={45}>
    <Chapter number="03 / TONE COLOR" title="Same pitch. A new recipe." detail="The fundamental stays at 220 Hz. Listen to the upper harmonics." />
    <Svg>
      <Spectrum a={a} x={175} y={740} gap={155} scale={300} />
      <Scope a={a} phase={phase} x={760} y={585} h={160} color={rich ? C.teal : C.orange} />
    </Svg>
    {["1×", "3×", "5×"].map((v, i) => <Label key={v} x={160 + i * 155} y={775} size={34} width={150} color={COLORS[i]}>{v}</Label>)}
    <Label x={123} y={870} size={48} width={650} color={C.ink}>{rich ? "More upper harmonics" : "Fewer upper harmonics"}</Label>
    <Label x={1060} y={840} size={58} width={650} color={rich ? C.teal : C.orange}>{rich ? "Brighter" : "Softer"}</Label>
    <Label x={1130} y={918} size={28} width={700}>Sound examples matched in RMS level.</Label>
  </Fade>;
}

function Melody({ t }: { t: number }) {
  const n = NOTES.findLast(n => t >= n.at) ?? NOTES[0];
  const noteIndex = NOTES.indexOf(n);
  const envelope = out((t - n.at) / 0.06) * (1 - smooth((t - n.at - n.length) / 0.22));
  const phase = -t * TAU * 0.24;
  const xs = [230, 410, 590, 770, 950, 1130, 1310, 1490, 1670];
  const ys = [775, 720, 625, 665, 720, 775, 870, 820, 775];
  return <Fade t={t} start={45} end={56}>
    <Chapter number="04 / FROM TONES TO MUSIC" title="Keep the recipe. Move the notes." detail="Every harmonic follows the melody in the same proportion." />
    <Svg>
      <Line x1={120} y1={505} x2={1800} y2={505} />
      <Trace d={path(120, 505, 1680, 78 * (0.6 + 0.4 * envelope), RICH, phase, 3 * n.hz / 220)} color={C.ink} width={5} />
      <Trace d={xs.map((x, i) => `${i ? "L" : "M"}${x},${ys[i]}`).join(" ")} color={C.rule} width={2} />
      {xs.map((x, i) => <g key={i}>
        <Line x1={x} y1={ys[i]} x2={x} y2={920} color={C.rule} width={1} />
        <circle cx={x} cy={ys[i]} r={i === noteIndex ? 26 + 7 * envelope : 10} fill={i <= noteIndex ? C.orange : C.rule} />
        {i === noteIndex && <circle cx={x} cy={ys[i]} r={48 + 18 * (1 - envelope)} fill="none" stroke={C.orange} strokeWidth={2} opacity={envelope} />}
      </g>)}
    </Svg>
    <Label x={124} y={122} size={30} width={1650} color={C.orange} weight={700}>04 / FROM TONES TO MUSIC</Label>
    <Label x={124} y={898} size={32} width={600} color={C.ink}>{`${n.name}  /  ${Math.round(n.hz)} Hz`}</Label>
    <Label x={1150} y={898} size={32} width={700}>1× + ⅓ at 3× + ⅕ at 5×</Label>
  </Fade>;
}

function Ending({ t }: { t: number }) {
  const a = mix(RICH, SOFT, (t - 59.5) / 1);
  const phase = -t * TAU * 0.22;
  return <Fade t={t} start={56} end={64.5}>
    <Label x={120} y={122} size={30} color={C.orange} weight={700}>NOW YOU CAN HEAR IT.</Label>
    <Label x={112} y={205} size={102} color={C.ink} family="Georgia">One pitch. Many colors.</Label>
    <Svg>
      <Epicycles a={a} phase={phase} x={370} y={525} scale={95} connect={false} />
      <Trace d={path(620, 525, 1180, 105, a, phase, 2.2)} color={C.orange} width={5} />
    </Svg>
    <Label x={124} y={710} size={50} color={C.ink} width={1600}>Pitch follows how fast the pattern repeats.</Label>
    <Label x={124} y={794} size={50} color={C.ink} width={1650}>Harmonic balance helps shape its tone color.</Label>
    <Label x={124} y={910} size={31} width={1650}>Timbre also depends on attack, decay and other changes through time.</Label>
  </Fade>;
}

function Film() {
  const t = useCurrentFrame() / FPS;
  const event = eventAt(t);
  return <AbsoluteFill style={{ background: C.paper, fontFamily: "Arial", color: C.ink, overflow: "hidden" }}>
    <Opening t={t} />
    <PureTone t={t} />
    <Addition t={t} />
    <Recipe t={t} />
    <Melody t={t} />
    <Ending t={t} />
    <div style={{ position: "absolute", left: 0, top: 1074, height: 6, width: 1920 * t / DURATION, background: C.orange }} />
    <div style={{ position: "absolute", left: 1857, top: 124, width: 11, height: 11, borderRadius: 6, background: C.orange, opacity: event ? 0.8 : 0.15 }} />
    <Mix lufs={-14} ceiling={-1.5} />
  </AbsoluteFill>;
}

registerRoot(() => <Composition id="shape-of-a-note" component={Film} width={1920} height={1080} fps={FPS} durationInFrames={DURATION * FPS} />);
