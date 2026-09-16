// canvas_renderer.js - The Code-First Canvas Renderer
const { createCanvas } = require('canvas'); // Or browser HTML5 Canvas context

function renderCard(layoutJson) {
  const width = layoutJson.meta?.width || 1080;
  const height = layoutJson.meta?.height || 1350;
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  const styles = layoutJson.styles || {};
  const content = layoutJson.content || {};

  const bgColor = styles.backgroundColor || '#0D1117';
  const accentColor = styles.accentColor || '#0066FF';
  const textColor = styles.textColor || '#F0F6FC';
  const mutedColor = styles.mutedTextColor || '#8B949E';
  const font = styles.fontFamily || 'sans-serif';

  // 1. Background
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, width, height);

  // 2. Accent Top Border / Bar
  ctx.fillStyle = accentColor;
  ctx.fillRect(80, 100, 120, 8);

  // 3. Badge / Header
  if (content.badge) {
    ctx.fillStyle = accentColor;
    ctx.font = `bold 24px ${font}`;
    ctx.fillText(content.badge.toUpperCase(), 80, 150);
  }

  // Helper: Text Wrapping with Bounding Box Math
  function wrapText(text, x, startY, maxWidth, lineHeight, fontStyle) {
    ctx.font = fontStyle;
    const words = text.split(' ');
    let line = '';
    let currentY = startY;

    for (let n = 0; n < words.length; n++) {
      let testLine = line + words[n] + ' ';
      let metrics = ctx.measureText(testLine);
      if (metrics.width > maxWidth && n > 0) {
        ctx.fillText(line, x, currentY);
        line = words[n] + ' ';
        currentY += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, currentY);
    return currentY + lineHeight; // Returns next available Y coordinate
  }

  // 4. Headline (Auto-Wrapped & Scaled)
  let nextY = 240;
  if (content.headline) {
    ctx.fillStyle = textColor;
    const headlineFont = `bold 54px ${font}`;
    nextY = wrapText(content.headline, 80, nextY, width - 160, 68, headlineFont);
  }

  // 5. Body Copy
  if (content.body) {
    nextY += 20; // Padding
    ctx.fillStyle = mutedColor;
    const bodyFont = `32px ${font}`;
    nextY = wrapText(content.body, 80, nextY, width - 160, 46, bodyFont);
  }

  // 6. Footer & Watermark
  const footerY = height - 100;
  ctx.strokeStyle = '#21262D';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(80, footerY - 40);
  ctx.lineTo(width - 80, footerY - 40);
  ctx.stroke();

  if (content.footer) {
    ctx.fillStyle = mutedColor;
    ctx.font = `22px ${font}`;
    ctx.fillText(content.footer, 80, footerY);
  }

  if (content.author) {
    ctx.fillStyle = accentColor;
    ctx.font = `bold 22px ${font}`;
    const authorWidth = ctx.measureText(content.author).width;
    ctx.fillText(content.author, width - 80 - authorWidth, footerY);
  }

  return canvas.toBuffer('image/png');
}

module.exports = { renderCard };
