import random

def get_raw_trend():
    try:
        from pytrends.request import TrendReq
        regions = ['united_states', 'united_kingdom', 'canada', 'australia', 'india']
        pytrends = TrendReq(hl='en-US', tz=360)
        trends = pytrends.trending_searches(pn=random.choice(regions)).head(15)[0].tolist()
        return random.choice(trends).title()
    except Exception:
        return "Artificial Intelligence advancements"

def generate_viral_title_with_local_llm(raw_topic: str) -> str:
    try:
        from utility.llm.local_llm_client import generate_local_response
        
        system_prompt = (
            "You are an expert YouTube and TikTok viral content strategist in 2026. "
            "Generate ONE highly clickable, viral video title based on the user's topic. "
            "GOLDEN RULES: 1. Curiosity Gap. 2. Specificity (use numbers). 3. Emotional trigger. "
            "4. Brevity (under 60 characters). 5. No misleading clickbait. "
            "OUTPUT FORMAT: Return ONLY the title. No quotes, no explanations."
        )
        
        title = generate_local_response(system_prompt, f"Generate a viral video title about: {raw_topic}")
        
        if len(title) < 10 or len(title) > 80:
            raise ValueError("Generated title length is out of bounds.")
            
        return title

    except Exception as e:
        print(f"⚠️ Local LLM generation failed ({e}). Falling back to rule-based generator.")
        return _fallback_viral_title(raw_topic)

def _fallback_viral_title(raw_topic: str) -> str:
    templates = [
        f"The SHOCKING Truth About {raw_topic} Nobody Talks About",
        f"7 Mind-Blowing Facts About {raw_topic} You Won't Believe",
        f"Why Everyone Is Suddenly Obsessed With {raw_topic}",
        f"The Dark Side of {raw_topic} Exposed",
        f"I Tried {raw_topic} for 24 Hours and This Happened"
    ]
    return random.choice(templates)
