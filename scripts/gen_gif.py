#!/usr/bin/env python3
"""Generate premium ghosty.gif from PIL-drawn frames.

Ghost design: geometric slate body + cyber violet terminal eyes.
Animation: subtle float (6px) + eye blink (4 frames, 700ms each).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 400, 400
DARK   = (22, 27, 34)    # #161B22 — slate body
BORDER = (45, 55, 72)    # #2D3748
PITCH  = (13, 17, 23)    # #0D1117 — eye socket
ACCENT = (139, 92, 246)  # #8B5CF6 — cyber violet
DIM    = (60, 40, 100)   # dimmed eye blink
GRAY   = (75, 85, 99)    # #4B5563
BG     = (0, 0, 0, 0)    # transparent


def ghost_body(draw: ImageDraw, cx: int, cy: int) -> None:
    """Draw the polygonal ghost body centered at (cx, cy)."""
    # Main body polygon — geometric/draped shape
    body = [
        (cx,     cy - 130),  # top center
        (cx-80,  cy - 120),  # left shoulder
        (cx-140, cy - 50),   # left mid
        (cx-140, cy + 80),   # left bottom start
        (cx-110, cy + 100),  # fold 1
        (cx-80,  cy + 80),   # fold 2
        (cx-50,  cy + 100),  # fold 3
        (cx-20,  cy + 80),   # fold 4
        (cx,     cy + 96),   # center bottom
        (cx+20,  cy + 80),   # fold 4 mirror
        (cx+50,  cy + 100),  # fold 3 mirror
        (cx+80,  cy + 80),   # fold 2 mirror
        (cx+110, cy + 100),  # fold 1 mirror
        (cx+140, cy + 80),   # right bottom start
        (cx+140, cy - 50),   # right mid
        (cx+80,  cy - 120),  # right shoulder
    ]

    # Body fill
    draw.polygon(body, fill=DARK, outline=None)

    # Body stroke (outline)
    for i in range(len(body)):
        nxt = (i + 1) % len(body)
        draw.line([*body[i], *body[nxt]], fill=BORDER, width=2)

    # Highlight — subtle shine on upper-left
    highlight = [
        (cx,     cy - 130),
        (cx-50,  cy - 120),
        (cx-90,  cy - 80),
        (cx-70,  cy - 60),
        (cx,     cy - 80),
    ]
    for i in range(len(highlight) - 1):
        draw.line([*highlight[i], *highlight[i+1]], fill=(26, 32, 44), width=8)


def eye_socket(draw: ImageDraw, cx: int, cy: int, to_left: bool) -> None:
    """Draw a hexagonal eye socket."""
    if to_left:
        pts = [(cx-32, cy-20), (cx-8, cy-26), (cx+4, cy-12), (cx-12, cy)]
    else:
        pts = [(cx+32, cy-20), (cx+8, cy-26), (cx-4, cy-12), (cx+12, cy)]

    draw.polygon(pts, fill=PITCH, outline=BORDER, width=1)
    # Inner inset — offset toward centroid
    center_x = sum(p[0] for p in pts) / 4
    center_y = sum(p[1] for p in pts) / 4
    inner_pts = [(p[0] + (center_x - p[0]) * 0.3, p[1] + (center_y - p[1]) * 0.3) for p in pts]
    draw.polygon(inner_pts, fill=PITCH)


def render_frame(y_offset: int, eye_char: str, accent: tuple) -> Image.Image:
    """Render a single frame with given y_offset and eye character."""
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    cx, cy = W // 2, H // 2
    cy += y_offset

    # Ground shadow (stationary — sells the float)
    shadow_cy = H // 2 + 100
    draw.ellipse([cx-90, shadow_cy-8, cx+90, shadow_cy+8], fill=(0, 0, 0, 60))

    # Ghost body
    ghost_body(draw, cx, cy)

    # Left eye
    eye_socket(draw, cx, cy, to_left=True)
    # Draw eye character (« > » or « _ »)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    # Left eye char
    draw.text((cx - 28, cy - 16), eye_char, fill=accent, font=font)
    # Right eye char (« < » or « _ »)
    draw.text((cx + 12, cy - 16), eye_char, fill=accent, font=font)

    # Code line decoration
    try:
        small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttf", 12)
    except OSError:
        small = ImageFont.load_default()
    draw.text((cx - 52, cy + 48), "_ ~ $", fill=GRAY, font=small)

    return frame


FONTS = """ ... that's the rendered ghosty.gif ... """


def main():
    frames_info = [
        (0,    ">", ACCENT),   # frame 1: rest, bright
        (-6,   ">", ACCENT),   # frame 2: float up, bright
        (0,    "_", DIM),      # frame 3: blink, dimmed
        (0,    ">", ACCENT),   # frame 4: back to rest
    ]

    images = []
    for y_off, eye, col in frames_info:
        img = render_frame(y_off, eye, col)
        images.append(img)

    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    gif_path = assets_dir / "ghosty.gif"

    # Save as animated GIF: 700ms per frame, loop forever
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=700,
        loop=0,
        transparency=0,
        disposal=2,
    )

    print(f"✓ GIF written to {gif_path}")
    print(f"  {len(images)} frames, 700ms each, loop forever")

    # Cleanup frame SVGs
    for svg in assets_dir.glob("frame-*.svg"):
        svg.unlink()
    print(f"  cleaned up {len(frames_info)} frame SVG files")


if __name__ == "__main__":
    main()
