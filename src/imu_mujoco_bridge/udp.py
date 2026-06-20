from __future__ import annotations

import argparse
import socket
from typing import Iterator

from .packet import QuaternionPacket, parse_packet


def receive_packets(host: str, port: int, timeout: float | None = None) -> Iterator[QuaternionPacket]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(timeout)
    try:
        while True:
            payload, _address = sock.recvfrom(2048)
            yield parse_packet(payload)
    finally:
        sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Print BNO055 UDP quaternion packets.")
    parser.add_argument("--host", default="0.0.0.0", help="UDP listen host")
    parser.add_argument("--port", type=int, default=5005, help="UDP listen port")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N packets")
    args = parser.parse_args()

    for index, packet in enumerate(receive_packets(args.host, args.port), start=1):
        print(packet.normalized(), flush=True)
        if args.limit and index >= args.limit:
            break


if __name__ == "__main__":
    main()

