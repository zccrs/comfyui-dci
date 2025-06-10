"""
DCI Nodes for ComfyUI
"""

from .nodes.preview_node import DCIPreviewNode
from .nodes.image_node import DCIImage
from .nodes.image_preview_node import DCIImagePreview
from .nodes.file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver

NODE_CLASS_MAPPINGS = {
    "DCIPreviewNode": DCIPreviewNode,
    "DCIImage": DCIImage,
    "DCIImagePreview": DCIImagePreview,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIPreviewNode": "DCI Preview",
    "DCIImage": "DCI Image",
    "DCIImagePreview": "DCI Image Preview",
    "DCIFileNode": "DCI File",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
