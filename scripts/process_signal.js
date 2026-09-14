const fs = require("fs");

async function generate() {
  const apiKey = process.env.GEMINI_API_KEY;
  const rawText = process.env.RAW_TEXT;
  const type = process.env.SIGNAL_TYPE;

  if (!apiKey) {
    console.error("GEMINI_API_KEY secret is missing!");
    process.exit(1);
  }

  const prompt = `You are a content transformation engine. Convert this raw seed into 3 platform dispatches: Substack, Twitter, and LinkedIn.
Seed: "${rawText}"
Signal Type: "${type}"

Respond strictly with a JSON array of 3 objects containing: "id", "platform", "content", "created_at". No extra text.`;

  // Standard v1beta endpoint using gemini-1.5-flash for stable JSON response
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
  
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: "application/json"
      }
    })
  });

  const data = await response.json();
  console.log("Full Gemini API Response Structure:", JSON.stringify(data, null, 2));

  const rawTextResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "[]";
  console.log("Raw Gemini Text Output:", rawTextResponse);

  let newItems = [];
  try {
    newItems = JSON.parse(rawTextResponse);
  } catch (err) {
    const cleaned = rawTextResponse.replace(/```json|```/g, "").trim();
    newItems = JSON.parse(cleaned);
  }

  const validNewItems = Array.isArray(newItems) ? newItems : [];

  // Read existing feed safely
  const feedPath = "./MemoryVault/dashboard_feed.json";
  let existingFeed = [];
  if (fs.existsSync(feedPath)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(feedPath, "utf8"));
      if (Array.isArray(parsed)) existingFeed = parsed;
      else if (parsed && Array.isArray(parsed.items)) existingFeed = parsed.items;
    } catch (e) {
      existingFeed = [];
    }
  }

  const updatedFeed = [...validNewItems, ...existingFeed];
  fs.writeFileSync(feedPath, JSON.stringify(updatedFeed, null, 2));
  console.log(`Successfully appended ${validNewItems.length} dispatches.`);
}

generate().catch((err) => {
  console.error("Script Error:", err);
  process.exit(1);
});
