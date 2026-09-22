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

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent?key=${apiKey}`;

  const prompt = `Convert this seed into social media dispatches and a visual card layout: "${rawText}" (Type: "${type}")`;

  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: {
        type: "OBJECT",
        properties: {
          dispatches: {
            type: "ARRAY",
            items: {
              type: "OBJECT",
              properties: {
                platform: { type: "STRING" },
                content: { type: "STRING" }
              },
              required: ["platform", "content"]
            }
          },
          visual_card: {
            type: "OBJECT",
            properties: {
              meta: {
                type: "OBJECT",
                properties: {
                  aspectRatio: { type: "STRING" },
                  width: { type: "INTEGER" },
                  height: { type: "INTEGER" }
                }
              },
              styles: {
                type: "OBJECT",
                properties: {
                  backgroundColor: { type: "STRING" },
                  accentColor: { type: "STRING" },
                  textColor: { type: "STRING" },
                  mutedTextColor: { type: "STRING" }
                }
              },
              content: {
                type: "OBJECT",
                properties: {
                  badge: { type: "STRING" },
                  headline: { type: "STRING" },
                  body: { type: "STRING" },
                  footer: { type: "STRING" },
                  author: { type: "STRING" }
                }
              }
            }
          }
        },
        required: ["dispatches", "visual_card"]
      }
    }
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  const rawTextResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";

  console.log("[Engine Log] Raw Gemini Payload:", rawTextResponse);

  let geminiOutput = {};
  try {
    geminiOutput = JSON.parse(rawTextResponse);
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
  }

  // Extract dispatches
  const dispatches = Array.isArray(geminiOutput.dispatches) ? geminiOutput.dispatches : [];
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
