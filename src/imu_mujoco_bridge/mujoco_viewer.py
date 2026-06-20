from __future__ import annotations

import argparse
from collections.abc import Iterator
from pathlib import Path

from .demo import simulated_packets
from .packet import QuaternionPacket
from .udp import receive_packets


DEFAULT_MODEL = Path(__file__).resolve().parents[2] / "models" / "orientation_probe.xml"


def run_viewer(packets: Iterator[QuaternionPacket], model_path: Path) -> None:
    try:
        import mujoco
        import mujoco.viewer
    except ImportError as exc:
        raise SystemExit(
            "MuJoCo extra is not installed. Run: python -m pip install '.[mujoco]'"
        ) from exc

    model = mujoco.MjModel.from_xml_path(str(model_path))
    data = mujoco.MjData(model)
    free_qpos = 3

    with mujoco.viewer.launch_passive(model, data) as viewer:
        for packet in packets:
            data.qpos[free_qpos : free_qpos + 4] = packet.as_mujoco_qpos()
            mujoco.mj_forward(model, data)
            viewer.sync()
            if not viewer.is_running():
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Drive a MuJoCo model from IMU quaternions.")
    parser.add_argument("--host", default="0.0.0.0", help="UDP listen host")
    parser.add_argument("--port", type=int, default=5005, help="UDP listen port")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--simulate", action="store_true", help="Use generated packets instead of UDP")
    parser.add_argument("--rate-hz", type=float, default=60.0)
    args = parser.parse_args()

    packets = simulated_packets(args.rate_hz) if args.simulate else receive_packets(args.host, args.port)
    run_viewer(packets, args.model)


if __name__ == "__main__":
    main()
