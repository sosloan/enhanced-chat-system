import React from 'react';

interface ProgressProps {
  value: number;  // 0-100
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({ value, className = '' }) => {
  // Ensure value is between 0-100
  const normalizedValue = Math.min(100, Math.max(0, value));
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div
        className="bg-violet-600 h-2.5 rounded-full transition-all duration-300 ease-in-out"
        style={{ width: `${normalizedValue}%` }}
        role="progressbar"
        aria-valuenow={normalizedValue}
        aria-valuemin={0}
        aria-valuemax={100}
      />
    </div>
  );
}; 