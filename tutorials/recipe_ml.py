from typing import List, Dict, Any, Optional
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from recipe_exceptions import RecipeMLError
from recipe_validation import RecipeModel, IngredientModel
import json
import logging

logger = logging.getLogger(__name__)

class RecipeEmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            logger.info(f"Loaded recipe embedding model on {self.device}")
        except Exception as e:
            raise RecipeMLError(f"Failed to load embedding model: {str(e)}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for recipe text"""
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Convert to numpy and normalize
            embedding = embeddings[0].cpu().numpy()
            normalized_embedding = embedding / np.linalg.norm(embedding)
            return normalized_embedding.tolist()
            
        except Exception as e:
            raise RecipeMLError(f"Failed to generate embedding: {str(e)}")

    def get_recipe_text(self, recipe: RecipeModel) -> str:
        """Convert recipe to text for embedding"""
        text_parts = [
            recipe.name,
            recipe.description,
            " ".join(recipe.instructions),
            " ".join(ing.name for ing in recipe.ingredients),
            " ".join(recipe.tags)
        ]
        return " ".join(text_parts)

class RecipeNutritionModel:
    def __init__(self):
        # Load nutrition data (could be replaced with a real ML model)
        self.nutrition_data = {
            # Basic ingredients (per 100g/ml)
            "flour": {"calories": 364, "protein": 10, "carbs": 76, "fat": 1},
            "sugar": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0},
            "butter": {"calories": 717, "protein": 0.9, "carbs": 0, "fat": 81},
            "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
            "milk": {"calories": 42, "protein": 3.4, "carbs": 5, "fat": 1},
            "cream cheese": {"calories": 342, "protein": 6, "carbs": 4, "fat": 34},
            "chicken": {"calories": 239, "protein": 27, "carbs": 0, "fat": 14},
            "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 17},
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
            "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1},
            # Add more ingredients as needed
        }
        
        self.unit_conversions = {
            "g": 1,
            "kg": 1000,
            "oz": 28.35,
            "lb": 453.6,
            "ml": 1,
            "l": 1000,
            "cup": 240,
            "tbsp": 15,
            "tsp": 5,
            "piece": 100,  # assumption
            "whole": 100,  # assumption
            "pinch": 1,
            "dash": 1
        }

    def analyze_nutrition(self, ingredients: List[IngredientModel]) -> Dict[str, float]:
        """Analyze recipe nutrition based on ingredients"""
        try:
            total_nutrition = {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            }
            
            for ingredient in ingredients:
                # Find best matching ingredient in database
                ing_name = self._find_matching_ingredient(ingredient.name)
                if not ing_name:
                    continue
                    
                # Convert amount to grams/ml
                amount_in_base = ingredient.amount * self.unit_conversions.get(
                    ingredient.unit.lower(),
                    1  # default to 1 if unit not found
                )
                
                # Calculate nutrition values
                for nutrient, base_value in self.nutrition_data[ing_name].items():
                    total_nutrition[nutrient] += (base_value * amount_in_base) / 100
                    
            # Round values
            return {
                key: round(value, 1)
                for key, value in total_nutrition.items()
            }
            
        except Exception as e:
            raise RecipeMLError(f"Failed to analyze nutrition: {str(e)}")

    def _find_matching_ingredient(self, name: str) -> Optional[str]:
        """Find best matching ingredient in database"""
        name = name.lower()
        # Direct match
        if name in self.nutrition_data:
            return name
        # Partial match
        for ing_name in self.nutrition_data:
            if ing_name in name or name in ing_name:
                return ing_name
        return None

class RecipeRecommender:
    def __init__(self, embedding_model: RecipeEmbeddingModel):
        self.embedding_model = embedding_model
        
    def find_similar_recipes(
        self,
        query_embedding: List[float],
        recipe_embeddings: Dict[str, List[float]],
        top_k: int = 5
    ) -> List[tuple[str, float]]:
        """Find similar recipes using cosine similarity"""
        try:
            if not recipe_embeddings:
                return []
                
            # Convert embeddings to numpy array
            query_embedding = np.array(query_embedding).reshape(1, -1)
            recipe_ids = list(recipe_embeddings.keys())
            embeddings = np.array([recipe_embeddings[rid] for rid in recipe_ids])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            
            # Get top-k similar recipes
            similar_indices = similarities.argsort()[-top_k:][::-1]
            return [(recipe_ids[i], float(similarities[i])) for i in similar_indices]
            
        except Exception as e:
            raise RecipeMLError(f"Failed to find similar recipes: {str(e)}")
            
    def recommend_recipes(
        self,
        user_preferences: Dict[str, Any],
        available_recipes: List[RecipeModel],
        top_k: int = 5
    ) -> List[RecipeModel]:
        """Recommend recipes based on user preferences"""
        try:
            # Convert preferences to embedding
            pref_text = " ".join([
                str(value) for value in user_preferences.values()
                if isinstance(value, (str, int, float))
            ])
            pref_embedding = self.embedding_model.generate_embedding(pref_text)
            
            # Get embeddings for all recipes
            recipe_embeddings = {
                recipe.id: self.embedding_model.generate_embedding(
                    self.embedding_model.get_recipe_text(recipe)
                )
                for recipe in available_recipes
            }
            
            # Find similar recipes
            similar_recipes = self.find_similar_recipes(
                pref_embedding,
                recipe_embeddings,
                top_k=top_k
            )
            
            # Get recipe objects
            recipe_dict = {recipe.id: recipe for recipe in available_recipes}
            return [
                recipe_dict[recipe_id]
                for recipe_id, _ in similar_recipes
                if recipe_id in recipe_dict
            ]
            
        except Exception as e:
            raise RecipeMLError(f"Failed to recommend recipes: {str(e)}")

class RecipeTipGenerator:
    def __init__(self):
        self.cooking_tips = {
            "general": [
                "Prep all ingredients before starting",
                "Read the recipe thoroughly before beginning",
                "Keep your workspace clean and organized",
                "Use fresh ingredients when possible",
                "Taste and adjust seasoning as you cook"
            ],
            "baking": [
                "Ensure ingredients are at room temperature",
                "Measure ingredients precisely",
                "Preheat the oven properly",
                "Don't overmix the batter",
                "Check doneness a few minutes before the stated time"
            ],
            "meat": [
                "Let meat rest before cutting",
                "Pat meat dry before cooking",
                "Season generously",
                "Don't overcrowd the pan",
                "Use a meat thermometer"
            ],
            "vegetables": [
                "Don't overcook vegetables",
                "Cut vegetables uniformly for even cooking",
                "Season vegetables before roasting",
                "Don't wash mushrooms, wipe them clean",
                "Salt vegetables after cooking for stir-fries"
            ]
        }
        
    def generate_tips(self, recipe: RecipeModel) -> List[str]:
        """Generate cooking tips based on recipe content"""
        try:
            tips = []
            
            # Add general tips
            tips.extend(np.random.choice(
                self.cooking_tips["general"],
                size=min(2, len(self.cooking_tips["general"])),
                replace=False
            ))
            
            # Add category-specific tips
            if recipe.category.lower() == "dessert":
                tips.extend(np.random.choice(
                    self.cooking_tips["baking"],
                    size=min(2, len(self.cooking_tips["baking"])),
                    replace=False
                ))
                
            # Add ingredient-specific tips
            ingredient_names = [ing.name.lower() for ing in recipe.ingredients]
            if any(meat in " ".join(ingredient_names) for meat in ["chicken", "beef", "pork", "fish"]):
                tips.extend(np.random.choice(
                    self.cooking_tips["meat"],
                    size=min(2, len(self.cooking_tips["meat"])),
                    replace=False
                ))
                
            if any(veg in " ".join(ingredient_names) for veg in ["carrot", "broccoli", "spinach", "mushroom"]):
                tips.extend(np.random.choice(
                    self.cooking_tips["vegetables"],
                    size=min(2, len(self.cooking_tips["vegetables"])),
                    replace=False
                ))
                
            # Add recipe-specific tips
            tips.append(f"For best results, use fresh {np.random.choice([ing.name for ing in recipe.ingredients])}")
            
            return list(set(tips))  # Remove duplicates
            
        except Exception as e:
            raise RecipeMLError(f"Failed to generate cooking tips: {str(e)}")

class MLManager:
    def __init__(self):
        self.embedding_model = RecipeEmbeddingModel()
        self.nutrition_model = RecipeNutritionModel()
        self.recommender = RecipeRecommender(self.embedding_model)
        self.tip_generator = RecipeTipGenerator()
        
    def generate_recipe_embedding(self, recipe: RecipeModel) -> List[float]:
        """Generate embedding for a recipe"""
        text = self.embedding_model.get_recipe_text(recipe)
        return self.embedding_model.generate_embedding(text)
        
    def analyze_recipe_nutrition(self, ingredients: List[IngredientModel]) -> Dict[str, float]:
        """Analyze recipe nutrition"""
        return self.nutrition_model.analyze_nutrition(ingredients)
        
    def find_similar_recipes(
        self,
        query_embedding: List[float],
        recipe_embeddings: Dict[str, List[float]]
    ) -> List[tuple[str, float]]:
        """Find similar recipes"""
        return self.recommender.find_similar_recipes(query_embedding, recipe_embeddings)
        
    def recommend_recipes(
        self,
        user_preferences: Dict[str, Any],
        available_recipes: List[RecipeModel]
    ) -> List[RecipeModel]:
        """Recommend recipes based on preferences"""
        return self.recommender.recommend_recipes(user_preferences, available_recipes)
        
    def generate_recipe_tips(self, recipe: RecipeModel) -> List[str]:
        """Generate cooking tips for a recipe"""
        return self.tip_generator.generate_tips(recipe) 