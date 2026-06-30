#!/usr/bin/env python3
"""Generate ghosty.gif — ethereal white ghost with cyber violet eyes.

Body: semi-transparent white gradient (pops against dark GitHub bg).
Animation: subtle float (6px) + eye blink (4 frames, 700ms each).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 400, 400

# Ghost body — light/ethereal
BODY_TOP  = (255, 255, 255, 242)  # near-opaque white
BODY_BOT  = (224, 218, 255, 160)  # fading to violet-tinted
PITCH     = (13, 17, 23)          # eye socket
ACCENT    = (139, 92, 246)        # cyber violet
DIM       = (80, 50, 140)         # dimmed blink
CODE_GRAY = (180, 160, 220)       # code line decoration


def ghost_body(draw: ImageDraw, cx: int, cy: int) -> None:
    """Draw classic ghost: round dome + wavy sheet bottom."""
    body = [
        (cx,     cy - 135),  # top center
        (cx-70,  cy - 125),  # left shoulder arc
        (cx-130, cy - 70),   # left mid
        (cx-140, cy - 10),   # left hip
        (cx-138, cy + 60),   # left bottom start
        # wavy hem
        (cx-120, cy + 80),
        (cx-95,  cy + 60),
        (cx-70,  cy + 80),
        (cx-45,  cy + 60),
        (cx-20,  cy + 80),
        (cx,     cy + 62),
        (cx+20,  cy + 80),
        (cx+45,  cy + 60),
        (cx+70,  cy + 80),
        (cx+95,  cy + 60),
        (cx+120, cy + 80),
        (cx+138, cy + 60),
        # right side up
        (cx+140, cy - 10),
        (cx+130, cy - 70),
        (cx+70,  cy - 125),
    ]

    # Main body fill
    draw.polygon(body, fill=BODY_TOP, outline=None)

    # Subtle violet-tinted inner fill (smaller copy for depth)
    inner = [(cx + (p[0] - cx) * 0.85, cy + (p[1] - cy) * 0.85) for p in body]
    draw.polygon(inner, fill=BODY_BOT, outline=None)

    # Cheek highlights
    draw.ellipse([cx-75, cy-35, cx-35, cy+5], fill=(255, 255, 255, 180))
    draw.ellipse([cx+35, cy-35, cx+75, cy+5], fill=(255, 255, 255, 180))


def render_frame(y_offset: int, eye_char: str, accent: tuple) -> Image.Image:
    """Render a single animation frame."""
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    cx, cy = W // 2, H // 2
    cy += y_offset

    # Ground shadow (stationary — sells the float illusion)
    shadow_cy = H // 2 + 80
    draw.ellipse([cx-80, shadow_cy-6, cx+80, shadow_cy+6], fill=(0, 0, 0, 45))

    # Ghost body
    ghost_body(draw, cx, cy)

    # Left eye socket
    draw.ellipse([cx-48, cy-28, cx-20, cy+4], fill=PITCH)
    draw.ellipse([cx-44, cy-24, cx-24, cy+0], fill=PITCH)

    # Right eye socket
    draw.ellipse([cx+20, cy-28, cx+48, cy+4], fill=PITCH)
    draw.ellipse([cx+24, cy-24, cx+44, cy+0], fill=PITCH)

    # Eye glyphs
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttf", 28)
        small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
        small = font

    draw.text((cx - 38, cy - 22), eye_char, fill=accent, font=font)
    draw.text((cx + 14, cy - 22), eye_char if eye_char == "_" else "<", fill=accent, font=font)

    # Code line decoration
    draw.text((cx - 42, cy + 48), "_ ~ $", fill=CODE_GRAY, font=small)

    return frame


def main():
    frames_info = [
        (0,    ">", ACCENT),   # frame 1: rest, bright eyes
        (-6,   ">", ACCENT),   # frame 2: float up, bright
        (0,    "_", DIM),      # frame 3: back down, blink
        (0,    ">", ACCENT),   # frame 4: back to rest
    ]

    images = []
    for y_off, eye, col in frames_info:
        img = render_frame(y_off, eye, col)
        images.append(img)

    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    gif_path = assets_dir / "ghosty.gif"

    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=700,
        loop=0,
        transparency=0,
        disposal=2,
    )

    print(f"  GIF: {gif_path}")
    print(f"  {len(images)} frames x 700ms, looping")


if __name__ == "__main__":
    main()
