import React from 'react'
import type { Recipe } from '../types/recipe'
import type { CuisineProfile } from '../lib/actors/cuisine'

interface CuisineAnalysisProps {
  recipe: Recipe
  cuisineProfile?: CuisineProfile
}

const FlavorProfileChart: React.FC<{ profile: CuisineProfile['flavorProfile'] }> = ({ profile }) => {
  const maxValue = Math.max(...(Object.values(profile) as number[]))
  const normalizedProfile = Object.entries(profile).map(([key, value]) => ({
    name: key,
    value: value as number,
    percentage: ((value as number) / maxValue) * 100
  }))

  return (
    <div className="space-y-2">
      {normalizedProfile.map(({ name, value, percentage }) => (
        <div key={name} className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="capitalize">{name}</span>
            <span>{value.toFixed(2)}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-500"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

export const CuisineAnalysis: React.FC<CuisineAnalysisProps> = ({
  recipe,
  cuisineProfile
}) => {
  if (!cuisineProfile) return null

  return (
    <div className="space-y-6">
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Cuisine Analysis</h3>
        
        {/* Primary Cuisine */}
        <div className="mb-6">
          <h4 className="font-medium mb-2">Primary Cuisine</h4>
          <div className="flex items-center space-x-4">
            <span className="text-xl capitalize">{cuisineProfile.primaryCuisine}</span>
            <div className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
              {(cuisineProfile.authenticityScore * 100).toFixed(0)}% Authentic
            </div>
          </div>
        </div>

        {/* Secondary Cuisines */}
        {cuisineProfile.secondaryCuisines.length > 0 && (
          <div className="mb-6">
            <h4 className="font-medium mb-2">Fusion Influences</h4>
            <div className="flex flex-wrap gap-2">
              {cuisineProfile.secondaryCuisines.map((cuisine: string) => (
                <span
                  key={cuisine}
                  className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm capitalize"
                >
                  {cuisine}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Regional Variations */}
        {cuisineProfile.regionalVariations.length > 0 && (
          <div className="mb-6">
            <h4 className="font-medium mb-2">Regional Variations</h4>
            <div className="grid grid-cols-2 gap-4">
              {cuisineProfile.regionalVariations.map((variation: string) => (
                <div
                  key={variation}
                  className="p-2 border border-gray-200 rounded text-sm"
                >
                  {variation}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ingredients Analysis */}
        <div className="mb-6">
          <h4 className="font-medium mb-2">Ingredients Analysis</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h5 className="text-sm font-medium mb-1">Traditional Ingredients</h5>
              <ul className="text-sm list-disc list-inside">
                {cuisineProfile.traditionalIngredients.map((ingredient: string) => (
                  <li key={ingredient}>{ingredient}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 className="text-sm font-medium mb-1">Modern Adaptations</h5>
              <ul className="text-sm list-disc list-inside">
                {cuisineProfile.modernAdaptations.map((ingredient: string) => (
                  <li key={ingredient}>{ingredient}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Flavor Profile */}
        <div>
          <h4 className="font-medium mb-2">Flavor Profile</h4>
          <FlavorProfileChart profile={cuisineProfile.flavorProfile} />
        </div>
      </div>

      {/* Authenticity Tips */}
      <div className="p-4 bg-white rounded-lg shadow">
        <h4 className="font-medium mb-2">Authenticity Enhancement</h4>
        <div className="space-y-2">
          {cuisineProfile.authenticityScore < 0.7 && (
            <div className="p-3 bg-yellow-50 text-yellow-800 rounded">
              <p className="text-sm">
                This recipe shows some modern adaptations. To make it more authentic:
              </p>
              <ul className="mt-2 text-sm list-disc list-inside">
                <li>Consider using more traditional ingredients</li>
                <li>Follow traditional cooking methods</li>
                <li>Adjust seasoning to match regional preferences</li>
              </ul>
            </div>
          )}
          
          {cuisineProfile.authenticityScore >= 0.7 && (
            <div className="p-3 bg-green-50 text-green-800 rounded">
              <p className="text-sm">
                This recipe shows strong authenticity to {cuisineProfile.primaryCuisine} cuisine!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Regional Insights */}
      <div className="p-4 bg-white rounded-lg shadow">
        <h4 className="font-medium mb-2">Regional Insights</h4>
        <div className="grid grid-cols-2 gap-4">
          {cuisineProfile.regionalVariations.map((region: string) => (
            <div key={region} className="p-3 border border-gray-200 rounded">
              <h5 className="text-sm font-medium mb-1">{region}</h5>
              <p className="text-sm text-gray-600">
                This recipe could be adapted to {region} style by adjusting spices and cooking methods.
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Fusion Opportunities */}
      {cuisineProfile.secondaryCuisines.length > 0 && (
        <div className="p-4 bg-white rounded-lg shadow">
          <h4 className="font-medium mb-2">Fusion Opportunities</h4>
          <div className="space-y-3">
            {cuisineProfile.secondaryCuisines.map((cuisine: string) => (
              <div key={cuisine} className="p-3 border border-gray-200 rounded">
                <h5 className="text-sm font-medium mb-1 capitalize">{cuisine} Fusion</h5>
                <p className="text-sm text-gray-600">
                  This recipe already shows influence from {cuisine} cuisine. 
                  Consider enhancing these elements for an interesting fusion dish.
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 