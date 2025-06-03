# ComfyUI DCI Image Exporter Extension

A ComfyUI extension for converting images to DCI (DSG Combined Icons) format, following the desktop specification. This extension also provides comprehensive DCI file preview and analysis capabilities.

## Features

### Export Features
- **Basic DCI Export**: Convert single images to DCI format with customizable parameters
- **Advanced Multi-State Export**: Create DCI files with multiple icon states (normal, hover, pressed, disabled)
- **Multiple Scale Factors**: Support for 1x, 2x, 3x scaling and custom scale combinations
- **Format Support**: WebP, PNG, and JPEG formats
- **Tone Support**: Light and dark tone variants
- **Customizable Icon Sizes**: From 16x16 to 1024x1024 pixels

### Preview & Analysis Features
- **Visual Preview**: Generate grid-based previews of all images in a DCI file
- **Metadata Display**: Show comprehensive metadata for each image including size, state, tone, scale, format
- **Directory Structure Analysis**: Inspect the internal directory structure of DCI files
- **Filtering Capabilities**: Filter images by state, tone, scale factor, or format
- **File Information**: Display file sizes, image dimensions, and other technical details

## Installation

1. Clone this repository into your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/comfyui-deepin.git
```

2. Install the required dependencies:
```bash
cd comfyui-deepin
pip install -r requirements.txt
```

3. Restart ComfyUI

## Available Nodes

### Export Nodes

#### 1. DCI Image Exporter
Basic DCI export node for single-state icons.

**Inputs:**
- `image`: Input image (IMAGE)
- `filename`: Output filename without extension (STRING)
- `icon_size`: Target icon size in pixels (INT, default: 256)
- `icon_state`: Icon state (normal/disabled/hover/pressed, default: normal)
- `tone_type`: Tone type (light/dark, default: dark)
- `image_format`: Output format (webp/png/jpg, default: webp)
- `scale_factors`: Comma-separated scale factors (STRING, default: "1,2,3")
- `output_directory`: Optional output directory (STRING)

**Outputs:**
- `file_path`: Path to the created DCI file (STRING)

#### 2. DCI Image Exporter (Advanced)
Advanced DCI export node supporting multiple states and tones.

**Inputs:**
- `image`: Base image (IMAGE)
- `filename`: Output filename without extension (STRING)
- `icon_size`: Target icon size in pixels (INT, default: 256)
- `image_format`: Output format (webp/png/jpg, default: webp)
- `normal_image`: Normal state image (IMAGE, optional)
- `disabled_image`: Disabled state image (IMAGE, optional)
- `hover_image`: Hover state image (IMAGE, optional)
- `pressed_image`: Pressed state image (IMAGE, optional)
- `include_light_tone`: Include light tone variant (BOOLEAN, default: false)
- `include_dark_tone`: Include dark tone variant (BOOLEAN, default: true)
- `scale_factors`: Comma-separated scale factors (STRING, default: "1,2,3")
- `output_directory`: Optional output directory (STRING)

**Outputs:**
- `file_path`: Path to the created DCI file (STRING)

### Preview & Analysis Nodes

#### 3. DCI Preview
Visual preview node for DCI file contents.

**Inputs:**
- `dci_file_path`: Path to DCI file (STRING)
- `grid_columns`: Number of columns in preview grid (INT, default: 4)
- `show_metadata`: Show metadata labels (BOOLEAN, default: true)

**Outputs:**
- `preview_image`: Grid preview of all images (IMAGE)
- `metadata_summary`: Summary of DCI file metadata (STRING)

#### 4. DCI File Loader
Utility node for loading DCI file paths.

**Inputs:**
- `file_path`: DCI file path (STRING, optional)

**Outputs:**
- `dci_file_path`: Validated DCI file path (STRING)

#### 5. DCI Metadata Extractor
Detailed metadata extraction and filtering node.

**Inputs:**
- `dci_file_path`: Path to DCI file (STRING)
- `filter_by_state`: Filter by icon state (all/normal/disabled/hover/pressed, default: all)
- `filter_by_tone`: Filter by tone (all/light/dark, default: all)
- `filter_by_scale`: Filter by scale factors (STRING, default: "all")

**Outputs:**
- `detailed_metadata`: Detailed metadata for filtered images (STRING)
- `directory_structure`: DCI internal directory structure (STRING)
- `file_list`: List of files matching filters (STRING)

## Usage Examples

### Basic DCI Export
1. Load an image using `LoadImage`
2. Connect it to `DCI Image Exporter`
3. Configure the export parameters
4. Execute to create a DCI file

### DCI Preview Workflow
1. Use `DCI File Loader` to specify a DCI file path
2. Connect to `DCI Preview` node
3. Adjust grid columns and metadata display options
4. View the generated preview image and metadata summary

### Advanced Analysis
1. Load a DCI file using `DCI File Loader`
2. Connect to `DCI Metadata Extractor`
3. Apply filters to focus on specific images
4. Examine detailed metadata, directory structure, and file lists

### Multi-State Icon Creation
1. Load different images for each state (normal, hover, pressed, disabled)
2. Connect them to `DCI Image Exporter (Advanced)`
3. Configure tone options and scale factors
4. Generate a comprehensive multi-state DCI file

## Example Workflows

### Basic Export and Preview
```
LoadImage → DCI Image Exporter → DCI Preview → PreviewImage
                                      ↓
                                 ShowText (metadata)
```

### Advanced Multi-State Analysis
```
LoadImage (normal) ──┐
LoadImage (hover) ───┼─→ DCI Image Exporter (Advanced) → DCI Metadata Extractor → ShowText
LoadImage (pressed) ─┘                                           ↓
                                                            DCI Preview → PreviewImage
```

## DCI Format Specification

This extension implements the DCI format according to the desktop specification:
- **Magic Header**: "DCI\0"
- **Version**: 1
- **Directory Structure**: `size/state.tone/scale/layer.format`
- **Supported States**: normal, disabled, hover, pressed
- **Supported Tones**: light, dark
- **Supported Formats**: WebP, PNG, JPEG

## File Structure

```
comfyui-deepin/
├── __init__.py              # ComfyUI extension registration
├── nodes.py                 # All ComfyUI nodes (export + preview)
├── dci_format.py           # DCI file creation and building
├── dci_reader.py           # DCI file reading and parsing
├── test_dci.py             # Basic DCI export tests
├── test_dci_preview.py     # DCI preview functionality tests
├── example_workflow.json   # Basic export workflow example
├── example_dci_preview_workflow.json  # Preview workflow example
├── requirements.txt        # Python dependencies
└── README.md              # This documentation
```

## Testing

### Test DCI Export
```bash
python test_dci.py
```

### Test DCI Preview
```bash
python test_dci_preview.py
```

The preview test will:
1. Create a comprehensive test DCI file with multiple states, tones, and scales
2. Test DCI file reading and parsing
3. Generate preview grids with different column layouts
4. Test metadata extraction and filtering
5. Display directory structure analysis

## Technical Details

### DCI File Format
- **Header**: 4-byte magic + 1-byte version + 3-byte file count
- **File Entries**: Type (1 byte) + Name (63 bytes) + Size (8 bytes) + Content
- **Directory Structure**: Nested directories containing image files
- **Byte Order**: Little-endian

### Preview Generation
- **Grid Layout**: Configurable column count with automatic row calculation
- **Image Scaling**: Maintains aspect ratio while fitting in grid cells
- **Metadata Overlay**: Shows size, state, tone, scale, format, and file size
- **Font Handling**: Automatic fallback from system fonts to default

### Metadata Extraction
- **Path Parsing**: Extracts metadata from directory structure
- **Layer Information**: Parses complex layer filenames for additional properties
- **Filtering**: Supports multiple filter criteria simultaneously
- **Summary Generation**: Creates comprehensive statistics and summaries

## Dependencies

- **Pillow**: Image processing and manipulation
- **NumPy**: Array operations for ComfyUI tensor conversion
- **PyTorch**: ComfyUI tensor compatibility

## Troubleshooting

### Common Issues

1. **"DCI file not found"**: Ensure the file path is correct and the file exists
2. **"Failed to read DCI file"**: Check if the file is a valid DCI format with correct magic header
3. **"No images found"**: The DCI file may be empty or have an unsupported structure
4. **Font rendering issues**: The extension will fall back to default fonts if system fonts are unavailable

### Debug Information

Enable debug output by checking the ComfyUI console for detailed error messages and processing information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the desktop specification for DCI format
- Inspired by the Qt/C++ implementation in dtkcore
- Built for the ComfyUI ecosystem
