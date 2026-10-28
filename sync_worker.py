import os
from groq import Groq

def run_sync_worker():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")
        
    client = Groq(api_key=api_key)
    
    prompt = """
    Generate 3 distinct, high-leverage micro-niches for evergreen human demand (mindset, operator autonomy, and cognitive efficiency).
    For each niche, provide:
    1. Target Niche Title
    2. Core Pain Point / Problem
    3. High-Leverage Strategic Angle
    
    Keep it sharp, clinical, and actionable. No conversational filler or introductory text.
    """
    
    print("Executing system synchronization protocol via Groq LPU...")
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a ruthless sovereign market strategist and operator architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    
    print("\n================ SYSTEM OUTPUT ================\n")
    print(completion.choices[0].message.content)
    print("\n===============================================\n")

if __name__ == "__main__":
    run_sync_worker()
