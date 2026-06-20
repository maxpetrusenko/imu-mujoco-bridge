from __future__ import annotations

import argparse
import threading
from pathlib import Path

from .render_demo import render_demo_video_from_packets
from .udp import make_udp_socket, receive_packets_from_socket
from .virtual_device import VirtualDeviceConfig, send_virtual_packets


def collect_udp_flow_packets(config: VirtualDeviceConfig) -> list:
    host = "127.0.0.1"
    sock = make_udp_socket(host, 0, timeout=2.0)
    port = sock.getsockname()[1]
    receiver = receive_packets_from_socket(sock)
    sender = threading.Thread(
        target=send_virtual_packets,
        args=(host, port, config),
        kwargs={"realtime": False},
    )
    sender.start()
    try:
        packets = [next(receiver) for _ in range(config.packets)]
    finally:
        receiver.close()
        sender.join()
    return packets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a demo from the same UDP flow as the real hardware path."
    )
    parser.add_argument("--output", type=Path, default=Path("docs/demo.mp4"))
    parser.add_argument("--poster", type=Path, default=Path("docs/demo-poster.png"))
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--seconds", type=float, default=4.0)
    parser.add_argument("--noise", type=float, default=0.003)
    parser.add_argument("--drop-rate", type=float, default=0.0)
    parser.add_argument("--jitter-ms", type=float, default=0.0)
    args = parser.parse_args()

    config = VirtualDeviceConfig(
        rate_hz=args.fps,
        packets=int(args.fps * args.seconds),
        noise=args.noise,
        drop_rate=args.drop_rate,
        jitter_ms=args.jitter_ms,
    )
    packets = collect_udp_flow_packets(config)
    render_demo_video_from_packets(
        output=args.output,
        packets=packets,
        width=args.width,
        height=args.height,
        fps=args.fps,
        poster=args.poster,
    )


if __name__ == "__main__":
    main()

