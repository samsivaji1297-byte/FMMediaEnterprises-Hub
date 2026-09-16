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

  const prompt = `Convert this raw input into 3 social media dispatches and 1 visual card layout.
Seed: "${rawText}"
Signal Type: "${type}"

Output strictly valid JSON matching this structure:
{
  "dispatches": [
    { "platform": "Twitter", "content": "..." },
    { "platform": "LinkedIn", "content": "..." },
    { "platform": "Substack", "content": "..." }
  ],
  "visual_card": {
    "meta": { "aspectRatio": "4:5", "width": 1080, "height": 1350 },
    "styles": {
      "backgroundColor": "#0D1117",
      "accentColor": "#0066FF",
      "textColor": "#F0F6FC",
      "mutedTextColor": "#8B949E"
    },
    "content": {
      "badge": "PROTOCOL SIGNAL",
      "headline": "Punchy Summary Hook",
      "body": "Core takeaway message.",
      "footer": "COMMANDHUB // AUTOMATED DISPATCH",
      "author": "@SOVEREIGN"
    }
  }
}`;

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

  console.log("[Engine Log] Raw Gemini Payload:", rawTextResponse);

  let geminiOutput = {};
  try {
    const cleaned = rawTextResponse.replace(/```json|```/gi, "").trim();
    geminiOutput = JSON.parse(cleaned);
  } catch (err) {
    console.error("[Engine Error] JSON Parse failed:", err);
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

      console.log(`[Engine] Visual Card rendered: MemoryVault/media/${imageFilename}`);
      mediaUrl = `./MemoryVault/media/${imageFilename}`;
    } catch (renderErr) {
      console.error("[Engine Error] Render failed:", renderErr);
    }
  } else {
    console.warn("[Engine Warning] No 'visual_card' key found in JSON response.");
  }

  // Extract dispatches
  let dispatches = Array.isArray(geminiOutput.dispatches) ? geminiOutput.dispatches : [];
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
