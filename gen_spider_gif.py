"""
Precision Pixel-Art Spider-Man Swing Engine
- Two distinct iconic white eye lenses with red eyeliner
- Raised hands gripped on the web thread
- Exact mathematical pivot at the hands so the silk thread connects 100% seamlessly at every frame
- Dynamic web-shooting from free arm when swinging
"""

from PIL import Image, ImageDraw
import math
import os

W, H = 850, 240
FRAMES = 36
DUR = 50

C_TRANS = (0, 0, 0, 0)
C_OUT   = (0, 0, 4, 255)
C_K_D   = (10, 10, 16, 255)
C_K_M   = (22, 22, 32, 255)
C_K_L   = (40, 40, 56, 255)
C_R_D   = (130, 5, 10, 255)
C_R_M   = (225, 10, 24, 255)
C_R_L   = (255, 60, 65, 255)
C_W     = (255, 255, 255, 255)
C_W_S   = (200, 210, 235, 255)
C_E_R   = (235, 15, 25, 255)

COLOR_MAP = {
    '.': C_TRANS,
    '#': C_OUT,
    'K': C_K_D,
    'k': C_K_M,
    'L': C_K_L,
    'R': C_R_M,
    'r': C_R_D,
    'B': C_R_L,
    'W': C_W,
    'w': C_W_S,
    'E': C_E_R
}

# 36x44 High-Detail Pixel Art
# Pose 1: Center Swoop (Both hands gripped high on web line, two sharp distinct eyes)
SPRITE_CENTER = """
....................####....................
...................#RRRR#...................
...................#RBBB#...................
...................#kRRk#...................
..................#KKKKKK#..................
.................#KKkLLkKK#.................
................#KkLLLLLLkK#................
................#kLEWkkWELk#................
................#kEWWwwWWEk#................
................#kEWWwwWWEk#................
................#kLEEEEEELk#................
.................#kLLLLLLk#.................
..................#kkRRkk#..................
.........####......#kRRk#......####.........
........#RRRR#....#rRBBRr#....#RRRR#........
.......#RBBBBR#..#rRBBkBRr#..#RBBBBR#.......
.......#kRBkkR#.##kRBkKKkBR##.#RkkBRk#......
........#kRkkR##kRkkKKKKkkRk##RkkRk#........
.........#kRRkRkRkKKKKKKKKkRkRkRRk#.........
..........#kRRkRkKKKKKKKKKKkRkRRk#..........
...........#kRRkkKKKKKKKKKKkkRRk#...........
............#kRkKKKKKKKKKKKKkRk#............
.............#kRkKKKKKKKKKKkRk#.............
..............#kRkKKKKKKKKkRk#..............
...............#kkRRRRRRRRkk#...............
................#kRRRRRRRRk#................
...............#kKKKKKKKKKKk#...............
..............#kKKk......kKKk#..............
.............#kKKk........kKKk#.............
............#kKKk..........kKKk#............
...........#kKKk............kKKk#...........
...........#kKk..............kKk#...........
..........#kKk................kKk#..........
..........#kKk................kKk#..........
..........#rRk................kRr#..........
.........#rRBk................kBRr#.........
.........#rRBk................kBRr#.........
..........#RRk................kRR#..........
..........#kk#................#kk#..........
............................................
"""

# Pose 2: Angled Swing (Left hand gripping web high, right hand extended/shooting, legs trailing)
SPRITE_SWING = """
................####........................
...............#RRRR#.......................
...............#RBBB#.......................
...............#kRRk#.......................
..............#KKKKKK#......................
.............#KKkLLkKK#.....................
............#KkLLLLLLkK#....................
............#kLEWkkWELk#....................
............#kEWWwwWWEk#....................
............#kEWWwwWWEk#....................
............#kLEEEEEELk#....................
.............#kLLLLLLk#.....................
..............#kkRRkk#......................
...............#kRRk#.......####............
..............#rRBBRr#.....#RRRR#...........
.............#rRBBkBRr#...#RBBBBR#..........
............#kRBkKKkBRk#..#kRBkkR#..........
...........#kRkkKKKKkkRk###kRkkRk#..........
..........#kRkKKKKKKKKkRkRkRkkRk#...........
.........#kRkKKKKKKKKKKkRkRRRRk#............
..........#kRRkkKKKKKKKKkRkRRk#.............
...........#kRkKKKKKKKKKKkRk#...............
............#kRkKKKKKKKKkRk#................
.............#kkRRRRRRRRkk#.................
..............#kRRRRRRRRk#..................
.............#kKKKKKKKKKKk#.................
............#kKKk......kKKk#................
...........#kKKk........kKKk#...............
..........#kKKk..........kKKk#..............
.........#kKKk............kKk#..............
........#kKk...............#k#..............
.......#kKk.................................
......#rRBk.................................
......#rRBk.................................
.......#RRk.................................
.......#kk#.................................
............................................
"""

def parse_sprite(text_art):
    lines = [l.strip() for l in text_art.strip().split('\n') if l.strip()]
    height = len(lines)
    width = max(len(l) for l in lines)
    img = Image.new('RGBA', (width, height), C_TRANS)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            color = COLOR_MAP.get(char, C_TRANS)
            img.putpixel((x, y), color)
    return img

SPR_IMG_CENTER = parse_sprite(SPRITE_CENTER)
SPR_IMG_SWING = parse_sprite(SPRITE_SWING)

def render_scene():
    anchor = (425, 14)
    thread_len = 100
    max_angle = 35.0
    scale = 3.0
    
    spr_center = SPR_IMG_CENTER.resize(
        (int(SPR_IMG_CENTER.width * scale), int(SPR_IMG_CENTER.height * scale)),
        Image.NEAREST
    )
    spr_swing = SPR_IMG_SWING.resize(
        (int(SPR_IMG_SWING.width * scale), int(SPR_IMG_SWING.height * scale)),
        Image.NEAREST
    )
    
    # Hand grip position in sprite local coordinates (top row center of hands)
    center_hand_x = spr_center.width * 0.49
    center_hand_y = spr_center.height * 0.04
    
    swing_hand_x = spr_swing.width * 0.40
    swing_hand_y = spr_swing.height * 0.04
    
    frames = []
    
    for i in range(FRAMES):
        t = i / FRAMES
        angle = max_angle * math.sin(2.0 * math.pi * t)
        velocity = (2.0 * math.pi / FRAMES) * max_angle * math.cos(2.0 * math.pi * t)
        speed = abs(velocity)
        
        # Base canvas
        canvas = Image.new('RGBA', (W, H), (6, 6, 9, 255))
        draw = ImageDraw.Draw(canvas)
        
        # Outer Comic Panel Border & Dark Charcoal Surface
        draw.rectangle([5, 5, W-5, H-5], fill=(9, 9, 14, 255), outline=(30, 30, 42, 255), width=2)
        
        # Cinematic Noir Skyline Silhouettes
        skyline_pts = [
            (5, H-5), (40, 185), (90, 185), (115, 160), (145, 160), (165, 200),
            (260, 200), (285, 150), (335, 150), (355, 210), (500, 210),
            (530, 140), (575, 140), (605, 190), (715, 190), (745, 155),
            (795, 155), (825, 185), (W-5, 185), (W-5, H-5)
        ]
        draw.polygon(skyline_pts, fill=(15, 15, 23, 255))
        
        # Water tower & architectural spires
        draw.rectangle([120, 142, 140, 160], fill=(20, 20, 30, 255))
        draw.polygon([(115, 142), (145, 142), (130, 130)], fill=(22, 22, 34, 255))
        
        # Distant glowing crimson beacon dots in city
        draw.ellipse([730, 35, 735, 40], fill=(229, 9, 20, 255))
        draw.ellipse([150, 45, 154, 49], fill=(255, 48, 48, 255))
        
        # Background web strands
        draw.line([(5, 5), (190, 65)], fill=(28, 28, 40, 255), width=1)
        draw.line([(W-5, 5), (650, 65)], fill=(28, 28, 40, 255), width=1)
        
        # Sprite selection
        if abs(angle) < 14:
            base_spr = spr_center
            local_hx = center_hand_x
            local_hy = center_hand_y
            flip = False
        elif angle >= 14:
            base_spr = spr_swing
            local_hx = swing_hand_x
            local_hy = swing_hand_y
            flip = False
        else: # angle <= -14
            base_spr = spr_swing.transpose(Image.FLIP_LEFT_RIGHT)
            local_hx = base_spr.width - swing_hand_x
            local_hy = swing_hand_y
            flip = True
            
        # Physics rotation
        rot_angle = -angle * 0.75
        rad_rot = math.radians(rot_angle)
        
        # Rotate sprite
        rotated_spr = base_spr.rotate(rot_angle, resample=Image.BICUBIC, expand=True)
        
        # Pendulum trajectory for gripped hand
        rad_swing = math.radians(angle)
        hand_world_x = anchor[0] + thread_len * math.sin(rad_swing)
        hand_world_y = anchor[1] + thread_len * math.cos(rad_swing)
        
        # Calculate offset from sprite center to gripped hand in rotated sprite
        orig_cx = base_spr.width / 2.0
        orig_cy = base_spr.height / 2.0
        dx = local_hx - orig_cx
        dy = local_hy - orig_cy
        
        # Rotate offset
        rot_dx = dx * math.cos(rad_rot) - dy * math.sin(rad_rot)
        rot_dy = dx * math.sin(rad_rot) + dy * math.cos(rad_rot)
        
        # Rotated sprite center position in world space
        spr_world_cx = hand_world_x - rot_dx
        spr_world_cy = hand_world_y - rot_dy
        
        paste_x = int(spr_world_cx - rotated_spr.width / 2.0)
        paste_y = int(spr_world_cy - rotated_spr.height / 2.0)
        
        # Catenary silk tension sag
        sag_x = (1 if angle > 0 else -1) * (1.0 - speed / 6.0) * 8
        sag_y = abs(sag_x) * 0.35
        mid_x = (anchor[0] + hand_world_x) / 2 + sag_x
        mid_y = (anchor[1] + hand_world_y) / 2 + sag_y
        
        # Draw smooth silk web line directly to hand
        pts = []
        for step in range(16):
            u = step / 15.0
            bx = (1-u)**2 * anchor[0] + 2*(1-u)*u * mid_x + u**2 * hand_world_x
            by = (1-u)**2 * anchor[1] + 2*(1-u)*u * mid_y + u**2 * hand_world_y
            pts.append((bx, by))
            
        draw.line(pts, fill=(120, 130, 160, 255), width=3)
        draw.line(pts, fill=(245, 248, 255, 255), width=2)
        
        # Web shooting stream at apex from free hand
        is_rising = (angle * velocity) > 0
        if is_rising and speed > 0.3:
            shoot_target = (spr_world_cx + (380 if velocity > 0 else -380), spr_world_cy - 120)
            web_origin = (spr_world_cx + (30 if velocity > 0 else -30), spr_world_cy - 5)
            draw.line([web_origin, shoot_target], fill=(229, 9, 20, 180), width=4)
            draw.line([web_origin, shoot_target], fill=(255, 255, 255, 255), width=2)
            # Muzzle burst
            draw.ellipse([web_origin[0]-7, web_origin[1]-7, web_origin[0]+7, web_origin[1]+7], fill=(255, 255, 255, 255))
            draw.ellipse([web_origin[0]-4, web_origin[1]-4, web_origin[0]+4, web_origin[1]+4], fill=(229, 9, 20, 255))
            
        # Paste the high-detail Spider-Man character
        canvas.paste(rotated_spr, (paste_x, paste_y), rotated_spr)
        
        # Top anchor bracket
        draw.ellipse([anchor[0]-6, anchor[1]-6, anchor[0]+6, anchor[1]+6], fill=(229, 9, 20, 255))
        draw.ellipse([anchor[0]-2, anchor[1]-2, anchor[0]+2, anchor[1]+2], fill=(255, 255, 255, 255))
        draw.line([anchor[0]-16, anchor[1], anchor[0]+16, anchor[1]], fill=(229, 9, 20, 255), width=2)
        
        # Comic corner brackets
        draw.line([(5, 22), (5, 5), (22, 5)], fill=(229, 9, 20, 255), width=2)
        draw.line([(W-5, H-22), (W-5, H-5), (W-22, H-5)], fill=(229, 9, 20, 255), width=2)
        
        # Telemetry footer text
        draw.text((25, H-20), "LIVE CONTRIBUTION FEED // REAL-TIME GITHUB TELEMETRY", fill=(95, 95, 120, 255))
        draw.text((W-185, H-20), "STATUS: SWINGING // LIVE", fill=(200, 45, 50, 255))
        
        frames.append(canvas.convert("RGB"))
        if (i+1) % 6 == 0:
            print(f"Generated frame {i+1}/{FRAMES}...")
            
    out_path = "assets/swinging-spider.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=DUR,
        loop=0,
        optimize=False
    )
    print(f"Saved pixel-art GIF {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    render_scene()
