import { NextApiRequest, NextApiResponse } from 'next';
import { OpenAI } from 'openai';

// Configure OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

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
    const { text } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'No transcript text provided' });
    }

    // Analyze transcript using GPT-4
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
          content: text
        }
      ],
      response_format: { type: 'json_object' }
    });

    const result = JSON.parse(analysis.choices[0]?.message?.content || '{}') as AnalysisResponse;

    // Format response
    const response = {
      score: result.quality_score,
      sentiment: result.sentiment_score,
      clarity: result.clarity_score,
      engagement: result.engagement_score,
      professionalism: result.professionalism_score,
      summary: result.summary,
      keywords: result.keywords,
      suggestions: result.suggestions
    };

    res.status(200).json(response);
  } catch (error) {
    console.error('Error analyzing transcript:', error);
    res.status(500).json({ error: 'Failed to analyze transcript' });
  }
} 