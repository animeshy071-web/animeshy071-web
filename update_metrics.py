import urllib.request
import json
from datetime import datetime, timedelta

def update_github_metrics():
    # Fetch real user contributions
    url = "https://github-contributions-api.jogruber.de/v4/animeshy071-web"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    contributions = data.get("contributions", [])
    contrib_map = {d["date"]: d for d in contributions}
    total_2026 = data.get("total", {}).get("2026", 69)
    active_days_count = len([d for d in contributions if d.get("date", "").startswith("2026") and d.get("count", 0) > 0])

    today = datetime(2026, 8, 26)
    
    # 24 columns x 4 rows
    cols = 24
    rows = 4
    
    # Map levels to exact graphic novel palette colors
    level_colors = {
        0: "#121218",
        1: "#5c0a0e",
        2: "#9c0910",
        3: "#E50914",
        4: "#FF3030"
    }

    rect_svg_lines = []
    
    for c in range(cols):
        for r in range(rows):
            days_ago = (cols - 1 - c) * rows + (rows - 1 - r)
            target_date = today - timedelta(days=days_ago)
            d_str = target_date.strftime("%Y-%m-%d")
            entry = contrib_map.get(d_str, {"count": 0, "level": 0})
            lvl = entry.get("level", 0)
            cnt = entry.get("count", 0)
            
            x = c * 22
            y = r * 19
            fill_color = level_colors.get(lvl, "#121218")
            pulse_cls = ' class="pulse-cell-comic"' if lvl >= 3 else ''
            glow_attr = ' filter="url(#actCrimsonGlow)"' if lvl == 4 else ''
            
            rect_svg_lines.append(
                f'        <rect x="{x}" y="{y}" width="18" height="14" rx="1" fill="{fill_color}"{pulse_cls}{glow_attr}>\n'
                f'          <title>{d_str}: {cnt} commit{"s" if cnt != 1 else ""}</title>\n'
                f'        </rect>'
            )

    cells_svg = "\n".join(rect_svg_lines)

    svg_template = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 160" width="100%" height="100%">
  <defs>
    <linearGradient id="actGradP" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#09090d" />
      <stop offset="100%" stop-color="#060608" />
    </linearGradient>

    <pattern id="actDotsP" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.65" fill="#ffffff" fill-opacity="0.02" />
    </pattern>

    <filter id="actCrimsonGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    @keyframes heatPulseGlow {{
      0%, 100% {{ opacity: 0.8; }}
      50% {{ opacity: 1; }}
    }}
    .pulse-cell-comic {{
      animation: heatPulseGlow 3s infinite ease-in-out;
    }}
  </style>

  <rect width="850" height="160" fill="#050505" />

  <!-- Comic Shadow Underlayer -->
  <rect x="7" y="7" width="836" height="146" fill="#10182A" opacity="0.7" />

  <!-- Main Comic Telemetry Panel -->
  <rect x="5" y="5" width="840" height="150" fill="url(#actGradP)" stroke="#22222e" stroke-width="1.5" />
  <rect x="5" y="5" width="840" height="150" fill="url(#actDotsP)" />

  <!-- Corner Brackets & Crimson Ticks -->
  <path d="M 5 22 L 5 5 L 22 5" fill="none" stroke="#E50914" stroke-width="2" />
  <circle cx="16" cy="16" r="1.5" fill="#E50914" />
  <path d="M 845 137 L 845 155 L 828 155" fill="none" stroke="#E50914" stroke-width="2" />

  <!-- Left Column: Graphic Novel Profile Telemetry -->
  <g transform="translate(25, 24)">
    <text x="0" y="14" font-family="'Consolas', 'Fira Code', monospace" font-size="10.5" fill="#68687a" letter-spacing="1.5">
      REAL TELEMETRY // DATA_FEED
    </text>

    <!-- Telemetry Metric 1: Real Total Commits -->
    <g transform="translate(0, 32)">
      <rect x="0" y="0" width="220" height="36" fill="#0f0f15" stroke="#22222f" stroke-width="1" />
      <circle cx="12" cy="18" r="3" fill="#E50914" />
      <text x="24" y="15" font-family="'Consolas', monospace" font-size="9" fill="#757588">ANNUAL COMMITS</text>
      <text x="24" y="28" font-family="-apple-system, sans-serif" font-weight="800" font-size="12" fill="#E0E0EA">{total_2026} Commits (2026)</text>
    </g>

    <!-- Telemetry Metric 2: Real Active Cadence -->
    <g transform="translate(0, 78)">
      <rect x="0" y="0" width="220" height="36" fill="#0f0f15" stroke="#22222f" stroke-width="1" />
      <circle cx="12" cy="18" r="3" fill="#FF3030" filter="url(#actCrimsonGlow)" />
      <text x="24" y="15" font-family="'Consolas', monospace" font-size="9" fill="#757588">ACTIVE CADENCE</text>
      <text x="24" y="28" font-family="-apple-system, sans-serif" font-weight="800" font-size="12" fill="#E0E0EA">{active_days_count} Active Commit Days</text>
    </g>
  </g>

  <!-- Inked Vertical Divider -->
  <line x1="275" y1="20" x2="275" y2="140" stroke="#1c1c28" stroke-width="1.2" />

  <!-- Right Column: Real Contribution Heatmap Matrix -->
  <g transform="translate(295, 24)">
    <text x="0" y="14" font-family="'Consolas', 'Fira Code', monospace" font-size="10.5" fill="#68687a" letter-spacing="1.5">
      ACTIVITY DENSITY // REAL COMMIT MATRIX (LAST 96 DAYS)
    </text>

    <!-- Real Contribution Cells -->
    <g transform="translate(0, 32)">
{cells_svg}
    </g>

    <!-- Matrix Legend -->
    <g transform="translate(380, 115)" font-family="'Consolas', monospace" font-size="9" fill="#58586a">
      <text x="0" y="8">LESS</text>
      <rect x="28" y="0" width="9" height="9" rx="1" fill="#121218" />
      <rect x="40" y="0" width="9" height="9" rx="1" fill="#5c0a0e" />
      <rect x="52" y="0" width="9" height="9" rx="1" fill="#9c0910" />
      <rect x="64" y="0" width="9" height="9" rx="1" fill="#E50914" />
      <rect x="76" y="0" width="9" height="9" rx="1" fill="#FF3030" />
      <text x="92" y="8">MORE</text>
    </g>
  </g>
</svg>
'''

    with open("c:/Users/anime/Documents/GitHub/profile/assets/github-metrics.svg", "w", encoding="utf-8") as f:
        f.write(svg_template)
    
    print("Successfully generated assets/github-metrics.svg with REAL GitHub contribution data!")

if __name__ == "__main__":
    update_github_metrics()
