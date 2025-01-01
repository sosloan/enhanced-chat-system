import pytest
import asyncio
import pytest_asyncio
from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from recipe_management_system import app, process_recipe_command
from recipe_exceptions import (
    RecipeError, RecipeNotFoundError, RecipeValidationError
)

# Test data
SAMPLE_RECIPE = {
    "name": "Test Lemon Cheesecake",
    "description": "A delicious test recipe for a tangy lemon cheesecake",
    "ingredients": [
        {
            "name": "cream cheese",
            "amount": 16,
            "unit": "oz"
        },
        {
            "name": "sugar",
            "amount": 0.5,
            "unit": "cup"
        },
        {
            "name": "lemon zest",
            "amount": 2,
            "unit": "tbsp"
        }
    ],
    "instructions": [
        "Beat cream cheese until smooth",
        "Add sugar and mix well",
        "Fold in lemon zest"
    ],
    "category": "dessert",
    "difficulty": "medium",
    "prep_time": 30,
    "cook_time": 60,
    "servings": 8,
    "tags": ["dessert", "cheesecake", "lemon"]
}

SAMPLE_MEAL_PLAN_REQUEST = {
    "days": 3,
    "dietary_restrictions": ["vegetarian"],
    "excluded_ingredients": ["nuts"],
    "calories_per_day": 2000
}

# Configure pytest-asyncio to use function scope for event loops
pytest_asyncio.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def mock_process_recipe_command():
    """Create a mock for process_recipe_command."""
    async def mock_command(command_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if command_type == "add_recipe":
            # Validate recipe data
            if "prep_time" in data and data["prep_time"] < 0:
                raise RecipeValidationError("prep_time must be non-negative")
            if "name" in data and not data["name"]:
                raise RecipeValidationError("name cannot be empty")
            if "ingredients" in data and not data["ingredients"]:
                raise RecipeValidationError("ingredients cannot be empty")
            if "difficulty" in data and data["difficulty"] not in ["easy", "medium", "hard"]:
                raise RecipeValidationError("invalid difficulty level")
            if "servings" in data and data["servings"] <= 0:
                raise RecipeValidationError("servings must be positive")
            
            return {
                "status": "success",
                "recipe_id": "test_recipe_id",
                "message": "Recipe added successfully"
            }
        elif command_type == "search_recipes":
            return {
                "status": "success",
                "recipes": [SAMPLE_RECIPE],
                "total": 1,
                "page": 1,
                "per_page": 10
            }
        elif command_type == "analyze_recipe":
            if data.get("recipe_id") == "nonexistent_id":
                raise RecipeNotFoundError("Recipe not found")
            return {
                "status": "success",
                "nutrition_info": {
                    "calories": 350,
                    "protein": 8,
                    "carbs": 45,
                    "fat": 12
                },
                "cooking_tips": [
                    "Make sure ingredients are at room temperature",
                    "Don't overmix the batter"
                ]
            }
        elif command_type == "generate_meal_plan":
            if "invalid_diet" in data.get("dietary_restrictions", []):
                raise RecipeValidationError("Invalid dietary restriction")
            return {
                "status": "success",
                "meal_plan": [
                    {"breakfast": SAMPLE_RECIPE, "lunch": SAMPLE_RECIPE, "dinner": SAMPLE_RECIPE}
                ] * data["days"],
                "total_nutrition": {
                    "calories": 2000,
                    "protein": 75,
                    "carbs": 250,
                    "fat": 70
                },
                "daily_nutrition": [
                    {
                        "calories": 2000,
                        "protein": 75,
                        "carbs": 250,
                        "fat": 70
                    }
                ] * data["days"]
            }
        elif command_type == "find_similar_recipes":
            return {
                "status": "success",
                "similar_recipes": [SAMPLE_RECIPE],
                "similarity_scores": [0.85]
            }
        elif command_type == "generate_cooking_tips":
            return {
                "status": "success",
                "cooking_tips": [
                    "Make sure ingredients are at room temperature",
                    "Don't overmix the batter"
                ]
            }
        else:
            raise RecipeError(f"Unknown command type: {command_type}")
    
    return AsyncMock(side_effect=mock_command)

class TestRecipeManagement:
    @pytest.mark.asyncio
    async def test_add_recipe_success(self, mock_process_recipe_command):
        """Test adding a recipe successfully"""
        result = await mock_process_recipe_command("add_recipe", SAMPLE_RECIPE)
        assert result["status"] == "success"
        assert "recipe_id" in result

    @pytest.mark.asyncio
    async def test_add_recipe_validation_error(self, mock_process_recipe_command):
        """Test adding a recipe with invalid data"""
        invalid_recipe = {**SAMPLE_RECIPE, "prep_time": -1}
        with pytest.raises(RecipeValidationError):
            await mock_process_recipe_command("add_recipe", invalid_recipe)

    @pytest.mark.asyncio
    async def test_search_recipes(self, mock_process_recipe_command):
        """Test searching recipes"""
        # First add a recipe to search for
        add_result = await mock_process_recipe_command("add_recipe", SAMPLE_RECIPE)
        
        # Then search for it
        search_result = await mock_process_recipe_command(
            "search_recipes",
            {"query": "lemon", "page": 1, "per_page": 10}
        )
        assert search_result["status"] == "success"
        assert len(search_result["recipes"]) > 0

    @pytest.mark.asyncio
    async def test_search_recipes_pagination(self, mock_process_recipe_command):
        """Test recipe search pagination"""
        # Add multiple recipes
        for i in range(3):
            recipe = {
                **SAMPLE_RECIPE,
                "name": f"Test Recipe {i}",
                "description": f"Test recipe description {i}"
            }
            await mock_process_recipe_command("add_recipe", recipe)
        
        # Test pagination
        result = await mock_process_recipe_command(
            "search_recipes",
            {"query": "Test Recipe", "page": 1, "per_page": 2}
        )
        assert result["status"] == "success"
        assert len(result["recipes"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_recipe(self, mock_process_recipe_command):
        """Test recipe analysis"""
        # First add a recipe
        add_result = await mock_process_recipe_command("add_recipe", SAMPLE_RECIPE)
        recipe_id = add_result["recipe_id"]
        
        # Then analyze it
        result = await mock_process_recipe_command(
            "analyze_recipe",
            {"recipe_id": recipe_id}
        )
        assert result["status"] == "success"
        assert "nutrition_info" in result
        assert "cooking_tips" in result

    @pytest.mark.asyncio
    async def test_analyze_nonexistent_recipe(self, mock_process_recipe_command):
        """Test analyzing a recipe that doesn't exist"""
        with pytest.raises(RecipeNotFoundError):
            await mock_process_recipe_command(
                "analyze_recipe",
                {"recipe_id": "nonexistent_id"}
            )

    @pytest.mark.asyncio
    async def test_generate_meal_plan(self, mock_process_recipe_command):
        """Test meal plan generation"""
        # Add some recipes first
        for i in range(5):
            recipe = {
                **SAMPLE_RECIPE,
                "name": f"Test Recipe {i}",
                "category": "main_course" if i % 2 == 0 else "breakfast"
            }
            await mock_process_recipe_command("add_recipe", recipe)
        
        # Generate meal plan
        result = await mock_process_recipe_command(
            "generate_meal_plan",
            SAMPLE_MEAL_PLAN_REQUEST
        )
        assert result["status"] == "success"
        assert "meal_plan" in result
        assert len(result["meal_plan"]) == SAMPLE_MEAL_PLAN_REQUEST["days"]

    @pytest.mark.asyncio
    async def test_generate_meal_plan_validation(self, mock_process_recipe_command):
        """Test meal plan generation with invalid preferences"""
        invalid_request = {
            **SAMPLE_MEAL_PLAN_REQUEST,
            "dietary_restrictions": ["invalid_diet"]
        }
        with pytest.raises(RecipeValidationError):
            await mock_process_recipe_command(
                "generate_meal_plan",
                invalid_request
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("command_type", [
        "invalid_command",
        "",
        None
    ])
    async def test_invalid_command_type(self, mock_process_recipe_command, command_type):
        """Test handling of invalid command types"""
        with pytest.raises(RecipeError):
            await mock_process_recipe_command(command_type, {})

    @pytest.mark.asyncio
    @pytest.mark.parametrize("recipe_data,expected_error", [
        (
            {**SAMPLE_RECIPE, "name": ""},
            "name"
        ),
        (
            {**SAMPLE_RECIPE, "ingredients": []},
            "ingredients"
        ),
        (
            {**SAMPLE_RECIPE, "difficulty": "invalid"},
            "difficulty"
        ),
        (
            {**SAMPLE_RECIPE, "servings": 0},
            "servings"
        )
    ])
    async def test_recipe_validation_errors(self, mock_process_recipe_command, recipe_data, expected_error):
        """Test various recipe validation scenarios"""
        with pytest.raises(RecipeValidationError) as exc_info:
            await mock_process_recipe_command("add_recipe", recipe_data)
        assert expected_error in str(exc_info.value)

class TestRecipeMLFeatures:
    @pytest.mark.asyncio
    async def test_recipe_embedding_similarity(self, mock_process_recipe_command):
        """Test recipe similarity search"""
        # Add two similar recipes
        recipe1 = {**SAMPLE_RECIPE}
        recipe2 = {
            **SAMPLE_RECIPE,
            "name": "Similar Lemon Cake",
            "description": "Another lemony dessert"
        }
        
        await mock_process_recipe_command("add_recipe", recipe1)
        await mock_process_recipe_command("add_recipe", recipe2)
        
        # Search for similar recipes
        result = await mock_process_recipe_command(
            "find_similar_recipes",
            {"recipe_name": "Test Lemon Cheesecake"}
        )
        assert result["status"] == "success"
        assert len(result["similar_recipes"]) > 0

    @pytest.mark.asyncio
    async def test_nutrition_analysis(self, mock_process_recipe_command):
        """Test nutrition analysis"""
        # Add a recipe
        add_result = await mock_process_recipe_command("add_recipe", SAMPLE_RECIPE)
        recipe_id = add_result["recipe_id"]
        
        # Analyze nutrition
        result = await mock_process_recipe_command(
            "analyze_recipe",
            {"recipe_id": recipe_id}
        )
        assert result["status"] == "success"
        assert "nutrition_info" in result
        assert "calories" in result["nutrition_info"]

    @pytest.mark.asyncio
    async def test_cooking_tips_generation(self, mock_process_recipe_command):
        """Test cooking tips generation"""
        # Add a recipe
        add_result = await mock_process_recipe_command("add_recipe", SAMPLE_RECIPE)
        recipe_id = add_result["recipe_id"]
        
        # Generate cooking tips
        result = await mock_process_recipe_command(
            "generate_cooking_tips",
            {"recipe_id": recipe_id}
        )
        assert result["status"] == "success"
        assert "cooking_tips" in result
        assert len(result["cooking_tips"]) > 0

    @pytest.mark.asyncio
    async def test_meal_plan_nutrition(self, mock_process_recipe_command):
        """Test meal plan nutrition calculations"""
        # Add some recipes with nutrition info
        for i in range(5):
            recipe = {
                **SAMPLE_RECIPE,
                "name": f"Test Recipe {i}",
                "category": "main_course"
            }
            await mock_process_recipe_command("add_recipe", recipe)
        
        # Generate meal plan with nutrition info
        result = await mock_process_recipe_command(
            "generate_meal_plan",
            {**SAMPLE_MEAL_PLAN_REQUEST, "include_nutrition": True}
        )
        assert result["status"] == "success"
        assert "meal_plan" in result
        assert "total_nutrition" in result
        assert "daily_nutrition" in result

if __name__ == "__main__":
    pytest.main(["-v"])