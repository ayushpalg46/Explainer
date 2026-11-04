"""
Interactive HTML Dashboard Generator for Explainer.
Creates a self-contained, responsive web application featuring interactive dependency graphs,
instant search, language filters, and deep-dive file inspection drawers.
"""
import json
from typing import Dict, Any, List


class HTMLDashboardReporter:
    def generate_dashboard(
        self,
        arch_data: Dict[str, Any],
        compatibility: List[Dict[str, str]],
        file_explanations: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> str:
        data_json = json.dumps({
            "arch": arch_data,
            "compatibility": compatibility,
            "files": file_explanations,
            "edges": edges
        }, indent=2)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Explainer | Codebase Architecture & Deep Inspection Dashboard</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(18, 24, 38, 0.85);
      --border: #23304a;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.25);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --success: #10b981;
      --warning: #f59e0b;
      --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      line-height: 1.5;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 24px;
      background: rgba(15, 23, 42, 0.9);
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(12px);
      z-index: 100;
    }}
    .logo {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      background: var(--accent-glow);
      color: var(--accent);
      border: 1px solid var(--accent);
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 9999px;
      font-weight: 600;
    }}
    .metrics-bar {{
      display: flex;
      gap: 16px;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .metrics-bar strong {{ color: var(--text); }}
    .main-layout {{
      display: flex;
      flex: 1;
      overflow: hidden;
    }}
    .sidebar {{
      width: 380px;
      border-right: 1px solid var(--border);
      background: var(--card-bg);
      display: flex;
      flex-direction: column;
    }}
    .search-box {{
      padding: 14px;
      border-bottom: 1px solid var(--border);
    }}
    .search-input {{
      width: 100%;
      padding: 8px 12px;
      background: #0f172a;
      border: 1px solid var(--border);
      color: #fff;
      border-radius: 6px;
      font-size: 0.875rem;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-glow);
    }}
    .file-list {{
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }}
    .file-item {{
      padding: 10px 12px;
      border-radius: 6px;
      cursor: pointer;
      margin-bottom: 4px;
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }}
    .file-item:hover {{
      background: #1e293b;
      border-color: var(--border);
    }}
    .file-item.active {{
      background: rgba(56, 189, 248, 0.12);
      border-color: var(--accent);
    }}
    .file-item-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}
    .file-name {{
      font-weight: 600;
      font-size: 0.9rem;
      color: #fff;
    }}
    .file-loc {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }}
    .file-role {{
      font-size: 0.75rem;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .content-area {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }}
    .view-tabs {{
      display: flex;
      background: rgba(15, 23, 42, 0.7);
      border-bottom: 1px solid var(--border);
      padding: 0 16px;
    }}
    .tab-btn {{
      padding: 10px 18px;
      background: none;
      border: none;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.875rem;
      cursor: pointer;
      border-bottom: 2px solid transparent;
    }}
    .tab-btn.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}
    .tab-panel {{
      display: none;
      flex: 1;
      overflow: hidden;
    }}
    .tab-panel.active {{
      display: flex;
      flex-direction: column;
    }}
    #graph-container {{
      flex: 1;
      width: 100%;
      height: 100%;
      background: #090d16;
    }}
    #details-panel {{
      padding: 24px;
      overflow-y: auto;
    }}
    .section-title {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent);
      margin: 20px 0 10px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .card {{
      background: #111827;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin-top: 8px;
    }}
    th, td {{
      padding: 8px 12px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      color: var(--text-muted);
      background: rgba(15, 23, 42, 0.8);
      font-weight: 600;
    }}
    .badge-pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      background: #1e293b;
      color: #94a3b8;
    }}
    .pass-tag {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
    .warn-tag {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; }}
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <span>⚡ Explainer</span>
      <span class="badge">Deep Codebase Intelligence</span>
    </div>
    <div class="metrics-bar" id="top-metrics">
      <span>Files: <strong id="m-files">0</strong></span>
      <span>Lines of Code: <strong id="m-loc">0</strong></span>
      <span>Architecture: <strong id="m-arch">Scanning...</strong></span>
    </div>
  </header>

  <div class="main-layout">
    <div class="sidebar">
      <div class="search-box">
        <input type="text" id="file-search" class="search-input" placeholder="Search files, tags, symbols...">
      </div>
      <div class="file-list" id="file-list-container"></div>
    </div>

    <div class="content-area">
      <div class="view-tabs">
        <button class="tab-btn active" onclick="switchTab('graph')">🌐 Interconnection Graph</button>
        <button class="tab-btn" onclick="switchTab('details')">📄 File Deep Inspection</button>
        <button class="tab-btn" onclick="switchTab('compat')">🛡️ Compatibility Matrix</button>
      </div>

      <div id="tab-graph" class="tab-panel active">
        <div id="graph-container"></div>
      </div>

      <div id="tab-details" class="tab-panel">
        <div id="details-panel">
          <p style="color: var(--text-muted)">Select a file from the sidebar or click a node in the graph to view deep technical explanations.</p>
        </div>
      </div>

      <div id="tab-compat" class="tab-panel" style="padding: 24px; overflow-y: auto;">
        <h2 style="margin-bottom: 12px; color: #fff;">Tech Stack & Configuration Matrix</h2>
        <div class="card" id="compat-container"></div>
      </div>
    </div>
  </div>

  <script>
    const DATA = {data_json};

    document.getElementById('m-files').innerText = DATA.arch.total_files;
    document.getElementById('m-loc').innerText = DATA.arch.total_loc.toLocaleString();
    document.getElementById('m-arch').innerText = DATA.arch.architecture_type;

    let selectedFile = DATA.files[0] || null;
    let network = null;

    function renderFileList(filterText = '') {{
      const container = document.getElementById('file-list-container');
      container.innerHTML = '';
      const lower = filterText.toLowerCase();

      DATA.files.forEach(f => {{
        if (lower && !f.header.path.toLowerCase().includes(lower) && !f.header.language.toLowerCase().includes(lower)) return;

        const div = document.createElement('div');
        div.className = 'file-item' + (selectedFile && selectedFile.header.path === f.header.path ? ' active' : '');
        div.innerHTML = `
          <div class="file-item-header">
            <span class="file-name">${{f.header.filename}}</span>
            <span class="file-loc">${{f.header.loc}} LOC</span>
          </div>
          <div class="file-role">${{f.header.language}} • ${{f.header.role}}</div>
        `;
        div.onclick = () => {{
          selectFile(f);
          switchTab('details');
        }};
        container.appendChild(div);
      }});
    }}

    function selectFile(f) {{
      selectedFile = f;
      renderFileList(document.getElementById('file-search').value);
      renderDetails();
      if (network) {{
        network.selectNodes([f.header.path]);
      }}
    }}

    function renderDetails() {{
      const panel = document.getElementById('details-panel');
      if (!selectedFile) return;

      const h = selectedFile.header;
      const p = selectedFile.purpose_and_context;
      const conns = selectedFile.interconnections;

      let conceptsHtml = selectedFile.concepts_and_patterns.map(c => `
        <div style="margin-bottom: 8px;">
          <strong style="color: var(--accent);">${{c.concept}}:</strong>
          <span style="color: var(--text-muted);">${{c.explanation}}</span>
        </div>
      `).join('');

      let symbolsHtml = selectedFile.symbol_breakdown.map(s => `
        <tr>
          <td>${{s.line}}</td>
          <td><span class="badge-pill">${{s.kind}}</span></td>
          <td style="font-family: var(--font-mono); color: #fff;">${{escapeHtml(s.signature)}}</td>
          <td>${{s.description}}</td>
        </tr>
      `).join('');

      let outgoingHtml = conns.outgoing.map(o => `
        <tr>
          <td style="color: #38bdf8;">➔ ${{o.target}}</td>
          <td><span class="badge-pill">${{o.relation}}</span></td>
          <td style="font-family: var(--font-mono); font-size: 0.75rem;">${{escapeHtml(o.how)}}</td>
          <td>${{o.why}}</td>
        </tr>
      `).join('');

      let incomingHtml = conns.incoming.map(i => `
        <tr>
          <td style="color: #10b981;">⬅ ${{i.source}}</td>
          <td><span class="badge-pill">${{i.relation}}</span></td>
          <td style="font-family: var(--font-mono); font-size: 0.75rem;">${{escapeHtml(i.how)}}</td>
          <td>${{i.why}}</td>
        </tr>
      `).join('');

      panel.innerHTML = `
        <div style="margin-bottom: 20px;">
          <h1 style="font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${{h.filename}}</h1>
          <p style="color: var(--text-muted); font-size: 0.85rem;">${{h.path}} | ${{h.language}} | ${{h.loc}} LOC</p>
        </div>

        <div class="card">
          <h3 style="color: #fff; margin-bottom: 6px;">Executive Purpose</h3>
          <p style="color: var(--text); font-size: 0.95rem; margin-bottom: 10px;">${{p.summary}}</p>
          <p style="color: var(--text-muted); font-size: 0.85rem;">${{p.architectural_significance}}</p>
        </div>

        ${{conceptsHtml ? `<div class="card"><h3 style="color: #fff; margin-bottom: 8px;">Architectural Concepts</h3>${{conceptsHtml}}</div>` : ''}}

        <div class="section-title">🔗 Interconnections (HOW & WHY it works)</div>
        <div class="card">
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">Coupling: ${{conns.coupling_assessment}}</p>
          ${{outgoingHtml || incomingHtml ? `
            <table>
              <thead>
                <tr><th>File</th><th>Relation</th><th>HOW</th><th>WHY (Rationale)</th></tr>
              </thead>
              <tbody>
                ${{outgoingHtml}}
                ${{incomingHtml}}
              </tbody>
            </table>
          ` : '<p style="color: var(--text-muted); font-size: 0.85rem;">Standalone file with no direct dependencies.</p>'}
        </div>

        <div class="section-title">🧩 Symbol & Component Breakdown</div>
        <div class="card">
          <table>
            <thead>
              <tr><th>Line</th><th>Kind</th><th>Symbol / Signature</th><th>Role & Function</th></tr>
            </thead>
            <tbody>
              ${{symbolsHtml}}
            </tbody>
          </table>
        </div>
      `;
    }}

    function initGraph() {{
      const container = document.getElementById('graph-container');
      const nodes = DATA.files.map((f, i) => ({{
        id: f.header.path,
        label: f.header.filename,
        title: f.header.role,
        shape: 'box',
        color: {{
          background: '#1e293b',
          border: f.header.language === 'HTML' ? '#f97316' :
                  f.header.language === 'CSS' ? '#38bdf8' :
                  f.header.language === 'Python' ? '#3b82f6' :
                  f.header.language === 'Rust' ? '#ea580c' :
                  f.header.language === 'Go' ? '#06b6d4' :
                  f.header.language === 'Java' ? '#dc2626' :
                  f.header.language === 'Dockerfile' ? '#0284c7' : '#8b5cf6',
          highlight: {{ background: '#38bdf8', border: '#fff' }}
        }},
        font: {{ color: '#fff' }}
      }}));

      const edges = DATA.edges.map(e => ({{
        from: e.from,
        to: e.to,
        label: e.type,
        arrows: 'to',
        color: {{ color: '#334155', highlight: '#38bdf8' }},
        font: {{ color: '#64748b', size: 10 }}
      }}));

      const data = {{ nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) }};
      const options = {{
        physics: {{ stabilization: true, barnesHut: {{ springLength: 120 }} }},
        interaction: {{ hover: true }}
      }};

      network = new vis.Network(container, data, options);
      network.on('click', params => {{
        if (params.nodes.length > 0) {{
          const clickedPath = params.nodes[0];
          const fileObj = DATA.files.find(f => f.header.path === clickedPath);
          if (fileObj) selectFile(fileObj);
        }}
      }});
    }}

    function renderCompat() {{
      const cCont = document.getElementById('compat-container');
      let html = `
        <table>
          <thead><tr><th>Status</th><th>Category</th><th>Rule</th><th>Details</th></tr></thead>
          <tbody>
      `;
      DATA.compatibility.forEach(c => {{
        const isPass = c.status === 'PASS';
        html += `
          <tr>
            <td><span class="badge-pill ${{isPass ? 'pass-tag' : 'warn-tag'}}">${{c.status}}</span></td>
            <td style="color: var(--text-muted);">${{c.category}}</td>
            <td style="color: #fff; font-weight: 600;">${{c.title}}</td>
            <td>${{c.details}}</td>
          </tr>
        `;
      }});
      html += '</tbody></table>';
      cCont.innerHTML = html;
    }}

    function switchTab(name) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.getElementById('tab-' + name).classList.add('active');
      event.target.classList.add('active');
      if (name === 'graph' && network) {{
        setTimeout(() => network.fit(), 100);
      }}
    }}

    function escapeHtml(str) {{
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    document.getElementById('file-search').addEventListener('input', e => renderFileList(e.target.value));

    renderFileList();
    renderCompat();
    initGraph();
    if (DATA.files.length > 0) selectFile(DATA.files[0]);
  </script>
</body>
</html>
"""
        return html
