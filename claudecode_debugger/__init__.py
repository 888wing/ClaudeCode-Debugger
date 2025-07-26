"""ClaudeCode-Debugger: Smart debug prompt generator for Claude Code"""

__version__ = "0.1.0"
__author__ = "888wing"

from .core.detector import ErrorDetector
from .core.generator import PromptGenerator

__all__ = ["ErrorDetector", "PromptGenerator"]
