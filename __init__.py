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
    DCIMetadataExtractor,
    DCIImage,
    DCIFileNode,
    DCIPreviewFromBinary,
    BinaryFileLoader,
    BinaryFileSaver
)

# ComfyUI Node Registration
# Using DCI prefix to ensure unique node names and avoid conflicts
NODE_CLASS_MAPPINGS = {
    "DCI_ImageExporter": DCIImageExporter,
    "DCI_ImageExporterAdvanced": DCIImageExporterAdvanced,
    "DCI_PreviewNode": DCIPreviewNode,
    "DCI_MetadataExtractor": DCIMetadataExtractor,
    "DCI_Image": DCIImage,
    "DCI_FileNode": DCIFileNode,
    "DCI_PreviewFromBinary": DCIPreviewFromBinary,
    "DCI_BinaryFileLoader": BinaryFileLoader,
    "DCI_BinaryFileSaver": BinaryFileSaver,
}

# Display names for ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "DCI_ImageExporter": "DCI Image Exporter",
    "DCI_ImageExporterAdvanced": "DCI Image Exporter (Advanced)",
    "DCI_PreviewNode": "DCI Preview",
    "DCI_MetadataExtractor": "DCI Metadata Extractor",
    "DCI_Image": "DCI Image",
    "DCI_FileNode": "DCI File",
    "DCI_PreviewFromBinary": "DCI Preview (Binary)",
    "DCI_BinaryFileLoader": "Binary File Loader",
    "DCI_BinaryFileSaver": "Binary File Saver",
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
    "DCI_BINARY_DATA": "DCI_BINARY_DATA",
    "BINARY_DATA": "BINARY_DATA"
}

# Export for ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
