# ComfyUI DCI Extension - Python Module
# This module contains the core Python implementation for DCI format handling

__version__ = "1.0.0"
__author__ = "ComfyUI DCI Team"
__description__ = "DCI (DSG Combined Icons) format support for ComfyUI"

# Import core modules
from .dci_format import DCIFile
from .dci_reader import DCIReader
from .nodes import *

__all__ = [
    'DCIFile',
    'DCIReader',
]
