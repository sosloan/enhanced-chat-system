import asyncio
import json
import aiofiles
from src.lib.youtube_processor import YouTubeProcessor

# List of YouTube URLs to process
URLS = [
    # Add your YouTube URLs here
    "https://www.youtube.com/watch?v=example1",
    "https://www.youtube.com/watch?v=example2"
]

async def process_videos():
    # Initialize processor with 3 concurrent downloads
    processor = YouTubeProcessor(max_concurrent=3)
    
    print(f"Starting parallel processing of {len(URLS)} videos...")
    results = await processor.process_urls(URLS)
    
    # Save detailed results
    async with aiofiles.open("video_analysis_detailed.json", "w") as f:
        await f.write(json.dumps({
            "total_videos": len(results),
            "timestamp": str(asyncio.get_event_loop().time()),
            "results": results
        }, indent=2))
    
    # Print summary
    print("\nProcessing complete!")
    print(f"Successfully processed: {len([r for r in results if 'error' not in r])} videos")
    print(f"Failed: {len([r for r in results if 'error' in r])} videos")
    
    # Print any errors
    errors = [(i, r["error"]) for i, r in enumerate(results) if "error" in r]
    if errors:
        print("\nErrors encountered:")
        for idx, error in errors:
            print(f"Video {idx + 1}: {error}")
    
    print("\nDetailed results saved to video_analysis_detailed.json")

if __name__ == "__main__":
    asyncio.run(process_videos()) 