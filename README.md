# ascii-fx

A terminal logo tool that converts PNGs into animated or static ASCII. Includes profile support, fastfetch integration, and a minimal standalone version.

---

## Features
- Color ASCII rendering from PNG images
- Multiple style presets and optional character overrides
- Wave animation effect for dynamic display
- Terminal UI to manage profiles (`ascii-fx-settings.py`)
- Option to render system information using Fastfetch
- Minimal standalone version: `ascii-fx-lite.py`
- Clean exit from animation using the `q` key

---

## Usage

### Full Version
```bash
ascii-fx.py --image path/to/image.png --style retro --wave
```

Launch the settings TUI:
```bash
ascii-fx-settings.py
```

If no arguments are passed, the last used profile will be loaded automatically.

---

## Arguments (Full Version)
| Flag        | Description                         |
|-------------|-------------------------------------|
| `--image`   | Path to the image file (required)   |
| `--style`   | Character style preset              |
| `--width`   | Output width in characters          |
| `--char`    | Manually specify the ASCII character|
| `--wave`    | Enable animation mode               |
| `--profile` | Load a named saved profile          |

---

## ascii-fx-lite.py (Minimal Version)
A simplified version of the script that displays animated ASCII logos without profiles or Fastfetch integration.

```bash
ascii-fx-lite.py --image path/to/image.png --style retro --width 40
```

Use cases:
- Startup/splash animations
- Minimal setups or demos
- Low-configuration environments

Details:
- Renders animated wave effect
- Color support enabled by default
- Exits when `q` is pressed
- Does not load or save profiles

Supported styles: `blocky`, `retro`

---

## Fastfetch Integration
You can combine `ascii-fx` with [Fastfetch](https://github.com/fastfetch-cli/fastfetch) to show system information alongside your custom ASCII art.

### Example Integration:
1. Run your logo renderer first and save output to a file:
```bash
ascii-fx.py --image ~/.local/share/fastfetch/images/sample.png --style blocky > ~/.config/fastfetch/logo.txt
```
2. Use `--file-raw` to inject your logo into Fastfetch:
```bash
fastfetch --file-raw ~/.config/fastfetch/logo.txt
```

### Disabling the Built-In Fastfetch Logo
To prevent Fastfetch from showing its default logo (e.g. Arch), open your Fastfetch config file (`~/.config/fastfetch/config.jsonc`) and update this section:
```jsonc
"logo": {
  "source": "none"
},
```
This ensures only your custom logo appears with the system info.

---

## Installation
Make sure the scripts are marked executable and located in a directory included in your PATH:
```bash
chmod +x ~/.local/bin/ascii-fx.py
chmod +x ~/.local/bin/ascii-fx-lite.py
chmod +x ~/.local/bin/ascii-fx-settings.py
```

Then run them directly:
```bash
ascii-fx.py --image logo.png --style blocky
ascii-fx-settings.py
ascii-fx-lite.py --image logo.png --style retro
```

---

## Compatibility
- Linux (including Arch, Ubuntu)
- macOS (with Python installed via Homebrew)
- Windows (via Windows Terminal and Python 3.10+)

Note: Fastfetch is not officially available on Windows. Use the ASCII renderer standalone.

---

## Special Thanks
- [rich](https://github.com/Textualize/rich) – Terminal text rendering
- [Pillow](https://python-pillow.org/) – Image loading and scaling
- [Fastfetch](https://github.com/fastfetch-cli/fastfetch) – System information utility

---

## License
Apache 2.0

