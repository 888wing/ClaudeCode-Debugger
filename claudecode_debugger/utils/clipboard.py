"""Clipboard utilities for ClaudeCode-Debugger."""

import pyperclip


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard.
    
    Args:
        text: Text to copy.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def paste_from_clipboard() -> str:
    """
    Paste text from clipboard.
    
    Returns:
        Text from clipboard or empty string if failed.
    """
    try:
        return pyperclip.paste()
    except Exception:
        return ""