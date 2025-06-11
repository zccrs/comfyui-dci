"""
DCI Nodes Package
"""

from .preview_node import DCIPreviewNode
from .image_node import DCIImage
from .sample_image_node import DCISampleImage
from .image_preview_node import DCIImagePreview
from .file_node import DCIFileNode, BinaryFileLoader, BinaryFileSaver, Base64Decoder, Base64Encoder
from .dci_file_saver_node import DCIFileSaver
from .structure_node import DCIAnalysis
from .directory_loader_node import DirectoryLoader
from .deb_packager_node import DebPackager
from .deb_loader_node import DebLoader
from .drop_shadow_node import DropShadowNode
from ..utils.i18n import t

NODE_CLASS_MAPPINGS = {
    "DCIPreviewNode": DCIPreviewNode,
    "DCIImage": DCIImage,
    "DCISampleImage": DCISampleImage,
    "DCIImagePreview": DCIImagePreview,
    "DCIFileNode": DCIFileNode,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
    "Base64Decoder": Base64Decoder,
    "Base64Encoder": Base64Encoder,
    "DCIFileSaver": DCIFileSaver,
    "DCIAnalysis": DCIAnalysis,
    "DirectoryLoader": DirectoryLoader,
    "DebPackager": DebPackager,
    "DebLoader": DebLoader,
    "DropShadowNode": DropShadowNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIPreviewNode": t("DCI Preview"),
    "DCIImage": t("DCI Image"),
    "DCISampleImage": t("DCI Sample Image"),
    "DCIImagePreview": t("DCI Image Preview"),
    "DCIFileNode": t("DCI File"),
    "BinaryFileLoader": t("Binary File Loader"),
    "BinaryFileSaver": t("Binary File Saver"),
    "Base64Decoder": t("Base64 Decoder"),
    "Base64Encoder": t("Base64 Encoder"),
    "DCIFileSaver": t("DCI File Saver"),
    "DCIAnalysis": t("DCI Analysis"),
    "DirectoryLoader": t("Directory Loader"),
    "DebPackager": t("Deb Packager"),
    "DebLoader": t("Deb Loader"),
    "DropShadowNode": t("Drop Shadow"),
}

__all__ = [
    'DCIPreviewNode',
    'DCIImage',
    'DCISampleImage',
    'DCIImagePreview',
    'DCIFileNode',
    'BinaryFileLoader',
    'BinaryFileSaver',
    'Base64Decoder',
    'Base64Encoder',
    'DCIFileSaver',
    'DCIAnalysis',
    'DirectoryLoader',
    'DebPackager',
    'DebLoader',
    'DropShadowNode',
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
]
