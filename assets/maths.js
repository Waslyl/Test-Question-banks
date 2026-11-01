(function () {
  "use strict";

  var PAGE = 12;
  // Topic 2 (data/maths-t2.js) puis Topic 4 (data/maths-t4.js)
  function withTopic(src, topic) {
    return ((src && src.exercises) || []).map(function (e) { e.topic = topic; return e; });
  }
  var DATA = withTopic(window.QB_MATHS_T2, 2).concat(withTopic(window.QB_MATHS, 4));
  var SUBTOPICS = (window.QB_MATHS_T2 && window.QB_MATHS_T2.topic.subtopics) || [];
  var TOPICS = { 2: "Functions", 4: "Statistics and probability" };
  var LEGACY = { S_: "Mathematics SL", T_: "Mathematical studies SL", H_: "Mathematics HL" };
  var state = { topic: "", subtopic: "", paper: "", section: "", session: "", search: "", allMs: false, shown: PAGE };
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

  function marksOf(e) {
    return e.parts.reduce(function (n, p) { return n + (p.marks || 0); }, 0);
  }

  function visible(e) {
    if (state.topic && String(e.topic) !== state.topic) return false;
    if (state.subtopic && (e.subtopics || []).indexOf(state.subtopic) === -1) return false;
    if (state.paper && String(e.paper) !== state.paper) return false;
    if (state.section && e.section !== state.section) return false;
    if (state.session && e.session !== state.session) return false;
    var s = state.search.trim().toLowerCase();
    return !s || plain(e).indexOf(s) !== -1 || e.id.toLowerCase().indexOf(s) !== -1;
  }

  function panel(kind, html, open, src) {
    var title = kind === "er" ? "Rapport des examinateurs"
      : src ? "Corrigé rédigé par " + esc(src) + " (pas de markscheme officiel dans la source)" : "Markscheme";
    return '<div class="panel ' + kind + " qhtml" + (open ? "" : " hidden") + '"><h4>' + title + "</h4>" + html + "</div>";
  }

  function partBlock(p) {
    var label = '<span class="part-label">' + esc(partLabel(p.label)) + "</span>";
    if (p.type === "group_prompt") {
      return '<div class="m-part prompt"><div class="part-head">' + label + '<div class="part-body qhtml">' + p.q + "</div></div></div>";
    }
    return '<div class="m-part"><div class="part-head">' + label +
      '<div class="part-body qhtml">' + p.q + "</div>" + (p.marks ? '<span class="part-marks">[' + p.marks + "]</span>" : "") + "</div>" +
      '<div class="mini">' + (p.ms ? '<button class="toggle' + (state.allMs ? " on" : "") + '" data-panel="ms">' +
        (p.ms_src ? "Corrigé W4ss" : "Markscheme") + "</button>" : "") +
      (p.er ? '<button class="toggle" data-panel="er">Rapport des examinateurs</button>' : "") + "</div>" +
      (p.ms ? panel("ms", p.ms, state.allMs, p.ms_src) : "") + (p.er ? panel("er", p.er, false) : "") + "</div>";
  }

  function card(e) {
    var marks = marksOf(e);
    var unknown = e.parts.some(function (p) { return p.type !== "group_prompt" && !p.marks; });
    // l'ancien programme Mathematical studies permettait la calculatrice au Paper 1
    var calc = e.paper === 2 || e.legacy === "T_" ? " · calculatrice" : " · sans calculatrice";
    var head = '<div class="card-head"><span class="qid">' + esc(e.id) + "</span>" +
      '<span class="chip topic-' + e.topic + '">Topic ' + e.topic + "</span>" +
      (e.subtopics || []).map(function (c) { return '<span class="chip subt">' + esc(c) + "</span>"; }).join("") +
      '<span class="chip">' + esc(sessionLabel(e)) + (e.tz && e.tz !== "TZ0" ? " · " + e.tz : "") + "</span>" +
      '<span class="chip paper-' + e.paper + '">Paper ' + e.paper + calc + "</span>" +
      (e.section ? '<span class="chip sec">Section ' + e.section + "</span>" : "") +
      (e.legacy ? '<span class="chip legacy" title="Question de l\'ancien programme ' + esc(LEGACY[e.legacy] || "") + '">ancien programme</span>' : "") +
      '<span class="marks">' + (unknown ? "[barème non indiqué]" : "[" + marks + " points]") + "</span></div>";
    var notes = (e.notes || []).slice();
    if (e.context_status === "not_provided") notes.push("L'énoncé commun de cette question manque dans la source : certaines données peuvent manquer.");
    var note = notes.map(function (n) { return '<div class="q-note">' + esc(n) + "</div>"; }).join("");
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
    var marks = filtered.reduce(function (n, e) { return n + marksOf(e); }, 0);
    $("stats").innerHTML = "<span><b>" + filtered.length + "</b> exercices · <b>" + parts + "</b> questions · <b>" + marks + "</b> points</span>";
    var paperName = { "": "Paper 1 et Paper 2", "1": "Paper 1 — sans calculatrice", "2": "Paper 2 — avec calculatrice" }[state.paper];
    var sectionName = { "": "", A: " · Section A (questions courtes)", B: " · Section B (questions longues)" }[state.section];
    var sub = SUBTOPICS.filter(function (t) { return t.code === state.subtopic; })[0];
    var topicName = state.topic ? "Topic " + state.topic + " — " + TOPICS[state.topic] + (sub ? " · " + sub.code + " " + sub.title : "")
      : "Topic 2 Functions et Topic 4 Statistics and probability";
    $("crumbs").innerHTML = esc(topicName) + "<small>" + paperName + sectionName + "</small>";
    document.querySelectorAll("#topicSeg button").forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-topic") === state.topic); });
    $("subtopic").classList.toggle("hidden", state.topic !== "2");
    $("subtopic").value = state.subtopic;
    document.querySelectorAll("#paperTabs button").forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-paper") === state.paper); });
    document.querySelectorAll("#sectionSeg button").forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-section") === state.section); });
    renderList();
  }

  // ---------- Événements ----------
  $("topicSeg").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-topic]");
    if (!b) return;
    state.topic = b.getAttribute("data-topic");
    if (state.topic !== "2") state.subtopic = "";
    render();
  });
  $("subtopic").addEventListener("change", function () { state.subtopic = this.value; render(); });
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
  $("subtopic").innerHTML += SUBTOPICS.map(function (t) {
    return '<option value="' + esc(t.code) + '">' + esc(t.code + " " + t.title) + "</option>";
  }).join("");
  var seen = {};
  DATA.forEach(function (e) { seen[e.session] = e; });
  $("session").innerHTML += Object.keys(seen).sort(function (a, b) { return sessionOrder(a) - sessionOrder(b); })
    .map(function (c) { return '<option value="' + c + '">' + esc(c === "SPM" ? "Spécimen" : /^EX/.test(c) ? "Exemple (" + c + ")" : sessionLabel(seen[c])) + "</option>"; }).join("");
  render();
})();
