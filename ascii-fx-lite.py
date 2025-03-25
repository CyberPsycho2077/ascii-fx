#!/usr/bin/env python3

import os, sys, time, math, argparse, subprocess, json, tty, termios
from pathlib import Path
from PIL import Image
from rich.console import Console
from rich.text import Text
from rich.style import Style
from rich.live import Live
from rich.columns import Columns
from rich.padding import Padding
import threading

STYLE_PRESETS = {
    "blocky": " .░▒▓█",
    "retro": " .,:;clodxkO0KXNWM"
}

DEFAULT_WIDTH = 38
CHAR_ASPECT_RATIO = 0.45
console = Console()
running = True

def listen_for_quit():
    global running
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        while running:
            if sys.stdin.read(1) == 'q':
                running = False
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def brightness(r, g, b): return 0.2989 * r + 0.5870 * g + 0.1140 * b

def blend(r, g, b, a): return int(r * a), int(g * a), int(b * a)

def load_image(path, width):
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

def render_ascii(img, style, t=0):
    result, pixels = Text(), img.getdata()
    charset = STYLE_PRESETS.get(style, STYLE_PRESETS["blocky"])
    for i, px in enumerate(pixels):
        if i % img.width == 0 and i != 0:
            result.append("\n")
        r, g, b, *rest = px if len(px) == 4 else (*px, 255)
        a = rest[0] if rest else 255
        if a < 10:
            result.append(" "); continue
        if a < 255:
            r, g, b = blend(r, g, b, a / 255.0)
        wave = 0.5 + 0.5 * math.sin(i * 0.05 + t)
        r, g, b = int(r * wave), int(g * wave), int(b * wave)
        char = charset[min(int(sum((r, g, b)) / 3 / 255 * (len(charset) - 1)), len(charset) - 1)]
        result.append(Text(char, Style(color=f"rgb({r},{g},{b})")))
    return result

def animate_ascii(img, style):
    global running
    t = 0
    threading.Thread(target=listen_for_quit, daemon=True).start()
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while running:
            t += 0.2
            ascii_art = render_ascii(img, style, t)
            live.update(Padding(ascii_art, (0, 4)))
            time.sleep(0.05)
    console.clear()
    print("[Exited animation with 'q']")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--style", default="blocky")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    args = parser.parse_args()

    img = load_image(args.image, args.width)
    animate_ascii(img, args.style)

if __name__ == "__main__":
    main()
