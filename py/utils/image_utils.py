# 可选导入torch，支持在没有ComfyUI环境中运行
try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

import numpy as np
from PIL import Image
from io import BytesIO
import os
import tempfile
import hashlib
import time

def tensor_to_pil(image):
    """Convert ComfyUI image tensor to PIL Image"""
    # Handle both torch tensors and numpy arrays
    if HAS_TORCH and hasattr(image, 'cpu'):
        # PyTorch tensor
        if len(image.shape) == 4:
            img_array = image[0].cpu().numpy()
        else:
            img_array = image.cpu().numpy()
    else:
        # NumPy array
        if len(image.shape) == 4:
            img_array = image[0]
        else:
            img_array = image

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

def pil_to_tensor(pil_image):
    """Convert PIL Image to ComfyUI image tensor"""
    # Convert PIL image to numpy array
    if pil_image.mode == 'RGBA':
        # Convert RGBA to RGB by compositing on white background
        rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
        rgb_image.paste(pil_image, mask=pil_image.split()[-1])
        pil_image = rgb_image
    elif pil_image.mode != 'RGB':
        # Convert other modes to RGB
        pil_image = pil_image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(pil_image).astype(np.float32)

    # Normalize to 0-1 range
    img_array = img_array / 255.0

    if HAS_TORCH:
        # Convert to torch tensor with shape [1, H, W, C] (batch dimension)
        tensor = torch.from_numpy(img_array).unsqueeze(0)
    else:
        # Return numpy array with batch dimension for compatibility
        tensor = np.expand_dims(img_array, axis=0)

    return tensor

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
    # Handle different image modes for ComfyUI compatibility
    if pil_image.mode == 'RGBA':
        # For RGBA images, check if transparency is actually used
        # If no transparency, convert to RGB for better compatibility
        alpha_channel = pil_image.split()[-1]
        alpha_values = alpha_channel.getdata()
        has_transparency = any(alpha < 255 for alpha in alpha_values)

        if not has_transparency:
            # No transparency used, convert to RGB
            rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
            rgb_image.paste(pil_image, mask=alpha_channel)
            pil_image = rgb_image
        # If has transparency, keep as RGBA and save as PNG
    elif pil_image.mode not in ('RGB', 'RGBA'):
        # Convert other modes to RGB
        pil_image = pil_image.convert('RGB')

    # Save to bytes buffer
    buffer = BytesIO()
    if pil_image.mode == 'RGBA':
        # Save RGBA as PNG to preserve transparency
        pil_image.save(buffer, format='PNG')
    else:
        # Save RGB as PNG (ComfyUI handles PNG well)
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
