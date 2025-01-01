import React from 'react';
import { Zap, Code, Cpu } from 'lucide-react';
import { FeatureCard } from './FeatureCard';

const features = [
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Optimized for speed and performance, ensuring your applications run at peak efficiency.',
    iconColor: 'text-blue-400',
    iconBgColor: 'bg-blue-500/10'
  },
  {
    icon: Code,
    title: 'Clean Code',
    description: 'Write maintainable and scalable code with our modern development practices.',
    iconColor: 'text-emerald-400',
    iconBgColor: 'bg-emerald-500/10'
  },
  {
    icon: Cpu,
    title: 'Powerful Tools',
    description: 'Access a comprehensive suite of development tools to boost your productivity.',
    iconColor: 'text-purple-400',
    iconBgColor: 'bg-purple-500/10'
  }
];

export function Features() {
  return (
    <div className="container mx-auto px-4 py-20">
      <div className="grid md:grid-cols-3 gap-8">
        {features.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </div>
  );
}