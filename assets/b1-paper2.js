(function () {
  "use strict";

  var DATA = window.QB_B1_P2 || [];
  var state = { level: "", search: "", onlyB1: false, allMs: false };
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function norm(s) { return String(s).toLowerCase().replace(/[^a-z]/g, ""); }
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
    var isB1 = q.b1.indexOf(p.key) !== -1;
    var others = p.subtopics.filter(function (s) { return s !== "B.1"; });
    return (p.pre ? '<div class="qhtml part-context">' + p.pre + "</div>" : "") +
      '<div class="p2-part' + (isB1 ? " is-b1" : "") + '"><div class="part-head">' +
      (p.label ? '<span class="part-label">' + esc(p.label) + "</span>" : "") +
      (isB1 ? '<span class="b1-badge">B.1</span>' : "") +
      (!isB1 && others.length ? '<span class="other-subs">' + others.join(", ") + "</span>" : "") +
      '<span class="mini"><button class="toggle' + (state.allMs ? " on" : "") + '" data-panel="ms">Markscheme</button>' +
      (p.er ? ' <button class="toggle" data-panel="er">Rapport</button>' : "") + "</span></div>" +
      '<div class="qhtml">' + p.q + "</div>" +
      panel("ms", p.ms, state.allMs) + (p.er ? panel("er", p.er, false) : "") + "</div>";
  }

  function card(q) {
    var head = '<div class="card-head"><span class="qid">' + esc(q.id) + "</span>" +
      (q.aliases.length ? '<span class="chip" title="Même question listée sous un autre numéro">aussi ' + q.aliases.map(esc).join(", ") + "</span>" : "") +
      '<span class="chip">' +
      sessionLabel(q.session) + (q.tz !== "TZ0" ? " · " + q.tz : "") + '</span><span class="chip lvl-' + q.level + '">' +
      q.level + '</span><span class="b1-list">Parties B.1 : ' + q.b1.map(labelOf).join(", ") +
      '</span><span class="marks">[' + q.marks + " points]</span></div>";
    return '<article class="card">' + head + '<div class="card-body">' +
      q.parts.map(function (p) { return partBlock(q, p); }).join("") + "</div></article>";
  }

  function render() {
    var items = DATA.filter(visible);
    var nParts = items.reduce(function (n, q) { return n + q.b1.length; }, 0);
    $("stats").innerHTML = "<span><b>" + items.length + "</b> questions Paper 2 · <b>" + nParts + "</b> parties B.1</span>";
    var list = $("list");
    list.classList.toggle("only-b1", state.onlyB1);
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
  $("onlyB1").addEventListener("change", function () { state.onlyB1 = this.checked; render(); });
  $("allMs").addEventListener("change", function () { state.allMs = this.checked; render(); });
  var timer;
  $("search").addEventListener("input", function () {
    var v = this.value;
    clearTimeout(timer);
    timer = setTimeout(function () { state.search = v; render(); }, 250);
  });

  render();
})();
