import { NextApiRequest, NextApiResponse } from 'next';
import formidable, { Fields, Files } from 'formidable';
import { OpenAI } from 'openai';
import { AudioAnalysis } from '@/types/audio';
import { createReadStream } from 'fs';

// Configure OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export const config = {
  api: {
    bodyParser: false,
  },
};

interface WhisperResponse {
  text: string;
  segments?: Array<{
    start: number;
    end: number;
    text: string;
  }>;
  duration?: number;
}

interface AnalysisResponse {
  quality_score: number;
  sentiment_score: number;
  clarity_score: number;
  engagement_score: number;
  professionalism_score: number;
  summary: string;
  keywords: string[];
  suggestions: string[];
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Parse form data
    const form = formidable();
    const [fields, files]: [Fields, Files] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const audioFile = files.audio?.[0];
    if (!audioFile) {
      return res.status(400).json({ error: 'No audio file provided' });
    }

    // Get options if provided
    const options = fields.options ? JSON.parse(fields.options[0]) : {};

    // Transcribe audio using Whisper
    const transcription = await openai.audio.transcriptions.create({
      file: createReadStream(audioFile.filepath),
      model: 'whisper-1',
      language: 'en',
      response_format: 'verbose_json',
      timestamp_granularities: ['segment']
    }) as unknown as WhisperResponse;

    // Analyze transcription using GPT-4
    const analysis = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: `Analyze the following call center conversation transcript and provide:
1. Overall quality score (0-100)
2. Sentiment score (0-100)
3. Clarity score (0-100)
4. Engagement score (0-100)
5. Professionalism score (0-100)
6. Brief summary
7. Key topics/keywords
8. Improvement suggestions
Format the response as JSON.`
        },
        {
          role: 'user',
          content: transcription.text
        }
      ],
      response_format: { type: 'json_object' }
    });

    const result = JSON.parse(analysis.choices[0]?.message?.content || '{}') as AnalysisResponse;

    // Calculate audio quality metrics
    const audioMetrics = {
      duration: typeof transcription.duration === 'number' ? transcription.duration : 0,
      snr: calculateSNR(audioFile),
      clarity: calculateClarity(audioFile)
    };

    // Format response
    const response: AudioAnalysis = {
      score: result.quality_score,
      sentiment: result.sentiment_score,
      clarity: result.clarity_score,
      engagement: result.engagement_score,
      professionalism: result.professionalism_score,
      summary: result.summary,
      keywords: result.keywords,
      suggestions: result.suggestions,
      transcript: {
        text: transcription.text,
        segments: (transcription.segments || []).map(segment => ({
          start: segment.start,
          end: segment.end,
          text: segment.text
        }))
      },
      duration: audioMetrics.duration,
      snr: audioMetrics.snr
    };

    res.status(200).json(response);
  } catch (error) {
    console.error('Error processing audio:', error);
    res.status(500).json({ error: 'Failed to process audio' });
  }
}

// Audio quality analysis functions
function calculateSNR(audioFile: formidable.File): number {
  // Implement SNR calculation
  // This is a placeholder - you would need to implement actual audio analysis
  return 75;
}

function calculateClarity(audioFile: formidable.File): number {
  // Implement clarity calculation
  // This is a placeholder - you would need to implement actual audio analysis
  return 80;
} 