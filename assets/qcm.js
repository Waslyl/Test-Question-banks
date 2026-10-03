(function () {
  "use strict";

  var STORE_KEY = "qb-physics-answers";
  var PAGE = window.QCM_PAGE || null;
  var DATA = window.QB_P1A || [];
  if (PAGE) {
    var all = {};
    DATA.forEach(function (q) { all[q.id] = q; });
    DATA = PAGE.ids.map(function (id) { return all[id]; }).filter(Boolean);
  }
  var state = { level: "", session: "", search: "", showAll: false };
  var answers = load();
  var byId = {};
  DATA.forEach(function (q) { byId[q.id] = q; });

  var $ = function (id) { return document.getElementById(id); };

  function load() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; } catch (e) { return {}; }
  }
  function save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(answers)); } catch (e) { /* stockage indisponible */ }
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function sessionLabel(code) {
    if (code === "SPM") return "Spécimen";
    if (code === "EXE") return "Exemple";
    var m = /^(\d\d)([MN])$/.exec(code);
    return m ? (m[2] === "M" ? "Mai " : "Nov. ") + "20" + m[1] : code;
  }
  function sessionOrder(code) {
    if (code === "SPM") return 9000;
    if (code === "EXE") return 9001;
    var m = /^(\d\d)([MN])$/.exec(code);
    return m ? -(+m[1] * 2 + (m[2] === "N" ? 1 : 0)) : 9999;
  }
  function plain(q) {
    if (q._t === undefined) q._t = q.q.replace(/<img[^>]*>/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").toLowerCase();
    return q._t;
  }

  // Sections : une par sous-thème (sous-thème principal de chaque question)
  var sections = [];
  if (PAGE) SYLLABUS = [{ code: "", title: "", subtopics: [] }];
  SYLLABUS.forEach(function (t) {
    t.subtopics.forEach(function (st) {
      sections.push({ code: st.code, title: st.title, topic: t.code + ". " + t.title, hl: st.hl, items: [] });
    });
  });
  var other = PAGE ? { code: "page", title: PAGE.title, topic: "Paper 1A", items: [] }
    : { code: "autres", title: "Sans sous-thème", topic: "Autres", items: [] };
  sections.push(other);
  var sectionByCode = {};
  sections.forEach(function (s) { sectionByCode[s.code] = s; });
  DATA.forEach(function (q) {
    var s = sectionByCode[q.subtopics[0]] || other;
    s.items.push(q);
  });

  function visible(q) {
    if (state.level && q.level !== state.level) return false;
    if (state.session && q.session !== state.session) return false;
    var s = state.search.trim().toLowerCase();
    if (s && plain(q).indexOf(s) === -1 && q.id.toLowerCase().indexOf(s) === -1) return false;
    return true;
  }

  function card(q) {
    var prev = answers[q.id];
    var reveal = prev || state.showAll;
    var opts = ["A", "B", "C", "D"].map(function (l) {
      var cls = "opt";
      if (reveal && l === q.answer) cls += " right";
      else if (prev && l === prev) cls += " wrong";
      return '<button class="' + cls + '" data-opt="' + l + '"' + (prev ? " disabled" : "") + ">" + l + "</button>";
    }).join("");
    var verdict = "";
    if (prev) {
      verdict = prev === q.answer ? '<span class="verdict ok">✓ Bonne réponse</span>'
        : '<span class="verdict ko">✗ La bonne réponse est ' + q.answer + "</span>";
    } else if (state.showAll) {
      verdict = '<span class="verdict ok">Réponse : ' + q.answer + "</span>";
    }
    var actions = "";
    if (q.er) actions += '<button class="toggle" data-panel="er">Rapport des examinateurs</button>';
    if (prev) actions += '<button class="toggle" data-retry="1">Réessayer</button>';
    var chips = q.subtopics.map(function (s) { return '<span class="chip sub">' + s + "</span>"; }).join("");
    return '<article class="card" data-id="' + esc(q.id) + '"><div class="card-head"><span class="qid">' + esc(q.id) +
      '</span><span class="chip">' + sessionLabel(q.session) + (q.tz !== "TZ0" ? " · " + q.tz : "") +
      '</span><span class="chip lvl-' + q.level + '">' + q.level + "</span>" + chips + '<span class="marks">[1]</span></div>' +
      '<div class="card-body qhtml">' + q.q + '</div><div class="mcq">' + opts + verdict + "</div>" +
      (actions ? '<div class="actions">' + actions + "</div>" : "") +
      (q.er ? '<div class="panel er qhtml hidden"><h4>Rapport des examinateurs</h4>' + q.er + "</div>" : "") +
      "</article>";
  }

  function renderSection(det) {
    var s = sectionByCode[det.getAttribute("data-code")];
    var items = s.items.filter(visible);
    det.querySelector(".list").innerHTML = items.length ? items.map(card).join("")
      : '<div class="empty-state">Aucune question avec ces filtres.</div>';
    det._rendered = true;
  }

  function render() {
    var total = 0, done = 0, ok = 0;
    var toc = "", html = "";
    sections.forEach(function (s) {
      var items = s.items.filter(visible);
      if (!items.length) return;
      total += items.length;
      items.forEach(function (q) { if (answers[q.id]) { done++; if (answers[q.id] === q.answer) ok++; } });
      var id = "s-" + s.code.replace(".", "-");
      toc += '<a href="#' + id + '">' + s.code + '<span class="n">' + items.length + "</span></a>";
      html += '<details class="section' + (s.hl ? " hl-only" : "") + '" id="' + id + '" data-code="' + s.code + '"' +
        (state.search || PAGE ? " open" : "") + "><summary>" + (s.code !== "autres" && s.code !== "page" ? s.code + " " : "") + esc(s.title) +
        (s.hl ? ' <span class="hl">HL</span>' : "") + ' <span class="topic-title">' + esc(s.topic) + '</span><span class="count">' +
        items.length + " question" + (items.length > 1 ? "s" : "") + '</span></summary><div class="list"></div></details>';
    });
    $("toc").innerHTML = PAGE ? "" : toc;
    $("sections").innerHTML = html || '<div class="empty-state">Aucune question ne correspond.</div>';
    document.querySelectorAll("#sections details[open]").forEach(renderSection);
    var stats = "<span><b>" + total + "</b> questions Paper 1A</span>";
    if (done) stats += "<span>Répondues : <b>" + done + "</b> · Score : <b>" + ok + "/" + done + "</b> (" + Math.round(100 * ok / done) + " %)</span>";
    $("stats").innerHTML = stats;
  }

  // ---------- Événements ----------
  $("sections").addEventListener("toggle", function (e) {
    if (e.target.open && !e.target._rendered) renderSection(e.target);
  }, true);

  $("toc").addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    var det = document.querySelector(a.getAttribute("href"));
    if (det) det.open = true;
  });

  $("sections").addEventListener("click", function (e) {
    var c = e.target.closest(".card");
    if (!c) return;
    var q = byId[c.getAttribute("data-id")];
    var opt = e.target.closest("button[data-opt]");
    if (opt && !opt.disabled) {
      answers[q.id] = opt.getAttribute("data-opt");
      save();
      c.outerHTML = card(q);
      return;
    }
    if (e.target.closest("button[data-retry]")) {
      delete answers[q.id];
      save();
      c.outerHTML = card(q);
      return;
    }
    var t = e.target.closest("button[data-panel]");
    if (t) {
      var open = c.querySelector(".panel." + t.getAttribute("data-panel")).classList.toggle("hidden") === false;
      t.classList.toggle("on", open);
    }
  });

  $("levelSeg").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-level]");
    if (!b) return;
    state.level = b.getAttribute("data-level");
    document.querySelectorAll("#levelSeg button").forEach(function (x) { x.classList.toggle("active", x === b); });
    render();
  });
  $("session").addEventListener("change", function () { state.session = this.value; render(); });
  $("showAnswers").addEventListener("change", function () { state.showAll = this.checked; render(); });
  var timer;
  $("search").addEventListener("input", function () {
    var v = this.value;
    clearTimeout(timer);
    timer = setTimeout(function () { state.search = v; render(); }, 250);
  });

  // ---------- Démarrage ----------
  var seen = {};
  DATA.forEach(function (q) { seen[q.session] = true; });
  $("session").innerHTML += Object.keys(seen).sort(function (a, b) { return sessionOrder(a) - sessionOrder(b); })
    .map(function (c) { return '<option value="' + c + '">' + sessionLabel(c) + "</option>"; }).join("");
  $("loading").classList.add("hidden");
  render();
})();
