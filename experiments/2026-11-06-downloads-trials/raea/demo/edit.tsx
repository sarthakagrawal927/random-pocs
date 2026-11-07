import { AbsoluteFill, Composition, Easing, interpolate, registerRoot, useCurrentFrame } from "raea";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

function Demo() {
  const f = useCurrentFrame();
  const enter = interpolate(f, [0, 24], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const progress = interpolate(f, [0, 179], [0, 1], clamp);
  const colors = ["#f5a648", "#f26b52", "#f5db9a"];
  return (
    <AbsoluteFill style={{ background: "#121719", fontFamily: "Arial", color: "#faf6eb", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 120, top: 180, fontSize: 150, fontWeight: 700,
        opacity: enter, transform: `translateY(${(1 - enter) * 36}px)` }}>raea</div>
      <div style={{ position: "absolute", left: 128, top: 390, fontSize: 60,
        opacity: enter, transform: `translateY(${(1 - enter) * 20}px)` }}>React to pixels.</div>
      <div style={{ position: "absolute", left: 128, top: 520, fontSize: 60, color: "#acb8bc", opacity: enter }}>Local GPU render</div>
      <div style={{ position: "absolute", left: 1140, top: 240, width: 480, height: 480, borderRadius: 240,
        border: "2px solid #3c494e", opacity: 1 }} />
      <div style={{ position: "absolute", left: 1220, top: 320, width: 320, height: 320, borderRadius: 160,
        border: "2px solid #3c494e", opacity: 1 }} />
      {colors.map((color, i) => {
        const angle = f / 180 * Math.PI * 2 + i * Math.PI * 2 / 3;
        const r = 160 + i * 40;
        const size = 88 + i * 24;
        return <div key={i} style={{ position: "absolute", left: 1380 + Math.cos(angle) * r - size / 2,
          top: 480 + Math.sin(angle) * r - size / 2, width: size, height: size, borderRadius: size / 2,
          background: color, opacity: enter, transform: `scale(${0.6 + 0.4 * enter})` }} />;
      })}
      <div style={{ position: "absolute", left: 120, top: 870, width: 1680, height: 8, borderRadius: 4, background: "#3c494e" }} />
      <div style={{ position: "absolute", left: 120, top: 870, width: 1680 * progress, height: 8,
        borderRadius: 4, background: "#f5a648" }} />
    </AbsoluteFill>
  );
}

registerRoot(() => <Composition id="demo" component={Demo} width={1920} height={1080} fps={30} durationInFrames={180} />);
