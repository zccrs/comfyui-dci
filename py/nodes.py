"""
DCI Nodes for ComfyUI
"""

from .nodes.preview_node import DCIPreviewNode
from .nodes.image_node import DCIImage
from .nodes.debug_node import DCIImageDebug
from .nodes.file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver

NODE_CLASS_MAPPINGS = {
    "DCIPreviewNode": DCIPreviewNode,
    "DCIImage": DCIImage,
    "DCIImageDebug": DCIImageDebug,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIPreviewNode": "DCI Preview",
    "DCIImage": "DCI Image",
    "DCIImageDebug": "DCI Image Debug",
    "DCIFileNode": "DCI File",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
