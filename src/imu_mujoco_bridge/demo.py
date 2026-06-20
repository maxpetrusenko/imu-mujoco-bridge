from __future__ import annotations

import argparse
import json
import math
import time
from typing import Iterator

from .packet import QuaternionPacket


def simulated_packet_at(elapsed_s: float) -> QuaternionPacket:
    yaw = elapsed_s * 0.8
    pitch = math.sin(elapsed_s * 1.3) * 0.35
    roll = math.sin(elapsed_s * 0.7) * 0.22
    w, x, y, z = euler_to_quaternion(roll=roll, pitch=pitch, yaw=yaw)
    return QuaternionPacket(
        w=w,
        x=x,
        y=y,
        z=z,
        timestamp_ms=int(elapsed_s * 1000),
        calibration=(3, 3, 3, 3),
    )


def simulated_packets(rate_hz: float = 60.0) -> Iterator[QuaternionPacket]:
    start = time.monotonic()
    sleep_s = 1.0 / rate_hz
    while True:
        elapsed = time.monotonic() - start
        yield simulated_packet_at(elapsed)
        time.sleep(sleep_s)


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return (w, x, y, z)


def packet_to_json(packet: QuaternionPacket) -> str:
    q = packet.normalized()
    return json.dumps(
        {
            "qw": q.w,
            "qx": q.x,
            "qy": q.y,
            "qz": q.z,
            "t_ms": q.timestamp_ms,
            "calibration": q.calibration,
        },
        separators=(",", ":"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate simulated quaternion packets.")
    parser.add_argument("--rate-hz", type=float, default=60.0)
    parser.add_argument("--packets", type=int, default=10)
    args = parser.parse_args()

    for index, packet in enumerate(simulated_packets(args.rate_hz), start=1):
        print(packet_to_json(packet), flush=True)
        if index >= args.packets:
            break


if __name__ == "__main__":
    main()
