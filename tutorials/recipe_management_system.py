from typing import Dict, List, Optional, Any
import modal
from datetime import datetime
import asyncio
import logging
import json
from pathlib import Path

from recipe_exceptions import (
    RecipeError, RecipeNotFoundError, RecipeValidationError,
    RecipeStorageError, RecipeMLError
)
from recipe_validation import (
    RecipeModel, IngredientModel, validate_recipe_data,
    validate_search_query, validate_meal_plan_preferences
)
from tutorials.recipe_db import RecipeDatabase
from recipe_ml import MLManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Modal app and persistent volume
app = modal.App("recipe-management-system")
VOLUME_NAME = "recipe-db"
recipe_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# Define the image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "scikit-learn",
    "numpy",
    "pandas",
    "tensorflow",
    "transformers",
    "torch",
    "sqlalchemy",
    "pydantic"
)

class RecipeManager:
    def __init__(self):
        self.db = RecipeDatabase()
        self.ml = MLManager()
        
    async def add_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new recipe with ML-enhanced analysis"""
        try:
            # Validate recipe data
            recipe_model = validate_recipe_data(recipe_data)
            
            # Generate recipe embedding
            recipe_embedding = self.ml.generate_recipe_embedding(recipe_model)
            
            # Add recipe to database
            recipe_id = self.db.add_recipe(recipe_model, recipe_embedding)
            
            # Get recipe for analysis
            recipe = self.db.get_recipe(recipe_id)
            
            # Generate analysis and recommendations
            similar_recipes = self.ml.find_similar_recipes(
                recipe_embedding,
                self.db.get_all_embeddings()
            )
            
            return {
                "recipe_id": recipe_id,
                "analysis": {
                    "nutrition": recipe.nutrition_info,
                    "cooking_tips": self.ml.generate_recipe_tips(recipe),
                    "similar_recipes": [
                        {
                            "recipe": self.db.get_recipe(recipe_id),
                            "similarity_score": score
                        }
                        for recipe_id, score in similar_recipes
                    ]
                }
            }
            
        except RecipeValidationError as e:
            logger.error(f"Recipe validation failed: {str(e)}")
            raise
        except RecipeMLError as e:
            logger.error(f"ML operation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to add recipe: {str(e)}")
            raise RecipeError(f"Failed to add recipe: {str(e)}")
            
    async def search_recipes(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search recipes using ML-powered similarity search"""
        try:
            # Validate search query
            search_model = validate_search_query(search_data)
            
            # Search recipes
            recipes, total = self.db.search_recipes(
                search_model.query,
                search_model.filters,
                search_model.page,
                search_model.page_size
            )
            
            return {
                "results": recipes,
                "total": total,
                "page": search_model.page,
                "page_size": search_model.page_size
            }
            
        except RecipeValidationError as e:
            logger.error(f"Search validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to search recipes: {str(e)}")
            raise RecipeError(f"Failed to search recipes: {str(e)}")
            
    async def analyze_recipe(self, recipe_id: str) -> Dict[str, Any]:
        """Analyze recipe for nutrition, complexity, and suggestions"""
        try:
            # Get recipe
            recipe = self.db.get_recipe(recipe_id)
            recipe_embedding = self.db.get_recipe_embedding(recipe_id)
            
            # Generate analysis
            similar_recipes = self.ml.find_similar_recipes(
                recipe_embedding,
                self.db.get_all_embeddings()
            )
            
            return {
                "nutrition": recipe.nutrition_info,
                "cooking_tips": self.ml.generate_recipe_tips(recipe),
                "similar_recipes": [
                    {
                        "recipe": self.db.get_recipe(recipe_id),
                        "similarity_score": score
                    }
                    for recipe_id, score in similar_recipes
                ],
                "complexity_analysis": {
                    "prep_complexity": len(recipe.instructions) / 5,
                    "ingredient_complexity": len(recipe.ingredients) / 5,
                    "time_complexity": (recipe.prep_time + recipe.cook_time) / 60
                }
            }
            
        except RecipeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to analyze recipe: {str(e)}")
            raise RecipeError(f"Failed to analyze recipe: {str(e)}")
            
    async def generate_meal_plan(self, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized meal plan using ML"""
        try:
            # Validate preferences
            preferences = validate_meal_plan_preferences(preferences_data)
            
            # Get all recipes
            recipes = self.db.search_recipes("", {}, page_size=1000)[0]
            
            # Generate recommendations for each meal
            meal_plan = []
            for day in range(preferences_data.get("days", 7)):
                # Get recommendations for each meal type
                breakfast = self.ml.recommend_recipes(
                    {**preferences.dict(), "category": "breakfast"},
                    recipes,
                    top_k=1
                )
                lunch = self.ml.recommend_recipes(
                    {**preferences.dict(), "category": "main_course"},
                    recipes,
                    top_k=1
                )
                dinner = self.ml.recommend_recipes(
                    {**preferences.dict(), "category": "main_course"},
                    recipes,
                    top_k=1
                )
                
                meal_plan.append({
                    "day": day + 1,
                    "breakfast": breakfast[0] if breakfast else None,
                    "lunch": lunch[0] if lunch else None,
                    "dinner": dinner[0] if dinner else None
                })
            
            # Calculate nutrition summary
            nutrition_summary = self._calculate_meal_plan_nutrition(meal_plan)
            
            return {
                "meal_plan": meal_plan,
                "nutrition_summary": nutrition_summary
            }
            
        except RecipeValidationError as e:
            logger.error(f"Meal plan preferences validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate meal plan: {str(e)}")
            raise RecipeError(f"Failed to generate meal plan: {str(e)}")
            
    def _calculate_meal_plan_nutrition(self, meal_plan: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate nutrition summary for meal plan"""
        total_nutrition = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }
        
        for day in meal_plan:
            for meal in ["breakfast", "lunch", "dinner"]:
                if day[meal] and day[meal].nutrition_info:
                    for key in total_nutrition:
                        total_nutrition[key] += day[meal].nutrition_info.get(key, 0)
        
        days = len(meal_plan)
        return {
            f"average_daily_{key}": round(value / days, 1)
            for key, value in total_nutrition.items()
        }

@app.function(volumes={"/data": recipe_volume}, image=image)
async def process_recipe_command(command_type: str, command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a recipe command"""
    try:
        manager = RecipeManager()
        
        if command_type == "add_recipe":
            result = await manager.add_recipe(command_data)
        elif command_type == "search_recipes":
            result = await manager.search_recipes(command_data)
        elif command_type == "analyze_recipe":
            result = await manager.analyze_recipe(command_data["recipe_id"])
        elif command_type == "generate_meal_plan":
            result = await manager.generate_meal_plan(command_data)
        else:
            raise RecipeError(f"Unknown command type: {command_type}")
            
        return {
            "status": "success",
            "result": result
        }
        
    except RecipeError as e:
        return {
            "status": "error",
            "error": str(e),
            "details": e.details if hasattr(e, "details") else None
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error": "An unexpected error occurred",
            "details": {"message": str(e)}
        }

@app.local_entrypoint()
def main():
    """Example usage of the recipe management system"""
    async def run_example():
        # Add a recipe
        add_result = await process_recipe_command(
            "add_recipe",
            {
                "name": "Lemon Cheesecake",
                "description": "A delicious and tangy lemon cheesecake",
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
                    },
                    {
                        "name": "eggs",
                        "amount": 4,
                        "unit": "whole"
                    }
                ],
                "instructions": [
                    "Beat cream cheese until smooth",
                    "Add sugar and mix well",
                    "Add eggs one at a time",
                    "Fold in lemon zest",
                    "Bake at 325°F for 1 hour"
                ],
                "category": "dessert",
                "difficulty": "medium",
                "prep_time": 30,
                "cook_time": 60,
                "servings": 8,
                "tags": ["dessert", "cheesecake", "lemon"]
            }
        )
        
        print("\nAdd Recipe Result:")
        print(json.dumps(add_result, indent=2))
        
        # Search recipes
        search_result = await process_recipe_command(
            "search_recipes",
            {
                "query": "lemon dessert",
                "filters": {
                    "difficulty": "medium"
                },
                "page": 1,
                "page_size": 10
            }
        )
        
        print("\nSearch Result:")
        print(json.dumps(search_result, indent=2))
        
        # Generate meal plan
        meal_plan_result = await process_recipe_command(
            "generate_meal_plan",
            {
                "days": 3,
                "dietary_restrictions": ["vegetarian"],
                "excluded_ingredients": ["nuts"],
                "max_prep_time": 45,
                "difficulty": "medium",
                "calories_per_meal": [400, 600]
            }
        )
        
        print("\nMeal Plan Result:")
        print(json.dumps(meal_plan_result, indent=2))

    asyncio.run(run_example())

if __name__ == "__main__":
    app.run() 