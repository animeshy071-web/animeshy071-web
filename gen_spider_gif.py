"""
Generate a high-quality animated GIF of a pixel-art Scarlet/Miles Spider-Man
swinging on a web thread across the banner, shooting webs at the apex.
"""
from PIL import Image, ImageDraw
import math
import os

# ─────────────────────────────────────────────────────────────────────────────
# CANVAS & ANIMATION PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
W, H    = 850, 220       # canvas size
B       = 9              # pixel-block size (larger = crisper, more visible)
FRAMES  = 36             # frames per full loop
DUR     = 60             # ms per frame → 36 × 60ms = 2.16s seamless loop

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
BG      = (5,   5,   5)
DARK    = (22,  22,  32)   # main suit body
DRK     = (11,  11,  18)   # shadow / deep suit
RED     = (200, 0,   14)   # red accent
BRED    = (229, 9,   20)   # bright red (logo / glow)
EYE     = (238, 242, 255)  # white eye lens
EYE2    = (200, 210, 240)  # inner eye tint
SILK    = (190, 192, 215)  # web silk thread
WEB_SHT = (229, 9,   20)   # web-shooting beam (crimson)
ANCHOR  = (229, 9,   20)   # anchor dot
LABEL   = (80,  80,  100)  # bottom label text

# ─────────────────────────────────────────────────────────────────────────────
# PENDULUM PHYSICS
# ─────────────────────────────────────────────────────────────────────────────
AX, AY   = 425, 6     # top anchor point
TLEN     = 112        # thread length (anchor → character torso center)
AMP      = 40.0       # swing amplitude in degrees

def swing_angle(frame):
    """Smooth cosine pendulum — returns degrees, positive = swings right."""
    t = frame / FRAMES
    return AMP * math.cos(2.0 * math.pi * t)

# ─────────────────────────────────────────────────────────────────────────────
# PIXEL ART CHARACTER DEFINITION
# (col, row, color) in character-space.
# Origin (col=0, row=0) = torso center.
# Rows are positive downward. Each unit = B actual pixels.
#
# Design: Scarlet/Miles style. Black suit, red markings, large white eye lenses.
# Pose: left arm raised UP-LEFT (grabs silk), right arm extended right, 
#       legs swept back for dynamic swing look.
# ─────────────────────────────────────────────────────────────────────────────
def build_character():
    pix = []

    def a(col, row, color):
        pix.append((col, row, color))

    # ── HEAD ─────────────────────────────────────────────────────────────────
    # Top cap (row -13)
    for c in (-2,-1,0,1,2):         a(c, -13, DARK)
    # Wide head rows (-12 to -11)
    for r in (-12, -11):
        for c in range(-3, 4):      a(c, r, DARK)
    # Eye row 1 (row -10) — large angular lenses
    a(-3, -10, DARK)
    a(-2, -10, EYE);  a(-1, -10, EYE)   # left lens (2 wide)
    a(0,  -10, DARK)                      # bridge (1 wide)
    a(1,  -10, EYE);  a(2,  -10, EYE)   # right lens
    a(3,  -10, DARK)
    # Eye row 2 (row -9) — bottom of lenses, slightly wider
    a(-3, -9, DARK)
    a(-2, -9, EYE);  a(-1, -9, EYE);  a(0, -9, EYE)  # left lens wider
    a(1,  -9, DARK)                                     # bridge
    a(2,  -9, EYE);  a(3,  -9, EYE)                   # right lens
    a(4,  -9, DARK)
    # Below eyes (-8 to -7)
    for r in (-8, -7):
        for c in range(-3, 4):      a(c, r, DARK)
    # Chin (-6)
    for c in (-2,-1,0,1,2):         a(c, -6, DARK)

    # ── NECK ─────────────────────────────────────────────────────────────────
    for c in (-1, 0, 1):            a(c, -5, DARK)

    # ── TORSO ────────────────────────────────────────────────────────────────
    # Shoulders (row -4)
    for c, col_c in [
        (-5,DARK), (-4,RED), (-3,RED), (-2,DARK), (-1,DARK), (0,DARK),
        (1,DARK), (2,RED), (3,RED), (4,DARK), (5,DARK)
    ]:                               a(c, -4, col_c)

    # Upper chest (row -3)
    for c, col_c in [
        (-5,DRK), (-4,DARK), (-3,RED), (-2,RED), (-1,DARK),
        (0,DARK), (1,RED), (2,RED), (3,DARK), (4,DRK)
    ]:                               a(c, -3, col_c)

    # Web emblem row (row -2) — bright red wings spread out
    for c, col_c in [
        (-4,DRK), (-3,BRED), (-2,DARK), (-1,DARK),
        (0,DARK), (1,DARK), (2,BRED), (3,DRK)
    ]:                               a(c, -2, col_c)

    # Mid torso (rows -1 to 2)
    for r in (-1, 0, 1, 2):
        for c in range(-4, 5):      a(c, r, DARK)

    # Waist/hips (row 3)
    for c, col_c in [
        (-3,DARK),(-2,DARK),(-1,DRK),(0,DRK),(1,DRK),(2,DARK),(3,DARK)
    ]:                               a(c, 3, col_c)

    # ── LEFT ARM — raised UP-LEFT (grabbing the silk thread) ─────────────────
    # Goes diagonally from shoulder (-5,-4) up to hand at (-10,-11)
    a(-6, -4, DARK)
    a(-7, -5, DARK)
    a(-8, -7, DARK)
    a(-9, -8, DARK)
    a(-9, -9, RED)    # forearm red cuff
    a(-10, -9, RED)
    a(-10, -10, RED)  # wrist
    a(-9, -11, RED)   # hand / web-shooter tip (this is where thread attaches)
    a(-10, -11, RED)

    # ── RIGHT ARM — extended outward (free arm for balance / web-shooting) ────
    a(6, -3, DARK)
    a(7, -2, DARK)
    a(8, -1, DARK)
    a(8,  0, RED)   # forearm red
    a(7,  1, RED)
    a(6,  2, RED)   # fist

    # ── LEFT LEG — swept back/up ──────────────────────────────────────────────
    a(-3, 4, DARK);  a(-4, 4, RED)    # upper thigh, red stripe
    a(-4, 5, DARK)
    a(-5, 6, DARK);  a(-5, 7, RED)   # calf
    a(-6, 8, DARK);  a(-6, 9, RED)   # boot
    a(-5, 9, DARK);  a(-7, 9, DARK)

    # ── RIGHT LEG — sweeps forward ────────────────────────────────────────────
    a(3,  4, DARK);  a(4, 4, RED)     # upper thigh, red stripe
    a(4,  5, DARK)
    a(5,  6, DARK);  a(6, 6, RED)    # calf
    a(6,  7, DARK);  a(6, 8, RED)    # boot
    a(5,  8, DARK);  a(7, 8, DARK)

    return pix

CHARACTER = build_character()

# Hand attachment point in character-space (where silk thread meets)
HAND_COL = -9
HAND_ROW = -11

# Right-hand / web-shooter tip in character-space
RHAND_COL = 8
RHAND_ROW  = 0

# ─────────────────────────────────────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def char_to_world(cx, cy, col, row, cos_a, sin_a):
    """Convert character-space (col, row) to world (x, y)."""
    lx = col * B + B * 0.5
    ly = row * B + B * 0.5
    rx = lx * cos_a - ly * sin_a
    ry = lx * sin_a + ly * cos_a
    return cx + rx, cy + ry

def draw_block(draw, cx, cy, col, row, color, cos_a, sin_a):
    """Draw a rotated B×B block."""
    wx, wy = char_to_world(cx, cy, col, row, cos_a, sin_a)
    x0, y0 = int(wx - B * 0.5), int(wy - B * 0.5)
    draw.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], fill=color)

def draw_silk(draw, x1, y1, x2, y2, width=2):
    """Draw silk thread with slight double-line for thickness."""
    draw.line([(x1, y1), (x2, y2)], fill=SILK, width=width)

def draw_web_shoot(draw, hx, hy, angle_deg, strength):
    """Draw web-shooting streak from hand. strength 0–1."""
    if strength <= 0:
        return
    # Web goes to the OPPOSITE upper corner (classic swing swap)
    direction = 1 if angle_deg < 0 else -1  # shoot toward far side
    tx = AX + direction * 360
    ty = AY - 10

    # Draw beam with decreasing width/opacity effect (solid GIF, fake it with multiple lines)
    alpha_col = tuple(int(c * strength) for c in WEB_SHT)
    half_alpha = tuple(int(c * strength * 0.4) for c in WEB_SHT)

    # Core beam
    draw.line([(hx, hy), (tx, ty)], fill=alpha_col, width=2)
    # Fading outer glow lines
    draw.line([(hx-1, hy), (tx, ty-1)], fill=half_alpha, width=1)
    draw.line([(hx+1, hy), (tx, ty+1)], fill=half_alpha, width=1)

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE FRAMES
# ─────────────────────────────────────────────────────────────────────────────
def draw_frame(frame_idx):
    img  = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    angle_deg = swing_angle(frame_idx)
    angle_rad = math.radians(angle_deg)
    cos_a     = math.cos(angle_rad)
    sin_a     = math.sin(angle_rad)

    # Torso center along pendulum arc
    cx = AX + TLEN * math.sin(angle_rad)
    cy = AY + TLEN * math.cos(angle_rad)

    # Faint atmosphere web strands (static, baked into every frame)
    draw.line([(0,0),   (180, 70)], fill=(40,40,55), width=1)
    draw.line([(0,0),   (250, 90)], fill=(30,30,45), width=1)
    draw.line([(850,0), (670, 70)], fill=(40,40,55), width=1)
    draw.line([(850,0), (600, 90)], fill=(30,30,45), width=1)

    # ── Anchor glow dot ──
    draw.ellipse([AX-5, AY-5, AX+5, AY+5], fill=BRED)
    draw.ellipse([AX-3, AY-3, AX+3, AY+3], fill=(255, 60, 60))

    # ── Silk thread: anchor → character's left hand ──
    hand_wx, hand_wy = char_to_world(cx, cy, HAND_COL, HAND_ROW, cos_a, sin_a)
    draw_silk(draw, AX, AY, hand_wx, hand_wy, width=2)

    # ── Web-shooting from free right hand at apex ──
    # Strength peaks at |angle| > 30°, zero below 28°
    web_strength = max(0.0, (abs(angle_deg) - 28.0) / (AMP - 28.0))
    if web_strength > 0:
        rhand_wx, rhand_wy = char_to_world(cx, cy, RHAND_COL, RHAND_ROW, cos_a, sin_a)
        draw_web_shoot(draw, rhand_wx, rhand_wy, angle_deg, web_strength)

    # ── Draw all character pixels ──
    for col, row, color in CHARACTER:
        draw_block(draw, cx, cy, col, row, color, cos_a, sin_a)

    # ── Label ──
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
        label = "LIVE CONTRIBUTION FEED  //  github.com/animeshy071-web"
        draw.text((W//2 - len(label)*3, H - 18), label, fill=LABEL, font=font)
    except Exception:
        pass

    return img

print("Generating frames...")
frames = []
for i in range(FRAMES):
    f = draw_frame(i)
    frames.append(f)
    if (i + 1) % 6 == 0:
        print(f"  Frame {i+1}/{FRAMES}")

out_path = 'assets/swinging-spider.gif'
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=DUR,
    loop=0,
    optimize=False,
)
size_kb = os.path.getsize(out_path) / 1024
print(f"\n✅ Saved {out_path}")
print(f"   {FRAMES} frames × {DUR}ms = {FRAMES * DUR / 1000:.2f}s loop")
print(f"   File size: {size_kb:.1f} KB")
print(f"   Canvas: {W}×{H}px, Block size: {B}px")
