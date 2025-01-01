"""
Configuration for smol_loop.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .smol_loop_models import APIProvider

DEFAULT_TIMEOUT = 30.0
DEFAULT_MODEL = {
    APIProvider.ANTHROPIC: "claude-3-opus-20240229",
    APIProvider.OPENAI: "gpt-4-turbo-preview",
}

DEFAULT_ENDPOINTS = {
    APIProvider.ANTHROPIC: "https://api.anthropic.com/v1",
    APIProvider.OPENAI: "https://api.openai.com/v1",
}


@dataclass
class SmolLoopConfig:
    """Configuration for smol_loop execution."""

    api_key: str
    provider: APIProvider = APIProvider.ANTHROPIC
    model: Optional[str] = None
    endpoint_url: Optional[str] = None
    timeout: float = DEFAULT_TIMEOUT
    cleanup: bool = True
    output_dir: Path = field(default_factory=lambda: Path("/tmp"))
    max_retries: int = 3
    base_chaos_level: int = 0

    def __post_init__(self):
        """Post-initialization processing."""
        if not self.model:
            self.model = DEFAULT_MODEL[self.provider]
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if not self.endpoint_url:
            self.endpoint_url = DEFAULT_ENDPOINTS[self.provider]

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return self.provider.name.lower()


@dataclass
class ImprovementStrategy:
    """Strategy for improving code generation."""

    base_chaos_level: int = 0
    complexity_target: float = 0.7
    creativity_target: float = 0.8
    max_retries: int = 5
    adaptation_rate: float = 0.1
    min_success_rate: float = 0.8
    batch_size: int = 4
