"""Colors, fonts, ttk styles, and the app logo for the Tkinter window."""
from __future__ import annotations

import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from .i18n import get_language


BG = "#F3F5F8"
SURFACE = "#FFFFFF"
BORDER = "#DDE2EA"
TEXT = "#1E2430"
MUTED = "#667085"
FAINT = "#98A2B3"
HOVER = "#F2F4F7"
PRESSED = "#E6EAF0"
ACCENT = "#2F6FED"
ACCENT_HOVER = "#2459C9"
ACCENT_PRESSED = "#1D4AA8"
ACCENT_SOFT = "#E3ECFD"
ACCENT_DISABLED = "#A8C1F5"
WARNING_BG = "#FFF6E5"
WARNING_TEXT = "#9A5B00"

# Status kind -> color of the status dot and message.
STATUS_COLORS = {
    "idle": FAINT,
    "busy": ACCENT,
    "success": "#1E7F4F",
    "warning": WARNING_TEXT,
    "error": "#C0392B",
}

FONT_FAMILIES = {"ko": "Malgun Gothic", "en": "Segoe UI"}
# Named font -> (point size, weight).
FONTS = {
    "AppBody": (10, "normal"),
    "AppSmall": (9, "normal"),
    "AppStrong": (10, "bold"),
    "AppSection": (8, "bold"),
    "AppTitle": (15, "bold"),
}

_scale = 1.0
# Tk deletes a named font when its Python object is garbage collected, so keep them.
_fonts: dict[str, tkfont.Font] = {}


def px(value: float) -> int:
    """Scale a 96-DPI pixel size to the screen's DPI."""
    return round(value * _scale)


def enable_dpi_awareness() -> None:
    """Render crisply on high-DPI Windows screens instead of being stretched."""
    if sys.platform == "win32":
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass


def apply_fonts(root: tk.Tk) -> None:
    """Create the named fonts, or switch their family to suit the current language."""
    family = FONT_FAMILIES[get_language()]
    for name, (size, weight) in FONTS.items():
        if name in _fonts:
            _fonts[name].configure(family=family)
        else:
            _fonts[name] = tkfont.Font(root, name=name, family=family, size=size, weight=weight)
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        tkfont.nametofont(name, root).configure(family=family, size=10)


def setup_theme(root: tk.Tk) -> None:
    global _scale
    _scale = root.winfo_fpixels("1i") / 96
    apply_fonts(root)
    root.configure(background=BG)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        ".",
        background=BG,
        foreground=TEXT,
        font="AppBody",
        bordercolor=BORDER,
        lightcolor=SURFACE,
        darkcolor=SURFACE,
        troughcolor=BG,
        focuscolor=ACCENT,
        selectbackground=ACCENT,
        selectforeground=SURFACE,
        insertcolor=TEXT,
    )

    style.configure("Surface.TFrame", background=SURFACE)
    style.configure(
        "Card.TFrame",
        background=SURFACE,
        relief="solid",
        borderwidth=1,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
    )

    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Card.TLabel", background=SURFACE)
    style.configure("Section.TLabel", background=SURFACE, foreground=FAINT, font="AppSection")
    style.configure("Title.TLabel", background=SURFACE, font="AppTitle")
    style.configure("Subtitle.TLabel", background=SURFACE, foreground=MUTED, font="AppSmall")
    style.configure("Header.TLabel", background=SURFACE, foreground=MUTED, font="AppSmall")
    style.configure(
        "Nav.TLabel",
        background=SURFACE,
        foreground=MUTED,
        font="AppStrong",
        padding=(px(2), 0, px(2), px(8)),
    )
    style.map("Nav.TLabel", foreground=[("hover", TEXT)])
    style.configure("NavActive.Nav.TLabel", foreground=ACCENT)
    style.map("NavActive.Nav.TLabel", foreground=[("hover", ACCENT)])
    style.configure(
        "Warning.TLabel",
        background=WARNING_BG,
        foreground=WARNING_TEXT,
        font="AppSmall",
        padding=(px(10), px(6)),
    )
    for kind, color in STATUS_COLORS.items():
        style.configure(f"{kind.title()}.Status.TLabel", foreground=color)

    style.configure(
        "TEntry",
        fieldbackground=SURFACE,
        bordercolor=BORDER,
        lightcolor=SURFACE,
        darkcolor=SURFACE,
        padding=(px(8), px(5)),
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT_SOFT)])

    style.configure(
        "TButton",
        background=SURFACE,
        padding=(px(14), px(5)),
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("pressed", PRESSED), ("active", HOVER)],
        bordercolor=[("focus", ACCENT)],
    )
    accent_states = [
        ("disabled", ACCENT_DISABLED),
        ("pressed", ACCENT_PRESSED),
        ("active", ACCENT_HOVER),
    ]
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground=SURFACE,
        bordercolor=ACCENT,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
        font="AppStrong",
        padding=(px(22), px(7)),
    )
    style.map(
        "Accent.TButton",
        background=accent_states,
        bordercolor=[("focus", ACCENT_PRESSED), *accent_states],
        lightcolor=accent_states,
        darkcolor=accent_states,
        foreground=[("disabled", SURFACE)],
    )

    style.configure(
        "TRadiobutton",
        background=SURFACE,
        indicatorbackground=SURFACE,
        indicatorforeground=ACCENT,
        upperbordercolor=FAINT,
        lowerbordercolor=FAINT,
        indicatorsize=px(14),
        indicatormargin=(0, 0, px(7), 0),
        padding=(0, px(2), px(4), px(2)),
        focusthickness=0,
    )
    style.map(
        "TRadiobutton",
        background=[("active", SURFACE)],
        foreground=[("focus", ACCENT)],
        upperbordercolor=[("selected", ACCENT)],
        lowerbordercolor=[("selected", ACCENT)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=SURFACE,
        background=SURFACE,
        arrowcolor=MUTED,
        padding=(px(8), px(3)),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", SURFACE)],
        selectbackground=[("readonly", SURFACE)],
        selectforeground=[("readonly", TEXT)],
        background=[("active", HOVER)],
        bordercolor=[("focus", ACCENT)],
    )
    root.option_add("*TCombobox*Listbox.font", "AppBody")
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", SURFACE)

    # A thin bar that is invisible while idle and animates while a job runs.
    flat = {"bordercolor": BG, "lightcolor": BG, "darkcolor": BG}
    style.configure(
        "Idle.Horizontal.TProgressbar", troughcolor=BG, background=BG, thickness=px(4), **flat
    )
    style.configure(
        "Busy.Horizontal.TProgressbar",
        troughcolor=ACCENT_SOFT,
        background=ACCENT,
        thickness=px(4),
        bordercolor=ACCENT_SOFT,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
    )

    # Pages are switched from the header, so the notebook's own tabs are hidden.
    style.layout("Plain.TNotebook.Tab", [])
    style.configure("Plain.TNotebook", background=BG, borderwidth=0, **flat)

    root.iconphoto(True, *(make_icon(size) for size in (48, 32, 16)))


# The logo is a photo glyph (sun and mountains) on a rounded accent square.
# Shapes are in unit coordinates so the canvas logo and window icon match.
LOGO_RADIUS = 0.24
LOGO_SUN = (0.34, 0.35, 0.095)
LOGO_MOUNTAINS = [(0.16, 0.78), (0.42, 0.48), (0.58, 0.65), (0.68, 0.55), (0.84, 0.78)]


def draw_logo(parent: tk.Widget, size: int) -> tk.Canvas:
    canvas = tk.Canvas(
        parent, width=size, height=size, background=SURFACE, highlightthickness=0, borderwidth=0
    )
    r = size * LOGO_RADIUS
    canvas.create_polygon(
        r, 0, size - r, 0, size, 0, size, r, size, size - r, size, size,
        size - r, size, r, size, 0, size, 0, size - r, 0, r, 0, 0,
        smooth=True, fill=ACCENT, outline="",
    )
    cx, cy, radius = LOGO_SUN
    canvas.create_oval(
        (cx - radius) * size, (cy - radius) * size, (cx + radius) * size, (cy + radius) * size,
        fill=SURFACE, outline="",
    )
    canvas.create_polygon(
        *(coord * size for point in LOGO_MOUNTAINS for coord in point), fill=SURFACE, outline=""
    )
    return canvas


def in_logo_square(u: float, v: float) -> bool:
    r = LOGO_RADIUS
    dx = max(r - u, 0.0, u - (1 - r))
    dy = max(r - v, 0.0, v - (1 - r))
    return dx * dx + dy * dy <= r * r


def in_logo_glyph(u: float, v: float) -> bool:
    cx, cy, radius = LOGO_SUN
    if (u - cx) ** 2 + (v - cy) ** 2 <= radius * radius:
        return True

    inside = False
    points = LOGO_MOUNTAINS
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        if (y1 > v) != (y2 > v) and u < x1 + (v - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def blend(color_a: str, color_b: str, amount: float) -> str:
    a = [int(color_a[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(color_b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def make_icon(size: int, samples: int = 4) -> tk.PhotoImage:
    """Rasterize the logo, anti-aliasing the glyph by supersampling each pixel."""
    image = tk.PhotoImage(width=size, height=size)
    rows, transparent = [], []
    for y in range(size):
        row = []
        for x in range(size):
            shape = glyph = 0
            for sy in range(samples):
                for sx in range(samples):
                    u = (x + (sx + 0.5) / samples) / size
                    v = (y + (sy + 0.5) / samples) / size
                    if in_logo_square(u, v):
                        shape += 1
                        glyph += in_logo_glyph(u, v)
            if shape * 2 < samples * samples:
                transparent.append((x, y))
            row.append(blend(ACCENT, SURFACE, glyph / shape) if shape else ACCENT)
        rows.append("{" + " ".join(row) + "}")

    image.put(" ".join(rows))
    for x, y in transparent:
        image.tk.call(image, "transparency", "set", x, y, True)
    return image
