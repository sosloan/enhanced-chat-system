import { useState, useCallback, useMemo } from 'react'
import { Pipeline } from '../types/pipeline'
import { Recipe, RecipeAnalysis, MealPlan } from '../types/recipe'
import { 
  PipelineImpl, 
  RecipeProcessingActor,
  ActorSystemImpl 
} from '../lib/pipeline'
import {
  NutritionAnalysisActor,
  CookingTechniqueActor,
  SustainabilityActor,
  SeasonalityActor,
  DietaryAnalysisActor
} from '../lib/actors/specialized'
import {
  CuisineAnalysisActor,
  CookingMethodActor
} from '../lib/actors/cuisine'

interface ProcessResult {
  processedBy?: Array<{
    actorId: string
    actorName: string
    confidence: number
    timestamp: Date
  }>
  [key: string]: any
}

export const usePipeline = <T, U>(
  name: string,
  stages: Array<{
    name: string
    actor: string
  }>
) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [result, setResult] = useState<U | null>(null)

  // Initialize actor system with memoization
  const actorSystem = useMemo(() => {
    const system = new ActorSystemImpl()
    
    // Add specialized actors
    const actors = [
      new RecipeProcessingActor('recipe-processor', 'Recipe Processor'),
      new NutritionAnalysisActor('nutrition-analyzer', 'Nutrition Analyzer'),
      new CookingTechniqueActor('technique-analyzer', 'Cooking Technique Analyzer'),
      new SustainabilityActor('sustainability-analyzer', 'Sustainability Analyzer'),
      new SeasonalityActor('seasonality-analyzer', 'Seasonality Analyzer'),
      new DietaryAnalysisActor('dietary-analyzer', 'Dietary Analyzer'),
      new CuisineAnalysisActor('cuisine-analyzer', 'Cuisine Analyzer'),
      new CookingMethodActor('method-analyzer', 'Cooking Method Analyzer')
    ]
    
    actors.forEach(actor => system.addActor(actor))
    return system
  }, [])

  // Create pipeline stages with validation
  const pipelineStages = useMemo(() => stages.map(stage => ({
    name: stage.name,
    process: async (input: T): Promise<ProcessResult> => {
      const message = {
        type: 'PROCESS',
        payload: input,
        sender: 'pipeline',
        recipient: stage.actor,
        timestamp: new Date()
      }
      
      const result = await actorSystem.dispatch(message) as ProcessResult
      return {
        ...result,
        processedBy: [
          ...(result?.processedBy || []),
          {
            actorId: stage.actor,
            actorName: stage.name,
            confidence: actorSystem.actors.get(stage.actor)?.state.performance || 1,
            timestamp: new Date()
          }
        ]
      }
    },
    validate: (input: any) => {
      if (!input) return false
      
      // Add stage-specific validation
      switch (stage.actor) {
        case 'nutrition-analyzer':
          return input.ingredients?.length > 0
        case 'technique-analyzer':
        case 'method-analyzer':
          return input.instructions?.length > 0
        case 'sustainability-analyzer':
        case 'seasonality-analyzer':
        case 'dietary-analyzer':
          return input.ingredients?.length > 0
        case 'cuisine-analyzer':
          return input.ingredients?.length > 0 && input.instructions?.length > 0
        default:
          return true
      }
    },
    onError: (error: Error) => {
      console.error(`Error in stage ${stage.name}:`, error)
    }
  })), [stages, actorSystem])

  // Create pipeline instance
  const pipeline = useMemo(() => 
    new PipelineImpl<T, U>(name, pipelineStages), 
    [name, pipelineStages]
  )

  // Process function with error handling
  const process = useCallback(async (input: T) => {
    setLoading(true)
    setError(null)
    
    try {
      const output = await pipeline.process(input)
      setResult(output)
      return output
    } catch (err) {
      const error = err as Error
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [pipeline])

  return {
    process,
    loading,
    error,
    result,
    actorSystem // Expose actor system for advanced usage
  }
}

// Specialized hooks for different pipeline types
export const useRecipeProcessingPipeline = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Recipe Processing', [
    { name: 'Initial Processing', actor: 'recipe-processor' },
    { name: 'Nutrition Analysis', actor: 'nutrition-analyzer' },
    { name: 'Cooking Technique Analysis', actor: 'technique-analyzer' },
    { name: 'Cuisine Analysis', actor: 'cuisine-analyzer' },
    { name: 'Cooking Method Analysis', actor: 'method-analyzer' },
    { name: 'Sustainability Analysis', actor: 'sustainability-analyzer' },
    { name: 'Seasonality Analysis', actor: 'seasonality-analyzer' },
    { name: 'Dietary Analysis', actor: 'dietary-analyzer' }
  ])
}

export const useMealPlanPipeline = () => {
  return usePipeline<Recipe[], MealPlan>('Meal Planning', [
    { name: 'Recipe Collection', actor: 'recipe-processor' },
    { name: 'Nutritional Analysis', actor: 'nutrition-analyzer' },
    { name: 'Cuisine Compatibility', actor: 'cuisine-analyzer' },
    { name: 'Cooking Method Optimization', actor: 'method-analyzer' },
    { name: 'Sustainability Check', actor: 'sustainability-analyzer' },
    { name: 'Seasonal Optimization', actor: 'seasonality-analyzer' },
    { name: 'Dietary Compatibility', actor: 'dietary-analyzer' }
  ])
}

// Advanced hooks for specific analysis types
export const useNutritionAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Nutrition Analysis', [
    { name: 'Nutrition Analysis', actor: 'nutrition-analyzer' }
  ])
}

export const useSustainabilityAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Sustainability Analysis', [
    { name: 'Sustainability Analysis', actor: 'sustainability-analyzer' }
  ])
}

export const useSeasonalityAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Seasonality Analysis', [
    { name: 'Seasonality Analysis', actor: 'seasonality-analyzer' }
  ])
}

export const useDietaryAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Dietary Analysis', [
    { name: 'Dietary Analysis', actor: 'dietary-analyzer' }
  ])
}

export const useCuisineAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Cuisine Analysis', [
    { name: 'Cuisine Analysis', actor: 'cuisine-analyzer' }
  ])
}

export const useCookingMethodAnalysis = () => {
  return usePipeline<Recipe, RecipeAnalysis>('Cooking Method Analysis', [
    { name: 'Cooking Method Analysis', actor: 'method-analyzer' }
  ])
} 