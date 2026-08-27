import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    pass

REPO_ROOT = Path(__file__).parent.parent.resolve()
ASSETS_DIR = REPO_ROOT / "assets"

# Density ramp from darkest to lightest
DENSITY = " .`:-=+*cs#%@"

def create_placeholder_ascii():
    return [
        "      _..._      ",
        "    .'     '.    ",
        "   /  _   _  \\   ",
        "   | (o)_(o) |   ",
        "   \\    _    /   ",
        "    '.  _  .'    ",
        "      '---'      ",
        "                 ",
        " Placeholder!    ",
        " Add photo to    ",
        " assets/profile- ",
        " source.png and  ",
        " run scripts!    "
    ]

def image_to_ascii(image_path, width=40):
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        return create_placeholder_ascii()
        
    # Resize keeping aspect ratio
    aspect_ratio = img.height / img.width
    # ASCII characters are roughly twice as tall as they are wide
    height = int(width * aspect_ratio * 0.5)
    
    img = img.resize((width, height))
    img = img.convert('L') # Convert to grayscale
    
    pixels = np.array(img)
    
    # Map pixels to density ramp
    # Invert the pixel intensity so dark pixels map to dense characters (at the end of DENSITY)
    # The density ramp: index 0 (space) is lightest, index -1 (@) is darkest
    ascii_grid = []
    ramp_len = len(DENSITY)
    
    for row in pixels:
        ascii_row = ""
        for pixel in row:
            # pixel is 0 (black) to 255 (white)
            # Map 0 to ramp_len-1, and 255 to 0
            index = int((255 - pixel) / 255 * (ramp_len - 1))
            ascii_row += DENSITY[index]
        ascii_grid.append(ascii_row)
        
    return ascii_grid

def make_ascii_svg():
    prepped_path = ASSETS_DIR / "profile-prepped.png"
    
    if prepped_path.exists() and "PIL" in sys.modules:
        lines = image_to_ascii(prepped_path)
    else:
        lines = create_placeholder_ascii()
        
    # Generate SVG
    width = 300
    height = len(lines) * 12 + 20
    
    svg_elements = []
    
    svg_elements.append("""
    <style>
        .ascii {
            font-family: 'Courier New', Courier, monospace;
            font-size: 10px;
            font-weight: bold;
            fill: #c9d1d9;
            white-space: pre;
        }
        .line {
            opacity: 0;
            animation: typeIn 0.1s linear forwards;
        }
        @keyframes typeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """)
    
    # Draw background (optional, or transparent)
    svg_elements.append(f'<rect width="{width}" height="{height}" fill="transparent" />')
    
    for i, line in enumerate(lines):
        # Escape XML chars just in case
        line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        y = 15 + (i * 12)
        delay = i * 0.1 # Staggered typing animation
        
        svg_elements.append(f'<text x="10" y="{y}" class="ascii line" style="animation-delay: {delay}s;">{line_escaped}</text>')
        
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{''.join(svg_elements)}
</svg>"""

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ASSETS_DIR / "ascii-profile.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Saved ASCII SVG to {out_path}")

if __name__ == "__main__":
    make_ascii_svg()
