import React from 'react'
import type { Recipe, RecipeAnalysis } from '../types/recipe'
import {
  useNutritionAnalysis,
  useSustainabilityAnalysis,
  useSeasonalityAnalysis,
  useDietaryAnalysis
} from '../hooks/usePipeline'

interface RecipeAnalysisProps {
  recipe: Recipe
  onAnalysisComplete?: (analysis: RecipeAnalysis) => void
}

export const RecipeAnalysis: React.FC<RecipeAnalysisProps> = ({
  recipe,
  onAnalysisComplete
}) => {
  const nutrition = useNutritionAnalysis()
  const sustainability = useSustainabilityAnalysis()
  const seasonality = useSeasonalityAnalysis()
  const dietary = useDietaryAnalysis()

  const loading = 
    nutrition.loading || 
    sustainability.loading || 
    seasonality.loading || 
    dietary.loading

  const error = 
    nutrition.error || 
    sustainability.error || 
    seasonality.error || 
    dietary.error

  const handleAnalyze = async () => {
    try {
      const [
        nutritionAnalysis,
        sustainabilityAnalysis,
        seasonalityAnalysis,
        dietaryAnalysis
      ] = await Promise.all([
        nutrition.process(recipe),
        sustainability.process(recipe),
        seasonality.process(recipe),
        dietary.process(recipe)
      ])

      // Combine all analyses
      const combinedAnalysis: RecipeAnalysis = {
        ...nutritionAnalysis,
        environmentalImpact: sustainabilityAnalysis.environmentalImpact,
        sustainabilityScore: sustainabilityAnalysis.sustainabilityScore,
        seasonality: seasonalityAnalysis.seasonality,
        dietaryProfile: dietaryAnalysis.dietaryProfile,
        recommendations: {
          nutrition: nutritionAnalysis.recommendations?.nutrition || [],
          sustainability: sustainabilityAnalysis.recommendations?.sustainability || [],
          seasonal: seasonalityAnalysis.recommendations?.seasonal || [],
          dietary: dietaryAnalysis.recommendations?.dietary || [],
          cooking: []
        },
        alternatives: {
          seasonal: seasonalityAnalysis.alternatives?.seasonal || {},
          dietary: dietaryAnalysis.alternatives?.dietary || {},
          sustainable: sustainabilityAnalysis.alternatives?.sustainable || {}
        },
        processedBy: [
          ...(nutritionAnalysis.processedBy || []),
          ...(sustainabilityAnalysis.processedBy || []),
          ...(seasonalityAnalysis.processedBy || []),
          ...(dietaryAnalysis.processedBy || [])
        ]
      }

      onAnalysisComplete?.(combinedAnalysis)
    } catch (err) {
      console.error('Analysis failed:', err)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Recipe Analysis</h2>
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Recipe'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded">
          {error.message}
        </div>
      )}

      {/* Nutrition Analysis */}
      {nutrition.result && (
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">Nutrition Analysis</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Macronutrients</h4>
              <ul className="space-y-1 text-sm">
                <li>Calories: {nutrition.result.nutritionAnalysis.calories}kcal</li>
                <li>Protein: {nutrition.result.nutritionAnalysis.protein}g</li>
                <li>Carbs: {nutrition.result.nutritionAnalysis.carbs}g</li>
                <li>Fat: {nutrition.result.nutritionAnalysis.fat}g</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Micronutrients</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <h5 className="font-medium">Vitamins</h5>
                  <ul className="space-y-1">
                    {Object.entries(nutrition.result.nutritionAnalysis.vitamins || {}).map(([vitamin, amount]) => (
                      <li key={vitamin}>
                        {vitamin}: {amount.toFixed(1)}%
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5 className="font-medium">Minerals</h5>
                  <ul className="space-y-1">
                    {Object.entries(nutrition.result.nutritionAnalysis.minerals || {}).map(([mineral, amount]) => (
                      <li key={mineral}>
                        {mineral}: {amount.toFixed(1)}%
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sustainability Analysis */}
      {sustainability.result && (
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">Sustainability Analysis</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Environmental Impact</h4>
              <ul className="space-y-1 text-sm">
                <li>
                  Water Usage: {sustainability.result.environmentalImpact.waterUsage.toFixed(1)}L
                </li>
                <li>
                  Carbon Footprint: {sustainability.result.environmentalImpact.carbonFootprint.toFixed(1)}kg CO2
                </li>
                <li>
                  Food Miles: {sustainability.result.environmentalImpact.foodMiles.toFixed(1)}km
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Recommendations</h4>
              <ul className="space-y-1 text-sm list-disc list-inside">
                {sustainability.result.recommendations?.sustainability.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Seasonality Analysis */}
      {seasonality.result && (
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">Seasonality Analysis</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Current Season</h4>
              <div className="space-y-2">
                <div>
                  <h5 className="text-sm font-medium">In Season</h5>
                  <ul className="text-sm list-disc list-inside">
                    {seasonality.result.seasonality.inSeason.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5 className="text-sm font-medium">Out of Season</h5>
                  <ul className="text-sm list-disc list-inside">
                    {seasonality.result.seasonality.outOfSeason.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Seasonal Alternatives</h4>
              <div className="text-sm">
                {Object.entries(seasonality.result.alternatives?.seasonal || {}).map(([ingredient, alternatives]) => (
                  <div key={ingredient} className="mb-2">
                    <span className="font-medium">{ingredient}:</span>
                    <ul className="list-disc list-inside ml-2">
                      {alternatives.map((alt, i) => (
                        <li key={i}>{alt}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dietary Analysis */}
      {dietary.result && (
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3">Dietary Analysis</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Dietary Profile</h4>
              <ul className="space-y-1 text-sm">
                {Object.entries(dietary.result.dietaryProfile).map(([diet, isCompatible]) => (
                  <li key={diet} className={isCompatible ? 'text-green-600' : 'text-red-600'}>
                    {diet}: {isCompatible ? '✓' : '✗'}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Dietary Alternatives</h4>
              <div className="text-sm">
                {Object.entries(dietary.result.alternatives?.dietary || {}).map(([ingredient, alternatives]) => (
                  <div key={ingredient} className="mb-2">
                    <span className="font-medium">{ingredient}:</span>
                    <ul className="list-disc list-inside ml-2">
                      {alternatives.map((alt, i) => (
                        <li key={i}>{alt}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Processing Information */}
      {(nutrition.result?.processedBy || []).length > 0 && (
        <div className="p-4 bg-gray-50 rounded text-sm">
          <h4 className="font-medium mb-2">Processing Information</h4>
          <ul className="space-y-1">
            {nutrition.result?.processedBy.map((processor, i) => (
              <li key={i}>
                {processor.actorName} (Confidence: {(processor.confidence * 100).toFixed(1)}%) - 
                {new Date(processor.timestamp).toLocaleString()}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
} 