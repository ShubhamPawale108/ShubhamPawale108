import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance
    import numpy as np
    import cv2
    from rembg import remove
except ImportError:
    pass # Will be handled by the script if used

REPO_ROOT = Path(__file__).parent.parent.resolve()
ASSETS_DIR = REPO_ROOT / "assets"

def prep_photo():
    source_path = ASSETS_DIR / "profile-source.png"
    out_path = ASSETS_DIR / "profile-prepped.png"
    
    if not source_path.exists():
        # Maybe it's a jpg
        source_path = ASSETS_DIR / "profile-source.jpg"
        if not source_path.exists():
            print("No source photo found. Please add profile-source.png or profile-source.jpg to the assets folder.")
            return False
            
    print(f"Processing {source_path}...")
    
    try:
        # Load image
        input_image = Image.open(source_path)
        
        # Remove background
        print("Removing background...")
        output_image = remove(input_image)
        
        # Convert to OpenCV format (numpy array)
        open_cv_image = np.array(output_image)
        
        # Extract alpha channel to create a white background
        if open_cv_image.shape[2] == 4:
            alpha = open_cv_image[:, :, 3]
            rgb = open_cv_image[:, :, :3]
            
            # Create a white background
            white_background = np.ones_like(rgb, dtype=np.uint8) * 255
            
            # Blend
            alpha_factor = alpha[:, :, np.newaxis] / 255.0
            blended = (rgb * alpha_factor + white_background * (1 - alpha_factor)).astype(np.uint8)
        else:
            blended = open_cv_image

        # Convert to Grayscale
        gray = cv2.cvtColor(blended, cv2.COLOR_RGB2GRAY)
        
        # Enhance Contrast using CLAHE
        print("Enhancing contrast...")
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Convert back to PIL Image and save
        final_image = Image.fromarray(enhanced)
        final_image.save(out_path)
        
        print(f"Saved prepped photo to {out_path}")
        return True
        
    except Exception as e:
        print(f"Error prepping photo: {e}")
        return False

if __name__ == "__main__":
    if "rembg" not in sys.modules:
        print("Required modules for photo prep not installed. See requirements.txt.")
        sys.exit(1)
    prep_photo()
