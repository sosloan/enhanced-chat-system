import React from 'react';
import { ArrowRight } from 'lucide-react';

export function Hero() {
  return (
    <div className="container mx-auto px-4 py-20">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          Build Something Amazing
        </h1>
        <p className="text-xl text-gray-300 mb-8">
          Start your next project with our powerful and flexible development platform.
          Create, deploy, and scale with confidence.
        </p>
        <button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg inline-flex items-center gap-2 transition-colors">
          Get Started <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}