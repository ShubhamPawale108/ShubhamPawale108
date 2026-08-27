import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
ASSETS_DIR = REPO_ROOT / "assets"

def make_info_card():
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from profile_config import config
    except ImportError:
        print("Error: Could not import profile_config.py")
        sys.exit(1)

    lines = [
        f"NAME      : {config.get('name', '')}",
        f"ROLE      : {config.get('role', '')}",
        f"EDUCATION : {config.get('education', '')}",
        f"LOCATION  : {config.get('location', '')}",
        f"LANGUAGES : {config.get('languages', '')}",
        f"FRONTEND  : {config.get('frontend', '')}",
        f"BACKEND   : {config.get('backend', '')}",
        f"DATABASE  : {config.get('database', '')}",
        f"TOOLS     : {config.get('tools', '')}"
    ]

    # Filter out empty lines
    lines = [line for line in lines if not line.endswith(": ")]

    width = 500
    height = len(lines) * 25 + 60

    svg_elements = []
    
    # CSS for animation
    svg_elements.append("""
    <style>
        .terminal-text {
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            fill: #c9d1d9;
            opacity: 0;
            animation: slideIn 0.5s ease-out forwards;
        }
        .prompt {
            fill: #7ee787;
            font-weight: bold;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
    </style>
    """)

    # Background
    svg_elements.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="6" ry="6"/>')

    # Top bar (fake window controls)
    svg_elements.append('<circle cx="15" cy="15" r="5" fill="#ff5f56"/>')
    svg_elements.append('<circle cx="35" cy="15" r="5" fill="#ffbd2e"/>')
    svg_elements.append('<circle cx="55" cy="15" r="5" fill="#27c93f"/>')

    # Content
    y_start = 45
    
    # Fake command prompt
    svg_elements.append(f'<text x="15" y="{y_start}" class="terminal-text" style="animation-delay: 0.1s;"><tspan class="prompt">guest@github</tspan>:<tspan fill="#79c0ff">~</tspan>$ neofetch --profile</text>')
    
    for i, line in enumerate(lines):
        y = y_start + (i + 1) * 25
        delay = 0.3 + (i * 0.1)
        
        # Split key and value for colors
        parts = line.split(":", 1)
        if len(parts) == 2:
            key, val = parts
            svg_line = f'<tspan fill="#ff7b72" font-weight="bold">{key}</tspan>:{val}'
        else:
            svg_line = line
            
        svg_elements.append(f'<text x="15" y="{y}" class="terminal-text" style="animation-delay: {delay}s;">{svg_line}</text>')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{''.join(svg_elements)}
</svg>"""

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ASSETS_DIR / "info-card.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Saved info card SVG to {out_path}")

if __name__ == "__main__":
    make_info_card()
