# imu-mujoco-bridge

Stream BNO055 absolute-orientation quaternions into a MuJoCo model.

This repeats the useful part of the referenced demo: an M5 ATOM Lite reads a
BNO055 IMU, sends quaternion packets over UDP, and a PC uses those packets to
rotate a MuJoCo body in real time.

## Why

For all-direction orientation, use quaternions from a 9-axis absolute-orientation
sensor. The BNO055 handles fusion on-chip and outputs quaternion samples at up to
100 Hz, which is a good fit for a small wireless pose controller.

## Hardware

- M5Stack ATOM Lite or compatible ESP32 board.
- Adafruit BNO055 breakout or compatible BNO055 module.
- I2C wiring from ESP32 to BNO055.
- Same Wi-Fi network as the computer running the viewer.

## Packet Contract

UDP port defaults to `5005`.

CSV:

```text
qw,qx,qy,qz,cal_sys,cal_gyro,cal_accel,cal_mag,t_ms
```

Minimal CSV is also accepted:

```text
qw,qx,qy,qz
```

JSON is accepted too:

```json
{"qw":1,"qx":0,"qy":0,"qz":0,"t_ms":123,"calibration":[3,3,3,3]}
```

Quaternion order is `w,x,y,z`, matching MuJoCo free-joint orientation order.

## Quick Start Without Hardware

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m imu_mujoco_bridge.demo --packets 3
PYTHONPATH=src python -m unittest discover -s tests
```

Optional MuJoCo viewer:

```sh
python -m pip install -e '.[mujoco]'
imu-mujoco-viewer --simulate
```

## Run With Hardware

1. Copy firmware config:

```sh
cp firmware/include/config.example.h firmware/include/config.h
```

2. Edit `firmware/include/config.h` with Wi-Fi and the PC IP address.
3. Flash with PlatformIO:

```sh
pio run -d firmware -t upload
```

4. On the PC:

```sh
imu-udp-dump --port 5005
imu-mujoco-viewer --port 5005
```

## Notes

- Keep the BNO055 away from magnets and high-current wiring while testing yaw.
- Watch calibration values. `3,3,3,3` is ideal; lower magnetometer calibration can show up as yaw instability.
- Prefer quaternion packets over Euler angles for full-range orientation.

## License

MIT
