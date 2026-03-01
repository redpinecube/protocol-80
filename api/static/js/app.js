// ===== MOCK DATA =====
const mockEndpoints = [
  { method: 'GET', endpoint: '/users', desc: 'List all users', score: 92 },
  { method: 'POST', endpoint: '/users', desc: 'Create a new user', score: 88 },
  { method: 'GET', endpoint: '/users/:id', desc: 'Get user by ID', score: 95 },
  { method: 'PUT', endpoint: '/users/:id', desc: 'Update user', score: 76 },
  { method: 'DELETE', endpoint: '/users/:id', desc: 'Delete user', score: 61 },
  { method: 'GET', endpoint: '/products', desc: 'List products', score: 84 },
  { method: 'POST', endpoint: '/products', desc: 'Create product', score: 72 },
  { method: 'GET', endpoint: '/orders', desc: 'List orders', score: 90 },
  { method: 'POST', endpoint: '/auth/login', desc: 'Authenticate user', score: 67 },
  { method: 'GET', endpoint: '/health', desc: 'Health check', score: 98 },
  { method: 'GET', endpoint: '/docs', desc: 'API documentation', score: 55 },
  { method: 'POST', endpoint: '/webhooks', desc: 'Register webhook', score: 43 },
];

const mockFullAnalysis = {
  'https://api.stripe.com/v1': {
    overall: 94,
    criteria: { structural: 96, completeness: 93, docAlignment: 97, naming: 91, aiFriendly: 95 },
    tags: [['OpenAPI 3.1','pass'],['Rate Limits','pass'],['Versioned','pass'],['Idempotent','pass']],
    summary: [
      "Stripe's API demonstrates exceptional agent-readiness with comprehensive OpenAPI 3.1 specifications, consistent resource naming, and thorough error schemas. Every endpoint returns structured, predictable JSON that LLM-based agents can reliably parse and act upon.",
      "Structural clarity is near-perfect — responses follow a uniform envelope pattern with consistent typing. Documentation alignment is best-in-class; the live API matches its published contract with zero drift. Minor naming deductions for legacy Charges API field inconsistencies."
    ],
    recommendations: [
      { severity: 'info', title: 'Migrate legacy Charges endpoints', body: 'The /v1/charges path uses slightly different field naming conventions than PaymentIntents. Aligning these would improve naming clarity score.' },
      { severity: 'info', title: 'Add JSON:API sparse fieldsets', body: 'Supporting field filtering would improve AI-friendliness by reducing payload noise for agent parsing by up to 60%.' },
    ],
  },
  'https://api.github.com': {
    overall: 91,
    criteria: { structural: 93, completeness: 89, docAlignment: 95, naming: 88, aiFriendly: 90 },
    tags: [['REST','pass'],['GraphQL','pass'],['Pagination','pass'],['CORS','warn']],
    summary: [
      "GitHub's API offers dual REST and GraphQL interfaces with strong structural clarity. JSON responses are consistent and well-typed, and the GraphQL endpoint enables precise data fetching that minimizes token overhead for LLM agents.",
      "Completeness is solid but some REST endpoints omit nested relationships unless explicitly expanded. Documentation alignment is excellent — the OpenAPI spec is accurate and maintained. Naming is mostly clear, though some legacy fields use abbreviated conventions that reduce machine readability."
    ],
    recommendations: [
      { severity: 'warning', title: 'Standardize CORS headers', body: 'Browser-based AI agents are blocked by restrictive CORS policies. Consider a permissive policy for read-only endpoints.' },
      { severity: 'info', title: 'Unify pagination patterns', body: 'Some endpoints use Link headers while others use cursor-based pagination, reducing structural predictability.' },
      { severity: 'critical', title: 'Document secondary rate limits', body: 'Abuse detection rate limits are opaque and can block agents without clear error messaging.' },
    ],
  },
  'https://api.openai.com/v1': {
    overall: 87,
    criteria: { structural: 90, completeness: 84, docAlignment: 78, naming: 92, aiFriendly: 93 },
    tags: [['Streaming','pass'],['Auth','pass'],['Rate Limits','warn'],['Error Schema','pass']],
    summary: [
      "OpenAI's API excels in naming clarity and AI-friendliness — unsurprisingly, it's designed with machine consumers in mind. Field names are descriptive, responses are cleanly structured, and the function calling interface is purpose-built for agentic use.",
      "Documentation alignment is the weakest area: the published docs lag behind actual API behavior, with undocumented parameters and model-specific quirks. Completeness suffers from inconsistent field presence across different model responses."
    ],
    recommendations: [
      { severity: 'warning', title: 'Publish full OpenAPI specification', body: 'A complete, versioned OpenAPI spec would dramatically improve documentation alignment and enable automated agent onboarding.' },
      { severity: 'warning', title: 'Clarify rate limit recovery', body: 'The Retry-After header is sometimes missing on 429 responses, reducing structural predictability for agent retry logic.' },
      { severity: 'info', title: 'Standardize response shapes across models', body: 'Different models return slightly different response structures, reducing completeness score.' },
    ],
  },
  'https://jsonplaceholder.typicode.com': {
    overall: 68,
    criteria: { structural: 75, completeness: 70, docAlignment: 48, naming: 82, aiFriendly: 62 },
    tags: [['No Auth','warn'],['No Versioning','fail'],['JSON','pass'],['CORS','pass']],
    summary: [
      "JSONPlaceholder has decent structural clarity for a test API — responses are flat, consistent JSON with predictable schemas. Naming is reasonably clear with conventional field names that agents can interpret without ambiguity.",
      "However, documentation alignment is poor: there is no formal OpenAPI specification, and the informal docs don't fully describe edge cases. AI-friendliness suffers from missing error schemas, no content negotiation, and no machine-readable metadata for automated discovery."
    ],
    recommendations: [
      { severity: 'critical', title: 'Add API versioning', body: 'Without versioning, any breaking change disrupts all agent integrations simultaneously. This is the biggest structural clarity risk.' },
      { severity: 'critical', title: 'Publish OpenAPI specification', body: 'An OpenAPI spec would dramatically improve documentation alignment and AI-friendliness scores.' },
      { severity: 'warning', title: 'Add structured error responses', body: 'Current error responses lack machine-readable error codes, severely impacting AI-friendliness.' },
      { severity: 'warning', title: 'Implement content negotiation', body: 'Supporting Accept headers and content types would improve AI-friendliness for diverse agent frameworks.' },
    ],
  }
};

// ===== HELPERS =====
function getScoreColor(s) {
  if (s >= 80) return 'var(--green)';
  if (s >= 60) return 'var(--yellow)';
  return 'var(--pink)';
}

function generateFullAnalysis(url) {
  const st = 40 + Math.floor(Math.random() * 55);
  const co = 40 + Math.floor(Math.random() * 55);
  const da = 40 + Math.floor(Math.random() * 55);
  const na = 40 + Math.floor(Math.random() * 55);
  const ai = 40 + Math.floor(Math.random() * 55);
  const overall = Math.round((st + co + da + na + ai) / 5);
  return {
    overall,
    criteria: { structural: st, completeness: co, docAlignment: da, naming: na, aiFriendly: ai },
    tags: [
      ['OpenAPI', da > 70 ? 'pass' : 'fail'],
      ['Rate Limits', st > 65 ? 'pass' : 'warn'],
      ['Auth', co > 60 ? 'pass' : 'warn'],
      ['CORS', na > 50 ? 'pass' : 'warn']
    ],
    summary: [
      `This API received a Protocol 80 score of ${overall}/100. Structural Clarity scored ${st}, Completeness ${co}, Documentation Alignment ${da}, Naming Clarity ${na}, and AI-Friendliness ${ai}.`,
      `For the 2026 Agentic Economy, this API ${overall >= 80 ? 'is well-positioned' : overall >= 60 ? 'has room for improvement' : 'needs significant work'} to serve autonomous agent traffic. ${overall < 80 ? 'Key areas to address include documentation alignment and structured error responses.' : 'Strong patterns in schema consistency and naming conventions.'}`
    ],
    recommendations: [
      { severity: da < 70 ? 'critical' : 'warning', title: 'Improve documentation alignment', body: `Documentation alignment score of ${da} indicates ${da < 60 ? 'major drift' : 'minor gaps'} between published docs and actual API behavior. Agents depend on accurate contracts.` },
      { severity: ai < 70 ? 'critical' : 'info', title: 'Boost AI-friendliness', body: `AI-friendliness score of ${ai} suggests ${ai < 60 ? 'significant barriers' : 'some friction'} for LLM agents. Consider adding structured metadata, consistent enums, and machine-readable error codes.` },
      { severity: 'info', title: 'Add agent-specific headers', body: 'Supporting X-Agent-Id and X-Correlation-Id headers enables agent traceability and improves debugging workflows.' },
    ],
  };
}

// ===== LOADING OVERLAY (only runs on index.html) =====
const loadingStepDefs = [
  { status: 'Resolving endpoint schema', duration: 900 },
  { status: 'Crawling API surface', duration: 1400 },
  { status: 'Evaluating agent compatibility', duration: 1800 },
  { status: 'Scoring with Protocol 80', duration: 1200 },
  { status: 'Generating report', duration: 800 },
];

function showLoading(url, onComplete) {
  const overlay = document.getElementById('loadingOverlay');
  if (!overlay) { onComplete(); return; }

  const statusEl = document.getElementById('loadingStatus');
  const progressFill = document.getElementById('progressFill');

  for (let i = 0; i < 5; i++) {
    document.getElementById(`step-${i}`).className = 'load-step';
    document.getElementById(`step-${i}-time`).textContent = '';
  }
  progressFill.style.width = '0%';
  overlay.classList.remove('fade-out');
  overlay.classList.add('active');

  let currentStep = 0;
  let startTime = performance.now();

  function advanceStep() {
    if (currentStep >= loadingStepDefs.length) {
      statusEl.innerHTML = 'Analysis complete<span class="cursor-blink"></span>';
      progressFill.style.width = '100%';
      setTimeout(() => {
        overlay.classList.add('fade-out');
        setTimeout(() => { overlay.classList.remove('active', 'fade-out'); onComplete(); }, 500);
      }, 400);
      return;
    }
    const sd = loadingStepDefs[currentStep];
    const el = document.getElementById(`step-${currentStep}`);
    el.classList.add('active');
    statusEl.innerHTML = `${sd.status}<span class="cursor-blink"></span>`;
    progressFill.style.width = `${((currentStep + 0.5) / loadingStepDefs.length) * 100}%`;
    setTimeout(() => {
      document.getElementById(`step-${currentStep}-time`).textContent =
        ((performance.now() - startTime) / 1000).toFixed(1) + 's';
      el.classList.remove('active');
      el.classList.add('done');
      currentStep++;
      advanceStep();
    }, sd.duration);
  }

  setTimeout(advanceStep, 300);
}

// ===== HOME PAGE LOGIC =====
(function initHome() {
  const input = document.getElementById('apiInput');
  const dropdown = document.getElementById('dropdown');
  if (!input || !dropdown) return;

  let debounceTimer = null;

  input.addEventListener('input', () => {
    const val = input.value.trim();
    clearTimeout(debounceTimer);
    if (!val) { dropdown.classList.remove('active'); return; }
    dropdown.innerHTML = '<div class="dropdown-loading"><span class="spinner"></span>Discovering endpoints...</div>';
    dropdown.classList.add('active');
    debounceTimer = setTimeout(() => discoverEndpoints(val), 500);
  });

  window.discoverEndpoints = function(baseUrl) {
    const filtered = mockEndpoints.filter(e =>
      e.endpoint.toLowerCase().includes(baseUrl.replace(/https?:\/\/[^/]+/i, '').toLowerCase()) || baseUrl.length > 5
    );
    if (!filtered.length) { dropdown.innerHTML = '<div class="dropdown-loading">No endpoints discovered</div>'; return; }
    dropdown.innerHTML = filtered.map((e, i) => {
      const mc = `method-${e.method.toLowerCase()}`;
      const sc = e.score >= 80 ? 'score-high' : e.score >= 60 ? 'score-mid' : 'score-low';
      return `<div class="dropdown-item" onclick="selectEndpoint('${baseUrl}', ${i})">
        <span class="item-method ${mc}">${e.method}</span>
        <div class="item-info"><div class="item-endpoint">${e.endpoint}</div><div class="item-desc">${e.desc}</div></div>
        <span class="item-score ${sc}">${e.score}</span>
      </div>`;
    }).join('');
    dropdown.classList.add('active');
  };

  window.selectEndpoint = function(base, idx) {
    input.value = base + mockEndpoints[idx].endpoint;
    dropdown.classList.remove('active');
  };

  window.tryExample = function(url) {
    input.value = url; input.focus(); dropdown.classList.remove('active'); scanApi();
  };

  window.scanApi = function() {
    const url = input.value.trim();
    if (!url) return;
    dropdown.classList.remove('active');
    const btn = document.getElementById('scanBtn');
    btn.innerHTML = '<span class="spinner" style="width:14px;height:14px;border-width:2px;"></span> Scanning';
    btn.disabled = true;

    showLoading(url, () => {
      const data = mockFullAnalysis[url] || generateFullAnalysis(url);
      const payload = { url, analysisId: 'p80-' + Math.random().toString(36).substring(2, 10), ...data };
      sessionStorage.setItem('ratemyapi_analysis', JSON.stringify(payload));
      btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" width="15" height="15"><path d="M2 12l5 5L22 2"/></svg> Audit';
      btn.disabled = false;
      window.location.href = '/analysis/';
    });
  };

  document.addEventListener('click', e => {
    if (!document.getElementById('searchBar').contains(e.target)) dropdown.classList.remove('active');
  });
  input.addEventListener('keydown', e => { if (e.key === 'Enter') scanApi(); });
})();
