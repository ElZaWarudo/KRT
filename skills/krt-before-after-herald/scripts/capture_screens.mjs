#!/usr/bin/env node
// Capture every screen in both themes and both viewports for one side of a before/after report.
//
// Usage (needs Playwright with Chromium: `npm i -D playwright && npx playwright install chromium`):
//   node capture_screens.mjs routes.json OUT_DIR/after
//
// routes.json: [{ "key": "cart", "path": "/cart" }, ...]  (keys must match report.json screens)
//
// Environment:
//   CAPTURE_BASE_URL   app URL (default http://127.0.0.1:3000)
//   CAPTURE_STORAGE    JSON object written to localStorage before each page loads; "{theme}" is replaced
//                      with light/dark. Use it for session tokens and theme preferences,
//                      e.g. {"app-theme":"\"{theme}\"","session":"\"abc\""}
//   CAPTURE_WAIT_MS    extra wait after network idle (default 1200)
//
// Writes <key>-<theme>-<viewport>.png plus capture.json, and exits 1 when a page has horizontal overflow,
// a framework error overlay, or an uncaught page error, so a broken "after" never reaches the report.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { chromium } from "playwright";

const [routesFile, outArg] = process.argv.slice(2);
if (!routesFile || !outArg) {
    console.error("Usage: node capture_screens.mjs routes.json OUT_DIR/<side>");
    process.exit(2);
}
const baseUrl = (process.env.CAPTURE_BASE_URL || "http://127.0.0.1:3000").replace(/\/$/, "");
const storage = process.env.CAPTURE_STORAGE ? JSON.parse(process.env.CAPTURE_STORAGE) : {};
const waitMs = Number(process.env.CAPTURE_WAIT_MS || 1200);
const outDir = resolve(outArg);
const routes = JSON.parse(readFileSync(routesFile, "utf8"));
const themes = ["light", "dark"];
const viewports = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const results = [];
for (const route of routes) {
    for (const theme of themes) {
        for (const [viewportName, viewport] of Object.entries(viewports)) {
            const context = await browser.newContext({ viewport, colorScheme: theme });
            const values = Object.fromEntries(Object.entries(storage).map(([key, value]) => [key, String(value).replaceAll("{theme}", theme)]));
            await context.addInitScript((entries) => {
                for (const [key, value] of Object.entries(entries)) localStorage.setItem(key, value);
            }, values);
            const page = await context.newPage();
            const errors = [];
            page.on("pageerror", (error) => errors.push(String(error).slice(0, 200)));
            await page.goto(baseUrl + route.path, { waitUntil: "networkidle" }).catch((error) => errors.push(String(error).slice(0, 200)));
            await page.waitForTimeout(waitMs);
            const name = `${route.key}-${theme}-${viewportName}`;
            await page.screenshot({ path: join(outDir, `${name}.png`), fullPage: true });
            const layout = await page.evaluate(() => ({
                overflow: document.documentElement.scrollWidth > window.innerWidth,
                overlay: Boolean(document.querySelector("vite-error-overlay, nextjs-portal, #webpack-dev-server-client-overlay")),
            }));
            results.push({ name, path: route.path, ...layout, errors });
            await context.close();
        }
    }
}
await browser.close();
writeFileSync(join(outDir, "capture.json"), JSON.stringify(results, null, 2));
const bad = results.filter((item) => item.overflow || item.overlay || item.errors.length);
for (const item of bad) console.error(`FAIL ${item.name}: ${[item.overflow && "horizontal overflow", item.overlay && "error overlay", ...item.errors].filter(Boolean).join("; ")}`);
console.log(`${results.length} captures in ${outDir}, ${bad.length} with problems`);
process.exit(bad.length ? 1 : 0);
