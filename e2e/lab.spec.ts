import { expect, test } from "@playwright/test";

test("browser lab replays captured UDP packets", async ({ page }) => {
  await page.goto("/web/lab.html");

  await expect(page.getByRole("heading", { name: "IMU MuJoCo Bridge Lab" })).toBeVisible();
  await expect(page.getByText("Virtual ATOM Lite + BNO055 replay")).toBeVisible();
  await expect(page.locator("#packet")).not.toHaveText("waiting");

  const canvas = page.locator("#scene");
  await expect(canvas).toBeVisible();

  const nonBlankPixels = await canvas.evaluate((node: HTMLCanvasElement) => {
    const context = node.getContext("2d");
    if (!context) return 0;
    const image = context.getImageData(0, 0, node.width, node.height).data;
    let changed = 0;
    for (let index = 0; index < image.length; index += 4) {
      const r = image[index];
      const g = image[index + 1];
      const b = image[index + 2];
      if (!(r === 243 && g === 239 && b === 228)) changed += 1;
    }
    return changed;
  });
  expect(nonBlankPixels).toBeGreaterThan(1000);

  const before = await page.locator("#frame").textContent();
  await page.getByRole("button", { name: "Pause" }).click();
  await page.getByRole("button", { name: "Step" }).click();
  const after = await page.locator("#frame").textContent();
  expect(after).not.toEqual(before);

  await page.locator("#scrubber").fill("0");
  await expect(page.locator("#calibration")).toHaveText("0,0,0,0");
});

