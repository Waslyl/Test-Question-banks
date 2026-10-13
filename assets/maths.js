(function () {
  "use strict";

  var PAGE = 12;
  var DATA = (window.QB_MATHS && window.QB_MATHS.exercises) || [];
  var state = { paper: "", section: "", session: "", search: "", allMs: false, shown: PAGE };
  var filtered = [];
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  // « a.i » -> « (a)(i) »
  function partLabel(label) {
    return label ? label.split(".").map(function (x) { return "(" + x + ")"; }).join("") : "";
  }
  function sessionLabel(e) {
    var m = /^(\w+) (\d{4})$/.exec(e.date || "");
    var date = m ? (m[1] === "May" ? "Mai " : m[1] === "Nov" ? "Nov. " : m[1] + " ") + m[2] : e.date;
    if (e.session === "SPM") return "Spécimen";
    if (/^EX/.test(e.session)) return "Exemple · " + date;
    return date;
  }
  function sessionOrder(code) {
    var m = /^(\d\d)([MN])$/.exec(code);
    if (m) return -(+m[1] * 2 + (m[2] === "N" ? 1 : 0));
    return code === "SPM" ? 9000 : 9001;
  }
  function plain(e) {
    if (e._t === undefined) {
      var html = e.contexts.map(function (c) { return c.html; }).join(" ") + " " +
        e.parts.map(function (p) { return p.q; }).join(" ");
      e._t = html.replace(/<img[^>]*>/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").toLowerCase();
    }
    return e._t;
  }

  function visible(e) {
    if (state.paper && String(e.paper) !== state.paper) return false;
    if (state.section && e.section !== state.section) return false;
    if (state.session && e.session !== state.session) return false;
    var s = state.search.trim().toLowerCase();
    return !s || plain(e).indexOf(s) !== -1 || e.id.toLowerCase().indexOf(s) !== -1;
  }

  function panel(kind, html, open) {
    var title = kind === "ms" ? "Markscheme" : "Rapport des examinateurs";
    return '<div class="panel ' + kind + " qhtml" + (open ? "" : " hidden") + '"><h4>' + title + "</h4>" + html + "</div>";
  }

  function partBlock(p) {
    var label = '<span class="part-label">' + esc(partLabel(p.label)) + "</span>";
    if (p.type === "group_prompt") {
      return '<div class="m-part prompt"><div class="part-head">' + label + '<div class="part-body qhtml">' + p.q + "</div></div></div>";
    }
    return '<div class="m-part"><div class="part-head">' + label +
      '<div class="part-body qhtml">' + p.q + '</div><span class="part-marks">[' + p.marks + "]</span></div>" +
      '<div class="mini">' + (p.ms ? '<button class="toggle' + (state.allMs ? " on" : "") + '" data-panel="ms">Markscheme</button>' : "") +
      (p.er ? '<button class="toggle" data-panel="er">Rapport des examinateurs</button>' : "") + "</div>" +
      (p.ms ? panel("ms", p.ms, state.allMs) : "") + (p.er ? panel("er", p.er, false) : "") + "</div>";
  }

  function card(e) {
    var marks = e.parts.reduce(function (n, p) { return n + p.marks; }, 0);
    var head = '<div class="card-head"><span class="qid">' + esc(e.id) + "</span>" +
      '<span class="chip">' + esc(sessionLabel(e)) + (e.tz !== "TZ0" ? " · " + e.tz : "") + "</span>" +
      '<span class="chip paper-' + e.paper + '">Paper ' + e.paper + (e.paper === 1 ? " · sans calculatrice" : " · calculatrice") + "</span>" +
      '<span class="chip sec">Section ' + e.section + "</span>" +
      (e.legacy ? '<span class="chip legacy" title="Question de l\'ancien programme Mathematics SL">ancien programme</span>' : "") +
      '<span class="marks">[' + marks + " points]</span></div>";
    var note = e.context_status === "not_provided"
      ? '<div class="q-note">L\'énoncé commun de cette question manque dans la source : certaines données peuvent manquer.</div>' : "";
    var shownCtx = {};
    var ctxById = {};
    e.contexts.forEach(function (c) { ctxById[c.id] = c; });
    var body = e.parts.map(function (p) {
      var ctx = p.ctx.filter(function (id) { return ctxById[id] && !shownCtx[id]; }).map(function (id) {
        shownCtx[id] = true;
        return '<div class="m-context qhtml">' + ctxById[id].html + "</div>";
      }).join("");
      return ctx + partBlock(p);
    }).join("");
    return '<article class="card">' + head + note + '<div class="card-body">' + body + "</div></article>";
  }

  function renderList() {
    var list = $("list");
    list.innerHTML = filtered.length ? filtered.slice(0, state.shown).map(card).join("")
      : '<div class="empty-state">Aucune question ne correspond à ces filtres.</div>';
    var rest = filtered.length - state.shown;
    $("more").parentNode.classList.toggle("hidden", rest <= 0);
    $("more").textContent = "Afficher plus (" + rest + " restantes)";
  }

  function render() {
    filtered = DATA.filter(visible);
    state.shown = PAGE;
    var parts = filtered.reduce(function (n, e) { return n + e.parts.filter(function (p) { return p.type !== "group_prompt"; }).length; }, 0);
    var marks = filtered.reduce(function (n, e) { return n + e.parts.reduce(function (m, p) { return m + p.marks; }, 0); }, 0);
    $("stats").innerHTML = "<span><b>" + filtered.length + "</b> exercices · <b>" + parts + "</b> questions · <b>" + marks + "</b> points</span>";
    var paperName = { "": "Paper 1 et Paper 2", "1": "Paper 1 — sans calculatrice", "2": "Paper 2 — avec calculatrice" }[state.paper];
    var sectionName = { "": "", A: " · Section A (questions courtes)", B: " · Section B (questions longues)" }[state.section];
    $("crumbs").innerHTML = "Topic 4 — Statistics and probability<small>" + paperName + sectionName + "</small>";
    document.querySelectorAll("#paperTabs button").forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-paper") === state.paper); });
    document.querySelectorAll("#sectionSeg button").forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-section") === state.section); });
    renderList();
  }

  // ---------- Événements ----------
  $("paperTabs").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-paper]");
    if (!b) return;
    state.paper = b.getAttribute("data-paper");
    render();
  });
  $("sectionSeg").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-section]");
    if (!b) return;
    state.section = b.getAttribute("data-section");
    render();
  });
  $("session").addEventListener("change", function () { state.session = this.value; render(); });
  $("allMs").addEventListener("change", function () { state.allMs = this.checked; renderList(); });
  var timer;
  $("search").addEventListener("input", function () {
    var v = this.value;
    clearTimeout(timer);
    timer = setTimeout(function () { state.search = v; render(); }, 250);
  });
  $("more").addEventListener("click", function () {
    var next = filtered.slice(state.shown, state.shown + PAGE);
    $("list").insertAdjacentHTML("beforeend", next.map(card).join(""));
    state.shown += PAGE;
    var rest = filtered.length - state.shown;
    $("more").parentNode.classList.toggle("hidden", rest <= 0);
    $("more").textContent = "Afficher plus (" + rest + " restantes)";
  });
  $("list").addEventListener("click", function (ev) {
    var t = ev.target.closest("button[data-panel]");
    if (!t) return;
    var part = t.closest(".m-part");
    var p = part.querySelector(":scope > .panel." + t.getAttribute("data-panel"));
    var open = p.classList.toggle("hidden") === false;
    t.classList.toggle("on", open);
  });

  // ---------- Démarrage ----------
  var seen = {};
  DATA.forEach(function (e) { seen[e.session] = e; });
  $("session").innerHTML += Object.keys(seen).sort(function (a, b) { return sessionOrder(a) - sessionOrder(b); })
    .map(function (c) { return '<option value="' + c + '">' + esc(c === "SPM" ? "Spécimen" : /^EX/.test(c) ? "Exemple (" + c + ")" : sessionLabel(seen[c])) + "</option>"; }).join("");
  render();
})();
