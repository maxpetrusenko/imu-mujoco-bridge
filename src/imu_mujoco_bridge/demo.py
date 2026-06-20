from __future__ import annotations

import argparse
import json
import math
import time
from typing import Iterator

from .packet import QuaternionPacket


def simulated_packets(rate_hz: float = 60.0) -> Iterator[QuaternionPacket]:
    start = time.monotonic()
    sleep_s = 1.0 / rate_hz
    while True:
        elapsed = time.monotonic() - start
        yaw = elapsed * 0.8
        half = yaw / 2.0
        yield QuaternionPacket(
            w=math.cos(half),
            x=0.0,
            y=0.0,
            z=math.sin(half),
            timestamp_ms=int(elapsed * 1000),
            calibration=(3, 3, 3, 3),
        )
        time.sleep(sleep_s)


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

