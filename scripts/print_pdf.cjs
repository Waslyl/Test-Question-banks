// Imprime une page HTML générée par build_exam.py en PDF A4 (Chromium via Playwright).
// Usage : node scripts/print_pdf.cjs exams/w4ss-b3-test.html exams/W4ss_Academy_Physics_B3_Test.pdf
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const [src, out] = process.argv.slice(2);
  if (!src || !out) { console.error("Usage : node scripts/print_pdf.cjs page.html sortie.pdf"); process.exit(1); }
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || "/opt/pw-browsers/chromium" });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("file://" + path.resolve(src));
  await page.waitForSelector("body[data-ready]");
  const overflow = await page.$$eval(".page .body", (els) =>
    els.map((b, i) => (b.scrollHeight > b.clientHeight + 1 ? i + 1 : 0)).filter(Boolean));
  if (overflow.length) console.warn("Contenu trop haut sur les pages :", overflow.join(", "));
  await page.pdf({ path: out, format: "A4", printBackground: true, preferCSSPageSize: true });
  console.log(out, "—", await page.$$eval(".page", (p) => p.length), "pages", errors.length ? errors : "");
  await browser.close();
})();
