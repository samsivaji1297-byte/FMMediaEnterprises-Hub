const puppeteer = require('puppeteer');
const { GoogleGenAI, Type } = require('@google/genai');
const path = require('path');

// Initialize Gemini API (Uses GEMINI_API_KEY from environment variables)
const ai = new GoogleGenAI({});

/**
 * Step 1: Use Gemini to generate dynamic, high-converting carousel hooks
 */
async function generateCarouselHook() {
  console.log('Querying Gemini API for dynamic hook generation...');
  
  const prompt = `
    You are an expert Instagram content engineer creating high-converting carousel hooks.
    Generate a compelling, staccato carousel hook for a high-value digital system/framework product.
    
    Return JSON matching this exact structure:
    - mainText: High-impact uppercase title (2 to 4 words max, e.g., "BUILD A PRODUCT", "STOP WASTING TIME")
    - subText: Conversational opening lead-in (3 to 6 words max, e.g., "in 90 minutes using", "to unlock your first")
    - accentText: The core conversion trigger target (2 to 4 words max, e.g., "these 4 triggers", "zero-code pipeline")
  `;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          mainText: { type: Type.STRING },
          subText: { type: Type.STRING },
          accentText: { type: Type.STRING }
        },
        required: ['mainText', 'subText', 'accentText']
      }
    }
  });

  const hookData = JSON.parse(response.text);
  console.log('Generated Hook Data:', hookData);
  return hookData;
}

/**
 * Step 2: Inject AI payload into template.html and render exact 1080x1350 PNG
 */
async function renderCarouselSlide() {
  // 1. Get dynamic hook copy from Gemini
  const hookCopy = await generateCarouselHook();

  console.log('Launching headless browser engine...');
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  await page.setViewport({
    width: 1080,
    height: 1350,
    deviceScaleFactor: 1
  });

  const filePath = 'file://' + path.resolve(__dirname, 'template.html');
  await page.goto(filePath, { waitUntil: 'networkidle0' });

  // 2. Inject AI text directly into the HTML DOM elements
  await page.evaluate((data) => {
    const mainEl = document.querySelector('.hook-main');
    const subEl = document.querySelector('.hook-sub');
    
    if (mainEl) mainEl.textContent = data.mainText;
    if (subEl) {
      // Reconstruct subtext + accent underline span
      subEl.innerHTML = `${data.subText} <span class="accent-word">${data.accentText}</span>`;
    }
  }, hookCopy);

  // 3. Ensure fonts are loaded before capturing screenshot
  await page.evaluateHandle('document.fonts.ready');

  const outputPath = path.resolve(__dirname, 'output-slide-1.png');
  await page.screenshot({
    path: outputPath,
    type: 'png'
  });

  await browser.close();
  console.log(`Successfully rendered dynamic slide to: ${outputPath}`);
}

renderCarouselSlide().catch(err => {
  console.error('Error in engine execution:', err);
  process.exit(1);
});
