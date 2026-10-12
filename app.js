document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('#main-views .panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const target = document.getElementById(btn.dataset.target);
    if (target) target.classList.add('active');
  });
});

function fmt(n, digits = 2) {
  if (n == null || isNaN(n)) return '—';
  return Number(n).toLocaleString('zh-HK', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function pct(n) {
  if (n == null || isNaN(n)) return '—';
  const sign = n > 0 ? '+' : '';
  return sign + fmt(n, 2) + '%';
}

function renderTable(tableId, rows, columns) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  if (!tbody) return;
  tbody.innerHTML = rows.map((r, i) => {
    return `<tr>${columns.map(col => {
      const val = col.render ? col.render(r, i) : r[col.key];
      return `<td>${val}</td>`;
    }).join('')}</tr>`;
  }).join('');
}

function showDetail(stock) {
  document.getElementById('main-views').style.display = 'none';
  const panel = document.getElementById('detail');
  panel.style.display = 'block';
  const color = stock.verdict_color || 'neutral';
  document.getElementById('detail-content').innerHTML = `
    <div class="detail-card">
      <div class="detail-title">${stock.name || ''}</div>
      <div class="detail-code">${stock.code} · ${stock.sector || ''}</div>
      <div class="verdict-badge ${color}">${stock.verdict || '—'}</div>
      <div class="detail-grid">
        <div class="level-box">
          <div class="level-label">收盤</div>
          <div class="level-value">${fmt(stock.close, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">漲跌幅</div>
          <div class="level-value ${stock.change >= 0 ? 'up' : 'down'}">${pct(stock.change)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">評分</div>
          <div class="level-value" style="color:var(--yellow)">${fmt(stock.score, 1)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">成交額(億)</div>
          <div class="level-value">${fmt(stock.amount_yi, 2)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">建議入場</div>
          <div class="level-value entry">${fmt(stock.entry_low, 3)} – ${fmt(stock.entry_high, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">止損</div>
          <div class="level-value stop">${fmt(stock.stop, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">目標 1</div>
          <div class="level-value target">${fmt(stock.target1, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">目標 2</div>
          <div class="level-value target">${fmt(stock.target2, 3)}</div>
        </div>
      </div>
      <div class="pick-meta" style="margin-bottom:14px">
        <span>類型 <strong>${stock.entry_type || '—'}</strong></span>
        <span>量能倍數 <strong>${stock.vol_ratio != null ? stock.vol_ratio + 'x' : '—'}</strong></span>
        <span>20日線 <strong>${stock.ma20 != null ? fmt(stock.ma20, 3) : '—'}</strong></span>
      </div>
      <div class="detail-text">${(stock.detail_text || stock.reason || '—').replace(/\n/g, '<br>')}</div>
    </div>
  `;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideDetail() {
  document.getElementById('detail').style.display = 'none';
  document.getElementById('main-views').style.display = 'block';
  document.getElementById('search-hint').textContent = '';
}

function findStock(q) {
  if (!DATA || !DATA.all_stocks) return null;
  q = (q || '').trim().toLowerCase().replace(/\.hk$/i, '');
  if (!q) return null;
  // exact code
  let hit = DATA.all_stocks.find(s => String(s.code).toLowerCase() === q || String(s.code).padStart(4, '0') === q.padStart(4, '0'));
  if (hit) return hit;
  // name contains
  hit = DATA.all_stocks.find(s => (s.name || '').toLowerCase().includes(q));
  if (hit) return hit;
  // partial code
  hit = DATA.all_stocks.find(s => String(s.code).includes(q));
  return hit || null;
}

function doSearch() {
  const input = document.getElementById('search-input');
  const hint = document.getElementById('search-hint');
  const q = input.value;
  const stock = findStock(q);
  if (!stock) {
    hint.textContent = '找不到此股票。目前資料庫約涵蓋活躍主板股，可試 0700、騰訊、零跑、京東 等。';
    hint.style.color = 'var(--red)';
    return;
  }
  hint.textContent = '';
  showDetail(stock);
}

function renderPicks(picks) {
  const box = document.getElementById('picks-cards');
  if (!box) return;
  box.innerHTML = picks.map((r, i) => `
    <div class="pick-card">
      <div class="pick-header">
        <span class="pick-rank">${i + 1}</span>
        <span class="pick-name pick-name-link" data-code="${r.code}">${r.name}</span>
        <span class="pick-code">${r.code}</span>
        <span class="pick-score">分數 ${fmt(r.score, 1)}</span>
      </div>
      <div class="pick-meta">
        <span>收盤 <strong>${fmt(r.close, 3)}</strong></span>
        <span class="${r.change >= 0 ? 'up' : 'down'}">${pct(r.change)}</span>
        <span>成交額 <strong>${fmt(r.amount_yi, 2)}</strong> 億</span>
        <span>產業 <strong>${r.sector || '—'}</strong></span>
        <span>類型 <strong>${r.entry_type || '—'}</strong></span>
        ${r.verdict ? `<span class="verdict-badge ${r.verdict_color || 'neutral'}" style="margin:0;font-size:0.75rem;padding:2px 8px">${r.verdict}</span>` : ''}
      </div>
      <div class="levels">
        <div class="level-box">
          <div class="level-label">建議入場</div>
          <div class="level-value entry">${fmt(r.entry_low, 3)} – ${fmt(r.entry_high, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">止損</div>
          <div class="level-value stop">${fmt(r.stop, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">目標 1</div>
          <div class="level-value target">${fmt(r.target1, 3)}</div>
        </div>
        <div class="level-box">
          <div class="level-label">目標 2</div>
          <div class="level-value target">${fmt(r.target2, 3)}</div>
        </div>
      </div>
      <div class="pick-reason"><strong>原因：</strong>${r.reason || '—'}
        <a href="#" class="pick-name-link" data-code="${r.code}" style="margin-left:8px;font-size:0.85rem">完整分析 →</a>
      </div>
    </div>
  `).join('');

  box.querySelectorAll('.pick-name-link').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      const s = findStock(el.dataset.code);
      if (s) showDetail(s);
    });
  });
}

function init() {
  if (typeof DATA === 'undefined') {
    document.getElementById('update-time').textContent = '資料尚未載入';
    return;
  }

  document.getElementById('update-time').textContent = `資料更新：${DATA.update_time}`;
  document.getElementById('rec-count').textContent = DATA.summary.rec_count;
  document.getElementById('avg-score').textContent = fmt(DATA.summary.avg_score, 1);
  document.getElementById('up-down').textContent = `${DATA.summary.up} / ${DATA.summary.down}`;
  document.getElementById('top-sector').textContent = DATA.summary.top_sector || '—';

  renderPicks(DATA.picks || []);

  renderTable('volume-table', DATA.volume_top || [], [
    { render: (_, i) => i + 1 },
    { render: r => `<span class="pick-name-link" data-code="${r.code}">${r.name}</span> <span class="stock-code">${r.code}</span>` },
    { render: r => fmt(r.close, 2) },
    { render: r => `<span class="${r.change >= 0 ? 'up' : 'down'}">${pct(r.change)}</span>` },
    { render: r => fmt(r.amount_yi, 2) },
    { render: r => fmt(r.turnover * 100, 2) + '%' },
    { render: r => fmt(r.volume / 10000, 0) }
  ]);

  renderTable('turnover-table', DATA.turnover_top || [], [
    { render: (_, i) => i + 1 },
    { render: r => `<span class="pick-name-link" data-code="${r.code}">${r.name}</span> <span class="stock-code">${r.code}</span>` },
    { render: r => fmt(r.close, 2) },
    { render: r => `<span class="${r.change >= 0 ? 'up' : 'down'}">${pct(r.change)}</span>` },
    { render: r => fmt(r.volume / 10000, 0) },
    { render: r => fmt(r.amount_yi, 2) },
    { render: r => fmt(r.turnover * 100, 2) + '%' }
  ]);

  document.querySelectorAll('#volume-table .pick-name-link, #turnover-table .pick-name-link').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      const s = findStock(el.dataset.code);
      if (s) showDetail(s);
    });
  });

  document.getElementById('search-btn').addEventListener('click', doSearch);
  document.getElementById('search-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
  });
  document.getElementById('back-btn').addEventListener('click', hideDetail);
}

document.addEventListener('DOMContentLoaded', init);
