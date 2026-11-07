import json
from pathlib import Path
import subprocess
import time
import urllib.request
import wave

PROJECT = Path(__file__).resolve().parent
OUTPUT = PROJECT / "media" / "narration"
MODEL = "mlx-community/Kokoro-82M-bf16"
VOICE = "af_heart"
ENDPOINT = "http://127.0.0.1:8880/v1/audio/speech"


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def main():
    OUTPUT.mkdir(exist_ok=True)
    cues = json.loads((PROJECT / "narration-cues.json").read_text())
    measurements = []
    subtitles = []
    for index, cue in enumerate(cues):
        output = OUTPUT / (cue["id"] + ".wav")
        started = time.perf_counter()
        payload = {
            "model": MODEL,
            "voice": VOICE,
            "input": cue["text"],
            "response_format": "wav",
            "speed": 1.0,
            "stream": False,
        }
        if not output.exists():
            request = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                output.write_bytes(response.read())
        with wave.open(str(output)) as audio:
            duration = audio.getnframes() / audio.getframerate()
        end = cue["at"] + duration
        if end > cue["before"]:
            raise RuntimeError(f"{cue['id']} ends at {end:.2f}; retime the cue or rewrite the sentence before mixing")
        measurements.append({**cue, "duration": duration, "end": end, "file": str(output), "model": MODEL, "voice": VOICE})
        subtitles.append(f"{index + 1}\n{timestamp(cue['at'])} --> {timestamp(end)}\n{cue['text']}\n")
        print(f"{cue['id']}: {duration:.2f}s speech, {time.perf_counter() - started:.2f}s elapsed", flush=True)

    (PROJECT / "out" / "narration.json").write_text(json.dumps(measurements, indent=2))
    (PROJECT / "out" / "narration.srt").write_text("\n".join(subtitles))
    arguments = ["ffmpeg", "-v", "error"]
    filters = []
    for index, cue in enumerate(measurements):
        arguments += ["-i", cue["file"]]
        delay = round(cue["at"] * 1000)
        filters.append(f"[{index}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={delay}|{delay}[v{index}]")
    inputs = "".join(f"[v{index}]" for index in range(len(measurements)))
    filters.append(f"{inputs}amix=inputs={len(measurements)}:normalize=0,apad,atrim=duration=64[voice]")
    arguments += ["-filter_complex", ";".join(filters), "-map", "[voice]", "-c:a", "pcm_s24le", str(PROJECT / "out" / "narration.wav")]
    subprocess.run(arguments, check=True)


if __name__ == "__main__":
    main()
