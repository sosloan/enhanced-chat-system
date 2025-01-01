"""
Data models for smol_loop.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Set up logging
logger = logging.getLogger(__name__)


def _setup_logging():
    """Set up logging with a consistent format."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


_setup_logging()


class ValidationError(Exception):
    """Custom exception for data validation errors."""

    pass


@dataclass(frozen=True)
class CodeMetrics:
    """Metrics for code analysis.

    Attributes:
        complexity: Cyclomatic complexity score
        lines: Number of lines of code
        functions: Number of function definitions
        classes: Number of class definitions
        imports: Number of import statements
        max_depth: Maximum nesting depth
        creativity_score: Measure of code creativity (0.0-1.0)
    """

    complexity: int
    lines: int
    functions: int
    classes: int
    imports: int
    max_depth: int
    creativity_score: float

    def __post_init__(self):
        """Validate metrics after initialization."""
        try:
            self._validate_metrics()
        except ValidationError as e:
            logger.error(f"Invalid metrics: {e}")
            raise

    def _validate_metrics(self) -> None:
        """Validate metric values."""
        if self.complexity < 0:
            raise ValidationError("Complexity cannot be negative")
        if self.lines < 0:
            raise ValidationError("Lines cannot be negative")
        if self.functions < 0:
            raise ValidationError("Functions cannot be negative")
        if self.classes < 0:
            raise ValidationError("Classes cannot be negative")
        if self.imports < 0:
            raise ValidationError("Imports cannot be negative")
        if self.max_depth < 0:
            raise ValidationError("Max depth cannot be negative")
        if not 0.0 <= self.creativity_score <= 1.0:
            raise ValidationError("Creativity score must be between 0.0 and 1.0")


@dataclass(frozen=True)
class ExecutionResult:
    """Result of code execution.

    Attributes:
        file: Path to the executed file
        output: Standard output from execution
        success: Whether execution was successful
        execution_time: Time taken to execute (seconds)
        error: Error message if execution failed
    """

    file: str
    output: str
    success: bool
    execution_time: float
    error: Optional[str] = None

    def __post_init__(self):
        """Validate execution result after initialization."""
        try:
            self._validate_result()
        except ValidationError as e:
            logger.error(f"Invalid execution result: {e}")
            raise

    def _validate_result(self) -> None:
        """Validate execution result values."""
        if not self.file:
            raise ValidationError("File path cannot be empty")
        if self.execution_time < 0:
            raise ValidationError("Execution time cannot be negative")
        if not self.success and not self.error:
            raise ValidationError("Failed execution must have an error message")


@dataclass(frozen=True)
class FileIndex:
    """Index entry for a code file.

    Attributes:
        path: Path to the file
        task: Description of the task
        chaos_level: Chaos level used for generation
        timestamp: When the file was indexed
        hash: Hash of file contents
        metrics: Code metrics
        success: Whether execution was successful
        execution_time: Time taken to execute
        output: Execution output
        error: Error message if execution failed
    """

    path: Union[str, Path]
    task: str
    chaos_level: float
    timestamp: str
    hash: str
    metrics: CodeMetrics
    success: bool
    execution_time: float
    output: str
    error: Optional[str] = None

    def __post_init__(self):
        """Validate file index after initialization."""
        try:
            self._validate_index()
        except ValidationError as e:
            logger.error(f"Invalid file index: {e}")
            raise

    def _validate_index(self) -> None:
        """Validate index values."""
        if not self.path:
            raise ValidationError("File path cannot be empty")
        if not self.task.strip():
            raise ValidationError("Task description cannot be empty")
        if not 0.0 <= self.chaos_level <= 1.0:
            raise ValidationError("Chaos level must be between 0.0 and 1.0")
        try:
            datetime.fromisoformat(self.timestamp)
        except ValueError:
            raise ValidationError("Invalid timestamp format")
        if not self.hash:
            raise ValidationError("File hash cannot be empty")
        if self.execution_time < 0:
            raise ValidationError("Execution time cannot be negative")
        if not self.success and not self.error:
            raise ValidationError("Failed execution must have an error message")


@dataclass(frozen=True)
class SmolLoopResult:
    """Result of a smol_loop execution.

    Attributes:
        success: Whether execution was successful
        metrics: Execution metrics
        output: Output message
        error: Error message if execution failed
        execution_results: List of individual execution results
    """

    success: bool
    metrics: Dict[str, Any]
    output: str
    error: Optional[str] = None
    execution_results: List[ExecutionResult] = field(default_factory=list)

    def __post_init__(self):
        """Validate smol_loop result after initialization."""
        try:
            self._validate_result()
        except ValidationError as e:
            logger.error(f"Invalid smol_loop result: {e}")
            raise

    def _validate_result(self) -> None:
        """Validate result values."""
        if not isinstance(self.metrics, dict):
            raise ValidationError("Metrics must be a dictionary")
        if not self.output:
            raise ValidationError("Output cannot be empty")
        if not self.success and not self.error:
            raise ValidationError("Failed execution must have an error message")
        if not isinstance(self.execution_results, list):
            raise ValidationError("Execution results must be a list")


@dataclass(frozen=True)
class APIProvider:
    """Provider for API access.

    Attributes:
        name: Name of the API provider
        api_key: API key for authentication
        base_url: Base URL for API endpoints
        rate_limit: Maximum requests per second
        timeout: Request timeout in seconds
    """

    ANTHROPIC = "anthropic"  # Class attribute for Anthropic provider
    OPENAI = "openai"  # Class attribute for OpenAI provider

    name: str
    api_key: str
    base_url: str
    rate_limit: int = 10
    timeout: int = 30

    def __post_init__(self):
        """Validate API provider after initialization."""
        try:
            self._validate_provider()
        except ValidationError as e:
            logger.error(f"Invalid API provider: {e}")
            raise

    def _validate_provider(self) -> None:
        """Validate provider values."""
        if not self.name.strip():
            raise ValidationError("Provider name cannot be empty")
        if not self.api_key.strip():
            raise ValidationError("API key cannot be empty")
        if not self.base_url.strip():
            raise ValidationError("Base URL cannot be empty")
        if self.rate_limit < 1:
            raise ValidationError("Rate limit must be positive")
        if self.timeout < 1:
            raise ValidationError("Timeout must be positive")
