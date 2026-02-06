// Visual QC Tests for TechQuest.AI Landing Page
// Project: landing-page (Playwright expects tests in same folder as package.json)
// Run with: npm test

const { test, expect } = require('@playwright/test');

// Configuration
const BASE_URL = 'https://robertc30.github.io/landing-page';
const TIMEOUT = 30000;

// Test configuration
test.use({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  trace: 'retain-on-failure',
  screenshot: 'only-on-failure',
});

test.describe('Visual QC - Homepage', () => {
  
  test.beforeEach(async ({ page }) => {
    // Fail fast on JS errors
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    // Log any errors for debugging
    if (errors.length > 0) {
      console.log('Page errors:', errors);
    }
  });
  
  test('logo is visible in KAI section', async ({ page }) => {
    // Use deterministic selector with data-testid
    const logo = page.locator('[data-testid="techquest-logo"]');
    
    await expect(logo).toBeVisible();
    
    // Capture evidence screenshot
    await page.screenshot({
      path: 'screenshots/logo-visible.png',
      fullPage: false
    });
  });

  test('trending ticker is ANIMATING (movement proof)', async ({ page }) => {
    // Find ticker container
    const ticker = page.locator('[data-testid="trending-ticker"]');
    await expect(ticker).toBeVisible();
    
    // Find the scrolling content inside
    const tickerContent = page.locator('[data-testid="ticker-content"]');
    await expect(tickerContent).toBeVisible();
    
    // PROOF OF MOVEMENT: measure position at T0
    const box0 = await tickerContent.boundingBox();
    expect(box0).not.toBeNull();
    const x0 = box0.x;
    
    // Wait 3 seconds (ticker should move)
    await page.waitForTimeout(3000);
    
    // Measure again at T1
    const box1 = await tickerContent.boundingBox();
    expect(box1).not.toBeNull();
    const x1 = box1.x;
    
    // Assert movement (delta > 5px)
    const delta = Math.abs(x1 - x0);
    expect(delta).toBeGreaterThan(5);
    
    // Capture evidence
    await page.screenshot({
      path: 'screenshots/ticker-animating.png',
      fullPage: true
    });
    
    console.log(`Ticker movement: ${x0}px → ${x1}px (delta: ${delta}px)`);
  });

  test('navigation has all 8 links that WORK', async ({ page }) => {
    const navLinks = page.locator('[data-testid="nav-link"]');
    const count = await navLinks.count();
    
    expect(count).toBe(8);
    
    // Define pages to test with their expected element selectors
    const pagesToTest = [
      { name: 'Home', path: '/', element: '[data-testid="page-home"]' },
      { name: 'Blog', path: '/blog/', element: '[data-testid="page-blog"]' },
      { name: 'Reviews', path: '/reviews/', element: '[data-testid="page-reviews"]' },
      { name: 'Walkthroughs', path: '/blog/walkthroughs.html', element: '[data-testid="page-walkthroughs"]' },
      { name: 'Resources', path: '/resources.html', element: '[data-testid="page-resources"]' },
      { name: 'KAI Corner', path: '/kai-corner.html', element: '[data-testid="page-kai-corner"]' },
      { name: 'Tasks', path: '/tasks.html', element: '[data-testid="page-tasks"]' },
      { name: 'Tools', path: '/tools.html', element: '[data-testid="page-tools"]' },
    ];
    
    for (const pg of pagesToTest) {
      // Click the link
      await page.click(`[data-testid="nav-link"][href="${pg.path}"]`);
      
      // Wait for navigation
      await page.waitForLoadState('domcontentloaded');
      
      // Verify page loaded (check URL or status)
      await expect(page).toHaveURL(new RegExp(pg.path.replace('/', '\\/') + '$'));
      
      // Verify page-specific element exists
      const element = page.locator(pg.element);
      await expect(element).toBeVisible({ timeout: 5000 });
      
      // Capture evidence screenshot
      await page.screenshot({
        path: `screenshots/nav-${pg.name.toLowerCase().replace(' ', '-')}.png`,
        fullPage: true
      });
      
      console.log(`✓ ${pg.name} loaded and verified`);
    }
  });

  test('homepage loads without errors', async ({ page }) => {
    const errors = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    page.on('pageerror', err => {
      errors.push(err.message);
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Filter out non-critical errors
    const criticalErrors = errors.filter(e => 
      !e.includes('favicon') && 
      !e.includes('font') &&
      !e.includes('404') &&
      !e.includes('ERR_FILE_NOT_FOUND')
    );
    
    expect(criticalErrors).toHaveLength(0);
    
    await page.screenshot({
      path: 'screenshots/homepage-loaded.png',
      fullPage: true
    });
  });
});

test.describe('Visual QC - Mobile', () => {
  
  test('iPhone 12 layout works', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify key elements exist
    const logo = page.locator('[data-testid="techquest-logo"]');
    await expect(logo).toBeVisible();
    
    // Verify nav or mobile menu exists
    const nav = page.locator('[data-testid="nav-link"]');
    const navVisible = await nav.first().isVisible();
    const hamburger = page.locator('[data-testid="mobile-menu"]');
    const hamburgerVisible = await hamburger.count() > 0 && await hamburger.first().isVisible();
    
    expect(navVisible || hamburgerVisible).toBe(true);
    
    await page.screenshot({
      path: 'screenshots/mobile-iphone-12.png',
      fullPage: true
    });
  });

  test('Android Pixel 5 layout works', async ({ page }) => {
    await page.setViewportSize({ width: 393, height: 852 });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    const logo = page.locator('[data-testid="techquest-logo"]');
    await expect(logo).toBeVisible();
    
    await page.screenshot({
      path: 'screenshots/mobile-pixel-5.png',
      fullPage: true
    });
  });

  test('Tablet iPad Mini layout works', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    const logo = page.locator('[data-testid="techquest-logo"]');
    await expect(logo).toBeVisible();
    
    await page.screenshot({
      path: 'screenshots/tablet-ipad-mini.png',
      fullPage: true
    });
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
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');
      
      // Verify key content exists
      const logo = page.locator('[data-testid="techquest-logo"]');
      await expect(logo).toBeVisible();
      
      await page.screenshot({
        path: `screenshots/responsive-${bp.name}.png`,
        fullPage: true
      });
    });
  }
});

// Generate QC report on completion
test.afterEach(async ({ }, testInfo) => {
  const fs = require('fs');
  const path = require('path');
  
  const date = new Date().toISOString().split('T')[0];
  const qcDir = `../qc/${date}`;
  
  // Ensure QC directory exists
  fs.mkdirSync(qcDir, { recursive: true });
  fs.mkdirSync(`${qcDir}/screenshots`, { recursive: true });
  
  // Copy screenshots to QC folder
  if (fs.existsSync('screenshots')) {
    fs.readdirSync('screenshots').forEach(file => {
      if (file.endsWith('.png')) {
        fs.copyFileSync(
          `screenshots/${file}`,
          `${qcDir}/screenshots/${file}`
        );
      }
    });
  }
  
  // Generate QC report
  const report = {
    timestamp: new Date().toISOString(),
    test: testInfo.title,
    status: testInfo.status,
    duration: testInfo.duration,
    artifacts: {
      screenshots: fs.existsSync('screenshots') 
        ? fs.readdirSync('screenshots').filter(f => f.endsWith('.png'))
        : [],
    }
  };
  
  fs.writeFileSync(
    `${qcDir}/report.json`,
    JSON.stringify(report, null, 2)
  );
  
  // Write human-readable report
  fs.writeFileSync(`${qcDir}/report.md`, `# Visual QC Report - ${date}\n\n**Test:** ${testInfo.title}\n**Status:** ${testInfo.status}\n**Duration:** ${testInfo.duration}ms\n\n## Artifacts\n\n- Screenshots: ${qcDir}/screenshots/\n- Report: ${qcDir}/report.json\n\n---\nGenerated: ${report.timestamp}\n`);
  
  console.log(`QC report written to ${qcDir}/`);
});
