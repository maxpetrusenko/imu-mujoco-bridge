from __future__ import annotations

from dataclasses import dataclass
import json
import math


@dataclass(frozen=True)
class QuaternionPacket:
    """One orientation sample.

    MuJoCo free-joint orientation expects quaternion order w, x, y, z.
    """

    w: float
    x: float
    y: float
    z: float
    timestamp_ms: int | None = None
    calibration: tuple[int, int, int, int] | None = None

    def normalized(self) -> "QuaternionPacket":
        norm = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if norm == 0:
            raise ValueError("zero-length quaternion")
        return QuaternionPacket(
            w=self.w / norm,
            x=self.x / norm,
            y=self.y / norm,
            z=self.z / norm,
            timestamp_ms=self.timestamp_ms,
            calibration=self.calibration,
        )

    def as_mujoco_qpos(self) -> tuple[float, float, float, float]:
        q = self.normalized()
        return (q.w, q.x, q.y, q.z)


def parse_packet(payload: bytes | str) -> QuaternionPacket:
    text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    text = text.strip()
    if not text:
        raise ValueError("empty packet")

    if text.startswith("{"):
        return _parse_json_packet(text)

    return _parse_csv_packet(text)


def _parse_json_packet(text: str) -> QuaternionPacket:
    data = json.loads(text)
    try:
        w = float(data.get("w", data["qw"]))
        x = float(data.get("x", data["qx"]))
        y = float(data.get("y", data["qy"]))
        z = float(data.get("z", data["qz"]))
    except KeyError as exc:
        raise ValueError(f"missing quaternion field: {exc.args[0]}") from exc

    calibration = _calibration_from_json(data)
    timestamp_ms = data.get("t_ms", data.get("timestamp_ms"))
    return QuaternionPacket(
        w=w,
        x=x,
        y=y,
        z=z,
        timestamp_ms=int(timestamp_ms) if timestamp_ms is not None else None,
        calibration=calibration,
    )


def _parse_csv_packet(text: str) -> QuaternionPacket:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) not in {4, 5, 8, 9}:
        raise ValueError(
            "CSV packet must be w,x,y,z plus optional t_ms and calibration fields"
        )

    w, x, y, z = (float(value) for value in parts[:4])
    timestamp_ms: int | None = None
    calibration: tuple[int, int, int, int] | None = None

    if len(parts) == 5:
        timestamp_ms = int(float(parts[4]))
    elif len(parts) == 8:
        calibration = tuple(int(float(value)) for value in parts[4:8])  # type: ignore[assignment]
    elif len(parts) == 9:
        calibration = tuple(int(float(value)) for value in parts[4:8])  # type: ignore[assignment]
        timestamp_ms = int(float(parts[8]))

    return QuaternionPacket(
        w=w,
        x=x,
        y=y,
        z=z,
        timestamp_ms=timestamp_ms,
        calibration=calibration,
    )


def _calibration_from_json(data: dict[str, object]) -> tuple[int, int, int, int] | None:
    calibration = data.get("calibration")
    if isinstance(calibration, dict):
        return (
            int(calibration.get("sys", 0)),
            int(calibration.get("gyro", 0)),
            int(calibration.get("accel", 0)),
            int(calibration.get("mag", 0)),
        )
    if isinstance(calibration, list | tuple) and len(calibration) == 4:
        return tuple(int(value) for value in calibration)  # type: ignore[return-value]
    return None

