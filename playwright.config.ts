import { defineConfig, devices } from "@playwright/test";

const labHost = process.env.LAB_HOST || "127.0.0.1";
const labPort = process.env.LAB_PORT || "4173";
const labBaseURL = `http://${labHost}:${labPort}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: labBaseURL,
    trace: "on-first-retry"
  },
  webServer: {
    command: `npm run serve -- --host ${labHost} --port ${labPort}`,
    url: `${labBaseURL}/web/twin.html`,
    reuseExistingServer: false,
    timeout: 10_000
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 7"] }
    }
  ]
});
