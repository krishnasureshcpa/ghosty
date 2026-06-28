#!/usr/bin/env python3
"""Generate ghost GIF frames with subtle float + blink animation."""

from pathlib import Path

FRAMES_DIR = Path(__file__).parent.parent / "assets"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

# Frame configs: (suffix, y_offset_px, left_eye, right_eye)
# y_offset = how much to translate the body upward (float effect)
frames = [
    ("01-rest",      0, ">", "<"),   # rest, eyes bright
    ("02-float",    -6, ">", "<"),   # floated up 6px, eyes bright
    ("03-blink",     0, "_", "_"),   # back down, eyes blink
    ("04-rest",      0, ">", "<"),   # back to rest
]

SVG_TPL = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <defs>
    <radialGradient id="ambient" cx="50%" cy="40%" r="55%">
      <stop offset="0%"   stop-color="#8B5CF6" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="bodyShine" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#1A202C" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#161B22" stop-opacity="0"/>
    </linearGradient>
    <filter id="neon" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <rect width="400" height="400" fill="url(#ambient)"/>

  <!-- Ground shadow (stays at same Y, giving float illusion) -->
  <ellipse cx="200" cy="340" rx="90" ry="14" fill="#000" opacity="0.25"/>

  <g transform="translate(0, {y_offset})">
    <g filter="url(#shadow)">
      <!-- Body -->
      <path d="
        M 200 52
        C 120 52, 58 104, 58 188
        L 58 318
        L 90 340
        L 122 318
        L 154 340
        L 186 318
        L 200 336
        L 214 318
        L 246 340
        L 278 318
        L 310 340
        L 342 318
        L 342 188
        C 342 104, 280 52, 200 52 Z
      " fill="#161B22" stroke="#2D3748" stroke-width="1.8"/>

      <!-- Body highlight -->
      <path d="
        M 200 52
        C 120 52, 58 104, 58 188
        L 58 318
        L 90 340
        L 122 318
        L 154 340
        L 186 318
        L 200 336
        L 214 318
        L 246 340
        L 278 318
        L 310 340
        L 342 318
        L 342 188
        C 342 104, 280 52, 200 52 Z
      " fill="url(#bodyShine)" opacity="0.5"/>
    </g>

    <!-- Left eye socket -->
    <polygon points="140,150 170,142 180,164 156,180" fill="#0D1117" stroke="#1F2937" stroke-width="1.2"/>
    <polygon points="144,154 166,148 173,162 154,174" fill="#0D1117"/>

    <!-- Left eye glyph -->
    <text x="140" y="176" fill="#8B5CF6" font-family="'SF Mono','JetBrains Mono','Cascadia Code',monospace"
          font-size="28" font-weight="700" filter="url(#neon)">{left_eye}</text>

    <!-- Right eye socket -->
    <polygon points="260,150 230,142 220,164 244,180" fill="#0D1117" stroke="#1F2937" stroke-width="1.2"/>
    <polygon points="256,154 234,148 227,162 246,174" fill="#0D1117"/>

    <!-- Right eye glyph -->
    <text x="222" y="176" fill="#8B5CF6" font-family="'SF Mono','JetBrains Mono','Cascadia Code',monospace"
          font-size="28" font-weight="700" filter="url(#neon)">{right_eye}</text>

    <!-- Code line decoration -->
    <text x="148" y="245" fill="#4B5563" font-family="'SF Mono','JetBrains Mono',monospace"
          font-size="12" opacity="0.35" letter-spacing="1.5">_ ~ $</text>
  </g>
</svg>
'''

for suffix, y_off, le, re in frames:
    svg = SVG_TPL.format(y_offset=y_off, left_eye=le, right_eye=re)
    path = FRAMES_DIR / f"frame-{suffix}.svg"
    path.write_text(svg)
    print(f"  wrote {path.name}  (y_offset={y_off}, eyes='{le} {re}')")

print(f"\nDone — {len(frames)} frames in {FRAMES_DIR}")
