from typing import Optional

class RecipeError(Exception):
    """Base exception for recipe-related errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.details = details or {}

class RecipeNotFoundError(RecipeError):
    """Raised when a recipe cannot be found"""
    pass

class RecipeValidationError(RecipeError):
    """Raised when recipe data fails validation"""
    pass

class RecipeStorageError(RecipeError):
    """Raised when there are storage-related issues"""
    pass

class RecipeMLError(RecipeError):
    """Raised when ML-related operations fail"""
    pass

class RecipeDuplicateError(RecipeError):
    """Raised when attempting to create a duplicate recipe"""
    pass

class RecipeScalingError(RecipeError):
    """Raised when recipe scaling fails"""
    pass

class RecipeIngredientError(RecipeError):
    """Raised when there are issues with recipe ingredients"""
    pass

class RecipeAuthenticationError(RecipeError):
    """Raised when authentication fails"""
    pass

class RecipePermissionError(RecipeError):
    """Raised when user lacks permission for an operation"""
    pass 