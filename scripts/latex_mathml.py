"""Petit convertisseur LaTeX -> MathML, pour écrire des énoncés de maths dans les scripts de sujets.

Gère ce dont les énoncés ont besoin : \\frac, \\sqrt, ^, _, \\left( \\right), \\text, \\mathbb, \\mathrm,
les fonctions usuelles (ln, tan, arctan…), quelques symboles (\\pi, \\int, \\in, \\ne, \\le, \\ge, \\times…).
Dans un texte, $…$ devient une formule en ligne et $$…$$ une formule centrée (texte_math).
"""
import html
import re

FUNCS = {"ln", "tan", "arctan", "sin", "cos", "sec", "exp", "log"}
SYMBOLS = {"pi": ("mi", "π"), "int": ("mo", "∫"), "in": ("mo", "∈"), "ne": ("mo", "≠"), "le": ("mo", "≤"),
           "ge": ("mo", "≥"), "leqslant": ("mo", "⩽"), "geqslant": ("mo", "⩾"), "times": ("mo", "×"),
           "cdot": ("mo", "·"), "infty": ("mi", "∞"), "approx": ("mo", "≈"), "lt": ("mo", "&lt;"),
           "gt": ("mo", "&gt;"), "Rightarrow": ("mo", "⇒"), "pm": ("mo", "±"), ",": ("mspace", ""),
           "quad": ("mspace", "")}
BB = {"R": "ℝ", "Z": "ℤ", "N": "ℕ", "Q": "ℚ"}
TOKEN = re.compile(r"\\text\{[^}]*\}|\\[A-Za-z]+|\\.|\d+(?:\.\d+)?|[A-Za-z]|\S")


def tokens(s):
    return TOKEN.findall(s)


class Parser:
    def __init__(self, src):
        self.t = tokens(src)
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def group(self):
        """Contenu entre accolades (l'accolade ouvrante est déjà lue)."""
        out = []
        while self.peek() not in (None, "}"):
            out.append(self.atom_scripts())
        self.take()
        return "".join(out)

    def arg(self):
        if self.peek() == "{":
            self.take()
            return f"<mrow>{self.group()}</mrow>"
        return self.atom()

    def raw_arg(self):
        """Texte brut entre accolades (pour \\text, \\mathbb, \\mathrm)."""
        assert self.take() == "{"
        out = []
        while self.peek() not in (None, "}"):
            out.append(self.take())
        self.take()
        return out

    def atom(self):
        tok = self.take()
        if tok == "{":
            return f"<mrow>{self.group()}</mrow>"
        if tok == "\\frac":
            return f"<mfrac>{self.arg()}{self.arg()}</mfrac>"
        if tok == "\\sqrt":
            return f"<msqrt>{self.arg()}</msqrt>"
        if tok in ("\\left", "\\right"):
            nxt = self.take()
            return f'<mo stretchy="true">{html.escape(nxt.lstrip(chr(92)))}</mo>' if nxt != "." else ""
        if tok.startswith("\\text{"):
            return f"<mtext>{html.escape(tok[6:-1])}</mtext>"
        if tok == "\\mathbb":
            return f'<mi mathvariant="normal">{BB["".join(self.raw_arg())]}</mi>'
        if tok == "\\mathrm":
            return f'<mi mathvariant="normal">{"".join(self.raw_arg())}</mi>'
        if tok.startswith("\\"):
            name = tok[1:]
            if name in FUNCS:
                return f'<mi mathvariant="normal">{name}</mi><mo lspace="0" rspace="0.1em">&#x2061;</mo>'
            if name in SYMBOLS:
                kind, val = SYMBOLS[name]
                if kind == "mspace":
                    return '<mspace width="0.4em"></mspace>' if name == "quad" else '<mspace width="0.2em"></mspace>'
                return f"<{kind}>{val}</{kind}>"
            if name in ("{", "}", "|"):
                return f"<mo>{name}</mo>"
            raise ValueError(f"commande inconnue {tok}")
        if re.fullmatch(r"\d+(?:\.\d+)?", tok):
            return f"<mn>{tok}</mn>"
        if re.fullmatch(r"[A-Za-z]", tok):
            return f"<mi>{tok}</mi>"
        if tok == "-":
            return "<mo>−</mo>"
        if tok == "'":
            return '<mo lspace="0" rspace="0">′</mo>'
        return f"<mo>{html.escape(tok)}</mo>"

    def atom_scripts(self):
        base = self.atom()
        sub = sup = None
        while self.peek() in ("^", "_"):
            if self.take() == "^":
                sup = self.arg()
            else:
                sub = self.arg()
        if sub and sup:
            return f"<msubsup><mrow>{base}</mrow>{sub}{sup}</msubsup>"
        if sup:
            return f"<msup><mrow>{base}</mrow>{sup}</msup>"
        if sub:
            return f"<msub><mrow>{base}</mrow>{sub}</msub>"
        return base

    def parse(self):
        out = []
        while self.peek() is not None:
            out.append(self.atom_scripts())
        return "".join(out)


def math(tex, display=False):
    body = Parser(tex).parse()
    # moins unaire (en début de formule ou après « = ( , ») : sans espace
    body = re.sub(r'(^|<mo>[=(,]</mo>|<mo stretchy="true">\(</mo>)<mo>−</mo>', r'\1<mo lspace="0" rspace="0">−</mo>', body)
    return f'<math{" display=\"block\"" if display else ""}>{body}</math>'


def texte_math(s):
    """Remplace $$…$$ (formule centrée) et $…$ (formule en ligne) dans un texte HTML."""
    s = re.sub(r"\$\$(.+?)\$\$", lambda m: '<p class="center">' + math(m.group(1)) + "</p>", s, flags=re.S)
    return re.sub(r"\$(.+?)\$", lambda m: math(m.group(1)), s)
