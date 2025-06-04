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

from .py.nodes import (
    DCIImageExporter,
    DCIImageExporterAdvanced,
    DCIPreviewNode,
    DCIFileLoader,
    DCIMetadataExtractor,
    DCIImage,
    DCIFileNode,
    DCIPreviewFromBinary,
    BinaryFileLoader,
    BinaryFileSaver,
    BinaryFileUploader
)

# ComfyUI Node Registration
NODE_CLASS_MAPPINGS = {
    "DCIImageExporter": DCIImageExporter,
    "DCIImageExporterAdvanced": DCIImageExporterAdvanced,
    "DCIPreviewNode": DCIPreviewNode,
    "DCIFileLoader": DCIFileLoader,
    "DCIMetadataExtractor": DCIMetadataExtractor,
    "DCIImage": DCIImage,
    "DCIFileNode": DCIFileNode,
    "DCIPreviewFromBinary": DCIPreviewFromBinary,
    "BinaryFileLoader": BinaryFileLoader,
    "BinaryFileSaver": BinaryFileSaver,
    "BinaryFileUploader": BinaryFileUploader,
}

# Display names for ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIImageExporter": "DCI Image Exporter",
    "DCIImageExporterAdvanced": "DCI Image Exporter (Advanced)",
    "DCIPreviewNode": "DCI Preview",
    "DCIFileLoader": "DCI File Loader",
    "DCIMetadataExtractor": "DCI Metadata Extractor",
    "DCIImage": "DCI Image",
    "DCIFileNode": "DCI File",
    "DCIPreviewFromBinary": "DCI Preview (Binary)",
    "BinaryFileLoader": "Binary File Loader",
    "BinaryFileSaver": "Binary File Saver",
    "BinaryFileUploader": "Binary File Uploader",
}

# Extension metadata
__version__ = "1.0.0"
__author__ = "ComfyUI DCI Team"
__description__ = "DCI (DSG Combined Icons) format support for ComfyUI"

# Export for ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
