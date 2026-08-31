import json
import sys
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"
ASSETS_DIR = REPO_ROOT / "assets"

# GitHub inspired contribution palette (dark mode)
PALETTE = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353"
}

def render_heatmap():
    data_path = DATA_DIR / "contributions.json"
    if not data_path.exists():
        print(f"Error: Data file {data_path} not found.")
        sys.exit(1)
        
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data.get("days", [])
    if not days:
        print("Error: No days found in contribution data.")
        sys.exit(1)
        
    total = data.get("total_contributions", 0)
    
    # Grid layout parameters
    cell_size = 10
    cell_gap = 4
    weeks_count = 53
    days_count = 7
    left_margin = 30
    top_margin = 20
    
    # Calculate SVG dimensions
    width = left_margin + (cell_size + cell_gap) * weeks_count + cell_gap
    height = top_margin + (cell_size + cell_gap) * days_count + cell_gap + 40 # extra space for text
    
    svg_elements = []
    
    # Add animations and styles
    svg_elements.append("""
    <style>
        text { font-family: 'Courier New', Courier, monospace; }
        .cell {
            opacity: 0;
            animation: fadeIn 0.5s ease-in forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(2px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """)
    
    # Calculate starting day offset (0 = Sunday, 1 = Monday, etc.)
    days_to_render = days[-371:]
    first_date = datetime.datetime.strptime(days_to_render[0]["date"], "%Y-%m-%d")
    first_day_of_week = (first_date.weekday() + 1) % 7
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    
    # Add weekday labels
    svg_elements.append(f'<text x="0" y="{top_margin + 1 * (cell_size + cell_gap) + 9}" fill="#8b949e" font-size="10px">Mon</text>')
    svg_elements.append(f'<text x="0" y="{top_margin + 3 * (cell_size + cell_gap) + 9}" fill="#8b949e" font-size="10px">Wed</text>')
    svg_elements.append(f'<text x="0" y="{top_margin + 5 * (cell_size + cell_gap) + 9}" fill="#8b949e" font-size="10px">Fri</text>')
    
    # Draw cells
    for i, day in enumerate(days_to_render):
        offset = i + first_day_of_week
        week = offset // days_count
        day_of_week = offset % days_count
        
        day_date = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
        if day_date.month != last_month:
            # Add month label
            if week > 0 or day_date.day < 15: # Avoid adding label if it's the very first column and late in the month
                label_x = left_margin + week * (cell_size + cell_gap)
                svg_elements.append(f'<text x="{label_x}" y="{top_margin - 5}" fill="#8b949e" font-size="10px">{month_names[day_date.month - 1]}</text>')
            last_month = day_date.month
        
        x = left_margin + week * (cell_size + cell_gap) + cell_gap
        y = top_margin + day_of_week * (cell_size + cell_gap) + cell_gap
        
        level = min(day.get("level", 0), 4)
        color = PALETTE[level]
        
        # Staggered animation delay based on diagonal
        delay = (week + day_of_week) * 0.02
        
        cell = f'<rect class="cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" ry="2" style="animation-delay: {delay}s;" />'
        svg_elements.append(cell)
        
    # Add footer text
    footer_y = height - 10
    svg_elements.append(f'<text x="{left_margin}" y="{footer_y}" fill="#8b949e" font-size="12px">{total} contributions in the last year</text>')
    
    # Add legend
    legend_x = width - 100
    svg_elements.append(f'<text x="{legend_x - 30}" y="{footer_y}" fill="#8b949e" font-size="10px">Less</text>')
    for l in range(5):
        lx = legend_x + (l * (cell_size + cell_gap))
        ly = footer_y - 8
        svg_elements.append(f'<rect x="{lx}" y="{ly}" width="{cell_size}" height="{cell_size}" fill="{PALETTE[l]}" rx="2" ry="2" />')
    svg_elements.append(f'<text x="{legend_x + 5 * (cell_size + cell_gap)}" y="{footer_y}" fill="#8b949e" font-size="10px">More</text>')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
{''.join(svg_elements)}
</svg>"""

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ASSETS_DIR / "contrib-heatmap.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Saved heatmap SVG to {out_path}")

if __name__ == "__main__":
    render_heatmap()
