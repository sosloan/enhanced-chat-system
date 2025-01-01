import { useCallback } from 'react';
import { AudioAnalysis, AudioProcessorOptions } from '@/types/audio';

export const useAudioProcessor = () => {
  const processAudio = useCallback(async (file: File, options?: AudioProcessorOptions): Promise<AudioAnalysis> => {
    // Create form data with file and options
    const formData = new FormData();
    formData.append('audio', file);
    if (options) {
      formData.append('options', JSON.stringify(options));
    }

    // Send to API endpoint
    const response = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to process audio');
    }

    const result = await response.json();

    // Transform API response to AudioAnalysis format
    const analysis: AudioAnalysis = {
      score: result.score || 0,
      sentiment: result.sentiment || 0,
      clarity: result.clarity || 0,
      engagement: result.engagement || 0,
      professionalism: result.professionalism || 0,
      summary: result.summary || '',
      keywords: result.keywords || [],
      suggestions: result.suggestions || [],
      transcript: {
        text: result.transcript?.text || '',
        segments: result.transcript?.segments || []
      },
      duration: result.duration || 0,
      snr: result.snr || 0
    };

    return analysis;
  }, []);

  return {
    processAudio
  };
}; 