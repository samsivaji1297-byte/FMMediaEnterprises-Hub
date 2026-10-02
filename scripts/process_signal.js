const fs = require('fs');
const path = require('path');
const { renderCard } = require('../CanvasEngine/canvas_renderer');

// --- Path Configurations ---
const PROJECT_ROOT = path.resolve(__dirname, '..');
const MEDIA_DIR = path.join(PROJECT_ROOT, 'MemoryVault', 'media');
const FEED_PATH = path.join(PROJECT_ROOT, 'MemoryVault', 'dashboard_feed.json');

// --- Model Cascade Configuration ---
const MODEL_CASCADE = [
  "gemini-3.5-flash",
  "gemini-3.6-flash",
  "gemini-3.7-flash",
  "gemini-3.8-flash"
];

/**
 * Utility delay with randomized jitter for exponential backoff.
 */
function sleep(ms) {
  const jitter = Math.floor(Math.random() * 200);
  return new Promise((resolve) => setTimeout(resolve, ms + jitter));
}

/**
 * Executes Gemini API request with model fallback cascade and backoff.
 */
async function callGeminiWithFallback(apiKey, prompt, schema) {
  let lastError = null;

  for (const model of MODEL_CASCADE) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    const payload = {
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: schema
      }
    };

    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        console.log(`[Signal Engine] Calling model: ${model} (Attempt ${attempt})`);
        
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (response.status === 429 || response.status >= 500) {
          const backoff = Math.pow(2, attempt) * 1000;
          console.warn(`[Signal Engine Warning] HTTP ${response.status} from ${model}. Retrying in ${backoff}ms...`);
          await sleep(backoff);
          continue;
        }

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errText}`);
        }

        const data = await response.json();
        const rawTextResponse = data.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!rawTextResponse) {
          throw new Error("Empty candidate payload received from Gemini API");
        }

        return JSON.parse(rawTextResponse);
      } catch (err) {
        lastError = err;
        console.warn(`[Signal Engine Warning] Attempt ${attempt} on ${model} failed: ${err.message}`);
        await sleep(1000 * attempt);
      }
    }
    console.warn(`[Signal Engine Warning] Model ${model} exhausted. Cascading to next model...`);
  }

  throw new Error(`All model fallbacks exhausted. Last error: ${lastError?.message}`);
}

/**
 * Schema definition for signal dispatches and visual card layout.
 */
const RESPONSE_SCHEMA = {
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
};

async function generate() {
  const apiKey = process.env.GEMINI_API_KEY;
  const rawText = process.env.RAW_TEXT;
  const type = process.env.SIGNAL_TYPE || "content_dispatch";

  if (!apiKey) {
    console.error("[Signal Engine Fatal] GEMINI_API_KEY secret is missing!");
    process.exit(1);
  }

  if (!rawText) {
    console.error("[Signal Engine Fatal] RAW_TEXT environment variable is empty!");
    process.exit(1);
  }

  const prompt = `Convert this seed into social media dispatches and a visual card layout: "${rawText}" (Type: "${type}")`;

  // --- API Call with Fallback Cascade ---
  let geminiOutput = {};
  try {
    geminiOutput = await callGeminiWithFallback(apiKey, prompt, RESPONSE_SCHEMA);
  } catch (err) {
    console.error("[Signal Engine Error] Gemini API generation failed completely:", err);
    process.exit(1);
  }

  // --- Render Visual Card ---
  let mediaUrl = null;
  if (geminiOutput.visual_card) {
    try {
      const imageBuffer = await renderCard(geminiOutput.visual_card);
      const timestamp = Date.now();
      const imageFilename = `card_${timestamp}.png`;
      const mediaPath = path.join(MEDIA_DIR, imageFilename);

      fs.mkdirSync(MEDIA_DIR, { recursive: true });
      fs.writeFileSync(mediaPath, imageBuffer);

      console.log(`[Signal Engine] Visual Card successfully rendered: MemoryVault/media/${imageFilename}`);
      mediaUrl = `./MemoryVault/media/${imageFilename}`;
    } catch (renderErr) {
      console.error("[Signal Engine Error] Canvas rendering failed:", renderErr);
    }
  }

  // --- Process Dispatches & Feed Update ---
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

  let existingFeed = [];
  if (fs.existsSync(FEED_PATH)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(FEED_PATH, "utf8"));
      existingFeed = Array.isArray(parsed) ? parsed : (parsed.items || []);
    } catch (e) {
      console.warn("[Signal Engine Warning] Dashboard feed parse error. Resetting array.");
      existingFeed = [];
    }
  }

  const updatedFeed = [...validNewItems, ...existingFeed];
  
  // Ensure directory exists prior to writing feed
  fs.mkdirSync(path.dirname(FEED_PATH), { recursive: true });
  fs.writeFileSync(FEED_PATH, JSON.stringify(updatedFeed, null, 2));

  console.log(`[Signal Engine] Successfully appended ${validNewItems.length} dispatches to dashboard_feed.json.`);
}

generate().catch((err) => {
  console.error("[Signal Engine Fatal Error]:", err);
  process.exit(1);
});
