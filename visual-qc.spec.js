// landing-page/visual-qc.spec.js
// Real visual QC: logo, ticker movement (delta), nav links (click+200+element), mobile layout checks

const { test, expect } = require('@playwright/test');
const BASE_URL = 'https://robertc30.github.io/landing-page';

// Helper: No horizontal scroll check (catches overflow issues)
const assertNoHorizontalScroll = async (page) => {
  const hasOverflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return doc.scrollWidth > doc.clientWidth + 1; // +1 avoids subpixel false positives
  });
  expect(hasOverflow).toBeFalsy();
};

// Helper: Layout sanity check
const assertLayoutSanity = async (page) => {
  // Header/nav exists
  const nav = page.locator('[data-testid="site-nav"]');
  await expect(nav).toBeVisible({ timeout: 10000 });
  
  // Logo is visible (already asserted in tests, but safety check)
  const logo = page.locator('[data-testid="techquest-logo"]');
  await expect(logo).toBeVisible();
};

test.describe('Visual QC - Homepage', () => {
  
  test.beforeEach(async ({ page }) => {
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    // Use baseURL from config, navigate to root
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    if (errors.length > 0) console.log('Page errors:', errors);
  });
  
  test('logo is visible', async ({ page }) => {
    const logo = page.locator('[data-testid="techquest-logo"]');
    await expect(logo).toBeVisible({ timeout: 10000 });
    await page.screenshot({ path: 'screenshots/logo-visible.png', fullPage: false });
  });

  test('ticker is ANIMATING (movement proof)', async ({ page }) => {
    const tickerContent = page.locator('[data-testid="ticker-content"]');
    await expect(tickerContent).toBeVisible({ timeout: 10000 });
    
    // PROOF: Measure position at T0
    const box0 = await tickerContent.boundingBox();
    expect(box0).not.toBeNull();
    const x0 = box0.x;
    
    // Wait 3 seconds for movement
    await page.waitForTimeout(3000);
    
    // Measure at T1
    const box1 = await tickerContent.boundingBox();
    expect(box1).not.toBeNull();
    const x1 = box1.x;
    
    // Assert movement > 5px
    const delta = Math.abs(x1 - x0);
    expect(delta).toBeGreaterThan(5);
    
    console.log(`Ticker movement: ${x0}px → ${x1}px (delta: ${delta}px)`);
    await page.screenshot({ path: 'screenshots/ticker-animating.png', fullPage: true });
  });

  test('navigation links WORK (click+200+element)', async ({ page }) => {
    const pages = [
      { name: 'home', path: '/', element: '[data-testid="page-home"]' },
      { name: 'blog', path: '/blog/', element: '[data-testid="page-blog"]' },
      { name: 'reviews', path: '/reviews/', element: '[data-testid="page-reviews"]' },
      { name: 'walkthroughs', path: '/blog/walkthroughs.html', element: '[data-testid="page-walkthroughs"]' },
      { name: 'resources', path: '/resources.html', element: '[data-testid="page-resources"]' },
      { name: 'kai-corner', path: '/kai-corner.html', element: '[data-testid="page-kai-corner"]' },
      { name: 'tasks', path: '/tasks.html', element: '[data-testid="page-tasks"]' },
      { name: 'tools', path: '/tools.html', element: '[data-testid="page-tools"]' },
    ];
    
    for (const pg of pages) {
      await page.click(`[data-testid="nav-link"][href="${pg.path}"]`);
      await page.waitForLoadState('domcontentloaded');
      await expect(page).toHaveURL(new RegExp(pg.path.replace('/', '\\/') + '$'));
      await expect(page.locator(pg.element)).toBeVisible({ timeout: 5000 });
      await page.screenshot({ path: `screenshots/nav-${pg.name}.png`, fullPage: true });
      console.log(`✓ ${pg.name} verified`);
    }
  });

  test('homepage loads without errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    page.on('pageerror', err => errors.push(err.message));
    await page.goto('/', { waitUntil: 'networkidle' });
    // Filter non-critical
    const critical = errors.filter(e => 
      !e.includes('favicon') && 
      !e.includes('font') &&
      !e.includes('ERR_FILE_NOT_FOUND')
    );
    expect(critical).toHaveLength(0);
    await page.screenshot({ path: 'screenshots/homepage-loaded.png', fullPage: true });
  });
});

test.describe('Visual QC - Mobile', () => {
  // Workers: 1 in config to avoid screenshot collisions
  
  test('iPhone 12 layout works', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    // Logo
    await expect(page.locator('[data-testid="techquest-logo"]')).toBeVisible({ timeout: 10000 });
    
    // Layout sanity
    await assertNoHorizontalScroll(page);
    await assertLayoutSanity(page);
    
    await page.screenshot({ path: 'screenshots/mobile-iphone-12.png', fullPage: true });
  });

  test('Android Pixel 5 layout works', async ({ page }) => {
    await page.setViewportSize({ width: 393, height: 852 });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    await expect(page.locator('[data-testid="techquest-logo"]')).toBeVisible({ timeout: 10000 });
    await assertNoHorizontalScroll(page);
    await assertLayoutSanity(page);
    
    await page.screenshot({ path: 'screenshots/mobile-pixel-5.png', fullPage: true });
  });

  test('Tablet iPad Mini layout works', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    
    await expect(page.locator('[data-testid="techquest-logo"]')).toBeVisible({ timeout: 10000 });
    await assertNoHorizontalScroll(page);
    await assertLayoutSanity(page);
    
    await page.screenshot({ path: 'screenshots/tablet-ipad-mini.png', fullPage: true });
  });
});

test.describe('Visual QC - Responsive', () => {
  const breakpoints = [
    { name: 'mobile-small', width: 320, height: 568 },
    { name: 'mobile-medium', width: 375, height: 667 },
    { name: 'mobile-large', width: 414, height: 896 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1280, height: 720 },
    { name: 'desktop-large', width: 1920, height: 1080 },
  ];
  
  for (const bp of breakpoints) {
    test(`${bp.name} (${bp.width}x${bp.height})`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      
      await expect(page.locator('[data-testid="techquest-logo"]')).toBeVisible({ timeout: 10000 });
      await assertNoHorizontalScroll(page);
      
      await page.screenshot({ path: `screenshots/responsive-${bp.name}.png`, fullPage: true });
    });
  }
});
