from .nodes import (
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

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
