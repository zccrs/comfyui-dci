# ComfyUI DCI Extension

**Language / 语言**: [English](#english) | [中文](#中文)

---

## English

# ComfyUI DCI Image Export Extension

A comprehensive ComfyUI extension for creating, previewing, and analyzing DCI (DSG Combined Icons) format files. This extension implements the complete DCI specification, supporting multi-state icons, multi-tone variants, scaling factors, and advanced metadata analysis.

## DCI Specification Documentation

This project is designed and implemented strictly based on the **DCI (DSG Combined Icons) standard format documentation**.

### Official Specification Documents
- **Official Specification**: [Desktop Spec Group - Icon File Specification](https://desktopspec.org/unstable/%E5%9B%BE%E6%A0%87%E6%96%87%E4%BB%B6%E8%A7%84%E8%8C%83.html)
- **Local Documentation**: **[dci-specification.md](./dci-specification.md)**

### Documentation Features

The `dci-specification.md` document in this project is based on the official specification and optimized for practical use:

- 📋 **Complete DCI file format description**: Binary structure, file headers, metadata formats
- 📝 **Detailed layer file naming conventions**: Optimized naming formats and parameter descriptions
- 🎨 **Color adjustment algorithm explanations**: Precise color calculation formulas and examples
- 💡 **Practical application examples**: Complete directory structures and filename examples
- 🔍 **Lookup rules and fallback mechanisms**: Icon resource matching and selection logic
- ⚡ **Alpha8 format in-depth analysis**: Technical details based on [dtkgui implementation](https://github.com/linuxdeepin/dtkgui)

### Standard Compatibility

This tool fully complies with DCI standard specifications:
- ✅ **File format compatibility**: Generated DCI files fully conform to official binary format specifications
- ✅ **Directory structure standards**: Strictly follows `<icon_size>/<icon_state>.<tone_type>/<scale_factor>/<layer_file>` structure
- ✅ **File naming conventions**: Complete support for `priority.paddingp.palette.hue_saturation_brightness_red_green_blue_alpha.format[.alpha8]` format
- ✅ **Filename omission rules**: Supports DCI specification filename optimization strategies, default values can be omitted (e.g., `1.webp`)
- ✅ **Layer system support**: Complete implementation of priority, padding, palette, and color adjustment features
- ✅ **Alpha8 optimization**: Supports alpha channel storage optimization based on grayscale format
- ✅ **Backward compatibility**: Supports both simplified and complete filename formats

## Project Status

- ✅ **Complete DCI format implementation**: Full support for DCI file creation and reading
- ✅ **Multi-state icon support**: Normal, hover, pressed, disabled states
- ✅ **Multi-tone support**: Light and dark tone variants
- ✅ **Advanced preview system**: Grid-based visualization with metadata overlay
- ✅ **Modular node architecture**: Refactored into more flexible composable nodes
- ✅ **Binary data flow**: Support for inter-node binary data transfer
- ✅ **Binary file processing**: Dedicated binary file loading and saving nodes
- ✅ **Complete Chinese localization**: All interface elements fully support Chinese display
- ✅ **Enhanced error handling**: Detailed error reporting and debugging information
- ✅ **Checkerboard background support**: Checkerboard backgrounds for transparent image preview
- ✅ **Production ready**: Thoroughly tested with example workflows

## Directory Structure

```
comfyui-dci/
├── py/                          # Core Python modules
│   ├── __init__.py             # Module initialization
│   ├── dci_format.py           # DCI format implementation
│   ├── dci_reader.py           # DCI file reader
│   └── nodes.py                # ComfyUI node definitions
├── locales/                     # Internationalization files
├── resources/                   # Static resources
├── tools/                       # Development tools
├── tests/                       # Test files
├── examples/                    # Example workflows
├── web_version/                 # Web components (reserved)
├── __init__.py                  # Extension entry point
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── install.sh                   # Linux/Mac installation script
├── install.bat                  # Windows installation script
├── preliminary-design.md        # Preliminary design
└── detailed-design.md           # Detailed design
```

## Features

### Export Functions
- **DCI Image Creation**: Convert single images to DCI image data with custom parameters
- **DCI File Composition**: Combine multiple DCI images into complete DCI files
- **Multiple Scale Factors**: Support decimal scaling like 1x, 1.25x, 1.5x, 2x, etc.
- **Format Support**: WebP, PNG, and JPEG formats
- **Tone Support**: Light and dark tone variants
- **Customizable Icon Sizes**: From 16x16 to 1024x1024 pixels

### Preview Functions
- **Visual Preview**: Generate grid previews of all images in DCI files
- **Metadata Display**: Show comprehensive metadata for each image including size, state, tone, scale, format
- **In-node Display**: Display preview content directly in the node interface

### Binary File Processing Functions
- **Universal File Loading**: Load arbitrary binary files from the file system (DCI, images, archives, etc.)
- **Flexible File Saving**: Save binary data to specified locations with custom output directory support
- **Base64 Encoding/Decoding**: Convert binary data to/from base64 text format for data transfer and storage
- **Data Structuring**: Provide unified binary data structures including content, metadata, and path information
- **Cross-Format Support**: Works with any file type, not limited to DCI format
- **Workflow Integration**: Seamlessly integrate file operations into ComfyUI workflows

### Internationalization Support
- **Complete Chinese Interface**: All node names, parameter names, and output names support Chinese display
- **Bilingual Support**: Support switching between Chinese and English interfaces
- **Localized Translation**: All user interface elements are professionally translated
- **Color Name Translation**: 20 color names fully localized (Light Gray, Blue, Red, etc.)
- **Option Value Translation**: All dropdown options and default values support Chinese display

### Error Handling & Debugging
- **Detailed Error Reporting**: Display detailed error messages and solution suggestions directly in the interface
- **Visual Error Preview**: DCI preview node generates red preview images with error information when errors occur
- **Analysis Node Debugging**: DCI analysis node outputs detailed error logs and data status
- **Parameter Compatibility**: Support both translated and original parameter names for backward compatibility

## Installation

### From ComfyUI Registry (Recommended)

This extension is available on the official ComfyUI Registry. You can install it directly through ComfyUI Manager:

1. Open ComfyUI Manager in your ComfyUI interface
2. Search for "DCI Image Export Extension" or "comfyui-dci"
3. Click Install and restart ComfyUI

### Automatic Installation (Alternative)

1. Clone this repository to your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/comfyui-dci.git
```

2. Run the installation script:

**Linux/Mac:**
```bash
cd comfyui-dci
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
cd comfyui-dci
install.bat
```

### Manual Installation

1. Clone the repository (same as above)

2. Manually install dependencies:
```bash
cd comfyui-dci
pip install -r requirements.txt
```

3. Restart ComfyUI

4. After installation, all DCI nodes will appear in the ComfyUI node menu under the **"DCI"** category

## ComfyUI Node Detailed Description

This extension provides 8 ComfyUI nodes, all unified under the **"DCI"** group and divided into three functional subcategories:

### Node Groups

#### DCI/Export
- DCI_Image (DCI Image) - Full-featured DCI image creation node
- DCI_SampleImage (DCI Sample Image) - Simplified DCI image creation node
- DCI_FileNode (DCI File)

#### DCI/Preview
- DCI_PreviewNode (DCI Preview)
- DCI_ImagePreview (DCI Image Preview)

#### DCI/Analysis
- DCI_Analysis (DCI Analysis)

#### DCI/Effects
- DropShadowNode (Drop Shadow)

#### DCI/Files
- DCI_BinaryFileLoader (Binary File Loader)
- DCI_BinaryFileSaver (Binary File Saver)
- DCI_FileSaver (DCI File Saver)
- DCI_Base64Encoder (Base64 Encoder)
- DCI_Base64Decoder (Base64 Decoder)
- DCI_DirectoryLoader (Directory Loader)

### Available Node Detailed Description

#### 1. DCI Image
**Node Category**: `DCI/Export`
**Function Description**: Create single DCI image data, output metadata instead of directly creating files, providing more flexible workflows. Fully supports the layer system in DCI specification, including priority, padding, palette, and color adjustment features.

**Required Input Parameters:**
- **`image`** (IMAGE): ComfyUI image tensor
- **`icon_size`** (INT): Icon size (16-1024 pixels), default 256
- **`icon_state`** (COMBO): Icon state (normal/disabled/hover/pressed), default normal
- **`scale`** (FLOAT): Scale factor (0.1-10.0), default 1.0, supports decimals like 1.25

**Optional Input Parameters (Advanced Settings):**

*Basic Settings:*
- **`image_format`** (COMBO): Image format (webp/png/jpg), default webp
- **`image_quality** (INT): Image quality (1-100), default 90, only effective for webp and jpg formats

*Background Color Settings:*
- **`background_color`** (COMBO): Background color processing (transparent/white/black/custom), default transparent
- **`custom_bg_r`** (INT): Custom background red component (0-255), default 255
- **`custom_bg_g`** (INT): Custom background green component (0-255), default 255
- **`custom_bg_b`** (INT): Custom background blue component (0-255), default 255

*Layer Settings (DCI Specification Compliant):*
- **`layer_priority`** (INT): Layer priority (1-100), default 1, higher values draw on top
- **`layer_padding`** (INT): Padding value (0-100), default 0, used for shadow effects etc.
- **`palette_type`** (COMBO): Palette type (none/foreground/background/highlight_foreground/highlight), default none

*Color Adjustment Parameters (-100 to 100):*
- **`hue_adjustment`** (INT): Hue adjustment, default 0
- **`saturation_adjustment`** (INT): Saturation adjustment, default 0
- **`brightness_adjustment`** (INT): Brightness adjustment, default 0
- **`red_adjustment`** (INT): Red channel adjustment, default 0
- **`green_adjustment`** (INT): Green channel adjustment, default 0
- **`blue_adjustment`** (INT): Blue channel adjustment, default 0
- **`alpha_adjustment`** (INT): Alpha channel adjustment, default 0

**Output:**
- **`dci_image_data`** (DCI_IMAGE_DATA): DCI image metadata structure
- **`path`** (STRING): DCI image internal path string (e.g., "256/normal.light/1/1.0p.-1.0_0_0_0_0_0_0.webp")
- **`binary_data`** (BINARY_DATA): Binary data content of the image

**Usage Example:**
```
Image Input → DCI Image Node → DCI Image Data → DCI File Node → DCI Binary Data
```

#### 2. DCI Sample Image
**Node Category**: `DCI/Export`
**Function Description**: Create simplified DCI image data with only the most basic parameter settings, suitable for most common use cases. Compared to the full DCI Image node, this node has a cleaner interface with fewer parameters.

**Required Input Parameters:**
- **`image`** (IMAGE): ComfyUI image tensor
- **`icon_size`** (INT): Icon size (16-1024 pixels), default 256
- **`icon_state`** (COMBO): Icon state (normal/disabled/hover/pressed), default normal
- **`scale`** (FLOAT): Scale factor (0.1-10.0), default 1.0, supports decimals like 1.25
- **`tone_type`** (COMBO): Tone type (light/dark), default light
- **`image_format`** (COMBO): Image format (webp/png/jpg), default webp

**Output:**
- **`dci_image_data`** (DCI_IMAGE_DATA): Dictionary data containing path, content, and metadata
- **`path`** (STRING): DCI image internal path string (e.g., "256/normal.light/1/1.0p.-1.0_0_0_0_0_0_0.webp")
- **`binary_data`** (BINARY_DATA): Binary data content of the image

**Node Features:**
- **Simplified Interface**: Only shows the 5 most commonly used basic parameters, clean and easy to use
- **Default Settings**: All advanced parameters use reasonable defaults (priority 1, no padding, no palette, no color adjustments)
- **Transparent Background**: Maintains original image transparency by default, suitable for most icon creation scenarios
- **Quick Creation**: Suitable for quickly creating standard DCI images without complex configuration

#### 3. DCI File
**Node Category**: `DCI/Export`
**Function Description**: Receives multiple DCI Image outputs and combines them into a complete DCI file with composable design. This node supports chaining multiple DCI File nodes together to handle unlimited numbers of DCI images, making it highly flexible for complex icon sets.

**Optional Input Parameters:**
- **`dci_binary_data`** (BINARY_DATA): Existing DCI binary data to extend (for composable workflows)
- **`dci_image_1` to `dci_image_4`** (DCI_IMAGE_DATA): Up to 4 DCI image data per node

**Output:**
- **`dci_binary_data`** (BINARY_DATA): Binary data of the DCI file

**Composable Design Features:**
- **Unlimited Images**: Chain multiple DCI File nodes to handle any number of images
- **Flexible Workflow**: Each node can process 4 images, allowing modular icon creation
- **Data Preservation**: When only existing data is provided (no new images), the node passes through the data unchanged
- **Intelligent Merging**: When both existing DCI data and new images are provided, the node merges them intelligently
- **File Overwrite Behavior**: New DCI images will overwrite existing files with the same path (size/state.tone/scale), while preserving other existing files

**Usage Examples:**
```
# Basic usage (up to 4 images)
DCI Image 1 → DCI File → DCI Binary Data

# Composable usage (unlimited images)
DCI Image 1-4 → DCI File Node 1 → DCI Binary Data 1
DCI Binary Data 1 + DCI Image 5-8 → DCI File Node 2 → DCI Binary Data 2 (merged)
DCI Binary Data 2 + DCI Image 9-12 → DCI File Node 3 → DCI Binary Data 3 (merged)

# Data passthrough
Existing DCI Data → DCI File Node → Same DCI Data (unchanged)

# File overwrite behavior
Existing DCI Data (red image at 256px/normal.light/1.0x) +
New DCI Image (blue image at 256px/normal.light/1.0x) →
Result: Blue image replaces red image, other existing images preserved
```

#### 4. DCI Preview
**Node Category**: `DCI/Preview`
**Function Description**: Display visual preview and detailed metadata information of DCI file content directly within the node. Specialized for previewing DCI binary data, now supports separate display of Light and Dark related content. **Enhanced to support multiple DCI binary data inputs and IMAGE output**.

**Required Input Parameters:**
- **`dci_binary_data`** (BINARY_DATA,BINARY_DATA_LIST): Single DCI binary data or list of multiple DCI binary data

**Optional Input Parameters:**
- **`light_background_color`** (COMBO): Light theme preview background color, default light_gray
- **`dark_background_color`** (COMBO): Dark theme preview background color, default dark_gray
- **`text_font_size`** (INT): Text font size (8-50 pixels), default 18, controls both font size in preview images and text summary format

**Output:**
- **`preview_images`** (IMAGE): ComfyUI IMAGE tensor containing preview images. When processing multiple DCI files, outputs multiple preview images in batch format

**Background Color Options:**
Supports 20 preset colors including:
- **Basic Colors**: light_gray, dark_gray, white, black
- **Special Backgrounds**: transparent, checkerboard
- **Color Options**: blue, green, red, yellow, cyan, magenta, orange, purple, pink, brown, navy, teal, olive, maroon

**Multi-Data Processing:**
- **Single Input**: Processes one DCI file and generates one preview image
- **Multiple Input**: Processes multiple DCI files and generates corresponding preview images
- **Independent Processing**: Each DCI file is processed independently, generating separate preview images
- **Batch Output**: All preview images are combined into a single IMAGE tensor for downstream processing

#### 5. DCI Image Preview
**Node Category**: `DCI/Preview`
**Function Description**: Specialized for previewing DCI image data, providing clean image preview functionality. **Enhanced to support multiple DCI image data inputs and IMAGE output**.

**Required Input Parameters:**
- **`dci_image_data`** (DCI_IMAGE_DATA,DCI_IMAGE_DATA_LIST): Single DCI image data or list of multiple DCI image data

**Optional Input Parameters:**
- **`preview_background`** (COMBO): Preview background type (transparent/white/black/checkerboard), default checkerboard

**Output:**
- **`preview_images`** (IMAGE): ComfyUI IMAGE tensor containing preview images. When processing multiple DCI images, outputs multiple preview images in batch format

**Multi-Data Processing:**
- **Single Input**: Processes one DCI image and generates one preview image
- **Multiple Input**: Processes multiple DCI images and generates corresponding preview images
- **Independent Processing**: Each DCI image is processed independently, generating separate preview images
- **Batch Output**: All preview images are combined into a single IMAGE tensor for downstream processing

#### 6. Drop Shadow
**Node Category**: `DCI/Effects`
**Function Description**: Apply drop shadow effects to images, similar to CSS drop-shadow filter. Supports all standard drop shadow parameters including offset, blur, spread, color, and opacity. Automatically handles canvas expansion and provides cross-platform compatibility.

**Required Input Parameters:**
- **`image`** (IMAGE): ComfyUI image tensor to apply shadow effect

**Optional Input Parameters:**

*Shadow Position:*
- **`offset_x`** (INT): Horizontal shadow offset (-100 to 100 pixels), default 4
- **`offset_y`** (INT): Vertical shadow offset (-100 to 100 pixels), default 4

*Shadow Appearance:*
- **`blur_radius`** (INT): Shadow blur radius (0-100 pixels), default 8
- **`spread_radius`** (INT): Shadow spread radius (-50 to 50 pixels), default 0
  - Positive values expand the shadow
  - Negative values shrink the shadow

*Shadow Color (RGBA):*
- **`shadow_color_r`** (INT): Shadow red component (0-255), default 0
- **`shadow_color_g`** (INT): Shadow green component (0-255), default 0
- **`shadow_color_b`** (INT): Shadow blue component (0-255), default 0
- **`shadow_opacity`** (FLOAT): Shadow opacity (0.0-1.0), default 0.5

*Canvas Options:*
- **`auto_expand_canvas`** (BOOLEAN): Automatically expand canvas to fit shadow, default True
- **`canvas_padding`** (INT): Additional canvas padding (0-200 pixels), default 20

**Output:**
- **`image`** (IMAGE): Image with applied drop shadow effect

**CSS Compatibility Examples:**
```css
/* CSS: drop-shadow(4px 4px 8px rgba(0,0,0,0.5)) */
/* Node: offset_x=4, offset_y=4, blur_radius=8, shadow_color=(0,0,0), shadow_opacity=0.5 */

/* CSS: drop-shadow(-2px -2px 6px rgba(255,0,0,0.7)) */
/* Node: offset_x=-2, offset_y=-2, blur_radius=6, shadow_color=(255,0,0), shadow_opacity=0.7 */
```

**Technical Features:**
- **Pure Python Implementation**: No external dependencies, uses PIL and numpy
- **Alpha Channel Support**: Properly handles transparent images and creates shadows from alpha masks
- **Spread Effect**: Supports both positive (expand) and negative (shrink) spread values
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Performance Optimized**: Efficient shadow generation with optional scipy acceleration
- **Canvas Management**: Intelligent canvas sizing to accommodate shadow effects

#### 7. Binary File Loader
**Node Category**: `DCI/Files`
**Function Description**: Load binary files from the file system, designed for handling DCI icon files and other binary data.

**Optional Input Parameters:**
- **`file_path`** (STRING): File path to load, default empty string

**Output:**
- **`binary_data`** (BINARY_DATA): Binary content of the file (bytes type)
- **`file_path`** (STRING): Complete path of the loaded file

#### 7.1. Directory Loader
**Node Category**: `DCI/Files`
**Function Description**: Batch load multiple binary files from a directory with filtering and recursive search capabilities. Uses breadth-first traversal for consistent file ordering. **NEW**: Automatically detects and decodes image files, providing separate image outputs for direct use in ComfyUI workflows.

**Required Input Parameters:**
- **`directory_path`** (STRING): Directory path to scan, default empty string
- **`file_filter`** (STRING): File filter pattern using wildcards (e.g., "*.dci", "*.png,*.jpg"), default "*.dci"
- **`include_subdirectories`** (BOOLEAN): Whether to include subdirectories in search, default True

**Output:**
- **`binary_data_list`** (BINARY_DATA_LIST): List of binary data from loaded files
- **`relative_paths`** (STRING_LIST): List of relative file paths (relative to the specified directory)
- **`image_list`** (IMAGE): **NEW** - Batch tensor of decoded images (None if no images found)
- **`image_relative_paths`** (STRING_LIST): **NEW** - List of relative paths for decoded images

**Features:**
- **Wildcard Filtering**: Support for multiple patterns separated by commas (e.g., "*.dci,*.png")
- **Recursive Search**: Breadth-first directory traversal for consistent ordering
- **Path Normalization**: Automatic path normalization and trailing slash handling
- **Data Consistency**: Binary data list and path list maintain perfect order matching
- **Error Resilience**: Continues processing even if individual files fail to load
- **Cross-Platform**: Works on Windows, Linux, and macOS with proper path handling
- **🆕 Automatic Image Detection**: Recognizes image files by extension (.png, .jpg, .jpeg, .bmp, .gif, .tiff, .webp, .ico)
- **🆕 Image Decoding**: Automatically decodes detected images to ComfyUI IMAGE format (RGB, 0-1 range)
- **🆕 Dual Output System**: Provides both binary data (for all files) and decoded images (for image files only)
- **🆕 Format Conversion**: Handles various image formats and color modes (RGBA→RGB, grayscale→RGB)

**Example Usage:**
- Load all DCI files: `directory_path="/path/to/icons", file_filter="*.dci", include_subdirectories=True`
- Load images only: `directory_path="/path/to/images", file_filter="*.png,*.jpg,*.webp", include_subdirectories=False`
- Load all files: `directory_path="/path/to/data", file_filter="*", include_subdirectories=True`
- **🆕 Image workflow**: Connect `image_list` output directly to image processing nodes for automatic image handling

#### 6.2. Deb Loader
**Node Category**: `DCI/Files`
**Function Description**: Extract and load files from Debian packages (.deb files) with filtering capabilities. Parses both control.tar.* and data.tar.* archives within the deb package to extract matching files. **NEW**: Automatically detects and decodes image files from deb packages, providing separate image outputs for direct use in ComfyUI workflows.

**Required Input Parameters:**
- **`deb_file_path`** (STRING): Path to the .deb file to parse, default empty string
- **`file_filter`** (STRING): File filter pattern using wildcards (e.g., "*.dci", "*.png,*.jpg"), default "*.dci"

**Output:**
- **`binary_data_list`** (BINARY_DATA_LIST): List of binary data from extracted files
- **`relative_paths`** (STRING_LIST): List of relative file paths within the deb package
- **`image_list`** (IMAGE): **NEW** - Batch tensor of decoded images (None if no images found)
- **`image_relative_paths`** (STRING_LIST): **NEW** - List of relative paths for decoded images

**Features:**
- **Deb Package Parsing**: Uses `ar` command to extract deb package components
- **Multi-Archive Support**: Processes both control.tar.* and data.tar.* archives
- **Compression Support**: Handles .gz, .xz, .bz2, and uncompressed tar archives
- **Wildcard Filtering**: Support for multiple patterns separated by commas (e.g., "*.dci,*.png")
- **Path Cleaning**: Automatically removes leading "./" from extracted paths
- **Error Resilience**: Continues processing even if individual files fail to extract
- **Cross-Platform**: Works on systems with `ar` command available
- **🆕 Automatic Image Detection**: Recognizes image files by extension (.png, .jpg, .jpeg, .bmp, .gif, .tiff, .webp, .ico)
- **🆕 Image Decoding**: Automatically decodes detected images to ComfyUI IMAGE format (RGB, 0-1 range)
- **🆕 Dual Output System**: Provides both binary data (for all files) and decoded images (for image files only)
- **🆕 Format Conversion**: Handles various image formats and color modes (RGBA→RGB, grayscale→RGB)

**Technical Details:**
- **Extraction Process**: Uses temporary directories for safe extraction
- **Archive Detection**: Automatically detects compression format from file extension
- **Memory Efficient**: Processes files in memory without creating temporary files
- **Path Normalization**: Ensures consistent path formatting across platforms

**Example Usage:**
- Extract DCI files from deb: `deb_file_path="/path/to/package.deb", file_filter="*.dci"`
- Extract images from deb: `deb_file_path="/path/to/icons.deb", file_filter="*.png,*.svg"`
- Extract all files from deb: `deb_file_path="/path/to/data.deb", file_filter="*"`
- **🆕 Image workflow**: Connect `image_list` output directly to image processing nodes for automatic image handling

**Dependencies:**
- **System Requirement**: `ar` command preferred but not required (usually part of binutils package)
- **Cross-Platform Support**: Automatic fallback to pure Python implementation when `ar` command is unavailable
- **Python Modules**: Uses standard library modules (tarfile, subprocess, tempfile)
- **Path Handling**: Enhanced cross-platform path normalization for Windows paths on Linux/Unix systems

#### 7. Binary File Saver
**Node Category**: `DCI/Files`
**Function Description**: Save binary data to the file system with advanced filename handling, prefix/suffix support, and cross-platform path processing.

**Required Input Parameters:**
- **`binary_data`** (BINARY_DATA): Binary data to save
- **`file_name`** (STRING): Target filename or path, default "binary_file"

**Optional Input Parameters:**
- **`output_directory`** (STRING): Output directory, defaults to ComfyUI output directory. If specified directory doesn't exist, it will be created automatically. Supports paths with trailing slashes and automatically normalizes path separators
- **`filename_prefix`** (STRING): Filename prefix, default empty string
- **`filename_suffix`** (STRING): Filename suffix, default empty string
- **`allow_overwrite`** (BOOLEAN): Allow overwriting existing files, default False

**Output:**
- **`saved_path`** (STRING): Complete saved file path on success, detailed error message on failure (consistent with DCI File Saver behavior)

**Advanced Filename Handling Features:**

*Path Processing:*
- **Cross-Platform Compatibility**: Automatically handles Windows (`\`) and Linux (`/`) path separators
- **Path Extraction**: Automatically extracts filename from full paths
- **Example**: `/home/user/data.txt` → `data.txt`, `C:\Users\test\file.bin` → `file.bin`

*Prefix and Suffix Support:*
- **Flexible Naming**: Support for adding custom prefix and suffix to filenames
- **Extension Preservation**: Automatically preserves file extensions when applying prefix/suffix
- **Example**: Input `data.txt`, prefix `backup_`, suffix `_v2` → `backup_data_v2.txt`

*Special Cases Handling:*
- **Empty Input**: Uses default filename `binary_file` when input is empty
- **Path-Only Input**: Uses default filename when input contains only path separators
- **No Extension**: Handles files without extensions properly
- **File Cleaning**: Removes invalid characters from filenames for filesystem compatibility

**Usage Examples:**
- Basic save: `file_name="data.bin", output_directory="/path/to/output"`
- With prefix: `file_name="report.pdf", filename_prefix="backup_"`
- With suffix: `file_name="image.png", filename_suffix="_processed"`
- Full customization: `file_name="/tmp/data.txt", filename_prefix="new_", filename_suffix="_v2"`

**Technical Features:**
- **Path Safety**: Automatic path normalization and invalid character removal
- **Directory Creation**: Automatically creates output directories if they don't exist
- **Overwrite Protection**: Prevents accidental file overwriting with explicit control
- **Error Handling**: Comprehensive error reporting for debugging
- **Cross-Platform**: Works consistently on Windows, Linux, and macOS

#### 8. Base64 Decoder
**Node Category**: `DCI/Files`
**Function Description**: Decode binary data from base64 encoded strings, supporting multiline input for large data sets.

**Required Input Parameters:**
- **`base64_data`** (STRING): Base64 encoded string data (supports multiline input)

**Output:**
- **`binary_data`** (BINARY_DATA): Decoded binary data

**Features:**
- **Multiline Support**: Handles base64 strings with line breaks and whitespace
- **Error Handling**: Gracefully handles invalid base64 data
- **Large Data Support**: Efficiently processes large base64 encoded files

#### 9. Base64 Encoder
**Node Category**: `DCI/Files`
**Function Description**: Encode binary data to base64 strings for data exchange and storage. This is a pure conversion node without file operations.

**Required Input Parameters:**
- **`binary_data`** (BINARY_DATA): Binary data to encode

**Output:**
- **`base64_data`** (STRING): Base64 encoded string

**Features:**
- **Pure Conversion**: Only performs encoding, no file operations
- **Efficient Processing**: Direct binary-to-base64 conversion
- **Chain-Friendly**: Output can be directly used by other nodes or saved separately

#### 10. Binary File Saver (Enhanced)
**Node Category**: `DCI/Files`
**Function Description**: Save binary data to the file system, supports custom output paths and directories with overwrite protection.

**Required Input Parameters:**
- **`binary_data`** (BINARY_DATA): Binary data to save
- **`file_name`** (STRING): Target filename, default "binary_file"

**Optional Input Parameters:**
- **`output_directory`** (STRING): Output directory, defaults to ComfyUI output directory. If specified directory doesn't exist, it will be created automatically. Supports paths with trailing slashes and automatically normalizes path separators
- **`allow_overwrite`** (BOOLEAN): Allow overwriting existing files, default False

**Output:**
- **`saved_path`** (STRING): Actual saved file path on success, detailed error message on failure

#### 11. DCI File Saver (Enhanced)
**Node Category**: `DCI/Files`
**Function Description**: Advanced file saver specialized for saving DCI files, with intelligent filename parsing, prefix/suffix support, cross-platform path handling, and overwrite protection.

**Required Input Parameters:**
- **`binary_data`** (BINARY_DATA): DCI binary data to save
- **`input_filename`** (STRING): Input filename or path, default "icon.png"

**Optional Input Parameters:**
- **`output_directory`** (STRING): Output directory, defaults to ComfyUI output directory. If specified directory doesn't exist, it will be created automatically. Supports paths with trailing slashes and automatically normalizes path separators
- **`filename_prefix`** (STRING): Filename prefix, default empty string
- **`filename_suffix`** (STRING): Filename suffix, default empty string
- **`allow_overwrite`** (BOOLEAN): Allow overwriting existing files, default False

**Output:**
- **`saved_filename`** (STRING): Saved filename (without path), empty string if save failed
- **`saved_full_path`** (STRING): Complete saved file path on success, detailed error message on failure

#### 9. DCI Analysis
**Node Category**: `DCI/Analysis`
**Function Description**: Analyze DCI file internal organization structure and metadata in detail with tree structure, output text format analysis results, specialized for analyzing and debugging DCI file content.

**Required Input Parameters:**
- **`dci_binary_data`** (BINARY_DATA): Binary data of the DCI file

**Output:**
- **`analysis_text`** (STRING): Detailed analysis text in tree structure format

## Example Workflows

### Basic DCI Creation Workflow
```
Image Input → DCI Image → DCI File → Binary File Saver
```

### Advanced Multi-State Icon Workflow
```
Normal Image → DCI Image (state: normal) ┐
Hover Image → DCI Image (state: hover)   ├→ DCI File → DCI Preview
Press Image → DCI Image (state: pressed) ┘
```

### DCI Analysis and Debug Workflow
```
Binary File Loader → DCI Analysis (text output)
                  └→ DCI Preview (visual output)
```

## Technical Implementation

### DCI Format Support
- **Binary Structure**: Complete implementation of DCI binary format
- **Directory Hierarchy**: Support for nested directory structures
- **File Metadata**: Comprehensive metadata handling
- **Layer System**: Full layer priority and composition support

### Performance Optimization
- **Memory Efficient**: Optimized binary data handling
- **Streaming Support**: Large file processing capabilities
- **Caching**: Intelligent caching for repeated operations

### Error Handling
- **Graceful Degradation**: Continues operation when possible
- **Detailed Logging**: Comprehensive error reporting
- **User Feedback**: Clear error messages in UI
- **Consistent List Outputs**: All LIST type outputs return empty lists instead of None when no data is available, ensuring workflow compatibility

## Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ComfyUI team for the excellent framework
- Desktop Spec Group for the DCI specification
- dtkgui project for Alpha8 format insights

---

## 中文

# ComfyUI DCI 图像导出扩展

一个全面的 ComfyUI 扩展，用于创建、预览和分析 DCI（DSG Combined Icons）格式文件。此扩展实现了完整的 DCI 规范，支持多状态图标、多色调、缩放因子和高级元数据分析。

## DCI 规范文档

本项目严格基于 **DCI（DSG Combined Icons）标准格式文档** 设计和实现。

### 官方规范文档
- **官方规范**：[Desktop Spec Group - 图标文件规范](https://desktopspec.org/unstable/%E5%9B%BE%E6%A0%87%E6%96%87%E4%BB%B6%E8%A7%84%E8%8C%83.html)
- **本地文档**：**[dci-specification.md](./dci-specification.md)**

### 文档特色

本项目的 `dci-specification.md` 文档基于官方规范并进行了实用性优化：

- 📋 **完整的 DCI 文件格式说明**：二进制结构、文件头、元数据格式
- 📝 **详细的图层文件命名规范**：优化后的命名格式和参数说明
- 🎨 **颜色调整算法说明**：精确的颜色计算公式和示例
- 💡 **实际应用示例**：完整的目录结构和文件名示例
- 🔍 **查找规则和回退机制**：图标资源的匹配和选择逻辑
- ⚡ **Alpha8格式深度解析**：基于 [dtkgui实现](https://github.com/linuxdeepin/dtkgui) 的技术细节

### 标准兼容性

本工具完全遵循 DCI 标准规范：
- ✅ **文件格式兼容**：生成的DCI文件完全符合官方二进制格式规范
- ✅ **目录结构标准**：严格按照 `<图标大小>/<图标状态>.<色调类型>/<缩放倍数>/<图层文件>` 结构
- ✅ **文件命名规范**：完整支持 `优先级.外边框p.调色板.色调_饱和度_亮度_红_绿_蓝_透明度.格式[.alpha8]` 格式
- ✅ **文件名省略规则**：支持DCI规范的文件名优化策略，默认值可省略（如`1.webp`）
- ✅ **图层系统支持**：完整实现优先级、外边框、调色板和颜色调整功能
- ✅ **Alpha8优化**：支持基于灰度格式的alpha通道存储优化
- ✅ **向后兼容**：同时支持简化文件名和完整文件名格式

## 项目状态

- ✅ **完整的 DCI 格式实现**：完全支持 DCI 文件创建和读取
- ✅ **多状态图标支持**：正常、悬停、按下、禁用状态
- ✅ **多色调支持**：浅色和深色调变体
- ✅ **高级预览系统**：基于网格的可视化与元数据覆盖
- ✅ **模块化节点架构**：重构为更灵活的组合式节点
- ✅ **二进制数据流**：支持节点间二进制数据传递
- ✅ **二进制文件处理**：专用的二进制文件加载和保存节点
- ✅ **完整中文本地化**：所有界面元素完全支持中文显示
- ✅ **增强错误处理**：详细的错误报告和调试信息
- ✅ **棋盘格背景支持**：透明图像预览的棋盘格背景
- ✅ **生产就绪**：通过示例工作流程全面测试

## 目录结构

```
comfyui-dci/
├── py/                          # 核心Python模块
│   ├── __init__.py             # 模块初始化
│   ├── dci_format.py           # DCI格式实现
│   ├── dci_reader.py           # DCI文件读取器
│   └── nodes.py                # ComfyUI节点定义
├── locales/                     # 国际化文件
├── resources/                   # 静态资源
├── tools/                       # 开发工具
├── tests/                       # 测试文件
├── examples/                    # 示例工作流
├── web_version/                 # Web组件（预留）
├── __init__.py                  # 扩展入口点
├── README.md                    # 项目文档
├── requirements.txt             # Python依赖
├── install.sh                   # Linux/Mac安装脚本
├── install.bat                  # Windows安装脚本
├── preliminary-design.md        # 概要设计
└── detailed-design.md           # 详细设计
```

## 功能特性

### 导出功能
- **DCI 图像创建**：将单个图像转换为 DCI 图像数据，支持自定义参数
- **DCI 文件组合**：将多个 DCI 图像组合成完整的 DCI 文件
- **多种缩放因子**：支持小数缩放如 1x、1.25x、1.5x、2x 等自定义缩放组合
- **格式支持**：WebP、PNG 和 JPEG 格式
- **色调支持**：浅色和深色调变体
- **可自定义图标尺寸**：从 16x16 到 1024x1024 像素

### 预览功能
- **可视化预览**：生成 DCI 文件中所有图像的网格预览
- **元数据显示**：显示每个图像的全面元数据，包括尺寸、状态、色调、缩放、格式
- **节点内显示**：直接在节点界面中显示预览内容

### 二进制文件处理功能
- **文件加载**：从文件系统加载任意二进制文件，专为 DCI 图标文件优化
- **文件保存**：将二进制数据保存到指定位置，支持自定义输出目录
- **数据结构化**：提供统一的二进制数据结构，包含内容、元数据和路径信息

### 国际化支持
- **完整中文界面**：所有节点名称、参数名、输出名均支持中文显示
- **双语支持**：支持中文和英文界面切换
- **本地化翻译**：所有用户界面元素都经过专业翻译
- **颜色名称翻译**：20种颜色名称完全本地化（浅灰色、蓝色、红色等）
- **选项值翻译**：所有下拉选项和默认值都支持中文显示

### 错误处理与调试
- **详细错误报告**：在界面上直接显示详细的错误信息和解决建议
- **可视化错误预览**：DCI预览节点在出错时生成包含错误信息的红色预览图
- **分析节点调试**：DCI分析节点输出详细的错误日志和数据状态
- **参数兼容性**：同时支持翻译后和原始参数名，确保向后兼容

## 安装

### 自动安装（推荐）

1. 将此仓库克隆到您的 ComfyUI 自定义节点目录：
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/comfyui-dci.git
```

2. 运行安装脚本：

**Linux/Mac:**
```bash
cd comfyui-dci
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
cd comfyui-dci
install.bat
```

### 手动安装

1. 克隆仓库（同上）

2. 手动安装依赖项：
```bash
cd comfyui-dci
pip install -r requirements.txt
```

3. 重启 ComfyUI

4. 安装完成后，所有 DCI 节点将出现在 ComfyUI 节点菜单的 **"DCI"** 分类下

## ComfyUI 节点详细说明

本扩展提供了 8 个 ComfyUI 节点，所有节点都统一归类在 **"DCI"** 分组下，并按功能分为三个子分类：

### 节点分组

#### DCI/Export（导出）
- DCI_Image (DCI Image) - 完整功能的DCI图像创建节点
- DCI_SampleImage (DCI Sample Image) - 简化的DCI图像创建节点
- DCI_FileNode (DCI File)

#### DCI/Preview（预览）
- DCI_PreviewNode (DCI Preview)
- DCI_ImagePreview (DCI Image Preview)

#### DCI/Analysis（分析）
- DCI_Analysis (DCI Analysis)

#### DCI/Effects（效果）
- DropShadowNode（投影效果）

#### DCI/Files（文件处理）
- DCI_BinaryFileLoader (Binary File Loader)
- DCI_BinaryFileSaver (Binary File Saver)
- DCI_FileSaver (DCI File Saver)

### 可用节点详细说明

#### 1. DCI Image（DCI 图像）
**节点类别**：`DCI/Export`
**功能描述**：创建单个 DCI 图像数据，输出元数据而不是直接创建文件，提供更灵活的工作流程。完全支持 DCI 规范中的图层系统，包括优先级、外边框、调色板和颜色调整功能。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25

**可选输入参数（高级设置）：**

*基础设置：*
- **`image_format`** (COMBO)：图像格式（webp/png/jpg），默认webp
- **`image_quality`** (INT)：图片质量（1-100），默认90，仅对webp和jpg格式有效

*WebP高级设置：*
- **`webp_lossless`** (BOOLEAN)：WebP无损压缩，默认False
- **`webp_alpha_quality`** (INT)：WebP Alpha通道质量（0-100），默认100

*PNG高级设置：*
- **`png_compress_level`** (INT)：PNG压缩等级（0-9），默认6

*背景色设置：*
- **`background_color`** (COMBO)：背景色处理（transparent/white/black/custom），默认transparent
- **`custom_bg_r`** (INT)：自定义背景色红色分量（0-255），默认255
- **`custom_bg_g`** (INT)：自定义背景色绿色分量（0-255），默认255
- **`custom_bg_b`** (INT)：自定义背景色蓝色分量（0-255），默认255

*图层设置（符合 DCI 规范）：*
- **`layer_priority`** (INT)：图层优先级（1-100），默认1，数值越大绘制越靠上
- **`layer_padding`** (INT)：外边框值（0-100），默认0，用于阴影效果等
- **`palette_type`** (COMBO)：调色板类型（none/foreground/background/highlight_foreground/highlight），默认none

*颜色调整参数（-100 到 100）：*
- **`hue_adjustment`** (INT)：色调调整，默认0
- **`saturation_adjustment`** (INT)：饱和度调整，默认0
- **`brightness_adjustment`** (INT)：亮度调整，默认0
- **`red_adjustment`** (INT)：红色分量调整，默认0
- **`green_adjustment`** (INT)：绿色分量调整，默认0
- **`blue_adjustment`** (INT)：蓝色分量调整，默认0
- **`alpha_adjustment`** (INT)：透明度调整，默认0

**输出：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：包含路径、内容、元数据和图层信息的字典数据
- **`path`** (STRING)：DCI图像的内部路径字符串（如："256/normal.light/1/1.0p.-1.0_0_0_0_0_0_0.webp"）
- **`binary_data`** (BINARY_DATA)：图像的二进制数据内容

**背景色处理说明：**
- **transparent**：保持原始透明度（仅PNG和WebP支持）
- **white**：将透明背景替换为白色
- **black**：将透明背景替换为黑色
- **custom**：使用自定义RGB颜色作为背景

**图层系统说明：**
- **图层优先级**：控制图层绘制顺序，数值越大越靠上层
- **外边框**：为图标添加外围不被控件覆盖的区域，常用于阴影效果
- **调色板**：定义图标的颜色填充方式，支持前景色、背景色、高亮色等
- **颜色调整**：精确控制图标的色调、饱和度、亮度和RGBA分量
- **文件命名**：自动按照DCI规范生成图层文件名，格式为 `优先级.外边框p.调色板.色调_饱和度_亮度_红_绿_蓝_透明度.格式`
- **文件名省略**：支持DCI规范的优化策略，当参数为默认值时可省略（如简化为`1.webp`）
- **向后兼容**：同时支持完整文件名和简化文件名格式，确保与真实DCI文件兼容

#### 2. DCI Sample Image（DCI 简单图像）
**节点类别**：`DCI/Export`
**功能描述**：创建简化的 DCI 图像数据，只包含最基本的参数设置，适合大多数常见使用场景。相比完整的 DCI Image 节点，此节点界面更简洁，参数更少。

**必需输入参数：**
- **`image`** (IMAGE)：ComfyUI 图像张量
- **`icon_size`** (INT)：图标尺寸（16-1024像素），默认256
- **`icon_state`** (COMBO)：图标状态（normal/disabled/hover/pressed），默认normal
- **`scale`** (FLOAT)：缩放因子（0.1-10.0），默认1.0，支持小数如1.25
- **`tone_type`** (COMBO)：色调类型（light/dark），默认light
- **`image_format`** (COMBO)：图像格式（webp/png/jpg），默认webp
- **`image_quality`** (INT)：图片质量（1-100），默认90，仅对webp和jpg格式有效

*WebP高级设置：*
- **`webp_lossless`** (BOOLEAN)：WebP无损压缩，默认False
- **`webp_alpha_quality`** (INT)：WebP Alpha通道质量（0-100），默认100

*PNG高级设置：*
- **`png_compress_level`** (INT)：PNG压缩等级（0-9），默认6

**输出：**
- **`dci_image_data`** (DCI_IMAGE_DATA)：包含路径、内容、元数据的字典数据
- **`path`** (STRING)：DCI图像的内部路径字符串（如："256/normal.light/1/1.0p.-1.0_0_0_0_0_0_0.webp"）
- **`binary_data`** (BINARY_DATA)：图像的二进制数据内容

**节点特点：**
- **简化界面**：显示最常用的基本参数和高级压缩设置，界面清晰易用
- **默认设置**：所有高级参数使用合理的默认值（优先级1、无外边框、无调色板、无颜色调整）
- **透明背景**：默认保持图像原始透明度，适合大多数图标制作场景
- **高级压缩**：支持WebP无损压缩、Alpha通道质量控制和PNG压缩等级设置
- **质量控制**：在文件大小和图像质量之间提供精细平衡控制
- **快速创建**：适合快速创建标准DCI图像，无需复杂配置

**使用场景：**
- 快速创建标准图标，无需复杂的图层设置
- 批量处理多个图标文件
- 初学者或不需要高级功能的用户
- 简单的图标转换和格式化工作

#### 3. DCI File（DCI 文件）
**节点类别**：`DCI/Export`
**功能描述**：接收多个 DCI Image 输出并组合成完整的 DCI 文件，采用可组合设计。此节点支持将多个 DCI File 节点串联使用，以处理无限数量的 DCI 图像，为复杂图标集提供高度灵活性。

**可选输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：现有的 DCI 二进制数据，用于扩展（可组合工作流）
- **`dci_image_1` 到 `dci_image_4`** (DCI_IMAGE_DATA)：每个节点最多4个DCI图像数据

**输出：**
- **`dci_binary_data`** (BINARY_DATA)：DCI文件的二进制数据

**可组合设计特性：**
- **无限图像支持**：串联多个 DCI File 节点以处理任意数量的图像
- **灵活工作流**：每个节点可处理4个图像，允许模块化图标创建
- **数据保持**：当只提供现有数据（无新图像）时，节点会原样传递数据
- **智能合并**：当同时提供现有DCI数据和新图像时，节点会智能合并它们
- **文件覆盖行为**：新的DCI图像会覆盖具有相同路径（尺寸/状态.色调/缩放）的现有文件，同时保留其他现有文件

**使用示例：**
```
# 基本用法（最多4个图像）
DCI 图像 1 → DCI 文件 → DCI 二进制数据

# 可组合用法（无限图像）
DCI 图像 1-4 → DCI 文件节点 1 → DCI 二进制数据 1
DCI 二进制数据 1 + DCI 图像 5-8 → DCI 文件节点 2 → DCI 二进制数据 2（合并）
DCI 二进制数据 2 + DCI 图像 9-12 → DCI 文件节点 3 → DCI 二进制数据 3（合并）

# 数据传递
现有 DCI 数据 → DCI 文件节点 → 相同 DCI 数据（不变）

# 文件覆盖行为
现有 DCI 数据（256px/normal.light/1.0x 处有红色图像）+
新 DCI 图像（256px/normal.light/1.0x 处有蓝色图像）→
结果：蓝色图像替换红色图像，其他现有图像保留
```

#### 4. DCI Preview（DCI 预览）
**节点类别**：`DCI/Preview`
**功能描述**：直接在节点内显示 DCI 文件内容的可视化预览和详细元数据信息。专门用于预览 DCI 二进制数据，现支持将Light和Dark相关内容分开显示。**增强支持多个DCI二进制数据输入和IMAGE输出**。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA,BINARY_DATA_LIST)：单个DCI二进制数据或多个DCI二进制数据列表

**可选输入参数：**
- **`light_background_color`** (COMBO)：Light主题预览背景色，默认light_gray
- **`dark_background_color`** (COMBO)：Dark主题预览背景色，默认dark_gray
- **`text_font_size`** (INT)：文本字号大小（8-50像素），默认18，同时控制预览图像中的字体大小和文本摘要的格式

**输出：**
- **`preview_images`** (IMAGE)：包含预览图像的ComfyUI IMAGE张量。处理多个DCI文件时，以批次格式输出多个预览图像

**背景颜色选项：**
支持20种预设颜色，包括：
- **基础色**：light_gray、dark_gray、white、black
- **特殊背景**：transparent（支持Alpha通道透明度）、checkerboard
- **彩色选项**：blue、green、red、yellow、cyan、magenta、orange、purple、pink、brown、navy、teal、olive、maroon

**节点内预览功能：**
- **双列布局**：Light主题图标在左列，Dark主题图标在右列
- **独立背景设置**：Light和Dark主题可设置不同的背景颜色
- **丰富背景色选项**：每种主题支持20种预设背景色，包括特殊的透明和棋盘格背景
- **图标边框显示**：每个图标周围自动绘制细线边框，清晰显示图标的实际范围和尺寸
  - **智能边框颜色**：边框颜色自动跟随文字颜色，保持视觉一致性和界面协调
  - **颜色协调算法**：根据文字颜色自动计算边框颜色，浅色文字使用稍深的边框，深色文字使用稍浅的边框
  - **精确范围指示**：边框紧贴图标边缘，准确显示图标的像素边界
  - **多背景适配**：在所有背景颜色下都能清晰显示边框效果，边框与文字颜色保持一致的视觉风格
  - **透明背景支持**：完整支持Alpha通道透明度，透明背景设置能正确生效
- **自适应文本格式**：根据字体大小调整文本显示格式，较大字体使用更紧凑的布局
- **文件路径分组显示**：Light、Dark和其他色调图标的路径分别显示
- **预览图像标签**：每个图标下方显示详细信息，包括：
  - **文件路径**（第一行）：显示DCI内部的完整路径（如：64/normal.light/1.0.0.0.0.0.0.0.0.0.png）
  - 图标尺寸、状态、缩放因子
  - 文件大小
  - **注意**：不显示色调(tone)字段，因为已按Light/Dark分列显示；不显示格式(format)字段，因为文件名已包含格式信息
- **详细元数据显示**：在节点内显示全面的文件信息，包括：
  - 图标尺寸、状态、色调、缩放因子
  - 图像格式、文件大小、实际尺寸
  - 完整的DCI内部路径和文件名
  - 每个图像的优先级和详细属性
  - 统计汇总信息和文件路径列表

**多数据处理：**
- **单个输入**：处理一个DCI文件，生成一个预览图像
- **多个输入**：处理多个DCI文件，生成对应的预览图像
- **独立处理**：每个DCI文件独立处理，生成单独的预览图像
- **批次输出**：所有预览图像合并为单个IMAGE张量，供下游处理

**注意**：此节点专门用于处理二进制数据输入。不需要手动设置列数，默认将Light和Dark内容分开显示在两列，Light主题图标固定在左侧列，Dark主题图标固定在右侧列。文本格式会根据字体大小自动调整，提供最佳阅读体验。背景颜色选择简化为预设选项，移除了自定义RGB设置以提供更好的用户体验。

#### 5. DCI Image Preview（DCI 图像预览）
**节点类别**：`DCI/Preview`
**功能描述**：专门用于预览DCI图像数据，提供简洁的图像预览功能。**增强支持多个DCI图像数据输入和IMAGE输出**。

**必需输入参数：**
- **`dci_image_data`** (DCI_IMAGE_DATA,DCI_IMAGE_DATA_LIST)：单个DCI图像数据或多个DCI图像数据列表

**可选输入参数：**
- **`preview_background`** (COMBO)：预览背景类型（transparent/white/black/checkerboard），默认checkerboard

**输出：**
- **`preview_images`** (IMAGE)：包含预览图像的ComfyUI IMAGE张量。处理多个DCI图像时，以批次格式输出多个预览图像

**节点功能特性：**
- **图像预览**：直接在节点界面中显示处理后的图像
- **智能背景显示**：支持透明、白色、黑色和棋盘格背景，便于查看透明图像
- **简洁界面**：专注于图像显示，不显示复杂的调试信息

**多数据处理：**
- **单个输入**：处理一个DCI图像，生成一个预览图像
- **多个输入**：处理多个DCI图像，生成对应的预览图像
- **独立处理**：每个DCI图像独立处理，生成单独的预览图像
- **批次输出**：所有预览图像合并为单个IMAGE张量，供下游处理

**使用场景：**
- 快速预览DCI图像的最终效果
- 验证图像背景处理效果
- 检查图像质量和显示效果
- 在工作流程中进行图像效果确认

#### 6. Drop Shadow（投影效果）
**节点类别**：`DCI/Effects`
**功能描述**：为图像应用投影效果，类似于CSS的drop-shadow滤镜。支持所有标准投影参数，包括偏移、模糊、扩散、颜色和透明度。自动处理画布扩展，提供跨平台兼容性。

**必需输入参数：**
- **`image`** (IMAGE)：要应用阴影效果的ComfyUI图像张量

**可选输入参数：**

*阴影位置：*
- **`offset_x`** (INT)：水平阴影偏移（-100到100像素），默认4
- **`offset_y`** (INT)：垂直阴影偏移（-100到100像素），默认4

*阴影外观：*
- **`blur_radius`** (INT)：阴影模糊半径（0-100像素），默认8
- **`spread_radius`** (INT)：阴影扩散半径（-50到50像素），默认0
  - 正值扩展阴影
  - 负值收缩阴影

*阴影颜色（RGBA）：*
- **`shadow_color_r`** (INT)：阴影红色分量（0-255），默认0
- **`shadow_color_g`** (INT)：阴影绿色分量（0-255），默认0
- **`shadow_color_b`** (INT)：阴影蓝色分量（0-255），默认0
- **`shadow_opacity`** (FLOAT)：阴影透明度（0.0-1.0），默认0.5

*画布选项：*
- **`auto_expand_canvas`** (BOOLEAN)：自动扩展画布以适应阴影，默认True
- **`canvas_padding`** (INT)：额外画布填充（0-200像素），默认20

**输出：**
- **`image`** (IMAGE)：应用了投影效果的图像

**CSS兼容性示例：**
```css
/* CSS: drop-shadow(4px 4px 8px rgba(0,0,0,0.5)) */
/* 节点: offset_x=4, offset_y=4, blur_radius=8, shadow_color=(0,0,0), shadow_opacity=0.5 */

/* CSS: drop-shadow(-2px -2px 6px rgba(255,0,0,0.7)) */
/* 节点: offset_x=-2, offset_y=-2, blur_radius=6, shadow_color=(255,0,0), shadow_opacity=0.7 */
```

**技术特性：**
- **纯Python实现**：无外部依赖，使用PIL和numpy
- **Alpha通道支持**：正确处理透明图像并从alpha遮罩创建阴影
- **扩散效果**：支持正值（扩展）和负值（收缩）扩散值
- **跨平台**：在Windows、Linux和macOS上工作
- **性能优化**：高效的阴影生成，可选scipy加速
- **画布管理**：智能画布尺寸调整以适应阴影效果

#### 7. Binary File Loader（二进制文件加载器）
**节点类别**：`DCI/Files`
**功能描述**：从文件系统加载二进制文件，专为处理 DCI 图标文件等二进制数据设计。

**可选输入参数：**
- **`file_path`** (STRING)：要加载的文件路径，默认空字符串

**输出：**
- **`binary_data`** (BINARY_DATA)：文件的二进制内容（bytes 类型）
- **`file_path`** (STRING)：加载文件的完整路径

#### 7.1. Directory Loader（目录加载器）
**节点类别**：`DCI/Files`
**功能描述**：批量加载目录中的多个二进制文件，支持过滤条件和递归搜索功能。使用广度优先遍历确保文件顺序的一致性。**新功能**：自动识别和解码图像文件，提供独立的图像输出，可直接用于ComfyUI工作流。

**必需输入参数：**
- **`directory_path`** (STRING)：要扫描的目录路径，默认空字符串
- **`file_filter`** (STRING)：文件过滤模式，支持通配符（如"*.dci"、"*.png,*.jpg"），默认"*.dci"
- **`include_subdirectories`** (BOOLEAN)：是否包含子目录搜索，默认True

**输出：**
- **`binary_data_list`** (BINARY_DATA_LIST)：加载文件的二进制数据列表
- **`relative_paths`** (STRING_LIST)：相对文件路径列表（相对于指定目录）
- **`image_list`** (IMAGE)：**新增** - 解码后的图像批次张量（未找到图像时为None）
- **`image_relative_paths`** (STRING_LIST)：**新增** - 解码图像的相对路径列表

**功能特性：**
- **通配符过滤**：支持多种模式，用逗号分隔（如"*.dci,*.png"）
- **递归搜索**：广度优先目录遍历，确保顺序一致性
- **路径规范化**：自动路径规范化和尾部斜杠处理
- **数据一致性**：二进制数据列表和路径列表保持完美的顺序匹配
- **错误容错**：即使个别文件加载失败也会继续处理
- **跨平台支持**：在Windows、Linux和macOS上正确处理路径
- **🆕 自动图像识别**：根据扩展名识别图像文件（.png、.jpg、.jpeg、.bmp、.gif、.tiff、.webp、.ico）
- **🆕 图像解码**：自动将识别的图像解码为ComfyUI IMAGE格式（RGB，0-1范围）
- **🆕 双输出系统**：同时提供二进制数据（所有文件）和解码图像（仅图像文件）
- **🆕 格式转换**：处理各种图像格式和颜色模式（RGBA→RGB，灰度→RGB）

**使用示例：**
- 加载所有DCI文件：`directory_path="/path/to/icons", file_filter="*.dci", include_subdirectories=True`
- 仅加载图像文件：`directory_path="/path/to/images", file_filter="*.png,*.jpg,*.webp", include_subdirectories=False`
- 加载所有文件：`directory_path="/path/to/data", file_filter="*", include_subdirectories=True`
- **🆕 图像工作流**：将`image_list`输出直接连接到图像处理节点，实现自动图像处理

**使用场景：**
- **批量DCI文件处理**：一次性加载目录中的所有DCI文件进行批量分析
- **图标库管理**：扫描图标目录，获取所有图标文件的列表和内容
- **文件批量转换**：配合其他节点实现批量文件格式转换
- **目录内容分析**：分析目录结构和文件分布情况
- **工作流自动化**：在自动化工作流中批量处理文件

#### 7.2. Deb Packager（Deb 打包器）
**节点类别**：`DCI/Files`
**功能描述**：创建Debian软件包，支持基于现有deb包扩展或从头创建，具有文件过滤、目录扫描、智能包信息管理和自动版本递增功能。生成的deb包直接保存到指定目录，文件名按照标准格式自动生成。

**必需输入参数：**
- **`local_directory`** (STRING)：本地目录路径，要扫描和打包的文件所在目录
- **`file_filter`** (STRING)：文件过滤模式，支持通配符（如"*.dci"、"*.png,*.jpg"），默认"*.dci"
- **`include_subdirectories`** (BOOLEAN)：是否包含子目录搜索，默认True
- **`install_target_path`** (STRING)：安装目标路径，deb包内的目标安装路径，默认"/usr/share/dsg/icons"
- **`output_directory`** (STRING)：输出目录，deb包保存目录，默认为ComfyUI输出目录

**可选输入参数：**
- **`base_deb_path`** (STRING)：基础deb包路径，用作模板的现有deb包文件路径
- **`package_name`** (STRING)：包名，如果未指定且有基础包则复用基础包信息
- **`package_version`** (STRING)：包版本，如果未指定且有基础包则自动在基础版本上+1
- **`maintainer_name`** (STRING)：打包人姓名
- **`maintainer_email`** (STRING)：打包人邮箱
- **`package_description`** (STRING)：软件包描述信息，支持多行输入

**输出：**
- **`saved_deb_path`** (STRING)：保存成功时为完整deb包路径，失败时为错误信息
- **`file_list`** (STRING_LIST)：deb包内所有文件的路径列表（包括control.tar.*和data.tar.*中的所有文件）

**功能特性：**

*智能版本管理：*
- **自动版本递增**：基于基础deb包时，自动将版本号最后一位+1（如1.1.8→1.1.9）
- **版本格式支持**：支持标准版本格式（1.2.3、1.2.3-4、1.0.0+build1等）
- **智能解析**：自动识别版本号中的数字部分进行递增

*文件名和路径管理：*
- **标准文件名**：自动生成标准格式文件名（包名_版本号_架构.deb）
- **输出目录控制**：支持自定义输出目录，默认使用ComfyUI输出目录
- **目录自动创建**：输出目录不存在时自动创建

*基础包支持：*
- **智能继承**：基于现有deb包创建新包，自动继承包信息和依赖关系
- **控制信息复用**：自动复用基础包的维护者、依赖、架构等信息
- **简化配置**：基于基础包时，大部分参数可留空自动继承

*文件处理：*
- **通配符过滤**：支持多种模式，用逗号分隔（如"*.dci,*.png"）
- **递归搜索**：广度优先目录遍历，确保顺序一致性
- **目录结构保持**：自动保持子目录的目录结构关系
- **路径规范化**：自动处理跨平台路径分隔符

*deb格式支持：*
- **标准格式**：完全符合Debian包格式规范
- **压缩支持**：支持gzip、xz、bz2等多种压缩格式
- **控制文件**：自动生成标准的control文件和包结构
- **dpkg兼容**：生成的deb包可用dpkg-deb命令验证和安装
- **跨平台支持**：所有平台均使用纯Python ar实现，无需外部依赖

**使用示例：**
- 从头创建DCI图标包：`local_directory="/path/to/icons", file_filter="*.dci", output_directory="/tmp/output", package_name="my-icons", package_version="1.0.0"`
- 基于现有包自动递增版本：`base_deb_path="/path/to/base.deb", local_directory="/path/to/new/icons", output_directory="/tmp/output"`
- 指定新版本号：`base_deb_path="/path/to/base.deb", local_directory="/path/to/icons", package_version="2.0.0", output_directory="/tmp/output"`

**使用场景：**
- **DCI图标包分发**：将DCI图标文件打包成标准的Debian软件包，直接保存到指定目录
- **系统集成**：创建可通过apt安装的图标包，支持标准的deb包管理
- **版本管理**：基于现有包创建新版本，自动版本递增，简化版本控制
- **批量部署**：在多个系统间标准化部署图标资源，文件名格式统一
- **依赖管理**：利用deb包的依赖系统管理图标包关系，继承现有依赖配置
- **开发测试**：快速生成测试用deb包，可用dpkg-deb命令验证包结构

#### 7.3. Deb Loader（Deb 加载器）
**节点类别**：`DCI/Files`
**功能描述**：从Debian软件包（.deb文件）中提取和加载文件，支持文件过滤功能。解析deb包内的control.tar.*和data.tar.*归档文件，提取符合条件的文件。**新功能**：自动识别和解码deb包中的图像文件，提供独立的图像输出，可直接用于ComfyUI工作流。

**必需输入参数：**
- **`deb_file_path`** (STRING)：要解析的.deb文件路径，默认空字符串
- **`file_filter`** (STRING)：文件过滤模式，支持通配符（如"*.dci"、"*.png,*.jpg"），默认"*.dci"

**输出：**
- **`binary_data_list`** (BINARY_DATA_LIST)：提取文件的二进制数据列表
- **`relative_paths`** (STRING_LIST)：deb包内文件的相对路径列表
- **`image_list`** (IMAGE)：**新增** - 解码后的图像批次张量（未找到图像时为None）
- **`image_relative_paths`** (STRING_LIST)：**新增** - 解码图像的相对路径列表

**功能特性：**

*deb包解析：*
- **纯Python实现**：使用纯Python解析ar归档格式，无需外部命令
- **多归档支持**：处理control.tar.*和data.tar.*两个归档文件
- **压缩格式支持**：处理.gz、.xz、.bz2和未压缩的tar归档文件
- **通配符过滤**：支持多种模式，用逗号分隔（如"*.dci,*.png"）
- **路径清理**：自动移除提取路径中的前导"./"
- **错误恢复**：即使个别文件提取失败也继续处理
- **跨平台支持**：Linux、Windows、macOS等所有平台均支持
- **🆕 自动图像识别**：根据扩展名识别图像文件（.png、.jpg、.jpeg、.bmp、.gif、.tiff、.webp、.ico）
- **🆕 图像解码**：自动将识别的图像解码为ComfyUI IMAGE格式（RGB，0-1范围）
- **🆕 双输出系统**：同时提供二进制数据（所有文件）和解码图像（仅图像文件）
- **🆕 格式转换**：处理各种图像格式和颜色模式（RGBA→RGB，灰度→RGB）

*技术细节：*
- **提取过程**：使用临时目录进行安全提取
- **归档检测**：根据文件扩展名自动检测压缩格式
- **内存高效**：在内存中处理文件，不创建临时文件
- **路径规范化**：确保跨平台的路径格式一致性

**使用示例：**
- 从deb包提取DCI文件：`deb_file_path="/path/to/package.deb", file_filter="*.dci"`
- 从deb包提取图像文件：`deb_file_path="/path/to/icons.deb", file_filter="*.png,*.svg"`
- 从deb包提取所有文件：`deb_file_path="/path/to/data.deb", file_filter="*"`
- **🆕 图像工作流**：将`image_list`输出直接连接到图像处理节点，实现自动图像处理

**使用场景：**
- **DCI图标包分析**：从已安装或下载的deb包中提取DCI图标文件
- **包内容检查**：检查deb包内包含的文件和内容
- **文件提取**：从deb包中提取特定类型的文件进行处理
- **逆向工程**：分析现有deb包的文件结构和内容
- **批量处理**：从多个deb包中批量提取文件进行分析

**依赖要求：**
- **系统要求**：无需外部依赖，完全使用Python标准库实现
- **跨平台支持**：所有平台均使用纯Python实现，无需安装额外工具
- **Python模块**：使用标准库模块（tarfile、tempfile、os、struct）
- **路径处理**：增强的跨平台路径规范化，支持在Linux/Unix系统上处理Windows路径

#### 8. Binary File Saver（二进制文件保存器）
**节点类别**：`DCI/Files`
**功能描述**：将二进制数据保存到文件系统，具有高级文件名处理、前缀后缀支持和跨平台路径处理功能。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的二进制数据
- **`file_name`** (STRING)：目标文件名或路径，默认"binary_file"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录。如果指定的目录不存在，将自动创建。支持以反斜杠结尾的路径，自动规范化路径分隔符
- **`filename_prefix`** (STRING)：文件名前缀，默认空字符串
- **`filename_suffix`** (STRING)：文件名后缀，默认空字符串
- **`allow_overwrite`** (BOOLEAN)：允许覆盖现有文件，默认False

**输出：**
- **`saved_path`** (STRING)：保存成功时为完整文件路径，保存失败时为详细错误信息（与DCI文件保存器行为保持一致）

**高级文件名处理功能：**

*路径处理：*
- **跨平台兼容**：自动处理Windows（`\`）和Linux（`/`）路径分隔符
- **路径提取**：从完整路径中自动提取文件名部分
- **示例**：`/home/user/data.txt` → `data.txt`，`C:\Users\test\file.bin` → `file.bin`

*前缀后缀支持：*
- **灵活命名**：支持为文件名添加自定义前缀和后缀
- **扩展名保持**：应用前缀后缀时自动保持文件扩展名
- **示例**：输入`data.txt`，前缀`backup_`，后缀`_v2` → `backup_data_v2.txt`

*特殊情况处理：*
- **空输入**：输入为空时使用默认文件名`binary_file`
- **纯路径**：输入只是路径分隔符时使用默认文件名
- **无扩展名**：正确处理没有扩展名的文件
- **文件名清理**：移除文件名中的无效字符以确保文件系统兼容性

**使用示例：**
- 基本保存：`file_name="data.bin", output_directory="/path/to/output"`
- 添加前缀：`file_name="report.pdf", filename_prefix="backup_"`
- 添加后缀：`file_name="image.png", filename_suffix="_processed"`
- 完整自定义：`file_name="/tmp/data.txt", filename_prefix="new_", filename_suffix="_v2"`

**技术特性：**
- **路径安全**：自动路径规范化和无效字符移除
- **目录创建**：如果输出目录不存在则自动创建
- **覆盖保护**：通过明确控制防止意外文件覆盖
- **错误处理**：全面的错误报告用于调试
- **跨平台**：在Windows、Linux和macOS上保持一致工作

#### 8. Base64 Decoder（Base64 解码器）
**节点类别**：`DCI/Files`
**功能描述**：从base64编码字符串解码二进制数据，支持多行输入处理大型数据集。

**必需输入参数：**
- **`base64_data`** (STRING)：Base64编码的字符串数据（支持多行输入）

**输出：**
- **`binary_data`** (BINARY_DATA)：解码后的二进制数据

**功能特性：**
- **多行支持**：处理包含换行符和空格的base64字符串
- **错误处理**：优雅处理无效的base64数据
- **大数据支持**：高效处理大型base64编码文件

#### 9. Base64 Encoder（Base64 编码器）
**节点类别**：`DCI/Files`
**功能描述**：将二进制数据编码为base64字符串，用于数据交换和存储。这是一个纯转换节点，不涉及文件操作。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要编码的二进制数据

**输出：**
- **`base64_data`** (STRING)：Base64编码字符串

**功能特性：**
- **纯转换**：只执行编码操作，无文件操作
- **高效处理**：直接的二进制到base64转换
- **链式友好**：输出可直接被其他节点使用或单独保存

#### 10. Binary File Saver（二进制文件保存器 - 增强版）
**节点类别**：`DCI/Files`
**功能描述**：将二进制数据保存到文件系统，支持自定义输出路径和目录，具有覆盖保护功能。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的二进制数据
- **`file_name`** (STRING)：目标文件名，默认"binary_file"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录。如果指定的目录不存在，将自动创建。支持以反斜杠结尾的路径，自动规范化路径分隔符
- **`allow_overwrite`** (BOOLEAN)：允许覆盖现有文件，默认False

**输出：**
- **`saved_path`** (STRING)：保存成功时为实际保存的文件路径，保存失败时为详细错误信息

#### 11. DCI File Saver（DCI 文件保存器 - 增强版）
**节点类别**：`DCI/Files`
**功能描述**：专门用于保存DCI文件的高级文件保存器，具有智能文件名解析、前缀后缀支持、跨平台路径处理和覆盖保护功能。

**必需输入参数：**
- **`binary_data`** (BINARY_DATA)：要保存的DCI二进制数据
- **`input_filename`** (STRING)：输入文件名或路径，默认"icon.png"

**可选输入参数：**
- **`output_directory`** (STRING)：输出目录，默认使用 ComfyUI 输出目录。如果指定的目录不存在，将自动创建。支持以反斜杠结尾的路径，自动规范化路径分隔符
- **`filename_prefix`** (STRING)：文件名前缀，默认空字符串
- **`filename_suffix`** (STRING)：文件名后缀，默认空字符串
- **`allow_overwrite`** (BOOLEAN)：允许覆盖现有文件，默认False

**输出：**
- **`saved_filename`** (STRING)：保存后的文件名（不含路径），保存失败时为空字符串
- **`saved_full_path`** (STRING)：保存成功时为完整文件路径，保存失败时为详细错误信息

**智能文件名解析功能：**

*路径处理：*
- **跨平台兼容**：自动处理Windows（`\`）和Linux（`/`）路径分隔符
- **路径提取**：从完整路径中自动提取文件名部分
- **示例**：`/home/user/icon.png` → `icon.dci`，`C:\Users\test\image.webp` → `image.dci`

*扩展名处理：*
- **智能替换**：自动识别并移除常见图像扩展名（webp、png、jpg、jpeg、apng、gif、bmp、tiff、tif）
- **大小写不敏感**：支持大写和小写扩展名（如PNG、jpg、JPEG等）
- **DCI扩展名**：自动添加`.dci`扩展名
- **示例**：`a.png` → `a.dci`，`icon.WEBP` → `icon.dci`

*前缀后缀功能：*
- **灵活命名**：支持为文件名添加自定义前缀和后缀
- **示例**：输入`a.png`，前缀`prefix-`，后缀`-suffix` → `prefix-a-suffix.dci`
- **空值处理**：前缀或后缀为空时自动忽略

*特殊情况处理：*
- **空输入**：输入为空时使用默认文件名`icon.dci`
- **纯路径**：输入只是路径分隔符时使用默认文件名
- **无扩展名**：没有扩展名的文件名直接添加`.dci`扩展名
- **非图像扩展名**：保留非图像扩展名，如`file.txt` → `file.txt.dci`

**使用场景：**
- **批量DCI文件保存**：根据原始图像文件名自动生成对应的DCI文件名
- **工作流程自动化**：在图像处理工作流中自动保存DCI文件
- **文件名标准化**：统一DCI文件的命名规范，添加项目前缀或版本后缀
- **跨平台开发**：在不同操作系统间保持一致的文件名处理逻辑

**覆盖保护功能：**
- **安全默认**：默认不允许覆盖现有文件，防止意外数据丢失
- **明确控制**：通过`allow_overwrite`参数明确控制覆盖行为
- **友好提示**：当文件已存在且不允许覆盖时，提供清晰的错误信息
- **工作流安全**：在批量处理工作流中避免意外覆盖重要文件

**技术特性：**
- **路径安全**：自动处理路径分隔符，避免跨平台兼容性问题
- **文件名清理**：确保生成的文件名符合文件系统要求
- **错误处理**：对无效输入提供友好的默认处理
- **双输出设计**：同时提供文件名和完整路径，满足不同使用需求
- **覆盖保护**：防止意外覆盖现有文件，提高工作流安全性

#### 9. DCI Analysis（DCI 分析）
**节点类别**：`DCI/Analysis`
**功能描述**：以树状结构详细分析DCI文件的内部组织结构和元信息，输出文本格式的分析结果，专门用于分析和调试DCI文件内容。

**必需输入参数：**
- **`dci_binary_data`** (BINARY_DATA)：DCI 文件的二进制数据

**节点功能特性：**

*树状结构展示：*
```
└── 32
    └── normal.dark
        └── 1
            └── 1.0.0.0.0.0.0.0.0.0.png
                    [缩放: 1x]
                    [优先级: 1]
                    [调色板: 前景色]
```

*智能路径解析：*
- **目录结构解析**：正确解析DCI文件内部的目录结构（size/state.tone/scale）
- **文件名分离**：智能处理DCIReader返回的独立path和filename字段
- **路径组件识别**：准确识别尺寸、状态.色调、缩放因子等路径组件
- **兼容性处理**：适配DCIReader的数据结构，确保正确的树形结构生成

*智能元数据解析：*
- **图层优先级**：解析文件名中的优先级信息
- **外边框设置**：识别外边框像素值（如5p表示5像素外边框）
- **调色板类型**：解析调色板设置（无调色板、前景色、背景色、高亮前景色、高亮色）
- **颜色调整参数**：详细解析色调、饱和度、亮度、RGB、透明度调整
- **Alpha8格式识别**：特别标识用于调色板优化的Alpha8格式文件
- **文件名省略支持**：正确解析DCI规范中的简化文件名格式

*显示选项控制：*
- **紧凑模式**：隐藏详细的图层元数据，只显示文件结构
- **文件大小显示**：可选择是否显示每个文件的大小信息
- **图层元数据**：可选择是否显示详细的图层属性解析
- **人性化格式**：文件大小自动格式化为B、KB、MB单位

**输出：**
- **`analysis_text`** (STRING)：包含完整分析结果的文本字符串

**使用场景：**
- **DCI文件分析**：深入了解DCI文件的内部结构和组织方式
- **调试和验证**：验证DCI文件是否按照预期的结构生成
- **规范学习**：通过实际文件了解DCI规范的实现细节
- **文件对比**：比较不同DCI文件的结构差异
- **元数据检查**：验证图层文件名中的元数据是否正确设置
- **性能分析**：查看文件大小分布，优化DCI文件结构

**技术特性：**
- **完整DCI规范支持**：支持DCI 1.1规范的所有特性
- **智能文件名解析**：按照DCI规范解析复杂的图层文件名
- **省略格式兼容**：支持简化文件名和完整文件名格式
- **自然排序**：按照自然顺序排列文件和目录
- **Unicode支持**：正确处理UTF-8编码的文件名
- **错误容错**：对格式不正确的文件名提供友好的错误处理

## 使用示例

### 推荐的新工作流程（使用重构节点）

1. **创建 DCI 图像**：
   - 使用 `DCI Image` 节点将 ComfyUI 图像转换为 DCI 图像数据
   - 设置图标尺寸、状态、色调、缩放因子和格式
   - 可以创建多个不同状态和缩放的图像

2. **组合 DCI 文件**：
   - 使用 `DCI File` 节点将多个 DCI 图像组合成完整的 DCI 文件二进制数据
   - 支持可组合设计：每个节点处理最多4个图像，可串联多个节点处理无限数量图像

3. **预览 DCI 内容**：
   - 使用 `DCI Preview` 节点直接在节点内查看 DCI 文件的内容和元数据
   - 自动显示图像网格和详细的元数据信息

4. **保存 DCI 文件**：
   - 使用 `Binary File Saver` 节点将 DCI 二进制数据保存到磁盘

### 文件操作工作流程

1. **加载现有 DCI 文件**：
   - 使用 `Binary File Loader` 加载现有的 DCI 文件

2. **预览和分析**：
   - 将加载的二进制数据连接到 `DCI Preview` 节点进行预览

### 调试工作流程

1. **预览单个 DCI 图像**：
   - 使用 `DCI Image Preview` 节点快速查看单个 DCI 图像的最终效果
   - 验证背景色处理效果和图像质量
   - 检查图像的视觉效果

2. **工作流程验证**：
   - 在DCI图像创建后立即预览结果
   - 验证图像处理效果是否符合预期
   - 检查不同背景下的图像显示效果

### 高级用法

- **多状态图标**：为不同的交互状态（normal、hover、pressed、disabled）创建不同的图像
- **多色调支持**：为浅色和深色主题创建不同的色调变体
- **多缩放因子**：为不同的显示密度创建多种尺寸
- **批量处理**：一次性创建包含多个图像的完整 DCI 文件
- **背景色处理**：使用新的背景色选项解决透明图像的显示问题

## 工作流程示例

### 基础工作流程
```
LoadImage → DCI Image → DCI File → DCI Preview
```

### 多图像工作流程
```
LoadImage (normal) → DCI Image (normal) ──┐
LoadImage (hover)  → DCI Image (hover)  ──┼─→ DCI File ──→ Binary File Saver
LoadImage (pressed)→ DCI Image (pressed)──┘           └─→ DCI Preview
```

### 文件处理工作流程
```
Binary File Loader → DCI Preview
                  └→ Binary File Saver
```

### 预览工作流程
```
LoadImage → DCI Image → DCI Image Preview
                     └→ DCI File → DCI Preview
```

## DCI 格式规范

此扩展根据桌面规范实现 DCI 格式：
- **魔术头**："DCI\0"
- **版本**：1
- **目录结构**：`size/state.tone/scale/layer.format`
- **支持的状态**：normal、disabled、hover、pressed
- **支持的色调**：light、dark
- **支持的格式**：WebP、PNG、JPEG

## 技术细节

### 预览系统优化

#### 动态文本宽度计算
DCI Preview 节点现在支持智能的文本宽度计算，解决了长文件路径显示不全的问题：

**主要改进**：
- **动态宽度计算**：根据实际文本内容计算所需的最大宽度，而不是固定使用图像尺寸
- **文本换行支持**：当文本仍然过长时，自动进行智能换行处理
- **路径优化显示**：特别优化了长文件路径的显示效果
- **字体测量**：使用实际字体进行精确的文本宽度测量
- **自适应布局**：预览网格的单元格宽度自动适应文本内容需求

**技术实现**：
```python
# 计算所需的最大文本宽度
max_text_width = self._calculate_max_text_width(sorted_images)

# 单元格宽度同时考虑图像和文本需求
cell_width = max(max_image_size + margin * 2, max_text_width + margin * 2)

# 智能文本换行处理
wrapped_lines = self._wrap_text(line, text_width, font, draw)
```

**用户体验提升**：
- ✅ 长文件路径完整显示，不再被截断
- ✅ 自动换行保持可读性
- ✅ 预览网格自动调整尺寸
- ✅ 保持原有的视觉布局和美观性

#### 节点界面优化
DCI Image 节点现在采用更清晰的参数组织方式，提升用户体验：

**主要改进**：
- **核心参数前置**：将最常用的参数（icon_size、icon_state、scale、tone_type）放在必需参数区域
- **高级参数分组**：所有高级选项使用 `adv_` 前缀标识，便于识别和管理
- **简化界面**：默认情况下只显示核心参数，减少界面复杂度
- **逻辑分组**：高级参数按功能分为背景色设置、图层设置、颜色调整三个逻辑组

**参数组织结构**：
```
必需参数：
├── image (图像输入)
├── icon_size (图标尺寸)
├── icon_state (图标状态)
├── scale (缩放因子)
└── tone_type (色调类型)

可选参数：
├── image_format (图像格式)
└── 高级设置 (adv_ 前缀)
    ├── 背景色设置
    ├── 图层属性
    └── 颜色调整
```

**使用建议**：
- 🎯 **新用户**：只需关注必需参数和 image_format，即可创建基本的DCI图像
- 🎯 **高级用户**：使用 adv_ 前缀参数进行精细控制和专业定制
- 🎯 **批量处理**：核心参数的简化使得批量创建图标更加高效

### 输出类型一致性
所有节点的LIST类型输出现在保持一致的行为：

**主要改进**：
- **空列表输出**：当没有数据时，所有LIST类型输出（BINARY_DATA_LIST、STRING_LIST）返回空列表`[]`而不是`None`
- **工作流兼容性**：确保下游节点能够正确处理空列表，避免因`None`值导致的工作流中断
- **类型安全**：保持输出类型的一致性，提高节点间的互操作性

**影响的节点**：
- **目录加载器**：`binary_data_list`、`relative_paths`、`image_relative_paths`输出
- **Deb加载器**：`binary_data_list`、`relative_paths`、`image_relative_paths`输出
- **Deb打包器**：`file_list`输出

**技术实现**：
```python
# 修复前（可能返回None）
return ([], [], None, None)

# 修复后（始终返回列表）
return ([], [], [], [])
```

### DCI 文件格式实现
扩展实现了完整的 DCI 规范：

**二进制结构**：
```
DCI 头部（8 字节）：
├── 魔术（4 字节）：'DCI\0'
├── 版本（1 字节）：1
└── 文件计数（3 字节）：文件数量

文件条目（每个文件 72+ 字节）：
├── 文件类型（1 字节）：1=文件，2=目录
├── 文件名（63 字节）：以空字符结尾的 UTF-8
├── 内容大小（8 字节）：小端序 uint64
└── 内容（可变）：文件数据或目录内容
```

**目录结构**：
```
size/                    # 图标尺寸（16、32、64、128、256、512、1024）
└── state.tone/          # state: normal|disabled|hover|pressed
    └── scale/           # 缩放因子（1、1.25、1.5、2 等，支持小数）
        └── layer.format # priority.padding.palette.hue.saturation.brightness.red.green.blue.alpha.format
```

## 依赖项

- **Pillow**：图像处理和操作
- **NumPy**：ComfyUI 张量转换的数组操作
- **PyTorch**：ComfyUI 张量兼容性

## 故障排除

如果在 ComfyUI 中看不到 DCI 节点：

1. 确保已正确安装所有依赖项
2. 重启 ComfyUI
3. 检查 ComfyUI 控制台是否有错误信息
4. 确保扩展文件夹位于正确的 `custom_nodes` 目录中

### 菜单异常问题

如果在ComfyUI菜单中看到异常项目（如"group nodes>workflow"/"DCI结构预览"等不应该存在的项目）：

1. **重启ComfyUI**：这通常能解决节点缓存问题
2. **清除缓存**：删除ComfyUI的缓存文件（通常在用户目录下的`.comfyui`文件夹中）
3. **检查扩展冲突**：确保没有其他扩展与DCI扩展产生冲突
4. **重新安装扩展**：如果问题持续，可以尝试重新安装DCI扩展

### 目录加载器节点找不到

如果找不到"目录加载器"（Directory Loader）节点：

1. 确保使用的是最新版本的DCI扩展
2. 在ComfyUI菜单中查找 `DCI/Files` 分类下的"目录加载器"节点
3. 重启ComfyUI以确保节点注册生效

### 已知问题和修复

#### DCIAnalysis 节点输出为空（已修复）
**问题描述**：DCIAnalysis 节点在某些情况下可能输出空字符串，无法显示DCI文件的树形结构。

**原因**：节点期望的路径格式与DCIReader实际返回的数据结构不匹配。DCIReader将目录路径和文件名分别存储在`path`和`filename`字段中，而不是组合在一起。

**修复方案**：
- 更新路径解析逻辑，正确处理独立的`path`和`filename`字段
- 调整路径组件解析，期望3个部分（size/state.tone/scale）而不是4个
- 确保与DCIReader的数据结构完全兼容

**修复状态**：✅ 已在最新版本中修复

**验证方法**：
```python
# 测试DCIAnalysis节点是否正常工作
from py.nodes.structure_node import DCIAnalysis
analysis_node = DCIAnalysis()
result = analysis_node._execute(dci_binary_data)
# 应该返回包含树形结构的非空字符串
```

## 贡献

欢迎贡献！请提交 Pull Request 或创建 Issue 来报告问题或建议新功能。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
