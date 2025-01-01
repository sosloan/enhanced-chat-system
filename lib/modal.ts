export interface BlogPost {
  title: string;
  author?: string;
  date?: string;
  content: string;
  url: string;
  sections: Array<{
    title: string;
    content: string[];
    code_snippets: Array<{
      code: string;
      language: string;
      section: string;
    }>;
  }>;
  ai_summary?: string;
  ai_topics?: string[];
  ai_difficulty?: string;
  reading_time_minutes?: number;
  research_results?: Array<{
    task: string;
    findings: string[];
    sources: string[];
    confidence: number;
    suggestions: string[];
    related_topics: string[];
  }>;
}

const MODAL_TOKEN = process.env.MODAL_TOKEN;
const MODAL_API_URL = process.env.MODAL_API_URL || 'https://api.modal.com/v1';

export async function scrapeBlogPost(url: string): Promise<BlogPost | null> {
  try {
    const response = await fetch(`${MODAL_API_URL}/functions/scrape_blog_post/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${MODAL_TOKEN}`,
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error(`Modal API error: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error scraping blog post:', error);
    return null;
  }
} 