// Headless Chromium screenshot of Pinterest prep page to verify what
// the user actually sees on /companies/29/prep?tab=docs&doc=83.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 1800 },
  });
  const page = await ctx.newPage();
  page.on('console', m => console.log('[console]', m.type(), m.text()));
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  page.on('requestfailed', r => console.log('[reqfail]', r.url(), r.failure()?.errorText));

  const url = 'http://localhost:5173/companies/29/prep?tab=docs&doc=83';
  console.log('navigating to', url);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2500);

  const path = require('path').resolve('logs/pinterest_prep_screenshot.png');
  await page.screenshot({ path, fullPage: true });
  console.log('screenshot saved to', path);

  // Also dump what the page actually shows
  const visibleText = await page.evaluate(() => {
    return document.body.innerText.slice(0, 4000);
  });
  console.log('--- visible text (first 4000 chars) ---');
  console.log(visibleText);
  console.log('--- has CONFIRMED 2026-04-30? ---', visibleText.includes('CONFIRMED 2026-04-30'));
  console.log('--- has Yiyang Zhang?       ---', visibleText.includes('Yiyang Zhang'));
  console.log('--- has TBD this week?      ---', visibleText.includes('TBD this week'));

  await browser.close();
})();
