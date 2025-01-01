import React, { useState } from 'react'
import { Recipe } from '../types/recipe'
import { useRecipeProcessingPipeline, useMealPlanPipeline } from '../hooks/usePipeline'

interface RecipeProcessorProps {
  initialRecipe?: Recipe
  onProcessed?: (analysis: any) => void
  onError?: (error: Error) => void
}

export const RecipeProcessor: React.FC<RecipeProcessorProps> = ({
  initialRecipe,
  onProcessed,
  onError
}) => {
  const [recipe, setRecipe] = useState<Recipe | undefined>(initialRecipe)
  const {
    process: processRecipe,
    loading: recipeLoading,
    error: recipeError,
    result: recipeAnalysis
  } = useRecipeProcessingPipeline()

  const {
    process: generateMealPlan,
    loading: planLoading,
    error: planError,
    result: mealPlan
  } = useMealPlanPipeline()

  const handleProcess = async () => {
    if (!recipe) return

    try {
      const analysis = await processRecipe(recipe)
      onProcessed?.(analysis)
    } catch (err) {
      onError?.(err as Error)
    }
  }

  const handleGenerateMealPlan = async () => {
    if (!recipe) return

    try {
      await generateMealPlan([recipe])
    } catch (err) {
      onError?.(err as Error)
    }
  }

  return (
    <div className="space-y-4">
      <div className="p-4 bg-white rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Recipe Processor</h2>
        
        {/* Recipe Input */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Recipe Input</h3>
          {recipe ? (
            <div className="p-3 bg-gray-50 rounded">
              <h4 className="font-medium">{recipe.name}</h4>
              <p className="text-sm text-gray-600">{recipe.description}</p>
            </div>
          ) : (
            <p className="text-gray-500">No recipe loaded</p>
          )}
        </div>

        {/* Processing Controls */}
        <div className="flex space-x-4">
          <button
            onClick={handleProcess}
            disabled={!recipe || recipeLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {recipeLoading ? 'Processing...' : 'Process Recipe'}
          </button>
          
          <button
            onClick={handleGenerateMealPlan}
            disabled={!recipe || planLoading}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            {planLoading ? 'Generating...' : 'Generate Meal Plan'}
          </button>
        </div>

        {/* Error Display */}
        {(recipeError || planError) && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
            {recipeError?.message || planError?.message}
          </div>
        )}

        {/* Results Display */}
        {recipeAnalysis && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Analysis Results</h3>
            <div className="p-3 bg-gray-50 rounded">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">Nutrition</h4>
                  <pre className="text-sm">
                    {JSON.stringify(recipeAnalysis.nutritionAnalysis, null, 2)}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium">Scores</h4>
                  <ul className="text-sm">
                    <li>Complexity: {recipeAnalysis.complexity.toFixed(2)}</li>
                    <li>Health Score: {recipeAnalysis.healthScore.toFixed(2)}</li>
                    <li>
                      Sustainability: {recipeAnalysis.sustainabilityScore.toFixed(2)}
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-4">
                <h4 className="font-medium">Recommendations</h4>
                <ul className="text-sm list-disc list-inside">
                  {recipeAnalysis.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {mealPlan && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Meal Plan</h3>
            <div className="p-3 bg-gray-50 rounded">
              <div className="space-y-4">
                {mealPlan.days.map((day, i) => (
                  <div key={i} className="border-b pb-4">
                    <h4 className="font-medium">Day {i + 1}</h4>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <h5 className="font-medium">Breakfast</h5>
                        <p>{day.breakfast.name}</p>
                      </div>
                      <div>
                        <h5 className="font-medium">Lunch</h5>
                        <p>{day.lunch.name}</p>
                      </div>
                      <div>
                        <h5 className="font-medium">Dinner</h5>
                        <p>{day.dinner.name}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4">
                <h4 className="font-medium">Shopping List</h4>
                <ul className="text-sm list-disc list-inside">
                  {mealPlan.shoppingList.map((item, i) => (
                    <li key={i}>
                      {item.amount} {item.unit} {item.name}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 