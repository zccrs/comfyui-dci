"""
DCI Utilities Package
"""

# Import file and UI utilities (no external dependencies)
from .file_utils import load_binary_data, save_binary_data, get_output_directory, clean_file_name, ensure_directory
from .ui_utils import format_file_size, format_dci_path, format_image_info, format_binary_info

# Try to import image utilities (may fail if torch/PIL not available)
try:
    from .image_utils import tensor_to_pil, create_checkerboard_background, apply_background, pil_to_comfyui_format
    _image_utils_available = True
except ImportError as e:
    print(f"Warning: Image utilities not available: {e}")
    _image_utils_available = False

# Base utilities always available
__all__ = [
    # File utilities
    'load_binary_data',
    'save_binary_data',
    'get_output_directory',
    'clean_file_name',
    'ensure_directory',

    # UI utilities
    'format_file_size',
    'format_dci_path',
    'format_image_info',
    'format_binary_info',
]

# Add image utilities if available
if _image_utils_available:
    __all__.extend([
        'tensor_to_pil',
        'create_checkerboard_background',
        'apply_background',
        'pil_to_comfyui_format',
    ])
