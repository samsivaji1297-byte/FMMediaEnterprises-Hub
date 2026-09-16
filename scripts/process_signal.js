const fs = require('fs');
const path = require('path');
const { renderCard } = require('../CanvasEngine/canvas_renderer');

async function generate() {
  const apiKey = process.env.GEMINI_API_KEY;
  const rawText = process.env.RAW_TEXT;
  const type = process.env.SIGNAL_TYPE || "content_dispatch";

  if (!apiKey) {
    console.error("GEMINI_API_KEY secret is missing!");
    process.exit(1);
  }

  const canvasSchemaInstructions = `
In addition to text dispatches, output a "visual_card" JSON object adhering strictly to this layout schema:
{
  "meta": { "aspectRatio": "4:5", "width": 1080, "height": 1350 },
  "styles": {
    "backgroundColor": "#0D1117",
    "accentColor": "#0066FF",
    "textColor": "#F0F6FC",
    "mutedTextColor": "#8B949E"
  },
  "content": {
    "badge": "PROTOCOL SIGNAL",
    "headline": "<Punchy, 12 high-impact hook max summary, words>",
    "body": "<Core 30 insight key max or takeaway, words>",
    "footer": "COMMANDHUB // AUTOMATED DISPATCH",
    "author": "@SOVEREIGN"
  }
}
`;

  const prompt = `You are a content transformation engine. Convert this raw seed into 3 social media dispatches for Substack, Twitter/X, and LinkedIn.
Seed: "${rawText}"
Signal Type: "${type}"

${canvasSchemaInstructions}

Respond strictly with a single JSON object containing:
1. "dispatches": an array of 3 objects, each with keys "platform" and "content".
2. "visual_card": the visual card layout JSON object described above.

Do not include extra conversational text outside the JSON.`;

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

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
  const rawTextResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";

  let geminiOutput = {};
  try {
    const cleaned = rawTextResponse.replace(/```json/gi, "").replace(/```/g, "").trim();
    geminiOutput = JSON.parse(cleaned);
  } catch (err) {
    console.error("[Engine] Failed to parse JSON response:", err);
  }

  // --- Render Visual Card ---
  let mediaUrl = null;
  if (geminiOutput.visual_card) {
    try {
      const imageBuffer = renderCard(geminiOutput.visual_card);
      const imageFilename = `card_${Date.now()}.png`;
      const mediaPath = path.join(__dirname, '..', 'MemoryVault', 'media', imageFilename);

      fs.mkdirSync(path.dirname(mediaPath), { recursive: true });
      fs.writeFileSync(mediaPath, imageBuffer);

      console.log(`[Engine] Visual Card rendered: /MemoryVault/media/${imageFilename}`);
      mediaUrl = `./MemoryVault/media/${imageFilename}`;
    } catch (renderErr) {
      console.error("[Engine] Rendering error:", renderErr);
    }
  }

  // Robust fallback resolution for dispatches array
  let dispatches = [];
  if (Array.isArray(geminiOutput.dispatches)) {
    dispatches = geminiOutput.dispatches;
  } else if (Array.isArray(geminiOutput)) {
    dispatches = geminiOutput;
  }

  const now = new Date();
  const timestamp = now.getTime();
  const isoDate = now.toISOString();

  const validNewItems = dispatches.map((item, index) => {
    const prefix = item.platform ? item.platform.toLowerCase().replace(/[^a-z]/g, "") : "post";
    return {
      id: `${prefix}_${timestamp}_${index}`,
      platform: item.platform || "Platform",
      content: item.content || "",
      media_url: mediaUrl,
      created_at: isoDate
    };
  });

  const feedPath = path.join(__dirname, '..', 'MemoryVault', 'dashboard_feed.json');
  let existingFeed = [];
  if (fs.existsSync(feedPath)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(feedPath, "utf8"));
      existingFeed = Array.isArray(parsed) ? parsed : (parsed.items || []);
    } catch (e) {
      existingFeed = [];
    }
  }

  const updatedFeed = [...validNewItems, ...existingFeed];
  fs.writeFileSync(feedPath, JSON.stringify(updatedFeed, null, 2));
  console.log(`[Engine] Successfully appended ${validNewItems.length} unique dispatches.`);
}

generate().catch((err) => {
  console.error("Script Execution Error:", err);
  process.exit(1);
});
