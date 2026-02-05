// API base URL
const API_BASE = window.location.origin;

// State
let refreshInterval = null;
let currentTab = 'portfolio';

// Utility functions
function formatUSD(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

function formatSOL(value) {
  return `${value.toFixed(6)} SOL`;
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(value);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString();
}

function formatPercentage(value) {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

function getChangeClass(value) {
  if (value > 0) return 'positive';
  if (value < 0) return 'negative';
  return 'neutral';
}

// API calls
async function fetchAPI(endpoint) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
}

// Load statistics
async function loadStats() {
  try {
    const stats = await fetchAPI('/api/stats');

    const statsHTML = `
      <div class="stat-card">
        <h3>Portfolio Value</h3>
        <div class="value">${formatUSD(stats.portfolio.total_value_usd)}</div>
        <div class="change ${getChangeClass(stats.portfolio.unrealized_pnl_percentage)}">
          ${formatPercentage(stats.portfolio.unrealized_pnl_percentage)} PnL
        </div>
      </div>

      <div class="stat-card">
        <h3>Available Balance</h3>
        <div class="value">${formatSOL(stats.portfolio.available_balance_sol)}</div>
        <div class="change neutral">
          ${stats.portfolio.position_count} open positions
        </div>
      </div>

      <div class="stat-card">
        <h3>Daily PnL</h3>
        <div class="value">${formatUSD(stats.daily.pnl_usd)}</div>
        <div class="change ${getChangeClass(stats.daily.pnl_usd)}">
          ${stats.daily.trade_count} trades today
        </div>
      </div>

      <div class="stat-card">
        <h3>Signals Today</h3>
        <div class="value">${stats.signals.total}</div>
        <div class="change neutral">
          ${stats.signals.buy} buy / ${stats.signals.sell} sell
        </div>
      </div>
    `;

    document.getElementById('statsGrid').innerHTML = statsHTML;
  } catch (error) {
    document.getElementById('statsGrid').innerHTML = `
      <div class="stat-card" style="grid-column: 1 / -1;">
        <p style="color: #ef4444;">Error loading statistics. Is the backend running?</p>
      </div>
    `;
  }
}

// Load portfolio
async function loadPortfolio() {
  try {
    const portfolio = await fetchAPI('/api/portfolio');

    if (portfolio.positions.length === 0) {
      document.getElementById('positionsList').innerHTML = `
        <p style="text-align: center; color: #64748b; padding: 40px;">
          No open positions
        </p>
      `;
      return;
    }

    const positionsHTML = portfolio.positions.map(position => `
      <div class="position-item">
        <div class="position-header">
          <div class="position-symbol">${position.token_symbol}</div>
          <div class="position-value ${getChangeClass(position.pnl_percentage)}">
            ${formatUSD(position.value_usd)}
          </div>
        </div>
        <div class="position-details">
          <div>
            <strong>Amount:</strong> ${position.amount.toFixed(4)}
          </div>
          <div>
            <strong>Entry:</strong> ${formatUSD(position.average_entry_price)}
          </div>
          <div>
            <strong>Current:</strong> ${formatUSD(position.current_price)}
          </div>
          <div>
            <strong>PnL:</strong>
            <span class="${getChangeClass(position.pnl_percentage)}">
              ${formatUSD(position.pnl_usd)} (${formatPercentage(position.pnl_percentage)})
            </span>
          </div>
        </div>
      </div>
    `).join('');

    document.getElementById('positionsList').innerHTML = `
      <div class="position-list">${positionsHTML}</div>
    `;
  } catch (error) {
    document.getElementById('positionsList').innerHTML = `
      <p style="color: #ef4444;">Error loading portfolio</p>
    `;
  }
}

// Load trades
async function loadTrades() {
  try {
    const data = await fetchAPI('/api/trades?limit=50');

    if (data.trades.length === 0) {
      document.getElementById('tradesList').innerHTML = `
        <p style="text-align: center; color: #64748b; padding: 40px;">
          No trades yet
        </p>
      `;
      return;
    }

    const tradesHTML = data.trades.map(trade => `
      <tr>
        <td>${formatDate(trade.timestamp)}</td>
        <td>
          <span class="badge badge-${trade.type}">${trade.type.toUpperCase()}</span>
        </td>
        <td>${trade.token_symbol}</td>
        <td>${trade.amount.toFixed(6)}</td>
        <td>${formatUSD(trade.price)}</td>
        <td>${formatUSD(trade.value_usd)}</td>
        <td>
          <span class="badge badge-${trade.status === 'executed' ? 'buy' : 'hold'}">
            ${trade.status}
          </span>
        </td>
      </tr>
    `).join('');

    document.getElementById('tradesList').innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Type</th>
            <th>Token</th>
            <th>Amount</th>
            <th>Price</th>
            <th>Value</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>${tradesHTML}</tbody>
      </table>
    `;
  } catch (error) {
    document.getElementById('tradesList').innerHTML = `
      <p style="color: #ef4444;">Error loading trades</p>
    `;
  }
}

// Load signals
async function loadSignals() {
  try {
    const data = await fetchAPI('/api/signals?limit=50');

    if (data.signals.length === 0) {
      document.getElementById('signalsList').innerHTML = `
        <p style="text-align: center; color: #64748b; padding: 40px;">
          No signals yet
        </p>
      `;
      return;
    }

    const signalsHTML = data.signals.map(signal => `
      <tr>
        <td>${formatDate(signal.timestamp)}</td>
        <td>
          <span class="badge badge-${signal.action}">${signal.action.toUpperCase()}</span>
        </td>
        <td>${signal.token_symbol}</td>
        <td>${signal.strength}</td>
        <td>${(signal.confidence * 100).toFixed(0)}%</td>
        <td>${signal.risk_level}</td>
        <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${signal.reasoning}
        </td>
      </tr>
    `).join('');

    document.getElementById('signalsList').innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Action</th>
            <th>Token</th>
            <th>Strength</th>
            <th>Confidence</th>
            <th>Risk</th>
            <th>Reasoning</th>
          </tr>
        </thead>
        <tbody>${signalsHTML}</tbody>
      </table>
    `;
  } catch (error) {
    document.getElementById('signalsList').innerHTML = `
      <p style="color: #ef4444;">Error loading signals</p>
    `;
  }
}

// Load content based on active tab
function loadContent() {
  switch (currentTab) {
    case 'portfolio':
      loadPortfolio();
      break;
    case 'trades':
      loadTrades();
      break;
    case 'signals':
      loadSignals();
      break;
  }

  // Always load stats
  loadStats();

  // Update last update time
  document.getElementById('lastUpdate').textContent =
    `Last update: ${new Date().toLocaleTimeString()}`;
}

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    // Add active class to clicked tab
    tab.classList.add('active');
    currentTab = tab.dataset.tab;
    document.getElementById(currentTab).classList.add('active');

    // Load content
    loadContent();
  });
});

// Auto-refresh
document.getElementById('refreshInterval').addEventListener('change', (e) => {
  const interval = parseInt(e.target.value);

  // Clear existing interval
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }

  // Set new interval
  if (interval > 0) {
    refreshInterval = setInterval(loadContent, interval);
  }
});

// Initial load
loadContent();

// Set initial auto-refresh
const initialInterval = parseInt(document.getElementById('refreshInterval').value);
if (initialInterval > 0) {
  refreshInterval = setInterval(loadContent, initialInterval);
}
