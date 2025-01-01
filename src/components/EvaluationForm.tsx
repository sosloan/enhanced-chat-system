import React, { useState, useCallback } from 'react';
import { useEvaluation } from '@/hooks/useEvaluation';
import { Progress } from '@/components/ui/Progress';
import { ProgressVisualization } from '@/components/ui/progress_visualization';
import { EvaluationResult } from '@/types';

interface EvaluationFormProps {
  onSubmit: (result: EvaluationResult) => void;
  isProcessing: boolean;
  progress: number;
}

export const EvaluationForm: React.FC<EvaluationFormProps> = ({
  onSubmit,
  isProcessing,
  progress
}) => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcriptText, setTranscriptText] = useState('');
  const { evaluateAudio, evaluateTranscript } = useEvaluation();

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  }, []);

  const handleTranscriptChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTranscriptText(e.target.value);
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    let result: EvaluationResult | null = null;
    
    if (audioFile) {
      result = await evaluateAudio(audioFile);
    } else if (transcriptText) {
      result = await evaluateTranscript(transcriptText);
    }
    
    if (result) {
      onSubmit(result);
    }
  }, [audioFile, transcriptText, evaluateAudio, evaluateTranscript, onSubmit]);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div>
          <label 
            htmlFor="audio-upload"
            className="block text-sm font-medium text-gray-700"
          >
            Upload Audio File
          </label>
          <input
            id="audio-upload"
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="mt-1 block w-full text-sm text-gray-500
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-violet-50 file:text-violet-700
                     hover:file:bg-violet-100"
          />
        </div>

        <div>
          <label 
            htmlFor="transcript"
            className="block text-sm font-medium text-gray-700"
          >
            Or Paste Transcript
          </label>
          <textarea
            id="transcript"
            rows={4}
            value={transcriptText}
            onChange={handleTranscriptChange}
            placeholder="Enter call transcript here..."
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm
                     focus:border-violet-500 focus:ring-violet-500"
          />
        </div>
      </div>

      {isProcessing && (
        <div className="space-y-4">
          <Progress value={progress} />
          <ProgressVisualization progress={progress} />
        </div>
      )}

      <button
        type="submit"
        disabled={isProcessing || (!audioFile && !transcriptText)}
        className="w-full flex justify-center py-2 px-4 border border-transparent
                 rounded-md shadow-sm text-sm font-medium text-white
                 bg-violet-600 hover:bg-violet-700 focus:outline-none
                 focus:ring-2 focus:ring-offset-2 focus:ring-violet-500
                 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isProcessing ? 'Processing...' : 'Evaluate'}
      </button>
    </form>
  );
}; 