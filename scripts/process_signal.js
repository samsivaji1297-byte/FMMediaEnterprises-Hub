const fs = require("fs");

async function generate() {
  const apiKey = process.env.GEMINI_API_KEY;
  const rawText = process.env.RAW_TEXT;
  const type = process.env.SIGNAL_TYPE || "content_dispatch";

  if (!apiKey) {
    console.error("GEMINI_API_KEY secret is missing!");
    process.exit(1);
  }

  const prompt = `You are a content transformation engine. Convert this raw seed into 3 social media dispatches for Substack, Twitter/X, and LinkedIn.
Seed: "${rawText}"
Signal Type: "${type}"

Respond strictly with a JSON array of 3 objects with keys: "platform", "content". Do not include extra text or markdown backticks.`;

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${apiKey}`;

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
  const rawTextResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "[]";

  let newItems = [];
  try {
    newItems = JSON.parse(rawTextResponse);
  } catch (err) {
    const cleaned = rawTextResponse.replace(/```json|```/g, "").trim();
    newItems = JSON.parse(cleaned);
  }

  const now = new Date();
  const timestamp = now.getTime();
  const isoDate = now.toISOString();

  // Guarantee unique IDs and real-time timestamps
  const validNewItems = (Array.isArray(newItems) ? newItems : []).map((item, index) => {
    const prefix = item.platform ? item.platform.toLowerCase().replace(/[^a-z]/g, "") : "post";
    return {
      id: `${prefix}_${timestamp}_${index}`,
      platform: item.platform || "Platform",
      content: item.content || "",
      created_at: isoDate
    };
  });

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
  console.log(`Successfully appended ${validNewItems.length} unique dispatches.`);
}

generate().catch((err) => {
  console.error("Script Execution Error:", err);
  process.exit(1);
});
