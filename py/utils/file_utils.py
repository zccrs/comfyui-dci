import os
import tempfile
from io import BytesIO

def get_output_directory():
    """Get the output directory for saving files"""
    try:
        import folder_paths
        output_dir = folder_paths.get_output_directory()
    except ImportError:
        output_dir = tempfile.gettempdir()
    except Exception as e:
        print(f"Error accessing ComfyUI output directory: {e}")
        output_dir = tempfile.gettempdir()

    return output_dir

def clean_file_name(file_name):
    """Clean up file name by removing path separators"""
    clean_name = os.path.basename(file_name) if file_name else "binary_file"
    return clean_name if clean_name else "binary_file"

def ensure_directory(directory_path):
    """Ensure directory exists, create if not"""
    if directory_path:
        os.makedirs(directory_path, exist_ok=True)
        return True
    return False

def save_binary_data(binary_data, file_path):
    """Save binary data to file"""
    try:
        with open(file_path, 'wb') as f:
            bytes_written = f.write(binary_data)
        return bytes_written
    except Exception as e:
        print(f"Error saving binary data: {e}")
        return 0

def load_binary_data(file_path):
    """Load binary data from file"""
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading binary data: {e}")
        return None
