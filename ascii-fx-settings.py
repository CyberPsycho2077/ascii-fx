#!/usr/bin/env python3

import os, json, subprocess, shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

CONFIG_DIR = Path("~/.config/ascii-fx").expanduser()
DEFAULT_IMAGE = "~/.local/share/fastfetch/images/edg.png"
DEFAULT_PROFILE = CONFIG_DIR / "default.json"
STYLES = ["blocky", "smooth", "ultra", "retro", "dots", "bars", "squares", "wide", "dense"]
console = Console()

def create_default():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_PROFILE.exists():
        json.dump({"style": "blocky", "image": str(Path(DEFAULT_IMAGE).expanduser()), "width": 38, "theme": "dark", "wave": False, "char": ""}, open(DEFAULT_PROFILE, "w"), indent=2)
        console.print("[green]✔ Created default profile[/green]")

def show_preview(style, image, width, char):
    cmd = ["ascii-fx.py", "--style", style, "--image", image, "--width", str(width)]
    if char: cmd += ["--char", char]
    subprocess.run(cmd)

def select_image(default_path):
    folder = Path(default_path).expanduser().parent
    imgs = sorted([f.name for f in folder.glob("*.png")])
    if not imgs: return Prompt.ask("Path to image", default=default_path)
    t = Table(title="Available Images in images/", box=None)
    t.add_column("#", justify="right"); t.add_column("File name")
    [t.add_row(str(i+1), name) for i, name in enumerate(imgs)]
    console.print(t)
    idx = Prompt.ask("Select image number or type full path", default="1")
    return str(folder / imgs[int(idx)-1]) if idx.isdigit() and 1 <= int(idx) <= len(imgs) else idx

def select_profile():
    profiles = sorted(CONFIG_DIR.glob("*.json"))
    if not profiles: return "default"
    t = Table(title="Saved Profiles"); t.add_column("#", justify="right"); t.add_column("Profile Name")
    [t.add_row(str(i+1), p.stem) for i, p in enumerate(profiles)]
    console.print(t)
    choice = Prompt.ask("Select profile #, new name, or command (delete <name>, export <name>, import)", default="1")
    if choice.startswith("delete "):
        name = choice.split(" ", 1)[1].strip(); f = CONFIG_DIR / f"{name}.json"
        (f.unlink(), console.print(f"[red]🗑 Deleted profile '{name}'[/red]\n")) if f.exists() else console.print(f"[yellow]⚠ Profile '{name}' not found[/yellow]\n")
        return select_profile()
    elif choice.startswith("export "):
        name = choice.split(" ", 1)[1].strip(); src = CONFIG_DIR / f"{name}.json"
        if src.exists():
            dest = Prompt.ask("Path to save exported file", default=f"~/Downloads/{name}.json")
            shutil.copyfile(src, Path(dest).expanduser())
            console.print(f"[green]✔ Exported profile to {dest}[/green]\n")
        else: console.print(f"[yellow]⚠ Profile '{name}' not found[/yellow]\n")
        return select_profile()
    elif choice == "import":
        path = Prompt.ask("Path to JSON profile file to import")
        try:
            name = Path(path).stem
            shutil.copyfile(Path(path).expanduser(), CONFIG_DIR / f"{name}.json")
            console.print(f"[green]✔ Imported as profile '{name}'[/green]\n"); return name
        except Exception as e:
            console.print(f"[red]Failed to import profile: {e}[/red]"); return select_profile()
    elif choice.isdigit() and 1 <= int(choice) <= len(profiles): return profiles[int(choice)-1].stem
    return choice.strip()

def tui_menu():
    console.print(Panel("[bold cyan]ASCII-FX TUI Settings[/bold cyan]", expand=False))
    create_default()
    profile = select_profile(); config_path = CONFIG_DIR / f"{profile}.json"
    config = json.load(open(config_path)) if config_path.exists() else {}
    if config: console.print(f"[green]✔ Loaded profile '{profile}'. Press Enter to keep existing values.[/green]\n")
    t = Table(title="Available Styles"); t.add_column("Option", justify="right"); t.add_column("Style Name")
    [t.add_row(str(i+1), s) for i, s in enumerate(STYLES)]
    console.print(t)
    config['style'] = STYLES[int(Prompt.ask("Choose a style number", default=str(STYLES.index(config.get("style", "blocky"))+1)))-1]
    config['image'] = select_image(config.get('image', DEFAULT_IMAGE))
    config['width'] = int(Prompt.ask("Width (in characters)", default=str(config.get('width', 38))))
    config['theme'] = Prompt.ask("Terminal theme [dark/light]", choices=["dark", "light"], default=config.get('theme', 'dark'))
    config['wave'] = Confirm.ask("Enable wave animation?", default=config.get('wave', False))
    config['char'] = Prompt.ask("Override character (optional)", default=config.get('char', ''))
    if Confirm.ask("Show preview?", default=False): show_preview(config['style'], config['image'], config['width'], config['char'])
    json.dump(config, open(config_path, "w"), indent=2)
    console.print(f"\n[bold green]✅ Profile '{profile}' saved to {config_path}[/bold green]")
    if Confirm.ask("Launch ascii-fx now?", default=True):
        subprocess.run(["ascii-fx.py", "--profile", profile])

if __name__ == "__main__":
    tui_menu()
