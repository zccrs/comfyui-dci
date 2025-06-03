from .nodes import DCIImageExporter, DCIImageExporterAdvanced

NODE_CLASS_MAPPINGS = {
    "DCIImageExporter": DCIImageExporter,
    "DCIImageExporterAdvanced": DCIImageExporterAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DCIImageExporter": "DCI Image Exporter",
    "DCIImageExporterAdvanced": "DCI Image Exporter (Advanced)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
