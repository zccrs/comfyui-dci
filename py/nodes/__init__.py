"""
DCI Nodes Package
"""

from .preview_node import DCIPreviewNode
from .image_node import DCIImage
from .sample_image_node import DCISampleImage
from .image_preview_node import DCIImagePreview
from .file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver
from .dci_file_saver_node import DCIFileSaver
from .structure_node import DCIStructureNode

NODE_CLASS_MAPPINGS = {
    "DCIPreviewNode": DCIPreviewNode,
    "DCIImage": DCIImage,
    "DCISampleImage": DCISampleImage,
    "DCIImagePreview": DCIImagePreview,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
    "DCIFileSaver": DCIFileSaver,
    "DCIStructureNode": DCIStructureNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIPreviewNode": "DCI Preview",
    "DCIImage": "DCI Image",
    "DCISampleImage": "DCI Sample Image",
    "DCIImagePreview": "DCI Image Preview",
    "DCIFileNode": "DCI File",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
    "DCIFileSaver": "DCI File Saver",
    "DCIStructureNode": "DCI Structure Preview",
}

__all__ = [
    'DCIPreviewNode',
    'DCIImage',
    'DCISampleImage',
    'DCIImagePreview',
    'DCIFileNode',
    'BinaryFileLoader',
    'BinaryFileSaver',
    'DCIFileSaver',
    'DCIStructureNode',
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
]
