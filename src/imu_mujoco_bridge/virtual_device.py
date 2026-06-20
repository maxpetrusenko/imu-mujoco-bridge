from __future__ import annotations

import argparse
import random
import socket
import time
from dataclasses import dataclass
from typing import Iterator

from .demo import simulated_packet_at
from .packet import QuaternionPacket


@dataclass(frozen=True)
class VirtualDeviceConfig:
    rate_hz: float = 60.0
    packets: int = 240
    noise: float = 0.003
    drop_rate: float = 0.0
    jitter_ms: float = 0.0
    calibration_seconds: float = 2.0
    seed: int = 7


def virtual_bno055_packets(config: VirtualDeviceConfig) -> Iterator[QuaternionPacket]:
    rng = random.Random(config.seed)
    interval = 1.0 / config.rate_hz
    emitted = 0
    sample_index = 0
    while emitted < config.packets:
        elapsed = sample_index * interval
        sample_index += 1
        if rng.random() < config.drop_rate:
            continue

        packet = add_quaternion_noise(
            simulated_packet_at(elapsed),
            noise=config.noise,
            rng=rng,
        ).normalized()
        yield QuaternionPacket(
            w=packet.w,
            x=packet.x,
            y=packet.y,
            z=packet.z,
            timestamp_ms=int(elapsed * 1000),
            calibration=calibration_at(elapsed, config.calibration_seconds),
        )
        emitted += 1


def add_quaternion_noise(
    packet: QuaternionPacket,
    noise: float,
    rng: random.Random,
) -> QuaternionPacket:
    if noise <= 0:
        return packet
    return QuaternionPacket(
        w=packet.w + rng.uniform(-noise, noise),
        x=packet.x + rng.uniform(-noise, noise),
        y=packet.y + rng.uniform(-noise, noise),
        z=packet.z + rng.uniform(-noise, noise),
        timestamp_ms=packet.timestamp_ms,
        calibration=packet.calibration,
    )


def calibration_at(elapsed_s: float, settle_s: float) -> tuple[int, int, int, int]:
    if settle_s <= 0:
        return (3, 3, 3, 3)

    def level(scale: float) -> int:
        return max(0, min(3, int((elapsed_s / (settle_s * scale)) * 4)))

    return (
        level(1.0),
        level(0.45),
        level(0.65),
        level(1.25),
    )


def send_virtual_packets(
    host: str,
    port: int,
    config: VirtualDeviceConfig,
    realtime: bool = True,
) -> int:
    rng = random.Random(config.seed + 1)
    interval = 1.0 / config.rate_hz
    sent = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for packet in virtual_bno055_packets(config):
            sock.sendto(packet.as_csv().encode("utf-8"), (host, port))
            sent += 1
            if realtime:
                jitter_s = rng.uniform(-config.jitter_ms, config.jitter_ms) / 1000.0
                time.sleep(max(0.0, interval + jitter_s))
    finally:
        sock.close()
    return sent


def main() -> None:
    parser = argparse.ArgumentParser(description="Imitate an M5 ATOM Lite + BNO055 UDP sender.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--rate-hz", type=float, default=60.0)
    parser.add_argument("--packets", type=int, default=240)
    parser.add_argument("--noise", type=float, default=0.003)
    parser.add_argument("--drop-rate", type=float, default=0.0)
    parser.add_argument("--jitter-ms", type=float, default=0.0)
    parser.add_argument("--calibration-seconds", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--dry-run", action="store_true", help="Print packets instead of sending UDP.")
    args = parser.parse_args()

    config = VirtualDeviceConfig(
        rate_hz=args.rate_hz,
        packets=args.packets,
        noise=args.noise,
        drop_rate=args.drop_rate,
        jitter_ms=args.jitter_ms,
        calibration_seconds=args.calibration_seconds,
        seed=args.seed,
    )
    if args.dry_run:
        for packet in virtual_bno055_packets(config):
            print(packet.as_csv(), flush=True)
        return

    send_virtual_packets(args.host, args.port, config)


if __name__ == "__main__":
    main()

