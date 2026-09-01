import os
import io
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

def format_image_to_square_webp(image_input, output_path, target_size=1000, padding_margin=0.9):
    """
    Formats an image (filepath, BytesIO, or PIL Image) into a 1:1 square image
    with a solid white background (RGB 255, 255, 255) and saves it as WebP.
    
    Args:
        image_input: File path, BytesIO stream, or PIL.Image object.
        output_path: Target .webp output filepath.
        target_size: Square canvas dimension (default 1000x1000).
        padding_margin: Scale factor to leave padding around the centered product (0.9 = 90% size, 10% margin).
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

        # Convert palette/grayscale modes to RGBA for clean alpha handling
        if img.mode in ('P', 'PA', 'L', 'LA'):
            img = img.convert('RGBA')

        # Handle transparency or convert mode
        if img.mode in ('RGBA', 'RGBa'):
            # Create white canvas for alpha blending
            bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(bg, img)
            img = alpha_composite.convert('RGB')
        else:
            img = img.convert('RGB')

        # Calculate bounding box / crop transparent/white excess borders if desirable
        width, height = img.size
        
        # Scale to fit inside (target_size * padding_margin)
        max_dim = int(target_size * padding_margin)
        scale = min(max_dim / width, max_dim / height)
        new_w = max(1, int(width * scale))
        new_h = max(1, int(height * scale))

        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create final 1000x1000 solid white square canvas
        canvas = Image.new('RGB', (target_size, target_size), (255, 255, 255))
        
        # Paste centered
        offset_x = (target_size - new_w) // 2
        offset_y = (target_size - new_h) // 2
        canvas.paste(img_resized, (offset_x, offset_y))

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as WebP
        canvas.save(output_path, 'WEBP', quality=90)
        return True
    except Exception as e:
        print(f"Error formatting image to {output_path}: {e}")
        return False

if __name__ == '__main__':
    print("Image asset processing module ready.")
