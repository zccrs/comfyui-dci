"""
DCI Extension Enumerations

This module defines all enumeration values used internally in the DCI extension
to avoid string-based errors and confusion with translated UI text.
"""

from enum import Enum, auto


class ImageFormat(Enum):
    """Image format enumeration"""
    WEBP = "webp"
    PNG = "png"
    JPG = "jpg"

    def __str__(self):
        return self.value


class IconState(Enum):
    """Icon state enumeration"""
    NORMAL = "normal"
    DISABLED = "disabled"
    HOVER = "hover"
    PRESSED = "pressed"

    def __str__(self):
        return self.value


class ToneType(Enum):
    """Tone type enumeration"""
    UNIVERSAL = "universal"
    LIGHT = "light"
    DARK = "dark"

    def __str__(self):
        return self.value


class BackgroundColor(Enum):
    """Background color enumeration"""
    TRANSPARENT = "transparent"
    WHITE = "white"
    BLACK = "black"
    CUSTOM = "custom"
    CHECKERBOARD = "checkerboard"

    def __str__(self):
        return self.value


class PaletteType(Enum):
    """Palette type enumeration"""
    NONE = "none"
    FOREGROUND = "foreground"
    BACKGROUND = "background"
    HIGHLIGHT_FOREGROUND = "highlight_foreground"
    HIGHLIGHT = "highlight"

    def __str__(self):
        return self.value

    def to_numeric(self):
        """Convert palette type to numeric value according to DCI specification"""
        mapping = {
            PaletteType.NONE: -1,
            PaletteType.FOREGROUND: 0,
            PaletteType.BACKGROUND: 1,
            PaletteType.HIGHLIGHT_FOREGROUND: 2,
            PaletteType.HIGHLIGHT: 3
        }
        return mapping.get(self, -1)


class PreviewBackground(Enum):
    """Preview background enumeration"""
    TRANSPARENT = "transparent"
    WHITE = "white"
    BLACK = "black"
    CHECKERBOARD = "checkerboard"
    LIGHT_GRAY = "light_gray"
    DARK_GRAY = "dark_gray"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    CYAN = "cyan"
    MAGENTA = "magenta"
    ORANGE = "orange"
    PURPLE = "purple"
    PINK = "pink"
    BROWN = "brown"
    NAVY = "navy"
    TEAL = "teal"
    OLIVE = "olive"
    MAROON = "maroon"

    def __str__(self):
        return self.value


# Utility functions for enum conversion
def string_to_image_format(value: str) -> ImageFormat:
    """Convert string to ImageFormat enum"""
    for fmt in ImageFormat:
        if fmt.value == value:
            return fmt
    raise ValueError(f"Unknown image format: {value}")


def string_to_icon_state(value: str) -> IconState:
    """Convert string to IconState enum"""
    for state in IconState:
        if state.value == value:
            return state
    raise ValueError(f"Unknown icon state: {value}")


def string_to_tone_type(value: str) -> ToneType:
    """Convert string to ToneType enum"""
    for tone in ToneType:
        if tone.value == value:
            return tone
    raise ValueError(f"Unknown tone type: {value}")


def string_to_background_color(value: str) -> BackgroundColor:
    """Convert string to BackgroundColor enum"""
    for bg in BackgroundColor:
        if bg.value == value:
            return bg
    raise ValueError(f"Unknown background color: {value}")


def string_to_palette_type(value: str) -> PaletteType:
    """Convert string to PaletteType enum"""
    for palette in PaletteType:
        if palette.value == value:
            return palette
    raise ValueError(f"Unknown palette type: {value}")


def string_to_preview_background(value: str) -> PreviewBackground:
    """Convert string to PreviewBackground enum"""
    for bg in PreviewBackground:
        if bg.value == value:
            return bg
    raise ValueError(f"Unknown preview background: {value}")


# Translation mapping functions
def translate_ui_to_enum(ui_value: str, enum_type: type, translation_func) -> Enum:
    """
    Convert translated UI value back to enum

    Args:
        ui_value: The UI value (possibly translated)
        enum_type: The target enum type
        translation_func: The translation function (usually t())

    Returns:
        The corresponding enum value
    """
    # Create reverse mapping from translated values to enum values
    reverse_map = {}
    for enum_val in enum_type:
        translated = translation_func(enum_val.value)
        reverse_map[translated] = enum_val
        # Also map original value for fallback
        reverse_map[enum_val.value] = enum_val

    if ui_value in reverse_map:
        return reverse_map[ui_value]

    raise ValueError(f"Cannot convert UI value '{ui_value}' to {enum_type.__name__}")


def get_enum_ui_options(enum_type: type, translation_func) -> list:
    """
    Get list of translated UI options for an enum type

    Args:
        enum_type: The enum type
        translation_func: The translation function (usually t())

    Returns:
        List of translated option strings
    """
    return [translation_func(enum_val.value) for enum_val in enum_type]


def get_enum_default_ui_value(enum_value: Enum, translation_func) -> str:
    """
    Get translated UI value for an enum default

    Args:
        enum_value: The enum value
        translation_func: The translation function (usually t())

    Returns:
        Translated UI string
    """
    return translation_func(enum_value.value)
