(() => {
  const state = {
    entries: [],
    filtered: [],
    selectedIndex: 0,
    query: "",
  };

  const nodes = {
    app: document.getElementById("app"),
    search: document.getElementById("search"),
    results: document.getElementById("results"),
    details: document.getElementById("details"),
    status: document.getElementById("status"),
    count: document.getElementById("result-count"),
    open: document.getElementById("open-repo"),
    copy: document.getElementById("copy-repo"),
  };

  function setStatus(text) {
    nodes.status.textContent = text || "";
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function repoSlug(url) {
    try {
      const parsed = new URL(url);
      return parsed.pathname.replace(/^\//, "") || url;
    } catch {
      return url;
    }
  }

  function normalizeEntry(item) {
    return {
      name: item?.name || "(unnamed)",
      description: item?.description || "",
      repository: item?.repository || "",
      source_file: item?.source_file || "",
      source_format: item?.source_format || "",
    };
  }

  function scoreEntry(entry, terms) {
    let score = 0;
    const n = entry.name.toLowerCase();
    const d = entry.description.toLowerCase();
    const r = entry.repository.toLowerCase();

    for (const term of terms) {
      if (!term) continue;
      if (n.startsWith(term)) score += 120;
      else if (n.includes(term)) score += 80;
      if (d.includes(term)) score += 28;
      if (r.includes(term)) score += 16;
    }

    return score;
  }

  function highlight(text, query) {
    const safe = escapeHtml(text);
    const terms = query
      .trim()
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean)
      .sort((a, b) => b.length - a.length);

    if (!terms.length) return safe;

    let out = safe;
    for (const term of terms) {
      const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      out = out.replace(new RegExp(`(${escapedTerm})`, "ig"), "<mark>$1</mark>");
    }
    return out;
  }

  function applyFilter(raw) {
    state.query = raw;
    const query = raw.trim().toLowerCase();

    if (!query) {
      state.filtered = [...state.entries];
      state.selectedIndex = 0;
      render();
      syncQuery(raw);
      return;
    }

    const terms = query.split(/\s+/).filter(Boolean);
    const matches = [];

    for (const entry of state.entries) {
      const score = scoreEntry(entry, terms);
      if (score > 0) matches.push({ entry, score });
    }

    matches.sort((a, b) => b.score - a.score || a.entry.name.localeCompare(b.entry.name));
    state.filtered = matches.map((m) => m.entry);
    state.selectedIndex = 0;
    render();
    syncQuery(raw);
  }

  function selectedEntry() {
    return state.filtered[state.selectedIndex] || null;
  }

  function renderDetails(item) {
    if (!item) {
      nodes.details.innerHTML = "<h2>BOF Details</h2><p>No BOF selected.</p>";
      nodes.open.disabled = true;
      nodes.copy.disabled = true;
      return;
    }

    nodes.details.innerHTML = `
      <h2>${escapeHtml(item.name)}</h2>
      <p>${escapeHtml(item.description || "No description available.")}</p>
      <p><a href="${escapeHtml(item.repository)}" target="_blank" rel="noopener">${escapeHtml(item.repository)}</a></p>
      <p class="kv">Source: ${escapeHtml(item.source_file)} (${escapeHtml(item.source_format)})</p>
    `;

    nodes.open.disabled = !item.repository;
    nodes.copy.disabled = !item.repository;
  }

  function renderResults() {
    nodes.count.textContent = `${state.filtered.length} results`;

    if (!state.filtered.length) {
      nodes.results.innerHTML = `<li class="empty">No matches for "${escapeHtml(state.query)}".</li>`;
      renderDetails(null);
      return;
    }

    const selected = selectedEntry() || state.filtered[0];
    const listHtml = state.filtered
      .map((item, i) => {
        const selectedClass = i === state.selectedIndex ? " selected" : "";
        return `
          <li class="row${selectedClass}" data-index="${i}" tabindex="0" role="button" aria-label="${escapeHtml(item.name)}">
            <div class="name">${highlight(item.name, state.query)}</div>
            <div class="desc">${highlight(item.description, state.query)}</div>
            <div class="repo">${highlight(repoSlug(item.repository), state.query)}</div>
          </li>
        `;
      })
      .join("");

    nodes.results.innerHTML = listHtml;
    renderDetails(selected);
  }

  function render() {
    renderResults();
    nodes.app.setAttribute("aria-busy", "false");
  }

  function moveSelection(delta) {
    if (!state.filtered.length) return;
    const max = state.filtered.length - 1;
    state.selectedIndex = Math.max(0, Math.min(max, state.selectedIndex + delta));
    render();
    const row = nodes.results.querySelector(`.row[data-index="${state.selectedIndex}"]`);
    row?.scrollIntoView({ block: "nearest" });
  }

  function openSelected() {
    const item = selectedEntry();
    if (!item?.repository) return;
    window.open(item.repository, "_blank", "noopener");
  }

  async function copySelected() {
    const item = selectedEntry();
    if (!item?.repository) return;
    try {
      await navigator.clipboard.writeText(item.repository);
      setStatus("Copied repository URL.");
    } catch {
      setStatus("Clipboard write failed.");
    }
  }

  function syncQuery(query) {
    const url = new URL(window.location.href);
    if (query.trim()) url.searchParams.set("q", query.trim());
    else url.searchParams.delete("q");
    window.history.replaceState({}, "", url);
  }

  function readInitialQuery() {
    const params = new URLSearchParams(window.location.search);
    return params.get("q") || "";
  }

  function bindEvents() {
    nodes.search.addEventListener("input", (e) => applyFilter(e.target.value));

    nodes.results.addEventListener("click", (e) => {
      const row = e.target.closest(".row");
      if (!row) return;
      state.selectedIndex = Number.parseInt(row.dataset.index, 10) || 0;
      render();
    });

    nodes.results.addEventListener("dblclick", (e) => {
      const row = e.target.closest(".row");
      if (!row) return;
      state.selectedIndex = Number.parseInt(row.dataset.index, 10) || 0;
      render();
      openSelected();
    });

    nodes.open.addEventListener("click", openSelected);
    nodes.copy.addEventListener("click", copySelected);

    document.addEventListener("keydown", (e) => {
      const activeTag = document.activeElement?.tagName || "";
      const inInput = activeTag === "INPUT" || activeTag === "TEXTAREA";

      if (e.key === "/" && !inInput) {
        e.preventDefault();
        nodes.search.focus();
        nodes.search.select();
        return;
      }

      if (e.key === "Escape" && inInput) {
        nodes.search.value = "";
        applyFilter("");
        nodes.search.blur();
        return;
      }

      if (e.key === "j" || e.key === "ArrowDown") {
        if (!inInput || e.key === "ArrowDown") {
          e.preventDefault();
          moveSelection(1);
        }
        return;
      }

      if (e.key === "k" || e.key === "ArrowUp") {
        if (!inInput || e.key === "ArrowUp") {
          e.preventDefault();
          moveSelection(-1);
        }
        return;
      }

      if ((e.key === "Enter" || e.key.toLowerCase() === "o")) {
        if (e.key.toLowerCase() === "o" && inInput) return;
        e.preventDefault();
        openSelected();
      }
    });
  }

  async function loadIndex() {
    setStatus("Loading index...");
    try {
      const response = await fetch("./data/bof-index.json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const payload = await response.json();
      const rawEntries = Array.isArray(payload?.bofs) ? payload.bofs : [];
      state.entries = rawEntries.map(normalizeEntry);

      const initialQuery = readInitialQuery();
      nodes.search.value = initialQuery;
      applyFilter(initialQuery);

      setStatus("");
    } catch {
      state.entries = [];
      state.filtered = [];
      render();
      setStatus("Failed to load BOF index. Run scripts/update-site-data.sh and refresh.");
    }
  }

  bindEvents();
  loadIndex();
})();
