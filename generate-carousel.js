const puppeteer = require('puppeteer');
const path = require('path');

async function renderCarouselSlide() {
  console.log('Launching headless browser engine...');
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Set strict Instagram 4:5 resolution viewport
  await page.setViewport({
    width: 1080,
    height: 1350,
    deviceScaleFactor: 1
  });

  const filePath = 'file://' + path.resolve(__dirname, 'template.html');
  console.log(`Loading template from: ${filePath}`);
  
  await page.goto(filePath, { waitUntil: 'networkidle0' });

  // Ensure remote fonts are fully loaded before capturing
  await page.evaluateHandle('document.fonts.ready');

  const outputPath = path.resolve(__dirname, 'output-slide-1.png');
  await page.screenshot({
    path: outputPath,
    type: 'png'
  });

  await browser.close();
  console.log(`Carousel slide successfully rendered and saved to: ${outputPath}`);
}

renderCarouselSlide().catch(err => {
  console.error('Error rendering carousel slide:', err);
  process.exit(1);
});
