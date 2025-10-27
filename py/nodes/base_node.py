import traceback

class BaseNode:
    """Base class for all DCI nodes"""

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for the node"""
        return {"required": {}, "optional": {}}

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    CATEGORY = "DCI"
    OUTPUT_NODE = False

    def execute(self, *args, **kwargs):
        """Execute the node's main function"""
        try:
            return self._execute(*args, **kwargs)
        except Exception as e:
            try:
                print(f"Error in {self.__class__.__name__}: {str(e)}")
                traceback.print_exc()
            except Exception:
                # If even printing fails, just continue silently
                pass
            return self._handle_error(e)

    def _execute(self, *args, **kwargs):
        """Implement this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute method")

    def _handle_error(self, error):
        """Handle errors and return appropriate output"""
        if self.OUTPUT_NODE:
            return {"ui": {"text": [f"Error: {str(error)}"]}}
        return tuple(None for _ in self.RETURN_TYPES)
