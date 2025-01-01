"""
Code indexing and analysis for smol_loop.
"""

import ast
import hashlib
import json
import logging
import random
import statistics
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
import os

from .smol_loop_models import CodeMetrics, FileIndex

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


class MetricsVisitor(ast.NodeVisitor):
    """AST visitor to collect code metrics."""

    def __init__(self):
        """Initialize metrics."""
        self.complexity = 0
        self.functions = 0
        self.classes = 0
        self.imports = 0
        self.max_depth = 0
        self._current_depth = 0

    def visit(self, node: ast.AST) -> None:
        """Visit a node and track depth."""
        self._current_depth += 1
        self.max_depth = max(
            self.max_depth, self._current_depth - 1
        )  # -1 to account for root node
        super().visit(node)
        self._current_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self.functions += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.classes += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        self.imports += len(node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from import statement."""
        self.imports += len(node.names)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop."""
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop."""
        self.complexity += 1
        self.generic_visit(node)


class CodeIndexer:
    """Class for indexing and analyzing code files."""

    def __init__(self, index_file: Optional[Union[str, Path]] = None):
        """Initialize the code indexer."""
        self._index_file = Path(index_file) if index_file else None
        self.index: Dict[str, FileIndex] = {}
        self._metrics_cache: Dict[str, CodeMetrics] = {}
        self._load_index()

    def load_index(self) -> None:
        """Load the index from file."""
        if not self._index_file.exists():
            return

        try:
            with open(self._index_file, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return
                try:
                    self.index = {k: FileIndex(**v) for k, v in data.items()}
                except (TypeError, ValueError):
                    # Invalid data structure
                    self.index = {}
        except json.JSONDecodeError:
            # Invalid JSON
            self.index = {}

    def save_index(self) -> None:
        """Save the index to file."""
        self._index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._index_file, "w") as f:
            json.dump(
                {k: asdict(v) for k, v in self.index.items()},
                f,
                indent=2,
                default=str,
            )

    def analyze_code(self, source: str, is_file: bool = False) -> CodeMetrics:
        """Analyze Python code and return metrics.

        Args:
            source: Either a file path or Python code string
            is_file: Whether source is a file path
        """
        # Generate cache key
        if is_file:
            try:
                with open(source, "r") as f:
                    code = f.read()
                cache_key = f"file:{source}:{hashlib.sha256(code.encode()).hexdigest()}"
            except (IOError, OSError):
                # Return empty metrics for missing/unreadable files
                return CodeMetrics(
                    complexity=0,
                    lines=0,
                    functions=0,
                    classes=0,
                    imports=0,
                    max_depth=0,
                    creativity_score=0.0,
                )
        else:
            code = source
            cache_key = f"code:{hashlib.sha256(code.encode()).hexdigest()}"

        # Check cache
        if cache_key in self._metrics_cache:
            logger.debug(f"Using cached metrics for {cache_key}")
            return self._metrics_cache[cache_key]

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Return empty metrics for invalid syntax
            return CodeMetrics(
                complexity=0,
                lines=0,
                functions=0,
                classes=0,
                imports=0,
                max_depth=0,
                creativity_score=0.0,
            )

        visitor = MetricsVisitor()
        visitor.visit(tree)

        # Calculate lines of code
        lines = len(code.splitlines())

        # Calculate creativity score based on metrics
        creativity_score = min(
            1.0,
            (
                visitor.complexity * 0.2
                + visitor.functions * 0.2
                + visitor.classes * 0.2
                + visitor.imports * 0.2
                + visitor.max_depth * 0.2
            )
            / 10,
        )

        metrics = CodeMetrics(
            complexity=visitor.complexity,
            lines=lines,
            functions=visitor.functions,
            classes=visitor.classes,
            imports=visitor.imports,
            max_depth=visitor.max_depth,
            creativity_score=creativity_score,
        )

        # Cache the result
        self._metrics_cache[cache_key] = metrics
        logger.debug(f"Cached metrics for {cache_key}")

        return metrics

    def index_file(
        self,
        file_path: str,
        task: str,
        chaos_level: float,
        success: bool,
        execution_time: float,
        output: str,
        error: Optional[str] = None,
    ) -> FileIndex:
        """Index a Python file with execution results."""
        logger.debug(f"Indexing file {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                code = f.read()
        except (IOError, OSError) as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return FileIndex(
                path=file_path,
                task=task,
                chaos_level=chaos_level,
                timestamp=datetime.now().isoformat(),
                hash="",
                metrics=CodeMetrics(
                    complexity=0,
                    lines=0,
                    functions=0,
                    classes=0,
                    imports=0,
                    max_depth=0,
                    creativity_score=0.0,
                ),
                success=False,
                execution_time=execution_time,
                output=output,
                error=str(e),
            )

        metrics = self.analyze_code(file_path, is_file=True)
        file_hash = hashlib.sha256((code + file_path).encode()).hexdigest()

        logger.debug(f"Success: {success}, Chaos level: {chaos_level}")

        index = FileIndex(
            path=file_path,
            task=task,
            chaos_level=chaos_level,
            timestamp=datetime.now().isoformat(),
            hash=file_hash,
            metrics=metrics,
            success=success,
            execution_time=execution_time,
            output=output,
            error=error,
        )

        self.index[file_hash] = index
        self._save_index()

        return index

    def get_similar_tasks(
        self,
        task: str,
        limit: int = 5,
        success_only: bool = True,
        min_success_rate: float = 0.0,
    ) -> List[FileIndex]:
        """Find similar tasks based on metrics."""
        if not self.index:
            return []

        # Filter tasks by success rate if specified
        tasks = list(self.index.values())
        if success_only:
            tasks = [t for t in tasks if t.success]

        if min_success_rate > 0:
            success_rate = (
                len([t for t in tasks if t.success]) / len(tasks) if tasks else 0
            )
            if success_rate < min_success_rate:
                return []

        # Sort by timestamp (most recent first)
        tasks.sort(key=lambda x: x.timestamp, reverse=True)
        return tasks[:limit]

    def get_successful_patterns(
        self,
        min_success_rate: float = 0.8,
    ) -> Dict[str, float]:
        """Analyze patterns in successful code."""
        if not self.index:
            logger.info("No entries in index")
            return {}

        successful = [t for t in self.index.values() if t.success]
        total = len(self.index)

        logger.info(f"Found {len(successful)} successful tasks out of {total} total")

        if not successful:
            logger.info("No successful tasks found")
            return {}

        success_rate = len(successful) / total
        logger.info(
            f"Success rate: {success_rate:.2%}, min required: {min_success_rate:.2%}"
        )

        if success_rate < min_success_rate:
            logger.info("Success rate below minimum threshold")
            return {}

        # Aggregate metrics from successful tasks
        metrics = {
            "avg_complexity": float(
                statistics.mean(t.metrics.complexity for t in successful)
            ),
            "avg_lines": float(statistics.mean(t.metrics.lines for t in successful)),
            "avg_functions": float(
                statistics.mean(t.metrics.functions for t in successful)
            ),
            "avg_classes": float(
                statistics.mean(t.metrics.classes for t in successful)
            ),
            "avg_imports": float(
                statistics.mean(t.metrics.imports for t in successful)
            ),
            "avg_depth": float(
                statistics.mean(t.metrics.max_depth for t in successful)
            ),
            "avg_creativity": float(
                statistics.mean(t.metrics.creativity_score for t in successful)
            ),
            "success_rate": float(success_rate),
        }

        logger.debug(f"Computed metrics: {metrics}")
        return metrics

    def _save_index(self) -> None:
        """Save the index to disk."""
        if not self._index_file:
            logger.debug("No index file specified, skipping save")
            return

        # Convert FileIndex objects to dictionaries
        index_dict = {}
        for k, v in self.index.items():
            try:
                index_dict[k] = asdict(v)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to serialize index entry {k}: {e}")
                continue

        # Create parent directories if they don't exist
        try:
            self._index_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory {self._index_file.parent}: {e}")
            return

        try:
            with open(self._index_file, "w") as f:
                json.dump(index_dict, f, indent=2)
            logger.info(f"Saved {len(index_dict)} entries to {self._index_file}")
        except (OSError, TypeError) as e:
            logger.error(f"Failed to save index to {self._index_file}: {e}")

    def _load_index(self) -> None:
        """Load the index from disk."""
        if not self._index_file or not os.path.exists(self._index_file):
            logger.debug(f"Index file {self._index_file} does not exist")
            self.index = {}
            return

        try:
            with open(self._index_file, "r") as f:
                index_dict = json.load(f)

            if not isinstance(index_dict, dict):
                logger.warning(
                    f"Invalid index format in {self._index_file}, expected dict"
                )
                self.index = {}
                return

            # Convert dictionaries back to FileIndex objects
            self.index = {}
            for k, v in index_dict.items():
                try:
                    if isinstance(v, dict):
                        self.index[k] = FileIndex(**v)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Failed to deserialize index entry {k}: {e}")
                    continue

            logger.info(f"Loaded {len(self.index)} entries from {self._index_file}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load index from {self._index_file}: {e}")
            self.index = {}
