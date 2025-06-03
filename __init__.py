from .nodes import (
    DCIImageExporter,
    DCIImageExporterAdvanced,
    DCIPreviewNode,
    DCIFileLoader,
    DCIMetadataExtractor,
    DCIImage,
    DCIFileNode,
    DCIPreviewFromBinary
)

NODE_CLASS_MAPPINGS = {
    "DCIImageExporter": DCIImageExporter,
    "DCIImageExporterAdvanced": DCIImageExporterAdvanced,
    "DCIPreviewNode": DCIPreviewNode,
    "DCIFileLoader": DCIFileLoader,
    "DCIMetadataExtractor": DCIMetadataExtractor,
    "DCIImage": DCIImage,
    "DCIFileNode": DCIFileNode,
    "DCIPreviewFromBinary": DCIPreviewFromBinary,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIImageExporter": "DCI Image Exporter",
    "DCIImageExporterAdvanced": "DCI Image Exporter (Advanced)",
    "DCIPreviewNode": "DCI Preview",
    "DCIFileLoader": "DCI File Loader",
    "DCIMetadataExtractor": "DCI Metadata Extractor",
    "DCIImage": "DCI Image",
    "DCIFileNode": "DCI File",
    "DCIPreviewFromBinary": "DCI Preview (Binary)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
