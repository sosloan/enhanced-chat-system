import { useState, useCallback } from 'react';
import { EvaluationResult } from '@/types';
import { AudioAnalysis } from '@/types/audio';
import { useAudioProcessor } from './useAudioProcessor';

export const useEvaluation = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const { processAudio } = useAudioProcessor();

  const evaluateAudio = useCallback(async (file: File): Promise<EvaluationResult> => {
    setIsProcessing(true);
    try {
      const result: AudioAnalysis = await processAudio(file);
      
      // Process the audio analysis result into EvaluationResult format
      const evaluationResult: EvaluationResult = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        score: result.score,
        metrics: {
          sentiment: result.sentiment,
          clarity: result.clarity,
          engagement: result.engagement,
          professionalism: result.professionalism
        },
        analysis: {
          summary: result.summary,
          keywords: result.keywords,
          suggestions: result.suggestions
        },
        transcript: result.transcript,
        audio: {
          duration: result.duration,
          format: file.type,
          quality: {
            snr: result.snr,
            clarity: result.clarity
          }
        }
      };

      return evaluationResult;
    } finally {
      setIsProcessing(false);
    }
  }, [processAudio]);

  const evaluateTranscript = useCallback(async (text: string): Promise<EvaluationResult> => {
    setIsProcessing(true);
    try {
      // Analyze the transcript text
      const analysis = await fetch('/api/analyze-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      }).then(res => res.json());

      const evaluationResult: EvaluationResult = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        score: analysis.score || 0,
        metrics: {
          sentiment: analysis.sentiment || 0,
          clarity: analysis.clarity || 0,
          engagement: analysis.engagement || 0,
          professionalism: analysis.professionalism || 0
        },
        analysis: {
          summary: analysis.summary || '',
          keywords: analysis.keywords || [],
          suggestions: analysis.suggestions || []
        },
        transcript: {
          text,
          segments: [{
            start: 0,
            end: text.length,
            text
          }]
        }
      };

      return evaluationResult;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return {
    isProcessing,
    evaluateAudio,
    evaluateTranscript
  };
}; 