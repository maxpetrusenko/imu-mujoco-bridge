import { expect, test } from "@playwright/test";

test("3D twin shows linked source and response bodies", async ({ page }) => {
  await page.goto("/web/twin.html");

  await expect(page.getByRole("heading", { name: "IMU Twin Lab" })).toBeVisible();
  await expect(page.getByText("Response box follows")).toBeVisible();

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

