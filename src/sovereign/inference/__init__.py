"""
SOVEREIGN Inference Module.

Contains the memory-native inference wrapper that makes
memory invisible to the LLM but impossible to bypass.
"""

from sovereign.inference.memory_native import MemoryNativeInference


__all__ = ["MemoryNativeInference"]
