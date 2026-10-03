(function () {
  "use strict";

  var PAGE = 15;
  var PAPERS = {
    p1a: { label: "Paper 1A", sub: "Questions à choix multiple", file: "data/paper1a.js", global: "QB_P1A" },
    p2: { label: "Paper 2", sub: "Questions à réponse longue", file: "data/paper2.js", global: "QB_P2" }
  };
  var STORE_KEY = "qb-physics-answers";

  var state = { paper: "p1a", topic: "", level: "", session: "", search: "", shuffle: false, shown: PAGE };
  var cache = {};
  var filtered = [];
  var answers = loadAnswers();

  var $ = function (id) { return document.getElementById(id); };
  var el = {
    tree: $("tree"), list: $("list"), more: $("more"), stats: $("stats"), crumbs: $("crumbs"),
    search: $("search"), session: $("session"), shuffle: $("shuffle"), loading: $("loading"),
    sidebar: $("sidebar"), backdrop: $("backdrop")
  };

  // ---------- Utilitaires ----------
  function loadAnswers() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; } catch (e) { return {}; }
  }
  function saveAnswers() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(answers)); } catch (e) { /* stockage indisponible */ }
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function sessionLabel(code) {
    if (code === "SPM") return "Spécimen";
    if (code === "EXE") return "Exemple";
    var m = /^(\d\d)([MN])$/.exec(code);
    if (!m) return code;
    return (m[2] === "M" ? "Mai " : "Nov. ") + "20" + m[1];
  }
  function sessionOrder(code) {
    if (code === "SPM") return 9000;
    if (code === "EXE") return 9001;
    var m = /^(\d\d)([MN])$/.exec(code);
    return m ? -(+m[1] * 2 + (m[2] === "N" ? 1 : 0)) : 9999;
  }
  function plainText(q) {
    if (q._text === undefined) {
      var html = q.q + (q.parts ? q.parts.map(function (p) { return p.q; }).join(" ") : "");
      q._text = html.replace(/<img[^>]*>/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").toLowerCase();
    }
    return q._text;
  }
  function shuffled(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function subTitle(code) {
    for (var i = 0; i < SYLLABUS.length; i++) {
      var t = SYLLABUS[i];
      if (t.code === code) return t.code + " · " + t.title;
      for (var j = 0; j < t.subtopics.length; j++) {
        if (t.subtopics[j].code === code) return code + " · " + t.subtopics[j].title;
      }
    }
    return code;
  }

  // ---------- Chargement des données ----------
  function loadPaper(key) {
    if (cache[key]) return Promise.resolve(cache[key]);
    var p = PAPERS[key];
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = p.file;
      s.onload = function () { cache[key] = window[p.global] || []; resolve(cache[key]); };
      s.onerror = function () { reject(new Error("Impossible de charger " + p.file)); };
      document.head.appendChild(s);
    });
  }

  // ---------- URL (hash) ----------
  function readHash() {
    var h = location.hash.replace(/^#\/?/, "");
    var parts = h.split("?");
    if (PAPERS[parts[0]]) state.paper = parts[0];
    var params = new URLSearchParams(parts[1] || "");
    state.topic = params.get("t") || "";
    state.level = params.get("l") || "";
    state.session = params.get("s") || "";
  }
  function writeHash() {
    var params = new URLSearchParams();
    if (state.topic) params.set("t", state.topic);
    if (state.level) params.set("l", state.level);
    if (state.session) params.set("s", state.session);
    var qs = params.toString();
    var h = "#" + state.paper + (qs ? "?" + qs : "");
    if (location.hash !== h) history.replaceState(null, "", h);
  }

  // ---------- Filtrage ----------
  function matchesTopic(q, code) {
    if (!code) return true;
    if (code.indexOf(".") === -1) return q.topics.indexOf(code) !== -1;
    return q.subtopics.indexOf(code) !== -1;
  }
  function baseFilter(data, ignoreTopic) {
    var s = state.search.trim().toLowerCase();
    return data.filter(function (q) {
      if (state.level && q.level !== state.level) return false;
      if (state.session && q.session !== state.session) return false;
      if (!ignoreTopic && !matchesTopic(q, state.topic)) return false;
      if (s && plainText(q).indexOf(s) === -1 && q.id.toLowerCase().indexOf(s) === -1) return false;
      return true;
    });
  }

  // ---------- Barre latérale ----------
  function renderTree(data) {
    var pool = baseFilter(data, true);
    var count = function (code) { return pool.filter(function (q) { return matchesTopic(q, code); }).length; };
    var html = '<li class="topic"><a href="#" data-topic=""' + (state.topic === "" ? ' class="active"' : "") +
      '><span>Toutes les questions</span><span class="count">' + pool.length + "</span></a></li>";
    SYLLABUS.forEach(function (t) {
      var n = count(t.code);
      if (!n && "TIN".indexOf(t.code) !== -1) return;
      html += '<li class="topic' + (n ? "" : " empty") + '"><a href="#" data-topic="' + t.code + '"' +
        (state.topic === t.code ? ' class="active"' : "") + '><span class="code">' + t.code + "</span><span>" +
        esc(t.title) + '</span><span class="count">' + n + "</span></a><ul>";
      t.subtopics.forEach(function (st) {
        var m = count(st.code);
        html += '<li class="sub' + (m ? "" : " empty") + '"><a href="#" data-topic="' + st.code + '"' +
          (state.topic === st.code ? ' class="active"' : "") + '><span class="code">' + st.code + "</span><span>" +
          esc(st.title) + (st.hl ? ' <span class="hl">HL</span>' : "") + '</span><span class="count">' + m + "</span></a></li>";
      });
      html += "</ul></li>";
    });
    el.tree.innerHTML = html;
  }

  function renderSessions(data) {
    var seen = {};
    data.forEach(function (q) { seen[q.session] = true; });
    var codes = Object.keys(seen).sort(function (a, b) { return sessionOrder(a) - sessionOrder(b); });
    el.session.innerHTML = '<option value="">Toutes les sessions</option>' + codes.map(function (c) {
      return '<option value="' + c + '"' + (c === state.session ? " selected" : "") + ">" + sessionLabel(c) + "</option>";
    }).join("");
  }

  // ---------- Cartes ----------
  function head(q) {
    var chips = q.subtopics.map(function (s) { return '<span class="chip sub" title="' + esc(subTitle(s)) + '">' + s + "</span>"; }).join("");
    var marks = state.paper === "p1a" ? "[1]" : (q.marks ? "[" + q.marks + " points]" : "");
    return '<div class="card-head"><span class="qid">' + esc(q.id) + '</span>' +
      '<span class="chip">' + sessionLabel(q.session) + (q.tz !== "TZ0" ? " · " + q.tz : "") + "</span>" +
      '<span class="chip lvl-' + q.level + '">' + q.level + "</span>" + chips +
      (q.incomplete ? '<span class="chip warn" title="Le numéro de cette question manque dans les données d\'origine">N° de question inconnu</span>' : "") +
      '<span class="marks">' + marks + "</span></div>";
  }

  function cardP1A(q) {
    var prev = answers[q.id];
    var opts = ["A", "B", "C", "D"].map(function (l) {
      var cls = "opt";
      if (prev) {
        if (l === q.answer) cls += " right";
        else if (l === prev) cls += " wrong";
      }
      return '<button class="' + cls + '" data-opt="' + l + '"' + (prev ? " disabled" : "") + ">" + l + "</button>";
    }).join("");
    var verdict = prev ? (prev === q.answer
      ? '<span class="verdict ok">✓ Bonne réponse</span>'
      : '<span class="verdict ko">✗ La bonne réponse est ' + q.answer + "</span>") : "";
    var extra = "";
    if (q.er) extra += '<button class="toggle" data-panel="er">Rapport des examinateurs</button>';
    if (prev) extra += '<button class="toggle" data-retry="1">Réessayer</button>';
    return '<article class="card" data-id="' + esc(q.id) + '">' + head(q) +
      '<div class="card-body qhtml">' + q.q + "</div>" +
      '<div class="mcq">' + opts + verdict + "</div>" +
      (extra ? '<div class="actions">' + extra + "</div>" : "") +
      (q.er ? '<div class="panel er qhtml hidden"><h4>Rapport des examinateurs</h4>' + q.er + "</div>" : "") +
      "</article>";
  }

  function cardP2(q) {
    var body, ms, er;
    if (q.parts) {
      body = q.parts.map(function (p) {
        return '<div class="part">' + (p.label ? '<div class="part-label">Partie ' + esc(p.label) + "</div>" : "") + p.q + "</div>";
      }).join("");
      ms = q.parts.map(function (p) {
        return (p.label ? '<div class="part-label">Partie ' + esc(p.label) + "</div>" : "") + p.ms;
      }).join("");
      er = q.parts.filter(function (p) { return p.er; }).map(function (p) {
        return (p.label ? '<div class="part-label">Partie ' + esc(p.label) + "</div>" : "") + p.er;
      }).join("");
    } else {
      body = q.q; ms = q.ms; er = q.er;
    }
    return '<article class="card" data-id="' + esc(q.id) + '">' + head(q) +
      '<div class="card-body qhtml">' + body + "</div>" +
      '<div class="actions"><button class="toggle" data-panel="ms">Markscheme</button>' +
      (er ? '<button class="toggle" data-panel="er">Rapport des examinateurs</button>' : "") + "</div>" +
      '<div class="panel ms qhtml hidden"><h4>Markscheme</h4>' + ms + "</div>" +
      (er ? '<div class="panel er qhtml hidden"><h4>Rapport des examinateurs</h4>' + er + "</div>" : "") +
      "</article>";
  }

  function renderStats() {
    var parts = ["<span><b>" + filtered.length + "</b> question" + (filtered.length > 1 ? "s" : "") + "</span>"];
    if (state.paper === "p1a") {
      var done = 0, ok = 0;
      filtered.forEach(function (q) {
        if (answers[q.id]) { done++; if (answers[q.id] === q.answer) ok++; }
      });
      if (done) {
        parts.push("<span>Répondues : <b>" + done + "</b> · Score : <b>" + ok + "/" + done +
          "</b> (" + Math.round(100 * ok / done) + " %)</span>");
        parts.push('<button class="reset" id="resetScore">Remettre à zéro</button>');
      }
    }
    el.stats.innerHTML = parts.join("");
  }

  function renderList() {
    var cardFn = state.paper === "p1a" ? cardP1A : cardP2;
    if (!filtered.length) {
      el.list.innerHTML = '<div class="empty-state">Aucune question ne correspond à ces filtres.</div>';
    } else {
      el.list.innerHTML = filtered.slice(0, state.shown).map(cardFn).join("");
    }
    el.more.parentNode.classList.toggle("hidden", state.shown >= filtered.length);
    el.more.textContent = "Afficher plus (" + (filtered.length - state.shown) + " restantes)";
  }

  function renderCrumbs() {
    var p = PAPERS[state.paper];
    el.crumbs.innerHTML = esc(p.label) + (state.topic ? " — " + esc(subTitle(state.topic)) : "") +
      "<small>" + esc(p.sub) + "</small>";
    document.querySelectorAll("#paperTabs button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-paper") === state.paper);
    });
    document.querySelectorAll("#levelSeg button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-level") === state.level);
    });
  }

  function refresh(resetScroll) {
    var data = cache[state.paper];
    if (!data) return;
    var res = baseFilter(data, false);
    filtered = state.shuffle ? shuffled(res) : res;
    state.shown = PAGE;
    renderCrumbs();
    renderTree(data);
    renderStats();
    renderList();
    writeHash();
    if (resetScroll) window.scrollTo(0, 0);
  }

  function switchPaper(key) {
    state.paper = key;
    el.loading.classList.remove("hidden");
    el.list.innerHTML = "";
    renderCrumbs();
    loadPaper(key).then(function (data) {
      el.loading.classList.add("hidden");
      renderSessions(data);
      refresh(true);
    }).catch(function (err) {
      el.loading.textContent = err.message;
    });
  }

  // ---------- Événements ----------
  document.getElementById("paperTabs").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-paper]");
    if (!b || b.getAttribute("data-paper") === state.paper) return;
    state.topic = "";
    state.session = "";
    switchPaper(b.getAttribute("data-paper"));
  });

  el.tree.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-topic]");
    if (!a) return;
    e.preventDefault();
    state.topic = a.getAttribute("data-topic");
    closeMenu();
    refresh(true);
  });

  document.getElementById("levelSeg").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-level]");
    if (!b) return;
    state.level = b.getAttribute("data-level");
    refresh(false);
  });

  el.session.addEventListener("change", function () { state.session = el.session.value; refresh(false); });
  el.shuffle.addEventListener("change", function () { state.shuffle = el.shuffle.checked; refresh(false); });

  var searchTimer;
  el.search.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () { state.search = el.search.value; refresh(false); }, 250);
  });

  el.more.addEventListener("click", function () {
    var cardFn = state.paper === "p1a" ? cardP1A : cardP2;
    var next = filtered.slice(state.shown, state.shown + PAGE);
    el.list.insertAdjacentHTML("beforeend", next.map(cardFn).join(""));
    state.shown += PAGE;
    el.more.parentNode.classList.toggle("hidden", state.shown >= filtered.length);
    el.more.textContent = "Afficher plus (" + (filtered.length - state.shown) + " restantes)";
  });

  el.stats.addEventListener("click", function (e) {
    if (e.target.id !== "resetScore") return;
    if (!confirm("Effacer tes réponses pour les questions affichées ?")) return;
    filtered.forEach(function (q) { delete answers[q.id]; });
    saveAnswers();
    refresh(false);
  });

  el.list.addEventListener("click", function (e) {
    var card = e.target.closest(".card");
    if (!card) return;
    var id = card.getAttribute("data-id");

    var opt = e.target.closest("button[data-opt]");
    if (opt) {
      answers[id] = opt.getAttribute("data-opt");
      saveAnswers();
      var q = filtered.filter(function (x) { return x.id === id; })[0];
      card.outerHTML = cardP1A(q);
      renderStats();
      return;
    }

    if (e.target.closest("button[data-retry]")) {
      delete answers[id];
      saveAnswers();
      var q2 = filtered.filter(function (x) { return x.id === id; })[0];
      card.outerHTML = cardP1A(q2);
      renderStats();
      return;
    }

    var t = e.target.closest("button[data-panel]");
    if (t) {
      var panel = card.querySelector(".panel." + t.getAttribute("data-panel"));
      var open = panel.classList.toggle("hidden") === false;
      t.classList.toggle("on", open);
    }
  });

  function closeMenu() {
    el.sidebar.classList.remove("open");
    el.backdrop.classList.remove("open");
  }
  document.getElementById("menuBtn").addEventListener("click", function () {
    el.sidebar.classList.toggle("open");
    el.backdrop.classList.toggle("open");
  });
  el.backdrop.addEventListener("click", closeMenu);

  // ---------- Démarrage ----------
  readHash();
  switchPaper(state.paper);
})();
