from pathlib import Path
import json
import math
import subprocess

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
FPS = 30


def background():
    image = Image.new("RGB", (2560, 720), "#dce9eb")
    draw = ImageDraw.Draw(image)
    draw.ellipse((1890, 70, 2050, 230), fill="#e4b36d")
    for offset in [0, 800, 1600, 2400]:
        draw.ellipse((offset + 100, 115, offset + 380, 165), fill="#f4f6ef")
        draw.ellipse((offset + 200, 95, offset + 320, 155), fill="#f4f6ef")
    for level, color in [(0, "#a7c5c9"), (1, "#719fa7"), (2, "#4c7a86")]:
        points = [(0, 720)]
        for x in range(0, 2590, 30):
            y = 390 + 78 * level + 70 * math.sin(x / (160 + level * 45) + level)
            points.append((x, round(y)))
        points.extend([(2560, 720)])
        draw.polygon(points, fill=color)
    draw.rectangle((0, 640, 2560, 720), fill="#274d5a")
    for x in range(50, 2600, 175):
        draw.rounded_rectangle((x, 676, x + 65, 681), radius=2, fill="#98b1b5")
    image.save(ASSETS / "landscape.png")
    subprocess.run([
        "ffmpeg", "-v", "error", "-loop", "1", "-framerate", str(FPS),
        "-i", str(ASSETS / "landscape.png"), "-t", "8",
        "-vf", "crop=1280:720:x=(iw-ow)*n/239:y=0,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-movflags", "+faststart", str(ASSETS / "moving-landscape.mp4"),
    ], check=True)


def mascot_frame(frame):
    scale = 2
    image = Image.new("RGBA", (512 * scale, 512 * scale))
    draw = ImageDraw.Draw(image)
    phase = frame / FPS * math.tau * 2
    bob = -9 * abs(math.sin(phase))
    sway = 12 * math.sin(phase / 2)
    ink, teal, face, coral = "#244754", "#77b7b0", "#ffe1c7", "#db785e"

    def ellipse(box, fill, outline=ink, width=4):
        draw.ellipse(tuple(round(v * scale) for v in box), fill=fill, outline=outline, width=width * scale)

    def line(points, fill, width):
        draw.line([(round(x * scale), round(y * scale)) for x, y in points], fill=fill, width=width * scale, joint="curve")

    x, y = 256 + sway, 270 + bob
    for side in [-1, 1]:
        kick = 20 * max(0, math.sin(phase + (0 if side == 1 else math.pi)))
        hip = (x + side * 30, y + 94)
        foot = (x + side * (49 + kick), y + 145 - kick * 0.8)
        line([hip, foot], ink, 25)
        line([hip, foot], teal, 16)
        ellipse((foot[0] - 23, foot[1] - 8, foot[0] + 23, foot[1] + 15), coral)
    ellipse((x - 65, y + 7, x + 65, y + 116), teal)
    for side in [-1, 1]:
        lift = math.sin(phase + side * 0.75)
        shoulder = (x + side * 55, y + 30)
        elbow = (x + side * 91, y + 27 - 30 * lift)
        hand = (x + side * 114, y - 5 - 47 * lift)
        line([shoulder, elbow, hand], ink, 24)
        line([shoulder, elbow, hand], teal, 15)
        ellipse((hand[0] - 13, hand[1] - 13, hand[0] + 13, hand[1] + 13), face, width=3)
    ellipse((x - 81, y - 112, x + 81, y + 29), ink, width=2)
    ellipse((x - 72, y - 95, x + 72, y + 36), face)
    draw.polygon([(round(a * scale), round(b * scale)) for a, b in [
        (x - 75, y - 43), (x - 70, y - 112), (x - 34, y - 91),
        (x - 6, y - 118), (x + 19, y - 89), (x + 60, y - 106), (x + 76, y - 35),
        (x + 39, y - 61), (x + 5, y - 40), (x - 28, y - 63),
    ]], fill=ink)
    for side in [-1, 1]:
        eye_x = x + side * 28
        ellipse((eye_x - 9, y - 25, eye_x + 9, y - 2), ink, width=1)
        ellipse((eye_x - 3, y - 22, eye_x + 2, y - 16), "#ffffff", outline=None, width=0)
        ellipse((eye_x - 17, y + 5, eye_x + 7, y + 12), "#eaa08a", outline=None, width=0)
    draw.arc((round((x - 13) * scale), round((y - 4) * scale), round((x + 13) * scale), round((y + 16) * scale)), 5, 175, fill=ink, width=3 * scale)
    line([(x - 34, y + 44), (x + 30, y + 44)], coral, 13)
    line([(x + 20, y + 46), (x + 43 + 10 * math.sin(phase), y + 79)], coral, 13)
    return image.resize((512, 512), Image.Resampling.LANCZOS)


def foreground():
    command = [
        "ffmpeg", "-v", "error", "-f", "rawvideo", "-pixel_format", "rgba",
        "-video_size", "512x512", "-framerate", str(FPS), "-i", "pipe:0", "-an",
        "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le",
        str(ASSETS / "dancing-mascot.mov"),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    for frame in range(60):
        process.stdin.write(mascot_frame(frame).tobytes())
    process.stdin.close()
    if process.wait():
        raise RuntimeError("Foreground encoding failed")
    mascot_frame(14).save(ASSETS / "mascot-preview.png")


if __name__ == "__main__":
    background()
    foreground()
    (ROOT / "provenance.json").write_text(json.dumps({
        "creator": "Original procedural demonstration for the owner",
        "license": "creator-owned",
        "licenseUrl": "urn:rights:creator-owned",
        "background": "urn:fleet:original:procedural-landscape",
        "foreground": "urn:fleet:original:procedural-dancing-mascot",
        "note": "Original drawn geometry; no Chika or other third-party character is bundled.",
    }, indent=2))
    print(ASSETS)
