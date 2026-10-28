import os
from pathlib import Path
from groq import Groq

def generate_reel_code():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")

    client = Groq(api_key=api_key)

    prompt = """
Write a single, complete, standalone HTML5 file for an Instagram Reel (9:16 aspect ratio).
Target theme: 'THE SOVEREIGN CIRCUIT — OPERATOR REEL'.

Design & Technical Requirements:
1. Strict self-contained HTML file (embed all CSS inside <style> and JS inside <script>).
2. Pure dark mode palette (#050505 background, emerald green #00FF87 highlights, electric white text, subtle grid/glow backdrop).
3. 9:16 Mobile Viewport Canvas (#st with max dimensions suited for 1080x1920, scaled with CSS custom properties --u).
4. Continuous 60fps requestAnimationFrame JavaScript animation loop (duration ~20 seconds).
5. Animation sequence:
   - Phase 1: High-impact line-mask reveal of hook text: "SYSTEM OVERRIDE: 3 LAWS OF OPERATOR AUTONOMY".
   - Phase 2: Sequential terminal typing effect of 3 core laws with glowing status badges ("LAW 01: ELIMINATE FRICTION", "LAW 02: REJECT DISTRACTION", "LAW 03: OWN THE ENGINE").
   - Phase 3: Premium floating card reveal showing "TIMELINE REJECTION PROTOCOL" ($97 VALUE) with price ticker animation.
   - Phase 4: Strong punchline reveal and CTA: "FOLLOW @THEFINALMINDSET".
6. Include subtle canvas noise/grain texture, radial glow background, and smooth cubic-bezier / spring easing math.

Output ONLY valid raw HTML code without markdown formatting or conversational text.
"""

    print("Requesting 60fps Reel Artifact Code from Groq LPU...")

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an elite creative technician and award-winning creative coder who writes pristine, high-performance HTML5 canvas/DOM motion design engines for mobile video production."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    code = completion.choices[0].message.content.strip()

    # Clean potential markdown block wrappers if present
    if code.startswith("```"):
        lines = code.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        code = "\n".join(lines).strip()

    output_path = Path("groq_reel_test.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n[Success] Reel HTML artifact saved to: {output_path.resolve()}")
    print("Open 'groq_reel_test.html' in your browser or phone to preview the animation!")

if __name__ == "__main__":
    generate_reel_code()
