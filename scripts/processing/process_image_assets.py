import os
import io
import sys
from PIL import Image
try:
    from rembg import remove as rembg_remove
    HAS_REMBG = True
except Exception:
    HAS_REMBG = False

sys.stdout.reconfigure(encoding='utf-8')

def format_image_to_square_webp(image_input, output_path, target_size=1000, padding_margin=0.85, remove_bg=True):
    """
    Cleans background, removes non-white studio backdrop using AI (rembg),
    centers product onto a 1:1 square pure white canvas (1000x1000px), and saves as WebP.
    """
    try:
        if isinstance(image_input, (str, bytes, os.PathLike)):
            img = Image.open(image_input)
        elif isinstance(image_input, io.BytesIO):
            img = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ValueError("Unsupported image input type.")

        # Convert to RGBA for alpha processing
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Apply AI background removal if enabled
        if remove_bg and HAS_REMBG:
            try:
                # rembg expects PIL image or bytes, returns RGBA image with background removed
                img_no_bg = rembg_remove(img)
                if isinstance(img_no_bg, Image.Image):
                    img = img_no_bg
            except Exception as e:
                print(f"  [Warning] rembg background removal failed ({e}), continuing with standard composite...")

        # Crop tight bounding box around non-transparent subject
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        width, height = img.size
        
        # Scale image to fit inside target canvas with padding margin
        max_dim = int(target_size * padding_margin)
        scale = min(max_dim / width, max_dim / height)
        new_w = max(1, int(width * scale))
        new_h = max(1, int(height * scale))

        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create final 1000x1000 solid white square canvas
        canvas_rgba = Image.new('RGBA', (target_size, target_size), (255, 255, 255, 255))
        
        # Paste centered using alpha channel as mask
        offset_x = (target_size - new_w) // 2
        offset_y = (target_size - new_h) // 2
        canvas_rgba.paste(img_resized, (offset_x, offset_y), img_resized)

        # Convert to RGB (flatten transparency onto pure white background)
        final_rgb = Image.new('RGB', (target_size, target_size), (255, 255, 255))
        final_rgb.paste(canvas_rgba, (0, 0))

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as WebP
        final_rgb.save(output_path, 'WEBP', quality=95)
        return True
    except Exception as e:
        print(f"Error formatting image to {output_path}: {e}")
        return False

if __name__ == '__main__':
    print(f"Image asset processing module ready. rembg AI background removal: {'Available' if HAS_REMBG else 'Unavailable'}")
