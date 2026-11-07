import React from 'react';
import { AbsoluteFill, Composition, registerRoot, useCurrentFrame } from 'remotion';
import { C } from './brand/tokens';

const TAU = Math.PI * 2;
const HARMONICS = [1, 3, 5];
const AMPLITUDES = [1, 1 / 3, 1 / 5];
const COLORS = [C.accent, C.ink, C.mute];

const Overlay: React.FC = () => {
  const frame = useCurrentFrame();
  const phase = -TAU * frame / 240;
  let x = 230;
  let y = 360;
  const circles = AMPLITUDES.map((amplitude, index) => {
    const radius = 100 * amplitude;
    const nextX = x + radius * Math.cos(HARMONICS[index] * phase);
    const nextY = y - radius * Math.sin(HARMONICS[index] * phase);
    const part = <g key={index}>
      <circle cx={x} cy={y} r={radius} stroke={COLORS[index]} strokeWidth={2.5} fill="none" opacity={0.65} />
      <line x1={x} y1={y} x2={nextX} y2={nextY} stroke={COLORS[index]} strokeWidth={5} />
      <circle cx={nextX} cy={nextY} r={7} fill={COLORS[index]} />
    </g>;
    x = nextX;
    y = nextY;
    return part;
  });
  const curve = Array.from({ length: 601 }, (_, index) => {
    const u = index / 600;
    const height = AMPLITUDES.reduce((sum, a, i) => sum + a * Math.sin(HARMONICS[i] * (TAU * u * 2 + phase)), 0);
    return `${index ? 'L' : 'M'}${480 + 710 * u},${360 - 100 * height}`;
  }).join(' ');
  return <AbsoluteFill>
    <svg width={1280} height={720} viewBox="0 0 1280 720">
      {circles}
      <line x1={x} y1={y} x2={480} y2={y} stroke={COLORS[0]} strokeWidth={2} strokeDasharray="5 8" />
      <path d={curve} stroke={COLORS[0]} strokeWidth={6} fill="none" strokeLinecap="round" />
    </svg>
  </AbsoluteFill>;
};

registerRoot(() => <Composition id="WaveOverlay" component={Overlay} width={1280} height={720} fps={60} durationInFrames={240} />);
