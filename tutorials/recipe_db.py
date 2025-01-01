from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import json
from recipe_exceptions import RecipeStorageError, RecipeNotFoundError
from recipe_validation import RecipeModel, IngredientModel

class Base(DeclarativeBase):
    pass

# Association tables for many-to-many relationships
recipe_tags = Table(
    'recipe_tags',
    Base.metadata,
    Column('recipe_id', String, ForeignKey('recipes.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

recipe_dietary_restrictions = Table(
    'recipe_dietary_restrictions',
    Base.metadata,
    Column('recipe_id', String, ForeignKey('recipes.id')),
    Column('restriction_id', Integer, ForeignKey('dietary_restrictions.id'))
)

class Tag(Base):
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DietaryRestriction(Base):
    __tablename__ = 'dietary_restrictions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[str] = mapped_column(ForeignKey('recipes.id'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String)

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, nullable=False)
    prep_time: Mapped[int] = mapped_column(Integer, nullable=False)
    cook_time: Mapped[int] = mapped_column(Integer, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    instructions: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    nutrition_info: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ingredients: Mapped[List[Ingredient]] = relationship("Ingredient", cascade="all, delete-orphan")
    tags: Mapped[List[Tag]] = relationship("Tag", secondary=recipe_tags, backref="recipes")
    dietary_restrictions: Mapped[List[DietaryRestriction]] = relationship(
        "DietaryRestriction", 
        secondary=recipe_dietary_restrictions, 
        backref="recipes"
    )

class RecipeDatabase:
    def __init__(self, db_url: str = "sqlite:///recipes.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    async def add_recipe(self, recipe_data: RecipeModel) -> str:
        """Add a new recipe to the database."""
        session = self.Session()
        try:
            recipe = Recipe(
                id=recipe_data.id or str(datetime.utcnow().timestamp()),
                name=recipe_data.name,
                description=recipe_data.description,
                category=recipe_data.category.value,
                difficulty=recipe_data.difficulty.value,
                prep_time=recipe_data.prep_time,
                cook_time=recipe_data.cook_time,
                servings=recipe_data.servings,
                instructions=recipe_data.instructions,
                nutrition_info=recipe_data.nutrition_info
            )
            
            # Add ingredients
            recipe.ingredients = [
                Ingredient(
                    name=ing.name,
                    amount=ing.amount,
                    unit=ing.unit,
                    notes=ing.notes
                )
                for ing in recipe_data.ingredients
            ]
            
            # Add tags
            for tag_name in recipe_data.tags:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                recipe.tags.append(tag)
            
            session.add(recipe)
            session.commit()
            return recipe.id
            
        except Exception as e:
            session.rollback()
            raise RecipeStorageError(f"Failed to add recipe: {str(e)}")
        finally:
            session.close()
    
    async def get_recipe(self, recipe_id: str) -> RecipeModel:
        """Get a recipe by ID."""
        session = self.Session()
        try:
            recipe = session.query(Recipe).filter_by(id=recipe_id).first()
            if not recipe:
                raise RecipeNotFoundError(f"Recipe with ID {recipe_id} not found")
            
            return RecipeModel(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                category=recipe.category,
                difficulty=recipe.difficulty,
                prep_time=recipe.prep_time,
                cook_time=recipe.cook_time,
                servings=recipe.servings,
                instructions=recipe.instructions,
                nutrition_info=recipe.nutrition_info,
                ingredients=[
                    IngredientModel(
                        name=ing.name,
                        amount=ing.amount,
                        unit=ing.unit,
                        notes=ing.notes
                    )
                    for ing in recipe.ingredients
                ],
                tags=[tag.name for tag in recipe.tags],
                created_at=recipe.created_at,
                updated_at=recipe.updated_at
            )
            
        except RecipeNotFoundError:
            raise
        except Exception as e:
            raise RecipeStorageError(f"Failed to get recipe: {str(e)}")
        finally:
            session.close()
    
    async def update_recipe(self, recipe_id: str, recipe_data: RecipeModel) -> None:
        """Update an existing recipe."""
        session = self.Session()
        try:
            recipe = session.query(Recipe).filter_by(id=recipe_id).first()
            if not recipe:
                raise RecipeNotFoundError(f"Recipe with ID {recipe_id} not found")
            
            # Update basic fields
            recipe.name = recipe_data.name
            recipe.description = recipe_data.description
            recipe.category = recipe_data.category.value
            recipe.difficulty = recipe_data.difficulty.value
            recipe.prep_time = recipe_data.prep_time
            recipe.cook_time = recipe_data.cook_time
            recipe.servings = recipe_data.servings
            recipe.instructions = recipe_data.instructions
            recipe.nutrition_info = recipe_data.nutrition_info
            
            # Update ingredients
            recipe.ingredients = []
            recipe.ingredients = [
                Ingredient(
                    name=ing.name,
                    amount=ing.amount,
                    unit=ing.unit,
                    notes=ing.notes
                )
                for ing in recipe_data.ingredients
            ]
            
            # Update tags
            recipe.tags = []
            for tag_name in recipe_data.tags:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                recipe.tags.append(tag)
            
            session.commit()
            
        except RecipeNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise RecipeStorageError(f"Failed to update recipe: {str(e)}")
        finally:
            session.close()
    
    async def delete_recipe(self, recipe_id: str) -> None:
        """Delete a recipe by ID."""
        session = self.Session()
        try:
            recipe = session.query(Recipe).filter_by(id=recipe_id).first()
            if not recipe:
                raise RecipeNotFoundError(f"Recipe with ID {recipe_id} not found")
            
            session.delete(recipe)
            session.commit()
            
        except RecipeNotFoundError:
            raise
        except Exception as e:
            session.rollback()
            raise RecipeStorageError(f"Failed to delete recipe: {str(e)}")
        finally:
            session.close()
    
    async def search_recipes(
        self, 
        query: str, 
        page: int = 1, 
        per_page: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[RecipeModel], int]:
        """Search recipes with pagination and filters."""
        session = self.Session()
        try:
            # Base query
            q = session.query(Recipe)
            
            # Apply text search
            if query:
                q = q.filter(Recipe.name.ilike(f"%{query}%") | Recipe.description.ilike(f"%{query}%"))
            
            # Apply filters
            if filters:
                if "category" in filters:
                    q = q.filter(Recipe.category == filters["category"])
                if "difficulty" in filters:
                    q = q.filter(Recipe.difficulty == filters["difficulty"])
                if "max_prep_time" in filters:
                    q = q.filter(Recipe.prep_time <= filters["max_prep_time"])
                if "max_cook_time" in filters:
                    q = q.filter(Recipe.cook_time <= filters["max_cook_time"])
                if "tags" in filters:
                    q = q.join(Recipe.tags).filter(Tag.name.in_(filters["tags"]))
                if "dietary_restrictions" in filters:
                    q = q.join(Recipe.dietary_restrictions).filter(
                        DietaryRestriction.name.in_(filters["dietary_restrictions"])
                    )
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            recipes = q.offset((page - 1) * per_page).limit(per_page).all()
            
            # Convert to models
            recipe_models = [
                RecipeModel(
                    id=recipe.id,
                    name=recipe.name,
                    description=recipe.description,
                    category=recipe.category,
                    difficulty=recipe.difficulty,
                    prep_time=recipe.prep_time,
                    cook_time=recipe.cook_time,
                    servings=recipe.servings,
                    instructions=recipe.instructions,
                    nutrition_info=recipe.nutrition_info,
                    ingredients=[
                        IngredientModel(
                            name=ing.name,
                            amount=ing.amount,
                            unit=ing.unit,
                            notes=ing.notes
                        )
                        for ing in recipe.ingredients
                    ],
                    tags=[tag.name for tag in recipe.tags],
                    created_at=recipe.created_at,
                    updated_at=recipe.updated_at
                )
                for recipe in recipes
            ]
            
            return recipe_models, total
            
        except Exception as e:
            raise RecipeStorageError(f"Failed to search recipes: {str(e)}")
        finally:
            session.close() 