/**
 * Freyssinet Bearing Design Check — Web UI
 * Naidu Consulting technical assessment tool
 */

const SAMPLE = {
  l: 457, b: 254, T: 54, plate_thk: 4.5, no_plates: 4,
  te: 10, ti: 10, G: 0.9,
  Vmax: 1420, Vdl: 384, Vll: 1036,
  Hs: 50, Ht: 10,
  long_mvmt: 10.6, trans_mvmt: 4.19,
  alpha_b: 0.0001, alpha_l: 0,
};

const FIELD_IDS = [
  'l', 'b', 'T', 'plate_thk', 'no_plates', 'te', 'ti', 'G',
  'Vmax', 'Vdl', 'Vll', 'Hs', 'Ht', 'long_mvmt', 'trans_mvmt',
  'alpha_b', 'alpha_l',
];

const CHECK_META = [
  { key: 'check1_shear_strain', num: 1, name: 'Shear Strain', keyField: 'Eq' },
  { key: 'check2_max_design_strain', num: 2, name: 'Max Design Strain', keyField: 'Et' },
  { key: 'check3_plate_thickness', num: 3, name: 'Plate Thickness', keyField: 'tmin' },
  { key: 'check4_stability', num: 4, name: 'Stability', keyField: null },
  { key: 'check5_vertical_deflection', num: 5, name: 'Vertical Deflection', keyField: 'delta_total' },
  { key: 'check6_rotational_limit', num: 6, name: 'Rotational Limit', keyField: 'delta_total' },
  { key: 'check7_fixing_of_bearings', num: 7, name: 'Fixing of Bearings', keyField: null },
];

function fmtNum(v, decimals = 4) {
  if (typeof v !== 'number' || Number.isNaN(v)) return String(v);
  if (Math.abs(v) >= 1000) return v.toFixed(2);
  if (Math.abs(v) >= 10) return v.toFixed(3);
  return v.toFixed(decimals);
}

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach((btn, i) => {
    const names = ['manual', 'sample', 'json'];
    btn.classList.toggle('active', names[i] === name);
  });
  document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('action-row').style.display = name === 'manual' ? 'flex' : 'none';
}

function updateDerivedHint() {
  const el = document.getElementById('derived-hint');
  if (!el) return;
  const plates = parseInt(document.getElementById('no_plates')?.value, 10);
  const T = parseFloat(document.getElementById('T')?.value);
  const pt = parseFloat(document.getElementById('plate_thk')?.value);
  const ti = parseFloat(document.getElementById('ti')?.value);
  if (!plates || !T || !pt) {
    el.innerHTML = 'Derived values appear when dimensions are filled (matches spreadsheet).';
    return;
  }
  const layers = plates - 1;
  const tq = T - plates * pt;
  const sumTi = Number.isFinite(ti) ? ti * layers : '—';
  el.innerHTML =
    `<strong>Derived:</strong> no. layers = ${layers} · tq = ${fmtNum(tq, 2)} mm · Σti = ${sumTi} mm`;
}

function collectForm() {
  const data = {};
  let hasError = false;

  FIELD_IDS.forEach((id) => {
    const el = document.getElementById(id);
    const v = el?.value.trim() ?? '';
    el?.classList.remove('error');
    if (v === '') {
      el?.classList.add('error');
      hasError = true;
    } else {
      data[id] = id === 'no_plates' ? parseInt(v, 10) : parseFloat(v);
    }
  });

  if (hasError) {
    showToast('Please fill in all highlighted fields.');
    return null;
  }

  data.bearing_type = document.getElementById('bearing_type').value;
  return data;
}

function loadSampleIntoForm() {
  Object.entries(SAMPLE).forEach(([k, v]) => {
    const el = document.getElementById(k);
    if (el) {
      el.value = v;
      el.classList.remove('error');
    }
  });
  updateDerivedHint();
  showToast('Verification sample loaded (Naidu brief / spreadsheet).');
}

function loadSample() {
  loadSampleIntoForm();
  switchTab('manual');
  runChecks();
}

function runFromJson() {
  const txt = document.getElementById('json-input').value.trim();
  if (!txt) {
    showToast('Paste your JSON first.');
    return;
  }
  let data;
  try {
    data = JSON.parse(txt);
  } catch (e) {
    showToast('Invalid JSON: ' + e.message);
    return;
  }
  if (!data.bearing_type) data.bearing_type = 'pad';
  callApi(data);
}

function clearForm() {
  FIELD_IDS.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.value = '';
      el.classList.remove('error');
    }
  });
  document.getElementById('results-panel').classList.remove('visible');
  document.getElementById('results-body').innerHTML = `
    <div class="placeholder" id="placeholder">
      <div class="placeholder-icon">⚙</div>
      <div class="placeholder-text">No results yet</div>
      <div class="placeholder-sub">Enter parameters and click Run All Checks (Ctrl+Enter)</div>
    </div>`;
  updateDerivedHint();
}

function runChecks() {
  const data = collectForm();
  if (!data) return;
  callApi(data);
}

async function callApi(data) {
  const btn = document.getElementById('run-btn');
  const bar = document.getElementById('progress-bar');
  const fill = document.getElementById('progress-fill');

  btn?.classList.add('loading');
  if (btn) btn.disabled = true;
  bar?.classList.add('active');
  if (fill) fill.style.width = '0%';

  let pct = 0;
  const ticker = setInterval(() => {
    pct = Math.min(pct + Math.random() * 18, 88);
    if (fill) fill.style.width = pct + '%';
  }, 120);

  try {
    const resp = await fetch('/api/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    clearInterval(ticker);
    if (fill) fill.style.width = '100%';

    if (!resp.ok) {
      let msg = 'Request failed.';
      try {
        const err = await resp.json();
        const list = err.detail?.validation_errors;
        if (Array.isArray(list)) msg = list.join('\n');
        else if (typeof err.detail === 'string') msg = err.detail;
        else msg = JSON.stringify(err.detail);
      } catch (_) { /* ignore */ }
      showToast(msg);
      return;
    }

    const result = await resp.json();
    renderResults(result, data);
    document.querySelectorAll('.workflow span').forEach((s, i) => {
      s.classList.toggle('active', i <= 2);
    });
  } catch (e) {
    clearInterval(ticker);
    showToast('Could not reach the API. Start the server with:\npython main.py --web\n\n' + e.message);
  } finally {
    setTimeout(() => {
      bar?.classList.remove('active');
      if (fill) fill.style.width = '0%';
    }, 500);
    btn?.classList.remove('loading');
    if (btn) btn.disabled = false;
  }
}

function renderGeometry(geo) {
  if (!geo) return '';
  const items = [
    ['le', geo.le], ['be', geo.be], ['layers', geo.no_layers],
    ['tq', geo.tq], ['Σti', geo.sum_ti], ['Ae', geo.Ae],
    ['S', geo.S], ['δb', geo.delta_b], ['δl', geo.delta_l], ['δr', geo.delta_r],
  ];
  const cells = items.map(
    ([label, val]) => `
      <div class="geom-item">
        <span class="label">${label}</span>
        <span class="value">${typeof val === 'number' ? fmtNum(val) : val}</span>
      </div>`
  ).join('');

  return `
    <div class="geometry-panel">
      <h3>Derived geometry (spreadsheet)</h3>
      <div class="geometry-grid">${cells}</div>
    </div>`;
}

function renderResults(result, inputData) {
  const body = document.getElementById('results-body');
  const isPass = result.overall === 'BEARING PASSES';
  const failCount = CHECK_META.filter((m) => result[m.key].status === 'FAIL').length;
  const thresholds = result.thresholds || {};

  const bannerHtml = `
    <div class="verdict-banner ${isPass ? 'pass' : 'fail'}">
      <div class="verdict-icon">${isPass ? '✓' : '✗'}</div>
      <div>
        <div class="verdict-title">${result.overall}</div>
        <div class="verdict-sub">
          ${isPass
            ? 'All 7 Freyssinet design checks passed.'
            : `${failCount} check${failCount !== 1 ? 's' : ''} failed — review details below.`}
        </div>
        <span class="type-badge">${result.bearing_type || 'pad'} bearing</span>
      </div>
    </div>`;

  const rowsHtml = CHECK_META.map((meta) => {
    const chk = result[meta.key];
    const isOk = chk.status === 'OK';
    const keyVal =
      meta.keyField && chk[meta.keyField] != null
        ? `${meta.keyField} = ${fmtNum(chk[meta.keyField])}`
        : '';
    const criterion = thresholds[meta.key] || '';

    const rows = Object.entries(chk.intermediates || {})
      .map(([k, v]) => {
        let display;
        if (typeof v === 'boolean') display = v ? '✓' : '✗';
        else if (typeof v === 'number') display = fmtNum(v, 6);
        else display = String(v);
        return `<tr><td>${k}</td><td>${display}</td></tr>`;
      })
      .join('');

    return `
      <div class="check-row" id="row-${meta.num}">
        <div class="check-summary" onclick="toggleRow(${meta.num})" role="button" tabindex="0"
             onkeydown="if(event.key==='Enter')toggleRow(${meta.num})">
          <div class="check-num" style="background:${isOk ? '#e8f5e9' : '#ffebee'};color:${isOk ? '#2e7d32' : '#c62828'}">${meta.num}</div>
          <div class="check-name">Check ${meta.num} – ${meta.name}</div>
          <div class="check-key-val">${keyVal}</div>
          <div class="status-pill ${isOk ? 'ok' : 'fail'}">${isOk ? 'OK' : 'FAIL'}</div>
          <div class="expand-arrow">▼</div>
        </div>
        <div class="check-criterion">${criterion}</div>
        <div class="check-detail">
          <table class="intermediates-table">${rows}</table>
          ${chk.message ? `<div class="check-msg">${chk.message}</div>` : ''}
        </div>
      </div>`;
  }).join('');

  const exportHtml = `
    <div class="export-row">
      <span style="font-size:0.75rem;color:var(--mid);font-weight:600">Export</span>
      <button type="button" class="btn btn-outline" onclick="downloadPdf()">PDF report</button>
      <button type="button" class="btn btn-ghost" onclick="downloadCsv()">CSV</button>
      <button type="button" class="btn btn-ghost" onclick="copyJson()">Copy JSON</button>
    </div>`;

  body.innerHTML =
    bannerHtml + renderGeometry(result.geometry) +
    '<div class="checks-grid">' + rowsHtml + '</div>' + exportHtml;

  window._lastResult = result;
  window._lastInput = inputData;

  document.getElementById('results-panel').classList.add('visible');
  scrollToResults();

  CHECK_META.forEach((meta) => {
    if (result[meta.key].status === 'FAIL') {
      setTimeout(() => toggleRow(meta.num, true), 200 + meta.num * 50);
    }
  });
}

function toggleRow(num, forceOpen) {
  const row = document.getElementById('row-' + num);
  if (!row) return;
  if (forceOpen) row.classList.add('open');
  else row.classList.toggle('open');
}

async function downloadPdf() {
  if (!window._lastInput) return;
  try {
    const resp = await fetch('/api/check/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(window._lastInput),
    });
    if (!resp.ok) {
      showToast('PDF export failed.');
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bearing_check_${Date.now()}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('PDF downloaded.');
  } catch (e) {
    showToast('PDF error: ' + e.message);
  }
}

async function downloadCsv() {
  if (!window._lastInput) return;
  try {
    const resp = await fetch('/api/check/csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(window._lastInput),
    });
    if (!resp.ok) {
      showToast('CSV export failed.');
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bearing_check_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV downloaded.');
  } catch (e) {
    showToast('CSV error: ' + e.message);
  }
}

function copyJson() {
  if (!window._lastResult) return;
  navigator.clipboard
    .writeText(JSON.stringify(window._lastResult, null, 2))
    .then(() => showToast('Results copied to clipboard.'))
    .catch(() => showToast('Copy failed — select and copy manually.'));
}

function showToast(msg) {
  document.querySelector('.toast')?.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = 'opacity 0.3s';
  }, 4000);
  setTimeout(() => t.remove(), 4300);
}

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runChecks();
});

/** Scroll progress bar at top of page */
function initScrollProgress() {
  const bar = document.getElementById('scroll-progress');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const doc = document.documentElement;
    const pct = (doc.scrollTop / (doc.scrollHeight - doc.clientHeight)) * 100;
    bar.style.width = `${Math.min(100, pct)}%`;
  }, { passive: true });
}

/** Ping API and update header status badge */
async function checkApiHealth() {
  const el = document.getElementById('api-status');
  if (!el) return;
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 3000);
    const r = await fetch('/api/health', { signal: ctrl.signal });
    clearTimeout(timer);
    if (r.ok) {
      el.textContent = '● Online';
      el.classList.add('online');
      el.classList.remove('offline');
    } else throw new Error('bad status');
  } catch {
    el.textContent = '● Offline';
    el.classList.add('offline');
    el.classList.remove('online');
  }
}

/** Smooth scroll to results after a successful run */
function scrollToResults() {
  const panel = document.getElementById('results-panel');
  if (!panel) return;
  setTimeout(() => {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 200);
}

/** Subtle pulse on primary run button when form is complete */
function pulseRunIfReady() {
  const btn = document.getElementById('run-btn');
  if (!btn) return;
  let ok = true;
  FIELD_IDS.forEach((id) => {
    const v = document.getElementById(id)?.value.trim();
    if (!v) ok = false;
  });
  btn.style.animation = ok ? 'none' : '';
}

document.addEventListener('DOMContentLoaded', () => {
  ['no_plates', 'T', 'plate_thk', 'ti'].forEach((id) => {
    document.getElementById(id)?.addEventListener('input', () => {
      updateDerivedHint();
      pulseRunIfReady();
    });
  });
  FIELD_IDS.forEach((id) => {
    document.getElementById(id)?.addEventListener('input', pulseRunIfReady);
  });
  updateDerivedHint();
  initScrollProgress();
  checkApiHealth();
  setInterval(checkApiHealth, 60000);
});
