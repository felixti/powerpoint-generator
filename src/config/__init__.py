"""Configuration module for the PowerPoint Generator.

This package contains configuration classes and factory functions for
setting up various components of the PowerPoint generator, including
LLM providers and other external services.
"""

from src.config.llm_config import ChatOpenRouter, create_llm

__all__ = [
    "ChatOpenRouter",
    "create_llm",
]
