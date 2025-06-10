"""
ComfyUI DCI Extension

A comprehensive ComfyUI extension for creating, previewing, and analyzing
DCI (DSG Combined Icons) format files.

This extension provides complete DCI specification support including:
- Multi-state icons (normal, hover, pressed, disabled)
- Multi-tone support (light and dark)
- Multiple scale factors and advanced metadata analysis
- Binary data handling and file operations
"""

# Try relative imports first, fall back to absolute imports
try:
    from .py.nodes import (
        DCIPreviewNode,
        DCIImage,
        DCISampleImage,
        DCIImagePreview,
        DCIFileNode,
        BinaryFileLoader,
        BinaryFileSaver,
        DCIAnalysis
    )
except ImportError:
    # Fallback for when module is loaded directly
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from py.nodes import (
        DCIPreviewNode,
        DCIImage,
        DCISampleImage,
        DCIImagePreview,
        DCIFileNode,
        BinaryFileLoader,
        BinaryFileSaver,
        DCIAnalysis
    )

# ComfyUI Node Registration
# Using DCI prefix to ensure unique node names and avoid conflicts
NODE_CLASS_MAPPINGS = {
    "DCI_PreviewNode": DCIPreviewNode,
    "DCI_Image": DCIImage,
    "DCI_SampleImage": DCISampleImage,
    "DCI_ImagePreview": DCIImagePreview,
    "DCI_FileNode": DCIFileNode,
    "DCI_BinaryFileLoader": BinaryFileLoader,
    "DCI_BinaryFileSaver": BinaryFileSaver,
    "DCI_Analysis": DCIAnalysis,
}

# Display names for ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "DCI_PreviewNode": "DCI Preview",
    "DCI_Image": "DCI Image",
    "DCI_SampleImage": "DCI Sample Image",
    "DCI_ImagePreview": "DCI Image Preview",
    "DCI_FileNode": "DCI File",
    "DCI_BinaryFileLoader": "Binary File Loader",
    "DCI_BinaryFileSaver": "Binary File Saver",
    "DCI_Analysis": "DCI Analysis",
}

# Extension metadata
__version__ = "1.0.0"
__author__ = "ComfyUI DCI Team"
__description__ = "DCI (DSG Combined Icons) format support for ComfyUI"

# Custom data types for ComfyUI
# These types are used for passing structured data between nodes
# ComfyUI will treat them as opaque data that can be passed between nodes
# but won't be displayed in the UI
CUSTOM_DATA_TYPES = {
    "DCI_IMAGE_DATA": "DCI_IMAGE_DATA",
    "BINARY_DATA": "BINARY_DATA"
}

# Export for ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
