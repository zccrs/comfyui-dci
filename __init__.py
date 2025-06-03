from .nodes import (
    DCIImageExporter,
    DCIImageExporterAdvanced,
    DCIPreviewNode,
    DCIFileLoader,
    DCIMetadataExtractor
)

NODE_CLASS_MAPPINGS = {
    "DCIImageExporter": DCIImageExporter,
    "DCIImageExporterAdvanced": DCIImageExporterAdvanced,
    "DCIPreviewNode": DCIPreviewNode,
    "DCIFileLoader": DCIFileLoader,
    "DCIMetadataExtractor": DCIMetadataExtractor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIImageExporter": "DCI Image Exporter",
    "DCIImageExporterAdvanced": "DCI Image Exporter (Advanced)",
    "DCIPreviewNode": "DCI Preview",
    "DCIFileLoader": "DCI File Loader",
    "DCIMetadataExtractor": "DCI Metadata Extractor",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
