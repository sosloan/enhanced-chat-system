import type { NextApiRequest, NextApiResponse } from 'next';
import { scrapeBlogPost } from '../../lib/modal';

type Data = {
  success: boolean;
  data?: any;
  error?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ success: false, error: 'URL is required' });
    }

    const result = await scrapeBlogPost(url);

    if (!result) {
      return res.status(404).json({ success: false, error: 'Failed to scrape blog post' });
    }

    return res.status(200).json({ success: true, data: result });
  } catch (error: any) {
    console.error('Error processing request:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message || 'Internal server error' 
    });
  }
} 