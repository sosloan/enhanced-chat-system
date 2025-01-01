from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from recipe_exceptions import RecipeValidationError

class RecipeCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SNACK = "snack"
    BREAKFAST = "breakfast"

class RecipeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class IngredientModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    notes: str | None = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise RecipeValidationError("Ingredient name cannot be empty")
        return v.strip()

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        valid_units = {
            "g", "kg", "oz", "lb", "ml", "l", "cup", "tbsp", "tsp", 
            "piece", "whole", "pinch", "dash"
        }
        if v.lower() not in valid_units:
            raise RecipeValidationError(
                f"Invalid unit: {v}. Valid units are: {', '.join(valid_units)}"
            )
        return v.lower()

class RecipeModel(BaseModel):
    id: str | None = None
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    ingredients: List[IngredientModel] = Field(..., min_length=1)
    instructions: List[str] = Field(..., min_length=1)
    category: RecipeCategory
    difficulty: RecipeDifficulty
    prep_time: int = Field(..., ge=0)
    cook_time: int = Field(..., ge=0)
    servings: int = Field(..., gt=0)
    tags: List[str] = Field(default_factory=list)
    nutrition_info: Dict[str, float] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: List[str]) -> List[str]:
        if not all(step.strip() for step in v):
            raise RecipeValidationError("Instructions cannot contain empty steps")
        return [step.strip() for step in v]

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        return [tag.lower().strip() for tag in v if tag.strip()]

    @field_validator("nutrition_info")
    @classmethod
    def validate_nutrition_info(cls, v: Dict[str, float] | None) -> Dict[str, float] | None:
        if v is None:
            return None
        required_fields = {"calories", "protein", "carbs", "fat"}
        if not all(field in v for field in required_fields):
            raise RecipeValidationError(
                f"Nutrition info must include: {', '.join(required_fields)}"
            )
        return v

class MealPlanPreferences(BaseModel):
    days: int = Field(..., gt=0, le=31)
    dietary_restrictions: List[str] = Field(default_factory=list)
    excluded_ingredients: List[str] = Field(default_factory=list)
    calories_per_day: int | None = Field(None, gt=0)
    max_prep_time: int | None = Field(None, ge=0)
    difficulty: RecipeDifficulty | None = None

    @field_validator("dietary_restrictions")
    @classmethod
    def validate_dietary_restrictions(cls, v: List[str]) -> List[str]:
        valid_restrictions = {
            "vegetarian", "vegan", "gluten-free", "dairy-free", 
            "nut-free", "low-carb", "keto", "paleo"
        }
        invalid = [r for r in v if r.lower() not in valid_restrictions]
        if invalid:
            raise RecipeValidationError(
                f"Invalid dietary restrictions: {', '.join(invalid)}. "
                f"Valid options are: {', '.join(valid_restrictions)}"
            )
        return [r.lower() for r in v]

def validate_recipe_data(data: Dict[str, Any]) -> RecipeModel:
    """Validate recipe data using the RecipeModel."""
    try:
        return RecipeModel(**data)
    except Exception as e:
        raise RecipeValidationError(str(e))

def validate_search_query(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate search query parameters."""
    required = {"query", "page", "per_page"}
    if not all(key in data for key in required):
        raise RecipeValidationError(f"Missing required fields: {required - data.keys()}")
    
    if not isinstance(data["query"], str):
        raise RecipeValidationError("Query must be a string")
    
    try:
        page = int(data["page"])
        per_page = int(data["per_page"])
        if page < 1 or per_page < 1:
            raise ValueError
    except (ValueError, TypeError):
        raise RecipeValidationError("Page and per_page must be positive integers")
    
    return {
        "query": data["query"].strip(),
        "page": page,
        "per_page": per_page,
        "filters": data.get("filters", {})
    }

def validate_meal_plan_preferences(data: Dict[str, Any]) -> MealPlanPreferences:
    """Validate meal plan preferences using the MealPlanPreferences model."""
    try:
        return MealPlanPreferences(**data)
    except Exception as e:
        raise RecipeValidationError(str(e)) 