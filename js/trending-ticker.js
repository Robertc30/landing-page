// GitHub Trending Ticker - Fetches and displays trending repos
(function() {
  'use strict';
  
  const TICKER_CONTAINER = 'trending-ticker-content';
  const TICKER_DATA_URL = 'data/trending.json';
  const TICKER_SPEED = 50; // pixels per second
  const TICKER_PAUSE = 2000; // ms pause at each end
  
  let repos = [];
  let tickerElement = null;
  let animationId = null;
  let isPaused = false;
  let direction = 1; // 1 = right, -1 = left
  let currentPosition = 0;
  
  // Initialize on load
  document.addEventListener('DOMContentLoaded', initTicker);
  
  // Also try to init immediately if DOM already ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(initTicker, 100);
  }
  
  function initTicker() {
    tickerElement = document.getElementById(TICKER_CONTAINER);
    if (!tickerElement) {
      console.warn('Ticker container not found');
      return;
    }
    
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
    
    const containerWidth = tickerElement.parentElement.offsetWidth;
    let html = '';
    
    repos.forEach(repo => {
      const langColor = getLangColor(repo.language);
      html += `
        <a href="${repo.url}" target="_blank" rel="noopener noreferrer" class="ticker-item">
          <span class="ticker-name">${repo.name}</span>
          <span class="ticker-stars">⭐ ${formatNumber(repo.stars_today)}</span>
          <span class="ticker-lang" style="background: ${langColor}">${repo.language}</span>
        </a>
      `;
    });
    
    // Duplicate for seamless loop
    tickerElement.innerHTML = html + html;
    tickerElement.style.width = (repos.length * 2) + '00%';
  }
  
  function startAnimation() {
    const container = tickerElement.parentElement;
    const contentWidth = tickerElement.offsetWidth / 2;
    let lastTime = performance.now();
    
    function animate(currentTime) {
      if (!isPaused) {
        const deltaTime = (currentTime - lastTime) / 1000;
        lastTime = currentTime;
        
        currentPosition += TICKER_SPEED * direction * deltaTime;
        
        // Reverse direction at edges
        if (currentPosition >= 0) {
          direction = -1;
          isPaused = true;
          setTimeout(() => { isPaused = false; }, TICKER_PAUSE);
        } else if (currentPosition <= -(contentWidth - container.offsetWidth)) {
          direction = 1;
          isPaused = true;
          setTimeout(() => { isPaused = false; }, TICKER_PAUSE);
        }
        
        tickerElement.style.transform = `translateX(${currentPosition}px)`;
      }
      
      animationId = requestAnimationFrame(animate);
    }
    
    animationId = requestAnimationFrame(animate);
  }
  
  function getLangColor(lang) {
    const colors = {
      'JavaScript': '#f1e05a',
      'TypeScript': '#2b7489',
      'Python': '#3572A5',
      'Go': '#00ADD8',
      'Rust': '#dea584',
      'Java': '#b07219',
      'C++': '#f34b7d',
      'Ruby': '#701516',
      'PHP': '#4F5D95',
      'Shell': '#89e051'
    };
    return colors[lang] || '#8b8b8b';
  }
  
  function formatNumber(num) {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  }
  
  // Cleanup on page unload
  window.addEventListener('unload', () => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  });
})();
