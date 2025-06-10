"""
DCI Nodes Package
"""

from .preview_node import DCIPreviewNode
from .image_node import DCIImage
from .image_preview_node import DCIImagePreview
from .file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver
from .structure_node import DCIStructureNode

NODE_CLASS_MAPPINGS = {
    "DCIPreviewNode": DCIPreviewNode,
    "DCIImage": DCIImage,
    "DCIImagePreview": DCIImagePreview,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
    "DCIStructureNode": DCIStructureNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIPreviewNode": "DCI Preview",
    "DCIImage": "DCI Image",
    "DCIImagePreview": "DCI Image Preview",
    "DCIFileNode": "DCI File",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
    "DCIStructureNode": "DCI Structure Preview",
}

__all__ = [
    'DCIPreviewNode',
    'DCIImage',
    'DCIImagePreview',
    'DCIFileNode',
    'BinaryFileLoader',
    'BinaryFileSaver',
    'DCIStructureNode',
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
]
