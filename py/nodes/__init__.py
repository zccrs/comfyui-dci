"""
DCI Nodes Package
"""

from .preview_node import DCIAnalysisNode
from .image_node import DCIImage
from .sample_image_node import DCISampleImage
from .image_preview_node import DCIImagePreview
from .file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver
from .structure_node import DCIStructureNode

NODE_CLASS_MAPPINGS = {
    "DCIAnalysisNode": DCIAnalysisNode,
    "DCIImage": DCIImage,
    "DCISampleImage": DCISampleImage,
    "DCIImagePreview": DCIImagePreview,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
    "DCIStructureNode": DCIStructureNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIAnalysisNode": "DCI Analysis",
    "DCIImage": "DCI Image",
    "DCISampleImage": "DCI Sample Image",
    "DCIImagePreview": "DCI Image Preview",
    "DCIFileNode": "DCI File",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
    "DCIStructureNode": "DCI Structure Preview",
}

__all__ = [
    'DCIAnalysisNode',
    'DCIImage',
    'DCISampleImage',
    'DCIImagePreview',
    'DCIFileNode',
    'BinaryFileLoader',
    'BinaryFileSaver',
    'DCIStructureNode',
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
]
