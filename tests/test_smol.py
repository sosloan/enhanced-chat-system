"""
Tests for the SMOL loop functionality with Adaptive Chaos Evolution (ACE).
"""

import os
import pytest

from src.lib.code_generator import (
    CodeGenResult,
    clean_generated_code,
    test_generated_code,
    generate_code,
    is_valid_python,
)

from src.lib.improver import (
    SmolImprover,
)

from src.lib.ace import (
    ACEIndividual,
    evaluate_individual,
    mutate_individual,
    run_ace,
)


def test_clean_generated_code():
    """Test code cleaning functionality."""
    # Test markdown code block removal
    code = "```python\ndef hello():\n    print('world')\n```"
    cleaned = clean_generated_code(code)
    assert cleaned == "def hello():\n    print('world')"

    # Test whitespace handling
    code = "\n\n  def test():\n    pass\n\n"
    cleaned = clean_generated_code(code)
    assert cleaned == "def test():\n    pass"

    # Test comment handling
    code = "# This is a comment\ndef test(): # inline comment\n    pass"
    cleaned = clean_generated_code(code)
    assert cleaned == "def test():\n    pass"

    # Test docstring preservation
    code = '"""This is a docstring."""\ndef test():\n    """Function docstring."""\n    pass'
    cleaned = clean_generated_code(code)
    assert '"""This is a docstring."""' in cleaned
    assert '"""Function docstring."""' in cleaned


def test_is_valid_python():
    """Test Python syntax validation."""
    # Valid code
    assert is_valid_python("def test(): pass")
    assert is_valid_python("async def test(): await something()")
    assert is_valid_python("class Test:\n    def __init__(self): pass")

    # Invalid code
    assert not is_valid_python("def test() pass")  # Missing colon
    assert not is_valid_python(
        "class Test:\n def __init__(self) pass")  # Missing colon
    assert not is_valid_python("print('test'")  # Missing parenthesis


def test_code_execution():
    """Test code execution functionality."""
    # Test valid code
    result = test_generated_code(
        """
def greet():
    print('hello world')
    return 'hello world'
result = greet()
"""
    )
    assert result.success
    assert "hello world" in result.output
    assert result.metrics["execution_time"] >= 0

    # Test invalid code
    result = test_generated_code("print(undefined_variable)")
    assert not result.success
    assert result.error  # Check that an error message exists
    assert result.metrics["execution_time"] >= 0

    # Test timeout
    result = test_generated_code("while True: pass", timeout=5)
    assert not result.success
    assert "timed out" in result.error.lower()
    assert result.metrics["execution_time"] >= 0

    # Test complexity calculation
    result = test_generated_code(
        """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
result = factorial(5)
"""
    )
    assert result.success
    assert result.metrics["complexity_score"] > 5  # Complex enough
    assert "120" in result.output  # factorial(5) = 120
    assert result.metrics["execution_time"] >= 0


def test_code_gen_result():
    """Test CodeGenResult data class."""
    # Test successful result
    result = CodeGenResult(
        code="print('test')",
        success=True,
        output="test",
        metrics={"execution_time": 0.1, "complexity_score": 1.0},
    )
    assert result.success
    assert result.code == "print('test')"
    assert result.output == "test"
    assert result.metrics["execution_time"] == 0.1

    # Test failed result
    result = CodeGenResult(
        code="",
        success=False,
        error="API Error",
        metrics={"execution_time": 0.0, "complexity_score": 0.0},
    )
    assert not result.success
    assert result.error == "API Error"


@pytest.mark.skipif(
    not os.environ.get("TOGETHER_AI_API_KEY"),
    reason="TOGETHER_AI_API_KEY environment variable not set",
)
def test_generate_code(test_config):
    """Test code generation with Together AI."""
    # Test basic generation
    result = generate_code("Print hello world", chaos_level=0)
    assert result.success
    assert "print" in result.code.lower()
    assert "hello" in result.code.lower()

    # Test chaos level impact
    result_low = generate_code("Create a greeting", chaos_level=0)
    result_high = generate_code("Create a greeting", chaos_level=10)
    assert (result_high.metrics["complexity_score"]
            > result_low.metrics["complexity_score"])

    # Test error handling
    result = generate_code("", chaos_level=0)  # Empty prompt
    assert not result.success
    assert result.error is not None


@pytest.mark.skipif(
    not os.environ.get("TOGETHER_AI_API_KEY"),
    reason="TOGETHER_AI_API_KEY environment variable not set",
)
@pytest.mark.asyncio
async def test_ace_integration(test_config, mock_dspy_evaluator):
    """Test Adaptive Chaos Evolution integration."""
    # Test ACEIndividual
    individual = ACEIndividual(chaos_level=5, dspy_params={"time_budget": 100})
    assert individual.chaos_level == 5
    assert individual.dspy_params["time_budget"] == 100

    # Test mutation
    mutated = individual.copy()
    mutate_individual(mutated, temperature=1.0)
    assert mutated.chaos_level != individual.chaos_level

    # Force mutation of DSPy params
    mutated.dspy_params["time_budget"] = 200
    assert mutated.dspy_params != individual.dspy_params

    # Test evaluation
    score = await evaluate_individual(
        individual=individual,
        task="Create a simple calculator class",
        config=test_config,
        dspy_evaluator=mock_dspy_evaluator,
    )
    assert score >= 0.0

    # Test full ACE run
    best_individual = await run_ace(
        task="Create a function to calculate fibonacci numbers",
        config=test_config,
        dspy_evaluator=mock_dspy_evaluator,
        population_size=4,
        max_generations=2,
        temperature_init=2.0,
        cooling_rate=0.9,
    )
    assert isinstance(best_individual, ACEIndividual)
    assert best_individual.score > 0.0


@pytest.mark.skipif(
    not os.environ.get("TOGETHER_AI_API_KEY"),
    reason="TOGETHER_AI_API_KEY environment variable not set",
)
@pytest.mark.asyncio
async def test_improver_integration(test_config, test_strategy, test_output_dir):
    """Test SmolImprover with ACE integration."""
    improver = SmolImprover(
        config=test_config,
        index_path=test_output_dir / "test_index.json",
        strategy=test_strategy,
    )

    result, history = await improver.improve_task(
        task="Create a function that sorts a list using bubble sort",
        max_iterations=3,
        min_success_rate=0.7,
    )

    assert result.success
    assert len(history) > 0
    assert all(isinstance(entry, dict) for entry in history)
    assert "sort" in result.code.lower()
    assert "bubble" in result.code.lower()

    # Test pattern recognition
    patterns = improver.indexer.get_successful_patterns()
    assert len(patterns) > 0


"""Test script for the enhanced SMOL optimizer with chaos testing."""
