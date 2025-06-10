# Examples Directory

This directory contains example workflows and usage demonstrations for the ComfyUI DCI Extension.

## Example Files

### Workflow Examples
- **example_workflow.json**: Basic DCI export workflow
- **example_dci_preview_workflow.json**: DCI preview and analysis workflow

### Code Examples
- **decimal_scale_example.py**: Demonstrates decimal scale factors (1.25x, 1.5x, etc.) for high-DPI displays

## Usage

### Loading Examples in ComfyUI

1. Open ComfyUI
2. Use "Load" button or drag and drop the JSON files
3. The workflow will be loaded with all necessary nodes
4. Adjust input images and parameters as needed
5. Execute the workflow

### Example Workflows

#### Basic DCI Export (`example_workflow.json`)
Demonstrates:
- Loading an image
- Converting to DCI format
- Setting icon parameters
- Exporting DCI file

#### DCI Preview Workflow (`example_dci_preview_workflow.json`)
Demonstrates:
- Loading existing DCI files
- Generating visual previews
- Extracting metadata
- Analyzing DCI structure

#### Decimal Scale Example (`decimal_scale_example.py`)
Demonstrates:
- Using decimal scale factors like 1.25x, 1.5x for high-DPI displays
- Creating DCI files with mixed integer and decimal scales
- Benefits of decimal scaling for modern display technologies
- Programmatic DCI creation with the Python API

## Customization

You can modify these examples to:
- Use different input images
- Change export parameters
- Add additional processing steps
- Combine with other ComfyUI nodes

## Requirements

These examples require:
- ComfyUI with DCI extension installed
- Input images (for export workflows)
- Existing DCI files (for preview workflows)

## Tips

- Start with the basic workflow to understand the fundamentals
- Use the preview workflow to analyze existing DCI files
- Combine workflows for complete DCI processing pipelines
- Experiment with different parameters to see their effects
