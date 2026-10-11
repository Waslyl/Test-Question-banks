(function () {
  "use strict";

  var SUB = window.QB_SUB || { code: "", p2: [] };
  var CODE = SUB.code;
  var DATA = SUB.p2;
  var state = { level: "", search: "", onlyHit: false, allMs: false };
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function labelOf(key) {
    if (!key) return "";
    return "(" + key[0] + ")" + (key.length > 1 ? "(" + key.slice(1) + ")" : "");
  }
  function sessionLabel(code) {
    if (code === "SPM") return "Spécimen";
    if (code === "EXE") return "Exemple";
    var m = /^(\d\d)([MN])$/.exec(code);
    return m ? (m[2] === "M" ? "Mai " : "Nov. ") + "20" + m[1] : code;
  }
  function plain(q) {
    if (q._t === undefined) {
      var html = q.parts.map(function (p) { return p.pre + " " + p.q; }).join(" ");
      q._t = html.replace(/<img[^>]*>/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").toLowerCase();
    }
    return q._t;
  }
  function visible(q) {
    if (state.level && q.level !== state.level) return false;
    var s = state.search.trim().toLowerCase();
    return !s || plain(q).indexOf(s) !== -1 || [q.id].concat(q.aliases).join(" ").toLowerCase().indexOf(s) !== -1;
  }
  function panel(kind, html, open) {
    var title = kind === "ms" ? "Markscheme" : "Rapport des examinateurs";
    return '<div class="panel ' + kind + " qhtml" + (open ? "" : " hidden") + '"><h4>' + title + "</h4>" + html + "</div>";
  }

  function partBlock(q, p) {
    var hit = q.hits.indexOf(p.key) !== -1;
    var others = p.subtopics.filter(function (s) { return s !== CODE; });
    return (p.pre ? '<div class="qhtml part-context">' + p.pre + "</div>" : "") +
      '<div class="p2-part' + (hit ? " is-hit" : "") + '"><div class="part-head">' +
      (p.label ? '<span class="part-label">' + esc(p.label) + "</span>" : "") +
      (hit ? '<span class="hit-badge">' + esc(CODE) + "</span>" : "") +
      (!hit && others.length ? '<span class="other-subs">' + others.join(", ") + "</span>" : "") +
      '<span class="mini">' + (p.ms ? '<button class="toggle' + (state.allMs ? " on" : "") + '" data-panel="ms">Markscheme</button>' : "") +
      (p.er ? ' <button class="toggle" data-panel="er">Rapport</button>' : "") + "</span></div>" +
      '<div class="qhtml">' + p.q + "</div>" +
      (p.missing ? '<div class="missing-note">Énoncé tel qu\'affiché dans la liste de la Questionbank : le texte complet et le markscheme de cette partie manquent dans les fichiers.</div>' : "") +
      (p.ms ? panel("ms", p.ms, state.allMs) : "") + (p.er ? panel("er", p.er, false) : "") + "</div>";
  }

  function card(q) {
    var head = '<div class="card-head"><span class="qid">' + esc(q.id) + "</span>" +
      (q.aliases.length ? '<span class="chip" title="Même question listée sous un autre numéro">aussi ' + q.aliases.map(esc).join(", ") + "</span>" : "") +
      '<span class="chip">' +
      sessionLabel(q.session) + (q.tz !== "TZ0" ? " · " + q.tz : "") + '</span><span class="chip lvl-' + q.level + '">' +
      q.level + '</span><span class="hit-list">Parties ' + esc(CODE) + " : " + q.hits.map(labelOf).join(", ") +
      '</span><span class="marks">[' + q.marks + " points]</span></div>";
    return '<article class="card">' + head + (q.note ? '<div class="q-note">' + esc(q.note) + "</div>" : "") +
      '<div class="card-body">' +
      q.parts.map(function (p) { return partBlock(q, p); }).join("") + "</div></article>";
  }

  function render() {
    var items = DATA.filter(visible);
    var nParts = items.reduce(function (n, q) { return n + q.hits.length; }, 0);
    $("stats").innerHTML = "<span><b>" + items.length + "</b> questions Paper 2 · <b>" + nParts + "</b> parties " + esc(CODE) + "</span>";
    var list = $("list");
    list.classList.toggle("only-hit", state.onlyHit);
    list.innerHTML = items.length ? items.map(card).join("") : '<div class="empty-state">Aucune question ne correspond.</div>';
  }

  $("list").addEventListener("click", function (e) {
    var t = e.target.closest("button[data-panel]");
    if (!t) return;
    var scope = t.closest(".p2-part") || t.closest(".card");
    var p = scope.querySelector(":scope > .panel." + t.getAttribute("data-panel"));
    var open = p.classList.toggle("hidden") === false;
    t.classList.toggle("on", open);
  });
  $("levelSeg").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-level]");
    if (!b) return;
    state.level = b.getAttribute("data-level");
    document.querySelectorAll("#levelSeg button").forEach(function (x) { x.classList.toggle("active", x === b); });
    render();
  });
  $("onlyHit").addEventListener("change", function () { state.onlyHit = this.checked; render(); });
  $("allMs").addEventListener("change", function () { state.allMs = this.checked; render(); });
  var timer;
  $("search").addEventListener("input", function () {
    var v = this.value;
    clearTimeout(timer);
    timer = setTimeout(function () { state.search = v; render(); }, 250);
  });

  render();
})();
