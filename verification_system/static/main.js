const dropZone   = document.getElementById('dropZone');
const fileInput  = document.getElementById('fileInput');
const previewWrap= document.getElementById('previewWrap');
const previewImg = document.getElementById('previewImg');
const clearBtn   = document.getElementById('clearBtn');
const scanBtn    = document.getElementById('scanBtn');
const scanText   = document.getElementById('scanBtnText');
const scanLoader = document.getElementById('scanBtnLoader');
const resultsCard= document.getElementById('resultsCard');
const statusBadge= document.getElementById('statusBadge');
const fraudBanner= document.getElementById('fraudBanner');
const successBanner = document.getElementById('successBanner');
const warnBanner = document.getElementById('warnBanner');
const dataGrid   = document.getElementById('dataGrid');
const hashBox    = document.getElementById('hashBox');
const hashValue  = document.getElementById('hashValue');
const historyList= document.getElementById('historyList');
const userName   = document.getElementById('userName');
const userCredits= document.getElementById('userCredits');

let selectedFile = null;

// ── Drag & drop ──────────────────────────────────────────────
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(file) {
  selectedFile = file;
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewWrap.style.display = 'block';
  dropZone.style.display = 'none';
  scanBtn.disabled = false;
  hideResults();
}

clearBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  previewImg.src = '';
  previewWrap.style.display = 'none';
  dropZone.style.display = 'block';
  scanBtn.disabled = true;
  hideResults();
});

// ── Scan ─────────────────────────────────────────────────────
scanBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  // Show loader
  scanText.style.display  = 'none';
  scanLoader.style.display= 'flex';
  scanBtn.disabled = true;

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const resp = await fetch('/scan', { method: 'POST', body: formData });
    const data = await resp.json();
    renderResults(data);
    loadHistory();
  } catch (err) {
    alert('Network error. Is the Flask server running?');
  } finally {
    scanText.style.display  = 'inline';
    scanLoader.style.display= 'none';
    scanBtn.disabled = false;
  }
});

// ── Render Results ───────────────────────────────────────────
function renderResults(data) {
  hideResults();
  resultsCard.style.display = 'block';

  // Status badge
  if (data.status === 'accepted') {
    if (!data.bill_number || !data.date) {
      statusBadge.textContent = '⚠️ Unclear';
      statusBadge.className = 'status-badge rejected';
      warnBanner.style.display = 'flex';
    } else if (data.is_duplicate) {
      statusBadge.textContent = '🚨 Duplicate';
      statusBadge.className = 'status-badge duplicate';
      fraudBanner.style.display = 'flex';
    } else {
      statusBadge.textContent = '✅ Original';
      statusBadge.className = 'status-badge original';
      successBanner.style.display = 'flex';
    }
  } else if (data.status === 'rejected') {
    statusBadge.textContent = '⚠️ Rejected';
    statusBadge.className = 'status-badge rejected';
  } else {
    statusBadge.textContent = '❌ Error';
    statusBadge.className = 'status-badge rejected';
  }

  // Data grid
  const fields = [
    { label: 'Bill Number', value: data.bill_number || '—' },
    { label: 'Date',        value: data.date        || '—' },
    { label: 'Amount (INR)',value: data.amount ? `₹ ${data.amount}` : '—', cls: 'amount' },
    { label: 'Credits Earned', value: data.credits_earned !== undefined ? `🪙 ${data.credits_earned}` : '—', cls: 'amount' },
    { label: 'Status',      value: data.message     || '—' },
  ];
  dataGrid.innerHTML = fields.map(f => `
    <div class="data-cell">
      <div class="data-cell-label">${f.label}</div>
      <div class="data-cell-value ${f.cls || ''}">${f.value}</div>
    </div>
  `).join('');

  // Hash
  if (data.hash) {
    hashValue.textContent = data.hash;
    hashBox.style.display = 'flex';
  }
}

function hideResults() {
  resultsCard.style.display = 'none';
  fraudBanner.style.display = 'none';
  successBanner.style.display = 'none';
  if(warnBanner) warnBanner.style.display = 'none';
  hashBox.style.display = 'none';
  dataGrid.innerHTML = '';
  statusBadge.textContent = '';
  statusBadge.className = 'status-badge';
}

// ── History ──────────────────────────────────────────────────
async function loadHistory() {
  try {
    const resp = await fetch('/history');
    if (resp.redirected) {
      window.location.href = resp.url; // Handle login redirect
      return;
    }
    const data = await resp.json();
    
    if (userName) userName.textContent = data.username;
    if (userCredits) userCredits.textContent = `🪙 ${data.total_credits} Credits`;

    const records = data.history;

    if (records.length === 0) {
      historyList.innerHTML = '<p class="empty-history">No bills scanned yet.</p>';
      return;
    }
    historyList.innerHTML = records.map((r, i) => `
      <div class="history-item">
        <span class="history-hash" title="${r.hash}">#${records.length - i} &nbsp; ${r.hash}</span>
        <span class="history-amount">₹ ${r.amount} <br><small style="color:var(--accent2); font-size:0.75rem;">+${r.credits_earned} Cred</small></span>
      </div>
    `).join('');
  } catch (_) {}
}

// Load history on startup
loadHistory();
