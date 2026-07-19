import os
from utility.llm.local_llm_client import generate_local_response

def generate_metadata(topic, script):
    print("\n--- STAGE 7: Generating Upload Metadata (2026 Standards) ---")
    os.makedirs("metadata", exist_ok=True)
    
    print("Generating YouTube metadata...")
    
    # YouTube Title (Under 60 characters, Curiosity Gap)
    prompt = (
        "You are a YouTube SEO expert in 2026. The algorithm favors high CTR and retention. "
        "Generate a highly clickable, SEO-optimized title. "
        "Rules: Under 60 characters, use curiosity gap, specific numbers, or emotional triggers. "
        "No misleading clickbait. Return ONLY the title, nothing else."
    )
    yt_title = generate_local_response(prompt, f"Video topic: {topic}")
    save_to_file("metadata/youtube_title.txt", yt_title)
    
    # YouTube Description (Hook in first 2 lines, 3 hashtags max)
    prompt = (
        "You are a YouTube expert. Generate a description optimized for 2026 search. "
        "Rules: "
        "1. First 2 lines must be a strong hook containing main keywords. "
        "2. Brief summary of the video. "
        "3. Call to action (Subscribe). "
        "4. Exactly 3 relevant hashtags at the end (YouTube only shows first 3 above title). "
        "Return formatted text."
    )
    yt_desc = generate_local_response(prompt, f"Video topic: {topic}\nScript context: {script[:300]}...")
    save_to_file("metadata/youtube_description.txt", yt_desc)
    
    # YouTube Tags (One tag per line, mix of short and long-tail)
    prompt = (
        "Generate 12 highly relevant SEO tags for a YouTube video. "
        "Rules: "
        "1. Each tag on a separate line. "
        "2. Mix of short tags (2-3 words) and long-tail tags (4-6 words). "
        "3. Include niche-specific and trending tags. "
        "4. No spam or irrelevant tags. "
        "Return ONLY the tags, one per line, no numbering."
    )
    yt_tags = generate_local_response(prompt, f"Video topic: {topic}")
    save_to_file("metadata/youtube_tags.txt", yt_tags)
    
    # YouTube Category (Single best category)
    prompt = (
        "Suggest the single best YouTube category for this video. "
        "Return ONLY the category name. Options: Education, Entertainment, Science & Technology, "
        "People & Blogs, News & Politics, Howto & Style, Gaming, Sports, Music, Film & Animation."
    )
    yt_category = generate_local_response(prompt, f"Video topic: {topic}")
    save_to_file("metadata/youtube_category.txt", yt_category)
    
    print("Generating TikTok metadata...")
    
    # TikTok Caption (Short, hook, max 5 hashtags)
    prompt = (
        "Generate a short, highly engaging TikTok caption for 2026. "
        "Rules: "
        "1. Hook in first line with emoji. "
        "2. Use 'Wait for...' or similar retention hack. "
        "3. Exactly 5 viral hashtags at the end. "
        "4. Mix: 2 niche + 2 viral + 1 platform-specific hashtag. "
        "Return ONLY the caption."
    )
    tt_caption = generate_local_response(prompt, f"Video topic: {topic}")
    save_to_file("metadata/tiktok_caption.txt", tt_caption)
    
    print("Generating Instagram metadata...")
    
    # Instagram Caption (List format, dual CTA, 10 hashtags)
    prompt = (
        "Generate an engaging Instagram Reels caption for 2026. "
        "Rules: "
        "1. Start with emoji and strong hook. "
        "2. Use numbered list with emojis for key points. "
        "3. Dual CTA: Ask for comment AND 'Save this for later'. "
        "4. Follow CTA. "
        "5. Exactly 10 relevant hashtags at the end (optimal for 2026 algorithm). "
        "Return formatted text with line breaks."
    )
    ig_caption = generate_local_response(prompt, f"Video topic: {topic}\nScript context: {script[:300]}...")
    save_to_file("metadata/instagram_caption.txt", ig_caption)
    
    print("All metadata saved to 'metadata/' folder.")
    print("Open each file to copy its content for uploading.")

def save_to_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
