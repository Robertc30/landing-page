// GitHub Trending Ticker - Fetches and displays trending repos
(function () {
  'use strict';

  const TICKER_CONTAINER_ID = 'trending-ticker-content';
  const TICKER_DATA_URL = 'data/trending.json';
  const TICKER_SPEED = 50; // pixels per second
  const TICKER_PAUSE = 2000; // ms pause at each end

  let repos = [];
  let tickerElement = null;
  let animationId = null;
  let isPaused = false;
  let isVisible = true;
  let direction = -1; // Start moving left
  let currentPosition = 0;
  let lastTime = 0;

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTicker);
  } else {
    initTicker();
  }

  function initTicker() {
    tickerElement = document.getElementById(TICKER_CONTAINER_ID);
    if (!tickerElement) return;

    // Set up Intersection Observer to pause when not in view
    const observer = new IntersectionObserver((entries) => {
      isVisible = entries[0].isIntersecting;
      if (isVisible && !animationId) {
        lastTime = performance.now();
        animationId = requestAnimationFrame(animate);
      }
    }, { threshold: 0.1 });

    observer.observe(tickerElement.parentElement);

    fetch(TICKER_DATA_URL)
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch trending data');
        return response.json();
      })
      .then(data => {
        repos = data.sort((a, b) => b.trending_score - a.trending_score);
        renderTicker();
        startAnimation();
      })
      .catch(err => {
        console.error('Ticker error:', err);
        tickerElement.innerHTML = '<span class="ticker-error">Trending repos temporarily unavailable</span>';
      });
  }

  function renderTicker() {
    if (!repos.length) return;

    let html = '';
    repos.forEach(repo => {
      const langColor = getLangColor(repo.language);
      html += `
        <a href="${repo.url}" target="_blank" rel="noopener noreferrer" class="ticker-item">
          <span class="ticker-name">${repo.name}</span>
          <span class="ticker-stars" aria-label="${repo.stars_today} stars today">⭐ ${formatNumber(repo.stars_today)}</span>
          <span class="ticker-lang" style="background: ${langColor}">${repo.language}</span>
        </a>
      `;
    });

    // Duplicate for seamless loop
    tickerElement.innerHTML = html + html;
    // Set initial position
    tickerElement.style.transform = `translateX(0px)`;
  }

  function startAnimation() {
    lastTime = performance.now();
    animationId = requestAnimationFrame(animate);
  }

  function animate(currentTime) {
    if (!tickerElement || !isVisible) {
      animationId = null;
      return;
    }

    if (!isPaused) {
      const deltaTime = (currentTime - lastTime) / 1000;
      lastTime = currentTime;

      const container = tickerElement.parentElement;
      const contentWidth = tickerElement.scrollWidth / 2;

      currentPosition += TICKER_SPEED * direction * deltaTime;

      // Reverse direction at edges (simple ping-pong for now, can be changed to seamless loop if desired)
      if (currentPosition >= 0) {
        currentPosition = 0;
        direction = -1;
        pauseTicker();
      } else if (currentPosition <= -(contentWidth - container.offsetWidth)) {
        currentPosition = -(contentWidth - container.offsetWidth);
        direction = 1;
        pauseTicker();
      }

      tickerElement.style.transform = `translateX(${currentPosition}px)`;
    } else {
      lastTime = currentTime; // Keep lastTime current while paused
    }

    animationId = requestAnimationFrame(animate);
  }

  function pauseTicker() {
    isPaused = true;
    setTimeout(() => {
      isPaused = false;
    }, TICKER_PAUSE);
  }

  function getLangColor(lang) {
    const colors = {
      'JavaScript': '#f1e05a',
      'TypeScript': '#3572A5', // Actually TypeScript is #2b7489, but keeping brand colors or standardizing
      'Python': '#3572A5',
      'Go': '#00ADD8',
      'Rust': '#dea584',
      'Java': '#b07219',
      'C++': '#f34b7d',
      'Ruby': '#701516',
      'PHP': '#4F5D95',
      'Shell': '#89e051'
    };
    // Fix TypeScript color if needed, but let's stick to a clean palette
    if (lang === 'TypeScript') return '#3178c6';
    return colors[lang] || '#8b8b8b';
  }

  function formatNumber(num) {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  }
})();
