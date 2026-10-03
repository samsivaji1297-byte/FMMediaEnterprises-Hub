import os
from pathlib import Path

# Base Paths
SRC_DIR = Path(__file__).resolve().parent
MEDIA_FACTORY_DIR = SRC_DIR.parent
PROJECT_ROOT = MEDIA_FACTORY_DIR.parent

# Asset Vault Directories
ASSETS_DIR = MEDIA_FACTORY_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUT_DIR = MEDIA_FACTORY_DIR / "output"
VAULT_DIR = MEDIA_FACTORY_DIR / "vault"

for directory in [ASSETS_DIR, FONTS_DIR, OUTPUT_DIR, VAULT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def resolve_font_path(font_name: str = "LiberationSans-Bold.ttf") -> str:
    """Dynamically resolves font paths across Ubuntu runners, macOS, and local asset vaults."""
    local_font = FONTS_DIR / font_name
    if local_font.exists():
        return str(local_font)

    ubuntu_path = f"/usr/share/fonts/truetype/liberation/{font_name}"
    if os.path.exists(ubuntu_path):
        return ubuntu_path

    # Linux general search
    linux_alt = f"/usr/share/fonts/TTF/{font_name}"
    if os.path.exists(linux_alt):
        return linux_alt

    # Return default system fallback name for PIL/MoviePy
    return "DejaVuSans-Bold"


# Canvas Specifications (Reels / Shorts / TikTok 9:16)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_FPS = 30

# Sovereign Brand Color Tokens
COLOR_TOKENS = {
    "sovereign": {
        "bg": (10, 10, 10),
        "text": "#FFFFFF",
        "accent": "#00E5FF",  # Vibrant Cyber Blue Accent
        "mask_opacity": 0.60,
        "font_size": 85,
    },
    "kinetic": {
        "bg": (5, 5, 5),
        "text": "#FFE600",  # Kinetic Yellow Accent
        "stroke": "#000000",
        "mask_opacity": 0.45,
        "font_size": 100,
    },
    "ambient": {
        "bg": (15, 15, 20),
        "text": "#F0F0F0",
        "accent": "#FFD700",  # Muted Gold Accent
        "mask_opacity": 0.50,
        "font_size": 80,
    },
}
