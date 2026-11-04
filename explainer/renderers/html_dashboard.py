import json
from pathlib import Path
from ..models import CodebaseAnalysis, FileAnalysis


class HtmlDashboardRenderer:
    def render(self, analysis: CodebaseAnalysis, output_path: str) -> str:
        # Prepare JSON serialization of analysis data for client-side interactivity
        nodes = []
        edges = []
        for rel_path, fa in analysis.files.items():
            nodes.append({
                "id": rel_path,
                "label": Path(rel_path).name,
                "path": rel_path,
                "language": fa.language,
                "lines": fa.line_count,
                "role": fa.role_in_codebase
            })

        for conn in analysis.interconnections:
            edges.append({
                "from": conn.source_file,
                "to": conn.target_file,
                "label": conn.relation_type,
                "how": conn.how_it_works,
                "why": conn.why_it_works,
                "code": conn.code_reference or ""
            })

        # Pre-package files dictionary for client-side viewer
        files_payload = {}
        for rel_path, fa in analysis.files.items():
            files_payload[rel_path] = {
                "file_path": fa.file_path,
                "relative_path": fa.relative_path,
                "language": fa.language,
                "line_count": fa.line_count,
                "file_size_bytes": fa.file_size_bytes,
                "summary": fa.summary,
                "role_in_codebase": fa.role_in_codebase,
                "concepts_detected": fa.concepts_detected,
                "frameworks_detected": fa.frameworks_detected,
                "design_and_style_notes": fa.design_and_style_notes or "",
                "animations_and_interactions": fa.animations_and_interactions or "",
                "ai_insights": fa.ai_insights or "",
                "ai_model_used": fa.ai_model_used or "",
                "beginner_story": fa.beginner_story or "",
                "elements": [
                    {
                        "name": el.name,
                        "kind": el.kind,
                        "line_number": el.line_number,
                        "snippet": el.snippet or "",
                        "what_it_is": el.what_it_is,
                        "how_it_is_used": el.how_it_is_used,
                        "where_it_is_used": el.where_it_is_used,
                        "why_it_works": el.why_it_works,
                        "best_practices": el.best_practices_and_pitfalls or "",
                        "simple_analogy": el.simple_analogy or "",
                        "what_happens_on_screen": el.what_happens_on_screen or "",
                        "what_if_removed": el.what_if_removed or ""
                    }
                    for el in fa.elements
                ],
                "inbound": [
                    {"source": inb.source_file, "type": inb.relation_type, "how": inb.how_it_works, "why": inb.why_it_works}
                    for inb in fa.inbound_connections
                ],
                "outbound": [
                    {"target": outb.target_file, "type": outb.relation_type, "how": outb.how_it_works, "why": outb.why_it_works}
                    for outb in fa.outbound_connections
                ]
            }

        graph_data_json = json.dumps({"nodes": nodes, "edges": edges})
        files_data_json = json.dumps(files_payload)
        tech_stack_json = json.dumps(analysis.tech_stack.model_dump())
        folder_roles_json = json.dumps(analysis.folder_roles)

        beginner_codebase_html = ""
        if analysis.beginner_codebase_story:
            safe_story = (analysis.beginner_codebase_story
                          .replace("&", "&amp;")
                          .replace("<", "&lt;")
                          .replace(">", "&gt;"))
            beginner_codebase_html = f"""
            <div class="card" style="border: 1px solid #38bdf8; background: #0c1a30; margin-bottom:20px; box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);">
              <h2 style="color:#7dd3fc; font-size:1.15rem; margin-bottom:8px;">🏰 The Big Castle Story (Explain Like I'm 4 Years Old)</h2>
              <div style="color:#e0f2fe; line-height:1.65; font-size:0.95rem;">{safe_story}</div>
            </div>
            """

        ai_arch_html = ""
        if analysis.ai_architecture_critique:
            model_badge = analysis.ai_model_name or "Local AI Model"
            safe_critique = (analysis.ai_architecture_critique
                             .replace("&", "&amp;")
                             .replace("<", "&lt;")
                             .replace(">", "&gt;"))
            ai_arch_html = f"""
            <div class="card" style="border: 1px solid #a855f7; background: #181126; margin-bottom:20px; box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);">
              <h2 style="color:#e9d5ff; font-size:1.15rem; margin-bottom:8px;">🧠 Neural AI Architecture Review <small style="color:#c084fc; font-size:0.8rem;">({model_badge})</small></h2>
              <div style="color:#f3e8ff; line-height:1.65; white-space:pre-wrap; font-size:0.92rem;">{safe_critique}</div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Explainer Dashboard - {analysis.project_name}</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f293d;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --green: #10b981;
      --yellow: #f59e0b;
      --purple: #8b5cf6;
      --rose: #f43f5e;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }}
    
    /* Layout */
    #sidebar {{ width: 340px; background: #0c1322; border-right: 1px solid var(--card-border); display: flex; flex-direction: column; }}
    #main-content {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
    
    /* Sidebar header */
    .brand {{ padding: 18px 20px; border-bottom: 1px solid var(--card-border); display: flex; align-items: center; justify-content: space-between; }}
    .brand h1 {{ font-size: 1.15rem; color: #fff; font-weight: 700; letter-spacing: -0.5px; }}
    .brand .badge {{ font-size: 0.7rem; background: var(--accent-glow); color: var(--accent); padding: 3px 8px; border-radius: 999px; border: 1px solid var(--accent); }}
    
    .search-box {{ padding: 12px 16px; border-bottom: 1px solid var(--card-border); }}
    .search-box input {{ width: 100%; background: #162032; border: 1px solid var(--card-border); border-radius: 6px; padding: 8px 12px; color: #fff; font-size: 0.85rem; outline: none; }}
    .search-box input:focus {{ border-color: var(--accent); }}

    .file-tree {{ flex: 1; overflow-y: auto; padding: 10px; }}
    .file-item {{ padding: 10px 12px; border-radius: 6px; cursor: pointer; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between; transition: all 0.15s ease; border: 1px solid transparent; }}
    .file-item:hover {{ background: #162032; border-color: var(--card-border); }}
    .file-item.active {{ background: #1a2744; border-color: var(--accent); }}
    .file-name {{ font-size: 0.85rem; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px; }}
    .file-meta {{ font-size: 0.7rem; color: var(--text-muted); }}

    /* Main Navigation Tabs */
    .nav-tabs {{ display: flex; background: #0c1322; border-bottom: 1px solid var(--card-border); padding: 0 20px; }}
    .tab-btn {{ padding: 14px 20px; color: var(--text-muted); background: none; border: none; font-size: 0.9rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }}
    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

    /* Tab Panes */
    .tab-pane {{ flex: 1; overflow-y: auto; padding: 24px 30px; display: none; }}
    .tab-pane.active {{ display: block; }}

    /* Cards */
    .card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
    .card h2 {{ font-size: 1.2rem; margin-bottom: 12px; color: #fff; display: flex; align-items: center; gap: 8px; }}
    .card h3 {{ font-size: 1.0rem; margin: 16px 0 8px; color: var(--accent); }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }}
    
    .stat-box {{ background: #162032; border: 1px solid var(--card-border); border-radius: 8px; padding: 14px 18px; }}
    .stat-box .title {{ font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }}
    .stat-box .value {{ font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 4px; }}

    /* Graph Canvas */
    #graph-container {{ width: 100%; height: 550px; background: #0c1322; border-radius: 10px; border: 1px solid var(--card-border); position: relative; }}
    #graph-canvas {{ width: 100%; height: 100%; }}
    .graph-instructions {{ position: absolute; bottom: 12px; left: 16px; font-size: 0.8rem; color: var(--text-muted); background: rgba(12,19,34,0.85); padding: 6px 12px; border-radius: 4px; pointer-events: none; }}

    /* Table styling */
    table.data-table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    table.data-table th, table.data-table td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--card-border); font-size: 0.85rem; }}
    table.data-table th {{ background: #162032; color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }}
    table.data-table tr:hover td {{ background: #141d2f; }}
    
    .tag-badge {{ background: var(--accent-glow); color: var(--accent); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
    .kind-badge {{ background: #26334d; color: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; }}
    .pill {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; margin-right: 6px; margin-bottom: 6px; background: #1a2538; border: 1px solid #283750; color: #cbd5e1; }}
  </style>
</head>
<body>

  <!-- Sidebar File Browser -->
  <aside id="sidebar">
    <div class="brand">
      <div>
        <h1>{analysis.project_name}</h1>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">Dual-Engine Explainer</div>
      </div>
      <span class="badge">{analysis.total_files} Files</span>
    </div>

    <div class="search-box">
      <input type="text" id="fileSearch" placeholder="Filter files or tags..." onkeyup="filterFiles()">
    </div>

    <div class="file-tree" id="fileTree"></div>
  </aside>

  <!-- Main View Area -->
  <main id="main-content">
    <nav class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('overview')">🏛 Architecture & Stack</button>
      <button class="tab-btn" onclick="switchTab('graph')">🌐 Dependency Graph</button>
      <button class="tab-btn" onclick="switchTab('file-detail')">📄 File Deep Dive</button>
      <button class="tab-btn" onclick="switchTab('interconnections')">🔗 Interconnections ({len(analysis.interconnections)})</button>
    </nav>

    <!-- Tab 1: Architecture Overview -->
    <div id="tab-overview" class="tab-pane active">
      <div class="grid-4">
        <div class="stat-box">
          <div class="title">Total Files</div>
          <div class="value">{analysis.total_files}</div>
        </div>
        <div class="stat-box">
          <div class="title">Lines of Code</div>
          <div class="value">{analysis.total_lines:,}</div>
        </div>
        <div class="stat-box">
          <div class="title">Dependencies</div>
          <div class="value">{len(analysis.interconnections)} Links</div>
        </div>
        <div class="stat-box">
          <div class="title">Engine Mode</div>
          <div class="value" style="font-size:0.95rem; color:var(--accent); font-weight:600; margin-top:8px;">{analysis.engine_used[:22]}...</div>
        </div>
      </div>

      {beginner_codebase_html}

      <div class="card">
        <h2>🏛 Architecture Profile: {analysis.architecture_style}</h2>
        <p style="line-height:1.6; color:#d1d5db; margin-bottom:16px;">{analysis.architecture_summary}</p>
        
        <h3>Tech Stack Ecosystem Compatibility</h3>
        <p style="line-height:1.6; color:#9ca3af;">{analysis.tech_stack.compatibility_analysis}</p>
      </div>
      {ai_arch_html}

      <div class="grid-2">
        <div class="card">
          <h2>📦 Detected Frameworks & Tooling</h2>
          <div style="margin-top:12px;">
            <div style="margin-bottom:12px;">
              <strong style="color:var(--text-muted); font-size:0.8rem; display:block; margin-bottom:6px;">LANGUAGES:</strong>
              {" ".join([f"<span class='pill'>{k} ({v} files)</span>" for k, v in analysis.tech_stack.languages.items()])}
            </div>
            <div style="margin-bottom:12px;">
              <strong style="color:var(--text-muted); font-size:0.8rem; display:block; margin-bottom:6px;">FRAMEWORKS:</strong>
              {" ".join([f"<span class='pill' style='border-color:var(--accent); color:var(--accent);'>{f}</span>" for f in analysis.tech_stack.frameworks]) or "<span style='color:var(--text-muted); font-size:0.8rem;'>None detected</span>"}
            </div>
            <div>
              <strong style="color:var(--text-muted); font-size:0.8rem; display:block; margin-bottom:6px;">BUILD TOOLS & RUNTIMES:</strong>
              {" ".join([f"<span class='pill'>{b}</span>" for b in (analysis.tech_stack.build_tools + analysis.tech_stack.runtimes)]) or "<span style='color:var(--text-muted); font-size:0.8rem;'>Standard environment</span>"}
            </div>
          </div>
        </div>

        <div class="card">
          <h2>📂 Subsystem & Folder Roles</h2>
          <table class="data-table">
            <thead><tr><th>Folder</th><th>Architectural Responsibility</th></tr></thead>
            <tbody>
              {"".join([f"<tr><td><code>{k}/</code></td><td>{v}</td></tr>" for k, v in sorted(analysis.folder_roles.items())])}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab 2: Visual Graph -->
    <div id="tab-graph" class="tab-pane">
      <div class="card" style="margin-bottom:16px;">
        <h2>🌐 Cross-File Interactive Dependency Graph</h2>
        <p style="color:var(--text-muted); font-size:0.85rem;">Click any node to inspect its incoming/outgoing dependencies, or double-click to open its deep breakdown.</p>
      </div>
      <div id="graph-container">
        <div id="graph-canvas"></div>
        <div class="graph-instructions">Click node to inspect | Scroll to zoom | Drag to pan</div>
      </div>
      <div id="graph-info" class="card" style="margin-top:16px; display:none;"></div>
    </div>

    <!-- Tab 3: File Deep Dive -->
    <div id="tab-file-detail" class="tab-pane">
      <div id="file-detail-content">
        <div class="card" style="text-align:center; padding:50px;">
          <h2 style="justify-content:center;">👈 Select a file from the left sidebar</h2>
          <p style="color:var(--text-muted); margin-top:8px;">Choose any file to view all its tags, hooks, functions, CSS layouts, and architectural mechanics.</p>
        </div>
      </div>
    </div>

    <!-- Tab 4: Interconnections Table -->
    <div id="tab-interconnections" class="tab-pane">
      <div class="card">
        <h2>🔗 Cross-File Interconnections Ledger</h2>
        <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:16px;">Exhaustive mapping of how and why each module communicates with its neighbors.</p>
        <table class="data-table">
          <thead>
            <tr><th>Source File</th><th>Target File</th><th>Relation Type</th><th>How & Why It Works</th></tr>
          </thead>
          <tbody>
            {"".join([f"<tr><td><span class='tag-badge'>{c.source_file}</span></td><td><span class='tag-badge' style='background:rgba(16,185,129,0.15); color:var(--green); border:1px solid var(--green);'>{c.target_file}</span></td><td><span class='kind-badge'>{c.relation_type}</span></td><td><strong>How:</strong> {c.how_it_works}<br><br><strong>Why:</strong> {c.why_it_works}</td></tr>" for c in analysis.interconnections])}
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <script>
    const FILES = {files_data_json};
    const GRAPH_DATA = {graph_data_json};
    let activeFilePath = null;
    let network = null;

    function renderSidebar() {{
      const container = document.getElementById("fileTree");
      container.innerHTML = "";
      Object.keys(FILES).sort().forEach(relPath => {{
        const f = FILES[relPath];
        const item = document.createElement("div");
        item.className = "file-item" + (relPath === activeFilePath ? " active" : "");
        item.id = "side-" + btoa(relPath).replace(/=/g, "");
        item.onclick = () => selectFile(relPath);
        item.innerHTML = `
          <div>
            <div class="file-name">${{relPath}}</div>
            <div class="file-meta">${{f.language}}</div>
          </div>
          <span class="file-meta">${{f.line_count}}L</span>
        `;
        container.appendChild(item);
      }});
    }}

    function filterFiles() {{
      const query = document.getElementById("fileSearch").value.toLowerCase();
      document.querySelectorAll(".file-item").forEach(item => {{
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(query) ? "flex" : "none";
      }});
    }}

    function selectFile(relPath) {{
      activeFilePath = relPath;
      document.querySelectorAll(".file-item").forEach(i => i.classList.remove("active"));
      const activeEl = document.getElementById("side-" + btoa(relPath).replace(/=/g, ""));
      if (activeEl) activeEl.classList.add("active");

      renderFileDetail(relPath);
      switchTab('file-detail');
    }}

    function renderFileDetail(relPath) {{
      const f = FILES[relPath];
      const container = document.getElementById("file-detail-content");

      let elementsRows = "";
      f.elements.forEach(el => {{
        let analogyHtml = el.simple_analogy ? `<div style="background:#1e293b; border-left:3px solid #f59e0b; padding:6px 10px; margin:6px 0; border-radius:4px; font-size:0.85rem; color:#fef3c7;"><strong>🧸 Like I'm 4:</strong> ${{escapeHtml(el.simple_analogy)}}</div>` : '';
        let screenHtml = el.what_happens_on_screen ? `<div style="margin-top:4px; font-size:0.85rem; color:#7dd3fc;"><strong>🖥️ On Screen:</strong> ${{escapeHtml(el.what_happens_on_screen)}}</div>` : '';
        let removedHtml = el.what_if_removed ? `<div style="margin-top:4px; font-size:0.85rem; color:#f87171;"><strong>⚠️ If Removed:</strong> ${{escapeHtml(el.what_if_removed)}}</div>` : '';

        elementsRows += `
          <tr>
            <td>
              <strong style="color:var(--accent);">${{escapeHtml(el.name)}}</strong>
              ${{el.snippet ? '<pre style="background:#0b1120; padding:4px 8px; border-radius:4px; font-size:0.75rem; margin-top:4px; color:#cbd5e1; overflow-x:auto;">' + escapeHtml(el.snippet) + '</pre>' : ''}}
            </td>
            <td><span class="kind-badge">${{el.kind}}</span></td>
            <td>${{el.line_number || '-'}}</td>
            <td>
              <strong>What:</strong> ${{el.what_it_is}}<br>
              ${{analogyHtml}}
              <strong style="margin-top:4px; display:inline-block;">How:</strong> ${{el.how_it_is_used}}
              ${{screenHtml}}
              ${{removedHtml}}
            </td>
            <td>${{el.where_it_is_used}}</td>
            <td>
              <strong>Why:</strong> ${{el.why_it_works}}<br>
              ${{el.best_practices ? '<strong style="color:var(--green); margin-top:4px; display:inline-block;">Best Practice:</strong> ' + el.best_practices : ''}}
            </td>
          </tr>
        `;
      }});

      let inConn = f.inbound.map(c => `<li>⬅️ Referenced by <code>${{c.source}}</code> (${{c.type}})</li>`).join("");
      let outConn = f.outbound.map(c => `<li>➡️ References <code>${{c.target}}</code> (${{c.type}})</li>`).join("");

      let beginnerStoryHtml = "";
      if (f.beginner_story) {{
        beginnerStoryHtml = `
          <div class="card" style="border: 1px solid #38bdf8; background: #0c1a30; box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15); margin-bottom: 16px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
              <span style="font-size:1.2rem;">🧸</span>
              <h2 style="color:#7dd3fc; font-size:1.1rem;">The Big Picture Story (Explain Like I'm 4 Years Old)</h2>
            </div>
            <p style="color:#e0f2fe; line-height:1.6; font-size:0.95rem;">${{escapeHtml(f.beginner_story)}}</p>
          </div>
        `;
      }}

      let aiCardHtml = "";
      if (f.ai_insights) {{
        aiCardHtml = `
          <div class="card" style="border: 1px solid #a855f7; background: #181126; box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15); margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
              <h2 style="color:#e9d5ff; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                <span>🧠</span> Neural AI Deep Code Analysis
              </h2>
              <span class="pill" style="border-color:#c084fc; color:#c084fc; font-size:0.75rem;">Model: ${{f.ai_model_used || 'Local AI'}}</span>
            </div>
            <div style="color:#f3e8ff; line-height:1.65; white-space:pre-wrap; font-size:0.9rem;">${{escapeHtml(f.ai_insights)}}</div>
          </div>
        `;
      }}

      container.innerHTML = `
        ${{beginnerStoryHtml}}
        ${{aiCardHtml}}
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h2>📄 ${{f.relative_path}}</h2>
            <span class="tag-badge">${{f.language}} | ${{f.line_count}} Lines | ${{f.file_size_bytes}} Bytes</span>
          </div>
          <p style="font-size:1.05rem; color:#f3f4f6; margin-bottom:8px;"><strong>Role:</strong> ${{f.role_in_codebase}}</p>
          <p style="line-height:1.6; color:#9ca3af; margin-bottom:14px;">${{f.summary}}</p>

          ${{f.concepts_detected.length ? '<div style="margin-bottom:8px;"><strong style="font-size:0.8rem; color:var(--text-muted);">CONCEPTS:</strong> ' + f.concepts_detected.map(c => `<span class="pill">${{c}}</span>`).join('') + '</div>' : ''}}
          ${{f.design_and_style_notes ? '<p style="color:var(--accent); font-size:0.85rem; margin-top:8px;">🎨 <strong>Design & Style:</strong> ' + f.design_and_style_notes + '</p>' : ''}}
          ${{f.animations_and_interactions ? '<p style="color:var(--purple); font-size:0.85rem; margin-top:4px;">✨ <strong>Motion:</strong> ' + f.animations_and_interactions + '</p>' : ''}}

          ${{(inConn || outConn) ? `
            <div style="margin-top:16px; background:#162032; padding:12px 16px; border-radius:6px;">
              <strong style="font-size:0.85rem; color:#fff;">File Interconnections:</strong>
              <ul style="margin:6px 0 0 20px; font-size:0.85rem; color:#cbd5e1;">${{outConn}}${{inConn}}</ul>
            </div>
          ` : ''}}
        </div>

        <div class="card">
          <h2>🔍 Tag, Component & Function Explanations (${{f.elements.length}} Elements)</h2>
          <table class="data-table">
            <thead>
              <tr><th>Element</th><th>Kind</th><th>Line</th><th>What & How It's Used</th><th>Where Used</th><th>Why It Works</th></tr>
            </thead>
            <tbody>
              ${{elementsRows || '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No granular elements extracted for this file type.</td></tr>'}}
            </tbody>
          </table>
        </div>
      `;
    }}

    function switchTab(tabId) {{
      document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
      
      const targetBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabId));
      if (targetBtn) targetBtn.classList.add("active");
      const targetPane = document.getElementById("tab-" + tabId);
      if (targetPane) targetPane.classList.add("active");

      if (tabId === "graph") {{
        setTimeout(initGraph, 100);
      }}
    }}

    function initGraph() {{
      if (network) return;
      const container = document.getElementById("graph-canvas");
      const nodeItems = GRAPH_DATA.nodes.map(n => ({{
        id: n.id,
        label: n.label,
        shape: "box",
        margin: 10,
        color: {{
          background: "#162032",
          border: "#38bdf8",
          highlight: {{ background: "#38bdf8", border: "#fff" }}
        }},
        font: {{ color: "#f3f4f6", size: 13 }}
      }}));

      const edgeItems = GRAPH_DATA.edges.map(e => ({{
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: "to",
        color: {{ color: "#475569", highlight: "#38bdf8" }},
        font: {{ color: "#94a3b8", size: 10, align: "middle" }}
      }}));

      const data = {{
        nodes: new vis.DataSet(nodeItems),
        edges: new vis.DataSet(edgeItems)
      }};

      const options = {{
        physics: {{
          solver: "forceAtlas2Based",
          forceAtlas2Based: {{ gravitationalConstant: -50, centralGravity: 0.01, springLength: 100 }}
        }}
      }};

      network = new vis.Network(container, data, options);
      network.on("click", params => {{
        if (params.nodes.length > 0) {{
          const nodeId = params.nodes[0];
          showGraphInfo(nodeId);
        }}
      }});
      network.on("doubleClick", params => {{
        if (params.nodes.length > 0) {{
          selectFile(params.nodes[0]);
        }}
      }});
    }}

    function showGraphInfo(nodeId) {{
      const f = FILES[nodeId];
      if (!f) return;
      const box = document.getElementById("graph-info");
      box.style.display = "block";
      box.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3>📄 ${{f.relative_path}}</h3>
          <button onclick="selectFile('${{f.relative_path}}')" class="tab-btn" style="padding:4px 10px; font-size:0.8rem; background:var(--accent); color:#000; border-radius:4px;">Open File Inspector ➔</button>
        </div>
        <p style="font-size:0.85rem; color:#cbd5e1; margin-top:6px;"><strong>Role:</strong> ${{f.role_in_codebase}}</p>
        <p style="font-size:0.85rem; color:#9ca3af; margin-top:4px;">${{f.summary}}</p>
      `;
    }}

    function escapeHtml(str) {{
      return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }}

    // Auto-select first file on start
    renderSidebar();
    const firstKey = Object.keys(FILES)[0];
    if (firstKey) renderFileDetail(firstKey);
  </script>
</body>
</html>
"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(html_content, encoding="utf-8")
        return str(out_p)

