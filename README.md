# ComfyUI DCI Image Exporter

A ComfyUI extension for exporting images to DCI (DSG Combined Icons) format, following the [Desktop Spec Group icon file specification](https://desktopspec.org/unstable/%E5%9B%BE%E6%A0%87%E6%96%87%E4%BB%B6%E8%A7%84%E8%8C%83.html).

## Features

- Export images to DCI format with proper directory structure
- Support for multiple icon states (normal, disabled, hover, pressed)
- Support for light and dark tone types
- Multiple scale factors (1x, 2x, 3x, etc.)
- Multiple image formats (WebP, PNG, JPEG)
- Two node types: basic and advanced

## Installation

1. Clone or download this repository to your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone <repository-url> comfyui-dci-exporter
   ```

2. Install required dependencies:
   ```bash
   pip install Pillow
   ```

3. Restart ComfyUI

## Nodes

### DCI Image Exporter (Basic)

A simple node for basic DCI export functionality.

**Inputs:**
- `image` (IMAGE): Input image to convert
- `filename` (STRING): Output filename (without extension)
- `icon_size` (INT): Base icon size in pixels (default: 256)
- `icon_state` (ENUM): Icon state - normal, disabled, hover, pressed (default: normal)
- `tone_type` (ENUM): Tone type - light, dark (default: dark)
- `image_format` (ENUM): Output format - webp, png, jpg (default: webp)
- `scale_factors` (STRING): Comma-separated scale factors (default: "1,2,3")
- `output_directory` (STRING): Optional output directory

**Output:**
- `file_path` (STRING): Path to the generated DCI file

### DCI Image Exporter (Advanced)

An advanced node supporting multiple icon states and tones in a single DCI file.

**Inputs:**
- `image` (IMAGE): Default input image
- `filename` (STRING): Output filename (without extension)
- `icon_size` (INT): Base icon size in pixels (default: 256)
- `image_format` (ENUM): Output format - webp, png, jpg (default: webp)
- `normal_image` (IMAGE, optional): Image for normal state
- `disabled_image` (IMAGE, optional): Image for disabled state
- `hover_image` (IMAGE, optional): Image for hover state
- `pressed_image` (IMAGE, optional): Image for pressed state
- `include_light_tone` (BOOLEAN): Include light tone variants (default: false)
- `include_dark_tone` (BOOLEAN): Include dark tone variants (default: true)
- `scale_factors` (STRING): Comma-separated scale factors (default: "1,2,3")
- `output_directory` (STRING): Optional output directory

**Output:**
- `file_path` (STRING): Path to the generated DCI file

## DCI Format Specification

The DCI (DSG Combined Icons) format is an archive format that contains multiple icon images organized in a specific directory structure:

```
size/
├── state.tone/
│   ├── scale/
│   │   └── priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
```

Where:
- `size`: Icon size (e.g., "256")
- `state`: Icon state (normal, disabled, hover, pressed)
- `tone`: Tone type (light, dark)
- `scale`: Scale factor (1, 2, 3, etc.)
- The filename contains layer properties (currently using defaults: 1.0.0.0.0.0.0.0.0.0)

## Usage Examples

### Basic Usage

1. Load an image in ComfyUI
2. Add a "DCI Image Exporter" node
3. Connect the image to the node
4. Set desired parameters (filename, size, state, etc.)
5. Run the workflow
6. The DCI file will be saved to the output directory

### Advanced Usage

1. Load multiple images for different states (normal, hover, pressed, etc.)
2. Add a "DCI Image Exporter (Advanced)" node
3. Connect images to appropriate state inputs
4. Configure tone options and scale factors
5. Run the workflow
6. A comprehensive DCI file with all states and scales will be generated

### Scale Factors

Scale factors determine the pixel density variants included in the DCI file:
- `1`: Base size (e.g., 256x256)
- `2`: 2x size (e.g., 512x512)
- `3`: 3x size (e.g., 768x768)

You can specify custom scale factors as a comma-separated string: "1,2,3,4"

## Technical Details

### File Format

The DCI format uses little-endian byte order and includes:
- Magic header: "DCI\0"
- Version: 1 byte
- File count: 3 bytes
- File metadata and content for each file

### Directory Structure

The extension creates a proper nested directory structure within the DCI archive, following the specification for icon organization by size, state, tone, and scale.

### Image Processing

- Images are automatically resized to match the target size × scale factor
- RGBA images are supported for PNG and WebP formats
- JPEG format automatically converts RGBA to RGB with white background
- High-quality compression settings are used (90% quality for lossy formats)

## Requirements

- ComfyUI
- Python 3.7+
- Pillow (PIL)

## License

This project follows the same license as ComfyUI.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## References

- [DCI Format Specification](https://desktopspec.org/unstable/%E5%9B%BE%E6%A0%87%E6%96%87%E4%BB%B6%E8%A7%84%E8%8C%83.html)
- [DTK Core DCI Implementation](https://github.com/linuxdeepin/dtkcore/blob/master/src/dci/ddcifile.cpp)
