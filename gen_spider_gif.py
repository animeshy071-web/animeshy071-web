"""
gen_spider_gif.py v2 — High-quality animated GIF using SPRITE ROTATION.
The whole character image is rotated as one unit per frame, giving clean
anti-aliased motion instead of rotated individual pixel blocks.
"""
from PIL import Image, ImageDraw
import math, os

# ─────────────────────────────────────────────────────────────────────────────
# CANVAS & ANIMATION
# ─────────────────────────────────────────────────────────────────────────────
W, H   = 850, 220
FRAMES = 40
DUR    = 55       # ms/frame → 40×55 = 2.2s seamless loop

# ─────────────────────────────────────────────────────────────────────────────
# SPRITE SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
SCALE  = 7        # actual px per character-pixel block
# Character grid size in character-pixels
CW, CH = 22, 34   # 22 wide × 34 tall → sprite = 154×238px

# Colors (RGBA)
DARK  = (20,  20,  30,  255)
DRK   = (10,  10,  18,  255)
RED   = (196, 0,   12,  255)
BRED  = (229, 9,   20,  255)
EYE   = (240, 244, 255, 255)
EYE2  = (185, 200, 240, 255)
TRANS = (0, 0, 0, 0)

# Canvas colors (RGB)
BG    = (5,   5,   5)
SILK  = (185, 188, 208)
WEB_C = (229, 9,   20)
LABEL = (72,  72,  92)

# ─────────────────────────────────────────────────────────────────────────────
# PENDULUM
# ─────────────────────────────────────────────────────────────────────────────
AX, AY = 425, 5
TLEN   = 100    # anchor → hand distance (not torso center)
AMP    = 40.0   # swing degrees

def swing_angle(f):
    return AMP * math.cos(2.0 * math.pi * f / FRAMES)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD CHARACTER SPRITE (RGBA, transparent bg)
# ─────────────────────────────────────────────────────────────────────────────
def make_sprite():
    """
    Design: Scarlet-style spider-hero. Front-facing body.
    LEFT ARM raised UP-LEFT diagonally (web-grabbing arm) — this is the pivot.
    RIGHT ARM extended outward.
    Legs: dynamic swinging pose.
    """
    img = Image.new('RGBA', (CW * SCALE, CH * SCALE), TRANS)
    d   = ImageDraw.Draw(img)

    def b(col, row, color):
        if 0 <= col < CW and 0 <= row < CH:
            x0, y0 = col * SCALE, row * SCALE
            d.rectangle([x0, y0, x0 + SCALE - 1, y0 + SCALE - 1], fill=color)

    # ── RAISED LEFT ARM (web-grabbing, points up-left) ────────────────────
    # Hand/wrist at top-left area → this is the thread attachment
    b(1,  0,  RED)    # hand / web-shooter tip   ← thread attaches here
    b(2,  0,  RED)
    b(1,  1,  RED)    # wrist
    b(2,  2,  RED)    # forearm cuff
    b(3,  3,  DARK)   # forearm
    b(4,  4,  DARK)   # upper arm
    b(5,  5,  DARK)   # shoulder area

    # ── HEAD (centered ~cols 7–14) ────────────────────────────────────────
    # Row 2: narrow top
    for c in range(8, 14):    b(c, 2, DARK)
    # Row 3: wide head
    for c in range(7, 15):    b(c, 3, DARK)
    # Row 4: full head
    for c in range(7, 15):    b(c, 4, DARK)
    # Row 5: EYE ROW 1 — large angular white lenses
    b(7,  5, DARK)
    b(8,  5, EYE);  b(9,  5, EYE)     # left lens
    b(10, 5, DARK)                      # bridge
    b(11, 5, EYE);  b(12, 5, EYE);  b(13, 5, EYE)   # right lens (wider)
    b(14, 5, DARK)
    # Row 6: EYE ROW 2 — bottom of lenses
    b(7,  6, DARK)
    b(8,  6, EYE);  b(9,  6, EYE);  b(10, 6, EYE)   # left lens wider at bottom
    b(11, 6, DARK)                                     # bridge
    b(12, 6, EYE);  b(13, 6, EYE)                    # right lens
    b(14, 6, DARK)
    # Row 7: lower face
    for c in range(7, 15):    b(c, 7, DARK)
    # Row 8: chin
    for c in range(8, 14):    b(c, 8, DARK)

    # ── NECK ─────────────────────────────────────────────────────────────
    b(10, 9, DARK);  b(11, 9, DARK);  b(10, 10, DARK);  b(11, 10, DARK)

    # ── TORSO ────────────────────────────────────────────────────────────
    # Row 11: shoulders (red accents on outer edges)
    b(6,  11, DARK)
    b(7,  11, RED);  b(8,  11, RED)   # left shoulder red
    for c in range(9, 14):  b(c, 11, DARK)
    b(14, 11, RED);  b(15, 11, RED)   # right shoulder red
    b(16, 11, DARK)

    # Row 12: upper chest
    b(6,  12, DRK)
    b(7,  12, DARK)
    b(8,  12, RED)
    for c in range(9, 14):  b(c, 12, DARK)
    b(14, 12, RED)
    b(15, 12, DARK)
    b(16, 12, DRK)

    # Row 13: chest web logo — bright red wings
    b(7,  13, DARK)
    b(8,  13, BRED)    # logo left wing
    for c in range(9, 13):  b(c, 13, DARK)
    b(13, 13, BRED)    # logo right wing
    b(14, 13, DARK)

    # Row 14: mid-chest
    for c in range(7, 16):  b(c, 14, DARK)

    # Rows 15-17: torso body
    for r in (15, 16, 17):
        for c in range(7, 16):  b(c, r, DARK)

    # Row 18: waist
    for c in range(8, 15):  b(c, 18, DARK)

    # Row 19: hips
    for c in range(8, 15):  b(c, 19, DRK)

    # ── RIGHT ARM (free arm, extends RIGHT) ───────────────────────────────
    b(16, 12, DARK)
    b(17, 12, DARK)
    b(18, 13, DARK)
    b(19, 14, DARK)
    b(19, 15, RED)    # forearm red
    b(18, 16, RED)
    b(17, 16, RED)    # fist

    # ── LEFT LEG (swept back/left) ─────────────────────────────────────────
    b(9,  20, DARK);  b(8,  20, RED)    # thigh red stripe
    b(8,  21, DARK)
    b(7,  22, DARK);  b(7,  23, RED)    # calf
    b(6,  24, DARK);  b(6,  25, RED)    # boot
    b(5,  25, DARK);  b(7,  25, DARK)

    # ── RIGHT LEG (sweeps forward/right) ───────────────────────────────────
    b(12, 20, DARK);  b(13, 20, RED)    # thigh red stripe
    b(13, 21, DARK)
    b(14, 22, DARK);  b(14, 23, RED)    # calf
    b(15, 24, DARK);  b(15, 25, RED)    # boot
    b(14, 25, DARK);  b(16, 25, DARK)

    return img

SPRITE = make_sprite()

# Hand attachment point in SPRITE SPACE (before rotation)
# Hand is at character-pixel (1, 0) → in actual pixels relative to sprite origin
HAND_SX = 1 * SCALE + SCALE // 2   # center of block (1,0)
HAND_SY = 0 * SCALE + SCALE // 2

# Sprite center (reference point for rotation/positioning)
SPR_CX = CW * SCALE // 2   # 77
SPR_CY = CH * SCALE // 2   # 119

# Pre-compute: hand offset FROM sprite center (in sprite pixels, before rotation)
HAND_OFF_X = HAND_SX - SPR_CX   # negative → hand is to the left of center
HAND_OFF_Y = HAND_SY - SPR_CY   # negative → hand is above center

# Right-hand (free arm) offset for web-shooting
RHAND_SX = 17 * SCALE + SCALE // 2
RHAND_SY = 16 * SCALE + SCALE // 2
RHAND_OFF_X = RHAND_SX - SPR_CX
RHAND_OFF_Y = RHAND_SY - SPR_CY

# ─────────────────────────────────────────────────────────────────────────────
# FRAME RENDERING
# ─────────────────────────────────────────────────────────────────────────────
def rotated_offset(off_x, off_y, angle_deg):
    """Rotate an (off_x, off_y) vector by angle_deg (CW positive)."""
    rad   = math.radians(-angle_deg)   # PIL rotates CCW, swing is CW when +angle
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    return (off_x * cos_a - off_y * sin_a,
            off_x * sin_a + off_y * cos_a)

def draw_frame(f):
    canvas = Image.new('RGB', (W, H), BG)
    draw   = ImageDraw.Draw(canvas)
    angle  = swing_angle(f)
    rad    = math.radians(angle)

    # ── Atmosphere web lines ──
    draw.line([(0, 0),   (170, 62)],  fill=(36,36,50), width=1)
    draw.line([(0, 0),   (245, 82)],  fill=(26,26,40), width=1)
    draw.line([(850, 0), (680, 62)],  fill=(36,36,50), width=1)
    draw.line([(850, 0), (605, 82)],  fill=(26,26,40), width=1)

    # ── Hand world position: hangs at TLEN from anchor ──
    # The hand is the PIVOT of the swing.
    hand_wx = AX + TLEN * math.sin(rad)
    hand_wy = AY + TLEN * math.cos(rad)

    # ── Silk thread: anchor → hand ──
    draw.line([(AX, AY), (int(hand_wx), int(hand_wy))], fill=SILK, width=2)

    # ── Sprite center: hand pos MINUS the rotated hand offset ──
    # rotated_offset gives the hand's position relative to sprite center after rotation
    rox, roy = rotated_offset(HAND_OFF_X, HAND_OFF_Y, angle)
    spr_cx   = hand_wx - rox
    spr_cy   = hand_wy - roy

    # ── Rotate sprite ──
    # PIL.Image.rotate: positive angle = CCW. Swing right = CW = negative PIL angle.
    rotated = SPRITE.rotate(-angle, resample=Image.BICUBIC, expand=True)

    # Paste centered at (spr_cx, spr_cy)
    px = int(spr_cx - rotated.width  // 2)
    py = int(spr_cy - rotated.height // 2)
    canvas.paste(rotated, (px, py), rotated)

    # ── Anchor glow dot ──
    draw.ellipse([AX-5, AY-5, AX+5, AY+5], fill=(229, 9, 20))
    draw.ellipse([AX-2, AY-2, AX+2, AY+2], fill=(255, 90, 90))

    # ── Web-shooting at apex ──
    web_str = max(0.0, (abs(angle) - 27.0) / (AMP - 27.0))
    if web_str > 0.05:
        # Compute rotated right-hand position
        rrox, rroy = rotated_offset(RHAND_OFF_X, RHAND_OFF_Y, angle)
        rhx = spr_cx + rrox
        rhy = spr_cy + rroy
        direction = 1 if angle < 0 else -1
        tx = AX + direction * 370
        ty = AY - 8
        wc  = tuple(int(c * min(1.0, web_str)) for c in WEB_C)
        wc2 = tuple(int(c * web_str * 0.4) for c in WEB_C)
        draw.line([(rhx, rhy), (tx, ty)], fill=wc, width=2)
        draw.line([(rhx - 1, rhy), (tx, ty - 1)], fill=wc2, width=1)

    # ── Re-draw silk thread on top of sprite (so it's crisp above bg) ──
    draw.line([(AX, AY), (int(hand_wx), int(hand_wy))], fill=SILK, width=2)

    # ── Label ──
    label = "LIVE CONTRIBUTION FEED  //  github.com/animeshy071-web"
    draw.text((W // 2 - len(label) * 3, H - 18), label, fill=LABEL)

    return canvas

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE & SAVE
# ─────────────────────────────────────────────────────────────────────────────
print(f"Generating {FRAMES} frames (sprite: {CW*SCALE}x{CH*SCALE}px, block={SCALE}px)...")
frames = []
for i in range(FRAMES):
    frames.append(draw_frame(i))
    if (i + 1) % 8 == 0:
        print(f"  {i+1}/{FRAMES} frames done")

out = 'assets/swinging-spider.gif'
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    duration=DUR,
    loop=0,
    optimize=False,
)
kb = os.path.getsize(out) / 1024
print(f"Done: {out} | {FRAMES}f x {DUR}ms = {FRAMES*DUR/1000:.2f}s | {kb:.0f}KB")
