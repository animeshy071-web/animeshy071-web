"""
GitHub Contribution Cityscape with Travelling 90s Spider-Man
Renders an animated GIF where Spider-Man is travelling/swinging across a parallax
cityscape constructed entirely of GitHub commit contribution blocks.
"""

from PIL import Image, ImageDraw
import numpy as np
import math
import os

W, H = 850, 220
FRAMES = 20  # 20 frames loop (2 full cycles of the 10-frame sprite)
DUR = 100    # 100ms per frame -> 2.0s smooth loop

# Load devspidey90 frames and strip white background cleanly
def load_clean_spidey_frames():
    im = Image.open('assets/devspidey90.gif')
    raw_frames = []
    for i in range(im.n_frames):
        im.seek(i)
        f = im.convert('RGBA')
        data = np.array(f)
        r, g, b, a = data.T
        
        # Flood-fill or color key white background
        white_mask = (r > 235) & (g > 235) & (b > 235)
        data[..., 3][white_mask.T] = 0
        
        cleaned = Image.fromarray(data)
        raw_frames.append(cleaned)
    return raw_frames

CLEAN_SPIDEY_FRAMES = load_clean_spidey_frames()

# Commit heat map color palette for git block windows
GIT_EMPTY  = (22, 27, 34)
GIT_DARK1  = (33, 38, 45)
GIT_DARK2  = (40, 20, 24)
GIT_LOW    = (90, 16, 22)
GIT_MED    = (160, 12, 20)
GIT_HIGH   = (229, 9, 20)
GIT_PEAK   = (255, 60, 60)

# Predefined skyline blueprint of GitHub commit buildings
# Array of (building_width_cols, building_height_rows, building_style)
BUILDINGS_FAR = [
    (6, 11), (4, 15), (7, 9), (5, 17), (8, 12), (5, 14), (6, 16), (4, 10),
    (7, 13), (5, 18), (6, 12), (5, 15), (8, 11), (4, 16), (6, 14), (5, 12)
]

BUILDINGS_MID = [
    (5, 9), (4, 13), (6, 7), (5, 11), (7, 8), (4, 14), (5, 10), (6, 8),
    (4, 12), (5, 9), (6, 13), (4, 7), (5, 11), (7, 9), (4, 12), (6, 10)
]

def render_git_block(draw, x, y, size, color, alpha=255):
    # Rounded commit square
    draw.rounded_rectangle([x, y, x + size, y + size], radius=2, fill=color)

def generate_git_city_animation():
    # Grid parameters
    # Far layer: 7px blocks + 2px gap = 9px step
    far_step = 9
    far_size = 7
    far_speed = 3  # px per frame
    
    # Mid layer: 10px blocks + 3px gap = 13px step (matches GitHub commit cell exactly)
    mid_step = 13
    mid_size = 10
    mid_speed = 6.5 # px per frame -> 20 * 6.5 = 130px (exactly 10 columns! Perfect seamless loop)
    
    # Spider-Man scale and swing bobbing
    spidey_scale = 0.95
    
    frames = []
    
    # Deterministic pseudorandom window colors based on coordinate hashing
    def get_window_color(col, row, is_far=False):
        val = (math.sin(col * 12.9898 + row * 78.233) * 43758.5453) % 1.0
        if is_far:
            if val < 0.65: return (16, 20, 26)
            elif val < 0.85: return (35, 20, 24)
            elif val < 0.95: return (80, 14, 20)
            else: return (180, 20, 30)
        else:
            if val < 0.50: return GIT_EMPTY
            elif val < 0.70: return GIT_DARK2
            elif val < 0.85: return GIT_LOW
            elif val < 0.95: return GIT_MED
            elif val < 0.98: return GIT_HIGH
            else: return GIT_PEAK

    for frame_idx in range(FRAMES):
        # Canvas
        canvas = Image.new('RGB', (W, H), (8, 8, 12))
        draw = ImageDraw.Draw(canvas)
        
        # Outer panel frame
        draw.rectangle([4, 4, W-4, H-4], fill=(9, 9, 14), outline=(32, 32, 44), width=2)
        
        # Atmospheric night sky gradient / halftone stars
        for sx in range(20, W-20, 45):
            for sy in range(15, 75, 25):
                star_val = (math.sin(sx * 3.1 + sy * 5.7 + frame_idx * 0.2)) % 1.0
                if star_val > 0.85:
                    draw.ellipse([sx, sy, sx+1, sy+1], fill=(120, 125, 150))
        
        # ── 1. FAR LAYER: DISTANT GIT BLOCK TOWERS (Slow Parallax) ──
        far_offset = int((frame_idx * far_speed) % (len(BUILDINGS_FAR) * far_step * 6))
        col_x = -far_offset % (far_step * 6) - (far_step * 6)
        
        b_idx = 0
        while col_x < W + 50:
            b_w, b_h = BUILDINGS_FAR[b_idx % len(BUILDINGS_FAR)]
            for bc in range(b_w):
                cur_x = col_x + bc * far_step
                if -far_step <= cur_x <= W:
                    # Draw column of git commit squares from bottom up
                    for br in range(b_h):
                        cur_y = H - 20 - (br + 1) * far_step
                        w_color = get_window_color(b_idx * 10 + bc, br, is_far=True)
                        render_git_block(draw, cur_x, cur_y, far_size, w_color)
            # Antenna on tall buildings
            if b_h > 14 and 0 <= col_x + (b_w // 2) * far_step <= W:
                ant_x = col_x + (b_w // 2) * far_step + 3
                ant_top_y = H - 20 - (b_h + 3) * far_step
                draw.line([(ant_x, H - 20 - b_h * far_step), (ant_x, ant_top_y)], fill=(50, 50, 70), width=1)
                draw.ellipse([ant_x-1, ant_top_y-1, ant_x+2, ant_top_y+2], fill=(229, 9, 20))
                
            col_x += b_w * far_step + far_step # building gap
            b_idx += 1

        # ── 2. MIDGROUND LAYER: MAIN GIT COMMIT BUILDINGS (Fast Parallax) ──
        mid_offset = int((frame_idx * mid_speed))
        # Total midground loop period is 130px (10 columns = 2 buildings)
        col_x = - (mid_offset % 390) - 50
        
        b_idx = 0
        while col_x < W + 60:
            b_w, b_h = BUILDINGS_MID[b_idx % len(BUILDINGS_MID)]
            for bc in range(b_w):
                cur_x = col_x + bc * mid_step
                if -mid_step <= cur_x <= W:
                    for br in range(b_h):
                        cur_y = H - 16 - (br + 1) * mid_step
                        w_color = get_window_color(b_idx * 10 + bc, br, is_far=False)
                        render_git_block(draw, cur_x, cur_y, mid_size, w_color)
            # Architectural spire / red beacon
            if b_h > 11 and 0 <= col_x + (b_w // 2) * mid_step <= W:
                ant_x = col_x + (b_w // 2) * mid_step + 5
                ant_top_y = H - 16 - (b_h + 2) * mid_step
                draw.line([(ant_x, H - 16 - b_h * mid_step), (ant_x, ant_top_y)], fill=(90, 95, 120), width=1)
                draw.ellipse([ant_x-2, ant_top_y-2, ant_x+2, ant_top_y+2], fill=(255, 48, 48))
                
            col_x += b_w * mid_step + mid_step
            b_idx += 1

        # ── 3. HORIZONTAL SPEED LINES / COMIC TRAVELLING MOTION ──
        for line_y in [35, 55, 80, 110, 150]:
            lx = (W - (frame_idx * 18 + line_y * 7) % (W + 200)) - 100
            draw.line([(lx, line_y), (lx + 60, line_y)], fill=(40, 45, 60), width=1)

        # ── 4. SPIDER-MAN SWINGING / TRAVELLING SPRITE ──
        sp_frame = CLEAN_SPIDEY_FRAMES[frame_idx % len(CLEAN_SPIDEY_FRAMES)]
        
        # Smooth swing bobbing
        bob_y = int(math.sin(frame_idx * (2.0 * math.pi / 10.0)) * 14.0)
        bob_x = int(math.cos(frame_idx * (2.0 * math.pi / 10.0)) * 16.0)
        
        sp_w = int(sp_frame.width * spidey_scale)
        sp_h = int(sp_frame.height * spidey_scale)
        sp_resized = sp_frame.resize((sp_w, sp_h), Image.NEAREST)
        
        # Position Spider-Man centered-left
        sp_x = W // 2 - sp_w // 2 + bob_x - 30
        sp_y = H // 2 - sp_h // 2 + bob_y - 15
        
        # ── 5. EXTENDED SILK WEB STRANDS (Connected to skyscrapers) ──
        # Left hand web line shooting to upper-left building
        web1_start = (sp_x + int(sp_w * 0.35), sp_y + 10)
        web1_anchor = (sp_x - 220 + bob_x * 2, -10)
        draw.line([web1_start, web1_anchor], fill=(200, 205, 225), width=2)
        draw.line([web1_start, web1_anchor], fill=(130, 140, 170), width=3)
        
        # Right hand web line shooting to upper-right building
        web2_start = (sp_x + int(sp_w * 0.85), sp_y + 25)
        web2_anchor = (sp_x + 360 - bob_x * 2, -15)
        if frame_idx % 10 in [2, 3, 4, 5]:
            draw.line([web2_start, web2_anchor], fill=(229, 9, 20), width=3)
            draw.line([web2_start, web2_anchor], fill=(255, 255, 255), width=1)
        
        # Paste isolated Spider-Man sprite cleanly onto the canvas
        canvas.paste(sp_resized, (sp_x, sp_y), sp_resized)
        
        # ── 6. COMIC CORNER BRACKETS & TELEMETRY ──
        draw.line([(4, 22), (4, 4), (22, 4)], fill=(229, 9, 20), width=2)
        draw.line([(W-4, H-22), (W-4, H-4), (W-22, H-4)], fill=(229, 9, 20), width=2)
        
        # Telemetry footer
        draw.text((22, H-18), "GITHUB COMMITS METROPOLIS // TRAVELLING FEED", fill=(100, 105, 130))
        draw.text((W-180, H-18), "VELOCITY: SWINGING // LIVE", fill=(210, 40, 45))
        
        frames.append(canvas)
        if (frame_idx + 1) % 5 == 0:
            print(f"Rendered frame {frame_idx+1}/{FRAMES}...")
            
    out_path = "assets/devspidey90.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=DUR,
        loop=0,
        optimize=False
    )
    print(f"Generated {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_git_city_animation()
