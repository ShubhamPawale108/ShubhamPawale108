import json
import sys
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
    
    # Calculate SVG dimensions
    width = (cell_size + cell_gap) * weeks_count + cell_gap
    height = (cell_size + cell_gap) * days_count + cell_gap + 40 # extra space for text
    
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
    
    # Draw cells
    for i, day in enumerate(days[-371:]): # Ensure max 53 weeks * 7 days
        week = i // days_count
        day_of_week = i % days_count
        
        x = week * (cell_size + cell_gap) + cell_gap
        y = day_of_week * (cell_size + cell_gap) + cell_gap
        
        level = min(day.get("level", 0), 4)
        color = PALETTE[level]
        
        # Staggered animation delay based on diagonal
        delay = (week + day_of_week) * 0.02
        
        cell = f'<rect class="cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" ry="2" style="animation-delay: {delay}s;" />'
        svg_elements.append(cell)
        
    # Add footer text
    footer_y = height - 10
    svg_elements.append(f'<text x="{cell_gap}" y="{footer_y}" fill="#8b949e" font-size="12px">{total} contributions in the last year</text>')
    
    # Add legend
    legend_x = width - 80
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
