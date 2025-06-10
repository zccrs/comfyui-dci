import torch
import numpy as np
from PIL import Image
from io import BytesIO
import os
import tempfile
import hashlib
import time

def tensor_to_pil(image):
    """Convert ComfyUI image tensor to PIL Image"""
    if len(image.shape) == 4:
        img_array = image[0].cpu().numpy()
    else:
        img_array = image.cpu().numpy()

    # Convert from 0-1 range to 0-255 range
    img_array = (img_array * 255).astype(np.uint8)

    # Convert to PIL Image
    if img_array.shape[2] == 3:
        pil_image = Image.fromarray(img_array, 'RGB')
    elif img_array.shape[2] == 4:
        pil_image = Image.fromarray(img_array, 'RGBA')
    else:
        pil_image = Image.fromarray(img_array[:, :, 0], 'L').convert('RGB')

    return pil_image

def create_checkerboard_background(size, square_size=16):
    """Create a checkerboard pattern background"""
    width, height = size
    background = Image.new('RGB', size, (255, 255, 255))

    # Create checkerboard pattern
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            # Determine if this square should be gray
            if (x // square_size + y // square_size) % 2 == 1:
                # Draw gray square
                for py in range(y, min(y + square_size, height)):
                    for px in range(x, min(x + square_size, width)):
                        background.putpixel((px, py), (200, 200, 200))

    return background

def apply_background(pil_image, background_type, bg_color=None):
    """Apply background to an image with transparency"""
    if background_type == "transparent" or pil_image.mode != 'RGBA':
        return pil_image

    # Create background
    if background_type == "white":
        background = Image.new('RGB', pil_image.size, (255, 255, 255))
    elif background_type == "black":
        background = Image.new('RGB', pil_image.size, (0, 0, 0))
    elif background_type == "checkerboard":
        background = create_checkerboard_background(pil_image.size)
    elif background_type == "custom" and bg_color:
        background = Image.new('RGB', pil_image.size, bg_color)
    else:
        return pil_image

    # Composite image onto background
    if pil_image.mode == 'RGBA':
        background.paste(pil_image, mask=pil_image.split()[-1])
    else:
        background.paste(pil_image)

    return background

def pil_to_comfyui_format(pil_image, prefix="dci"):
    """Convert PIL image to ComfyUI format with temp file"""
    # Convert to RGB if necessary
    if pil_image.mode not in ('RGB', 'RGBA'):
        pil_image = pil_image.convert('RGB')

    # Save to bytes buffer
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()

    # Generate unique filename
    timestamp = str(int(time.time()))
    hash_obj = hashlib.md5(img_bytes)
    filename = f"{prefix}_{timestamp}_{hash_obj.hexdigest()[:8]}.png"

    # Save to temp directory for ComfyUI
    try:
        import folder_paths
        temp_dir = folder_paths.get_temp_directory()
    except:
        temp_dir = tempfile.gettempdir()

    temp_path = os.path.join(temp_dir, filename)
    with open(temp_path, 'wb') as f:
        f.write(img_bytes)

    # Return in format expected by ComfyUI
    return {
        "filename": filename,
        "subfolder": "",
        "type": "temp"
    }
