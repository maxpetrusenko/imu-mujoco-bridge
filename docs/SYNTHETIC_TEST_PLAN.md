# Synthetic Test Plan

This project cannot honestly claim real-hardware readiness until an ATOM Lite
and BNO055 are flashed and streamed into the viewer. The no-hardware gate is a
synthetic lab that proves every software-owned boundary.

## Covered

| Layer | Proof |
| --- | --- |
| Packet contract | Unit tests parse CSV, JSON, timestamps, calibration, normalization, and zero-quaternion rejection. |
| Virtual sensor | `imu-virtual-device` emits deterministic BNO055-like quaternions, calibration ramp, noise, jitter, and optional packet loss. |
| Transport | UDP loopback tests receive real datagrams through the same parser used by hardware. |
| Replay export | `imu-export-replay` captures the UDP-flow packets into `web/replay.js`. |
| Browser lab | `web/lab.html` replays captured packets and renders a MuJoCo-compatible orientation preview. |
| E2E | Playwright checks desktop and mobile lab views, telemetry, canvas pixels, and controls. |
| CI | GitHub Actions runs Python lint/tests and Playwright browser tests. |

## Not Covered

| Layer | Missing real proof |
| --- | --- |
| Hardware firmware | No flash/run on physical ATOM Lite plus BNO055 yet. |
| Sensor calibration | Calibration ramp is synthetic; no magnetic interference or real yaw-drift test yet. |
| Camera marker | Math is unit-tested; webcam capture is not run in CI. |
| MuJoCo desktop viewer | Optional MuJoCo package path is not exercised in CI. |

## 10/10 Without Hardware Bar

No-hardware 10/10 means:

- `ruff check .` passes.
- `PYTHONPATH=src python -m unittest discover -s tests` passes.
- `imu-export-replay --output web/replay.js` regenerates the replay fixture.
- `npm run test:e2e` passes locally and in CI.
- README shows the demo video, browser lab screenshot, setup commands, and known limits.

Run all of that locally with:

```sh
scripts/verify
```

Real-world 10/10 still requires hardware and camera evidence.
