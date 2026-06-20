import { expect, test } from "@playwright/test";

test("3D twin shows linked source and response bodies", async ({ page }) => {
  await page.goto("/web/twin.html");

  await expect(page.getByRole("heading", { name: "IMU Twin Lab" })).toBeVisible();
  await expect(page.getByText("Response body follows")).toBeVisible();

  const canvas = page.locator("#twin-scene");
  await expect(canvas).toBeVisible();

  await page.waitForFunction(() => window.__TWIN_READY === true);
  await page.waitForFunction(() => window.__TWIN_METRICS?.frame > 2);

  const metrics = await page.evaluate(() => window.__TWIN_METRICS);
  expect(metrics.leftX).toBeLessThan(0);
  expect(metrics.rightX).toBeGreaterThan(0);
  expect(metrics.lagDegrees).toBeGreaterThanOrEqual(0);

  const coloredPixels = await canvas.evaluate((node: HTMLCanvasElement) => {
    const gl = node.getContext("webgl2") || node.getContext("webgl");
    if (!gl) return 0;
    const width = gl.drawingBufferWidth;
    const height = gl.drawingBufferHeight;
    const pixels = new Uint8Array(width * height * 4);
    gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    let count = 0;
    for (let index = 0; index < pixels.length; index += 4) {
      const r = pixels[index];
      const g = pixels[index + 1];
      const b = pixels[index + 2];
      if (Math.abs(r - 245) > 12 || Math.abs(g - 239) > 12 || Math.abs(b - 226) > 12) {
        count += 1;
      }
    }
    return count;
  });
  expect(coloredPixels).toBeGreaterThan(1500);

  await page.getByRole("button", { name: "Pause" }).click();
  await expect(page.getByRole("button", { name: "Play" })).toBeVisible();
  await page.getByRole("button", { name: "Reset" }).click();
  await expect(page.locator("#twin-packet")).not.toHaveText("waiting");
});

test("3D twin lets a user control the source body", async ({ page }) => {
  await page.goto("/web/twin.html");
  await page.waitForFunction(() => window.__TWIN_READY === true);

  await page.getByRole("button", { name: "Manual source" }).click();
  await expect(page.locator("#twin-mode")).toHaveText("manual");

  await page.locator("#source-roll").fill("35");
  await page.locator("#source-pitch").fill("-28");
  await page.locator("#source-yaw").fill("62");

  await page.waitForFunction(
    () =>
      window.__TWIN_METRICS?.mode === "manual" &&
      window.__TWIN_METRICS?.manualRoll === 35 &&
      window.__TWIN_METRICS?.manualPitch === -28 &&
      window.__TWIN_METRICS?.manualYaw === 62
  );

  await expect(page.locator("#source-roll-value")).toHaveText("35 deg");
  await expect(page.locator("#source-pitch-value")).toHaveText("-28 deg");
  await expect(page.locator("#source-yaw-value")).toHaveText("62 deg");
  await expect(page.locator("#twin-packet")).toContainText(",3,3,3,3,");

  const manualMetrics = await page.evaluate(() => window.__TWIN_METRICS);
  expect(manualMetrics.leftY).toBeLessThan(0);
  expect(manualMetrics.leftZ).toBeGreaterThan(0);

  await page.waitForFunction(() => Math.abs(window.__TWIN_METRICS?.rightZ ?? 0) > 0.01);
  const respondingMetrics = await page.evaluate(() => window.__TWIN_METRICS);
  expect(respondingMetrics.rightZ).toBeGreaterThan(0);

  await page.getByRole("button", { name: "Auto replay" }).click();
  await expect(page.locator("#twin-mode")).toHaveText("replay");
});

test("3D twin supports direct 360 pointer control", async ({ page }, testInfo) => {
  await page.goto("/web/twin.html");
  await page.waitForFunction(() => window.__TWIN_READY === true);

  const canvas = page.locator("#twin-scene");
  const box = await canvas.boundingBox();
  expect(box).not.toBeNull();
  const startX = box!.x + box!.width * 0.18;
  const startY = box!.y + box!.height * 0.3;
  const endX = box!.x + box!.width * 0.88;
  const endY = box!.y + box!.height * 0.22;

  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(endX, endY, { steps: 18 });
  await page.mouse.up();

  await page.waitForFunction(
    () =>
      window.__TWIN_METRICS?.mode === "manual" &&
      Math.abs(window.__TWIN_METRICS?.manualYaw ?? 0) >= 360
  );

  const draggedMetrics = await page.evaluate(() => window.__TWIN_METRICS);
  expect(Math.abs(draggedMetrics.manualYaw)).toBeGreaterThanOrEqual(360);
  expect(Math.abs(draggedMetrics.manualPitch)).toBeGreaterThan(20);

  if (testInfo.project.name === "chromium") {
    await page.mouse.move(startX, startY);
    await page.mouse.wheel(0, 2400);
    await page.waitForFunction(() => Math.abs(window.__TWIN_METRICS?.manualRoll ?? 0) >= 360);
    const rolledMetrics = await page.evaluate(() => window.__TWIN_METRICS);
    expect(Math.abs(rolledMetrics.manualRoll)).toBeGreaterThanOrEqual(360);
    expect(rolledMetrics.rightX).toBeGreaterThan(0);
  }
});
