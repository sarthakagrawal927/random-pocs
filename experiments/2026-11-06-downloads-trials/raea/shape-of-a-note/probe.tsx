import {AbsoluteFill, Composition, registerRoot, useCurrentFrame, Mix} from "raea";
import * as Tone from "raea/tone";
const s = new Tone.Synth({oscillator:{type:"sine"},envelope:{attack:0.02,decay:0,sustain:1,release:0.1},volume:-15}).connect(Tone.buses.music);
s.triggerAttackRelease(220,1.7,0.1);
function Probe(){const f=useCurrentFrame();return <AbsoluteFill><svg width={512} height={512} viewBox="0 0 512 512"><circle cx={256} cy={256} r={120} fill="#cc622c"/><path d={`M 40 256 Q 140 ${80+f} 256 256 T 472 256`} stroke="#142e36" strokeWidth={6} fill="none"/></svg><Mix lufs={-14} ceiling={-1.5}/></AbsoluteFill>}
registerRoot(()=><Composition id="probe" component={Probe} width={512} height={512} fps={30} durationInFrames={60}/>);
