import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface ProgressVisualizationProps {
  progress: number;  // 0-100
  className?: string;
}

export const ProgressVisualization: React.FC<ProgressVisualizationProps> = ({ 
  progress,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const normalizedProgress = Math.min(100, Math.max(0, progress)) / 100;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set up canvas
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Draw progress visualization
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.4;

    // Draw background circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 10;
    ctx.stroke();

    // Draw progress arc
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, (-Math.PI / 2) + (Math.PI * 2 * normalizedProgress));
    ctx.strokeStyle = '#7c3aed';
    ctx.lineWidth = 10;
    ctx.stroke();

    // Draw percentage text
    ctx.font = 'bold 24px Inter';
    ctx.fillStyle = '#1f2937';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${Math.round(progress)}%`, centerX, centerY);
  }, [progress, normalizedProgress]);

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        width={200}
        height={200}
        className="w-full max-w-[200px] mx-auto"
      />
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ 
          scale: normalizedProgress >= 1 ? 1.1 : 0.8,
          opacity: normalizedProgress >= 1 ? 1 : 0
        }}
        transition={{ duration: 0.3 }}
      >
        {normalizedProgress >= 1 && (
          <div className="text-green-500 text-4xl">✓</div>
        )}
      </motion.div>
    </div>
  );
}; 