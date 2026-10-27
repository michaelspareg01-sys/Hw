// Print an HTML file to PDF with headless Chrome over the DevTools protocol.
// usage: node print.mjs in.html out.pdf "Footer text"
import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [inp, out, footer] = process.argv.slice(2);
const CHROME = process.env.CHROME || "/opt/pw-browsers/chromium";
const port = 9400 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(tmpdir(), "chr-"));
const chrome = spawn(CHROME, ["--headless=new", "--no-sandbox", `--remote-debugging-port=${port}`,
  `--user-data-dir=${prof}`, "--allow-file-access-from-files", "--no-first-run", "about:blank"],
  { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 60 && !target; i++) {
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page"); }
  catch { await sleep(250); }
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.method === "Runtime.exceptionThrown") console.error("PAGE EXCEPTION:", JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") console.error("PAGE ERROR:", JSON.stringify(m.params.args).slice(0, 400));
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

await send("Page.enable");
await send("Runtime.enable");
await send("Page.navigate", { url: pathToFileURL(resolve(inp)).href });
let ready = false;
for (let i = 0; i < 240 && !ready; i++) {
  await sleep(500);
  const r = await send("Runtime.evaluate", { expression: "window.__ready === true", returnByValue: true });
  ready = r.result?.result?.value === true;
}
console.error("ready?", ready, new Date().toISOString());
if (!ready) { const st = await send("Runtime.evaluate", { expression: "JSON.stringify({mj: !!window.MathJax, tp: !!(window.MathJax && MathJax.typesetPromise), n: document.querySelectorAll('mjx-container').length})", returnByValue: true }); console.error("page never became ready", st.result?.result?.value); chrome.kill(); process.exit(1); }
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const style = "font-family:Inter,Arial,sans-serif;font-size:8px;color:#8a96a3;width:100%;padding:0 15mm;display:flex;justify-content:space-between;";
const res = await send("Page.printToPDF", {
  printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true, transferMode: "ReturnAsStream",
  headerTemplate: `<div style="${style}color:#2563eb;letter-spacing:.06em;"><span>YEAR 12 MATHEMATICS EXTENSION 1</span><span></span></div>`,
  footerTemplate: `<div style="${style}"><span>${esc(footer)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
});
console.error("printed", new Date().toISOString());
if (!res.result) { console.error(JSON.stringify(res.error)); chrome.kill(); process.exit(1); }
const chunks = [];
for (;;) {
  const r = await send("IO.read", { handle: res.result.stream, size: 1 << 20 });
  chunks.push(Buffer.from(r.result.data, r.result.base64Encoded ? "base64" : "utf8"));
  if (r.result.eof) break;
}
await send("IO.close", { handle: res.result.stream });
writeFileSync(out, Buffer.concat(chunks));
ws.close(); chrome.kill();
