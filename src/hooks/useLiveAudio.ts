import { useState, useEffect, useCallback } from 'react';
import { LiveKitService } from '@/lib/livekit';
import { MockLiveKitService } from '@/lib/mock/livekit';
import { useTranscriptionCreate } from './useTranscriptions';

interface LiveAudioState {
  isConnected: boolean;
  isStreaming: boolean;
  currentTranscription: string;
  analysis: {
    sentiment: 'positive' | 'negative' | 'neutral';
    keywords: string[];
    summary: string;
  } | null;
}

// In a real app, this would come from environment variables
const USE_MOCK = true;

export function useLiveAudio(roomUrl: string, token: string) {
  const [state, setState] = useState<LiveAudioState>({
    isConnected: false,
    isStreaming: false,
    currentTranscription: '',
    analysis: null,
  });

  const createTranscription = useTranscriptionCreate();
  const [service, setService] = useState<LiveKitService | MockLiveKitService | null>(null);

  useEffect(() => {
    // Initialize service (real or mock)
    const ServiceClass = USE_MOCK ? MockLiveKitService : LiveKitService;
    const audioService = new ServiceClass(
      // Analysis callback
      (analysis) => {
        setState(prev => ({
          ...prev,
          analysis: {
            sentiment: analysis.sentiment,
            keywords: analysis.keywords,
            summary: analysis.summary
          }
        }));

        // Create transcription in database
        createTranscription.mutate({
          successfulCall: analysis.sentiment !== 'negative',
          classification: `LiveStream/${analysis.sentiment}`,
          filename: `live-stream-${Date.now()}.webm`
        });
      },
      // Transcription callback
      (text) => {
        setState(prev => ({
          ...prev,
          currentTranscription: text
        }));
      }
    );

    setService(audioService);

    return () => {
      audioService.disconnect();
    };
  }, [createTranscription]);

  const connect = useCallback(async () => {
    if (!service) return;

    try {
      await service.connect(roomUrl, token);
      setState(prev => ({ ...prev, isConnected: true }));
    } catch (error) {
      console.error('Failed to connect:', error);
      throw error;
    }
  }, [service, roomUrl, token]);

  const startStreaming = useCallback(async () => {
    if (!service) return;

    try {
      await service.startAudioStream();
      setState(prev => ({ ...prev, isStreaming: true }));
    } catch (error) {
      console.error('Failed to start streaming:', error);
      throw error;
    }
  }, [service]);

  const stopStreaming = useCallback(async () => {
    if (!service) return;

    try {
      await service.stopAudioStream();
      setState(prev => ({ ...prev, isStreaming: false }));
    } catch (error) {
      console.error('Failed to stop streaming:', error);
      throw error;
    }
  }, [service]);

  const disconnect = useCallback(() => {
    if (!service) return;

    service.disconnect();
    setState(prev => ({
      ...prev,
      isConnected: false,
      isStreaming: false
    }));
  }, [service]);

  return {
    ...state,
    connect,
    disconnect,
    startStreaming,
    stopStreaming
  };
} 