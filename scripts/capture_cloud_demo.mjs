import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const captureId = new Date().toISOString().replace(/[:.]/g, "-");
const outputDir = path.resolve("artifacts", `cloud-demo-frames-${captureId}`);
await fs.mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  headless: true,
  proxy: { server: process.env.RED_TAG_CAPTURE_PROXY ?? "http://127.0.0.1:7890" },
});

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto("https://red-tag-api-ododbqusqq-uc.a.run.app", {
    waitUntil: "domcontentloaded",
    timeout: 60_000,
  });
  await page.locator("#run").waitFor({ state: "visible", timeout: 30_000 });

  let frame = 0;
  const capture = async () => {
    const filename = path.join(outputDir, `frame-${String(frame).padStart(5, "0")}.jpg`);
    await page.screenshot({ path: filename, type: "jpeg", quality: 88 });
    frame += 1;
  };

  for (let index = 0; index < 6; index += 1) {
    await capture();
    await page.waitForTimeout(500);
  }

  await page.locator("#run").click();
  const startedAt = Date.now();
  let completedFrames = 0;
  while (Date.now() - startedAt < 170_000) {
    await capture();
    const clock = (await page.locator("#clock").innerText()).trim();
    if (clock === "PROOF COMPLETE") {
      completedFrames += 1;
      if (completedFrames >= 10) break;
    }
    if (clock === "ERROR") throw new Error("The live Judge Console reported an error");
    await page.waitForTimeout(500);
  }

  const finalClock = (await page.locator("#clock").innerText()).trim();
  if (finalClock !== "PROOF COMPLETE") {
    throw new Error(`Cloud proof did not complete: ${finalClock}`);
  }
  console.log(
    JSON.stringify({ outputDir, frames: frame, fps: 2, seconds: frame / 2, finalClock }),
  );
} finally {
  await browser.close();
}
