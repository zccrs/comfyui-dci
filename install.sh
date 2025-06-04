#!/bin/bash

# ComfyUI DCI Extension Installation Script
# This script installs the required dependencies for the DCI extension

echo "Installing ComfyUI DCI Extension dependencies..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"
else
    echo "Warning: No virtual environment detected. Consider using one."
fi

# Check if python is available
if ! command -v python &> /dev/null; then
    echo "Error: python is not installed or not in PATH"
    exit 1
fi

# Install dependencies using the recommended method
echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
else
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Check if ComfyUI is available
if [ -d "../../../ComfyUI" ]; then
    echo "ComfyUI installation detected"
elif [ -d "../../ComfyUI" ]; then
    echo "ComfyUI installation detected"
else
    echo "Warning: ComfyUI installation not found in expected locations"
    echo "Make sure this extension is installed in ComfyUI/custom_nodes/"
fi

echo ""
echo "Installation completed!"
echo ""
echo "To use the DCI extension:"
echo "1. Restart ComfyUI"
echo "2. Look for DCI nodes in the node menu under 'DCI' category"
echo "3. Check the examples/ directory for sample workflows"
echo ""
echo "For more information, see README.md"
