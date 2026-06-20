from __future__ import annotations

import argparse
import json
from pathlib import Path

from .flow_demo import collect_udp_flow_packets
from .virtual_device import VirtualDeviceConfig


def build_replay(config: VirtualDeviceConfig) -> list[dict[str, object]]:
    packets = collect_udp_flow_packets(config)
    frames: list[dict[str, object]] = []
    previous_ms = 0
    for index, packet in enumerate(packets):
        timestamp_ms = packet.timestamp_ms if packet.timestamp_ms is not None else previous_ms
        previous_ms = timestamp_ms
        q = packet.normalized()
        frames.append(
            {
                "index": index,
                "timestampMs": timestamp_ms,
                "quaternion": [q.w, q.x, q.y, q.z],
                "calibration": list(packet.calibration or (0, 0, 0, 0)),
                "csv": packet.as_csv(),
            }
        )
    return frames


def write_replay_js(output: Path, frames: list[dict[str, object]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(frames, indent=2)
    output.write_text(f"window.IMU_REPLAY = {payload};\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a UDP-flow replay fixture for the web lab.")
    parser.add_argument("--output", type=Path, default=Path("web/replay.js"))
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--seconds", type=float, default=4.0)
    parser.add_argument("--noise", type=float, default=0.003)
    parser.add_argument("--drop-rate", type=float, default=0.0)
    parser.add_argument("--jitter-ms", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    config = VirtualDeviceConfig(
        rate_hz=args.rate_hz,
        packets=int(args.rate_hz * args.seconds),
        noise=args.noise,
        drop_rate=args.drop_rate,
        jitter_ms=args.jitter_ms,
        seed=args.seed,
    )
    write_replay_js(args.output, build_replay(config))


if __name__ == "__main__":
    main()

