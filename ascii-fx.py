#!/usr/bin/env python3

import os, sys, time, math, argparse, subprocess, select, tty, termios, json
from pathlib import Path
from PIL import Image
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.live import Live
from rich.columns import Columns
from rich.padding import Padding

CONFIG_DIR = Path("~/.config/ascii-fx").expanduser()
LAST_PROFILE_PATH = CONFIG_DIR / "last_profile.txt"

STYLE_PRESETS = {
    "blocky":   " .░▒▓█",
    "smooth":   " .:-=+*#%@",
    "ultra":    "  .oO8@█▓",
    "retro":    " .,:;clodxkO0KXNWM",
    "dots":     "·",
    "bars":     "|█",
    "squares":  "[]#",
    "wide":     "__--==##",
    "dense":    " .:+xX$@",
}

DEFAULT_WIDTH = 38
CHAR_ASPECT_RATIO = 0.45

def load_config_from_profile(name):
    path = CONFIG_DIR / f"{name}.json"
    if not path.exists():
        sys.exit(f"[!] Profile '{name}' not found.")
    with open(path) as f:
        return json.load(f)

def save_last_profile(name):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LAST_PROFILE_PATH, "w") as f:
        f.write(name)

def load_last_profile():
    if LAST_PROFILE_PATH.exists():
        with open(LAST_PROFILE_PATH) as f:
            return f.read().strip()
    return "default"

def brightness(r, g, b): return 0.2989 * r + 0.5870 * g + 0.1140 * b

def blend(r, g, b, a): return int(r * a), int(g * a), int(b * a)

def key_pressed(): return select.select([sys.stdin], [], [], 0)[0] != []

def load_image(path, width):
    if not path or not os.path.exists(os.path.expanduser(path)):
        sys.exit(f"[!] Image path not set or doesn't exist: {path}")
    try:
        img = Image.open(os.path.expanduser(path))
        if img.mode in ("RGBA", "LA"):
            bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
            img = Image.alpha_composite(bg, img.convert("RGBA"))
        else:
            img = img.convert("RGB")
        h = int(width * (img.height / img.width) * CHAR_ASPECT_RATIO)
        return img.resize((width, h))
    except Exception as e:
        sys.exit(f"[!] Failed to open image: {e}")

def render_ascii(img, style, bw=False, t=0, animated=False, override=None):
    result, pixels = Text(), img.getdata()
    charset = STYLE_PRESETS.get(style, STYLE_PRESETS["blocky"])
    for i, px in enumerate(pixels):
        if i % img.width == 0 and i != 0: result.append("\n")
        r, g, b, *rest = px if len(px) == 4 else (*px, 255)
        a = rest[0] if rest else 255
        if a < 10: result.append(" "); continue
        if a < 255: r, g, b = blend(r, g, b, a / 255.0)
        if animated:
            wave = 0.5 + 0.5 * math.sin(i * 0.05 + t)
            r, g, b = int(r * wave), int(g * wave), int(b * wave)
        char = override or ("·" if style == "dots" else charset[min(int((brightness(r, g, b) if style == "retro" else sum((r, g, b)) / 3) / 255 * (len(charset)-1)), len(charset)-1)])
        result.append(" " if bw or char == " " else Text(char, Style(color=f"rgb({r},{g},{b})")))
    return result

def get_fastfetch(): 
    try: return Text(subprocess.check_output(["fastfetch"], text=True))
    except: return Text("[fastfetch error]")

def animate(img, style, bw, override):
    console, t = Console(), 0
    fastfetch = Padding(get_fastfetch(), (0, 0, 0, 4))  # Add left padding to push it right
    old = termios.tcgetattr(sys.stdin); tty.setcbreak(sys.stdin.fileno())
    try:
        with Live(console=console, refresh_per_second=20, screen=True) as live:
            while not key_pressed():
                t += 0.2
                ascii_img = render_ascii(img, style, bw, t, True, override)
                live.update(Columns([ascii_img, fastfetch], equal=False, expand=False))
                time.sleep(0.05)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        console.clear(); print("[Exited animation 👋]")

def render_static(img, style, bw, override):
    ascii_img = render_ascii(img, style, bw, override=override)
    fastfetch = Padding(get_fastfetch(), (0, 0, 0, 4))
    Console().print(Columns([ascii_img, fastfetch], equal=False, expand=False))

def main():
    p = argparse.ArgumentParser(description="ascii-fx: Terminal Logo Renderer")
    p.add_argument("--style"); p.add_argument("--image")
    p.add_argument("--width", type=int); p.add_argument("--wave", action="store_true")
    p.add_argument("--bw", action="store_true"); p.add_argument("--char")
    p.add_argument("--profile", help="Load from saved profile")
    args = p.parse_args()

    if len(sys.argv) == 1:
        args.profile = load_last_profile()

    if args.profile:
        config = load_config_from_profile(args.profile)
        args.style = args.style or config.get("style")
        args.image = args.image or config.get("image")
        args.width = args.width or config.get("width")
        args.wave = args.wave or config.get("wave")
        args.bw = args.bw or config.get("bw")
        args.char = args.char or config.get("char")
        save_last_profile(args.profile)

    img = load_image(args.image, args.width or DEFAULT_WIDTH)
    if args.wave:
        animate(img, args.style, args.bw, args.char)
    else:
        render_static(img, args.style, args.bw, args.char)

if __name__ == "__main__":
    main()
