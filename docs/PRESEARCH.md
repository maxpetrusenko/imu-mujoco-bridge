# Presearch

## Reference Being Repeated

The X thread shows a compact IMU-to-MuJoCo demo:

- M5 ATOM Lite controller.
- BNO055 absolute-orientation IMU.
- Device sends quaternions over UDP to a PC.
- PC updates a MuJoCo model from the streamed quaternion.
- The author calls out the value of 9-axis fusion for avoiding yaw drift.

## Source Notes

- X post: https://x.com/H0meMadeGarbage/status/2068259209200959643
- Thread reply: "UDPでクォータニオンをPCに送信して MuJoCoモデル動かしてるだけです。"
- M5Stack ATOM Lite docs: https://docs.m5stack.com/en/core/ATOM%20Lite
- Adafruit BNO055 guide: https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/overview
- Adafruit BNO055 FAQ: https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/faqs
- MuJoCo Python docs: https://mujoco.readthedocs.io/en/stable/python.html

## Product Shape

This repo should be a small open source bridge, not a one-off video clone:

- Firmware sketch for M5 ATOM Lite plus BNO055.
- UDP packet contract documented and tested.
- Python receiver that can print packets.
- MuJoCo viewer that can run from real UDP or simulated packets.
- Virtual ATOM Lite plus BNO055 sender that uses the same UDP path as real hardware.
- Camera-marker pose source so people can get an IRL demo with a webcam and printed marker.
- Simulated packet generator so contributors can verify the repo without hardware.
- Browser lab with Playwright proof so CI can validate visual replay without hardware.

## Non-Goals

- Full sensor fusion implementation. BNO055 does this on-chip.
- Browser-only clone. The point is a live MuJoCo model.
- Hardware-specific calibration wizard. Calibration values are exposed so users can build that later.
