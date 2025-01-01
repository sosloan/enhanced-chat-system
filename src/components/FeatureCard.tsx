import React from 'react';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  iconColor: string;
  iconBgColor: string;
}

export function FeatureCard({ icon: Icon, title, description, iconColor, iconBgColor }: FeatureCardProps) {
  return (
    <div className="bg-gray-800/50 p-8 rounded-xl backdrop-blur-sm border border-gray-700">
      <div className={`${iconBgColor} w-12 h-12 flex items-center justify-center rounded-lg mb-4`}>
        <Icon className={`w-6 h-6 ${iconColor}`} />
      </div>
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}