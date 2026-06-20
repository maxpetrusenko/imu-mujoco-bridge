from __future__ import annotations

import argparse
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

from .demo import simulated_packet_at
from .packet import QuaternionPacket

Point2 = tuple[int, int]
Point3 = tuple[float, float, float]

EDGES = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
    (8, 9),
    (10, 11),
)

VERTICES: tuple[Point3, ...] = (
    (-1.2, -0.4, -0.22),
    (1.2, -0.4, -0.22),
    (1.2, 0.4, -0.22),
    (-1.2, 0.4, -0.22),
    (-1.2, -0.4, 0.22),
    (1.2, -0.4, 0.22),
    (1.2, 0.4, 0.22),
    (-1.2, 0.4, 0.22),
    (1.2, 0.0, 0.0),
    (1.75, 0.0, 0.0),
    (0.0, 0.0, 0.22),
    (0.0, 0.0, 0.75),
)


def rotate_point(point: Point3, packet: QuaternionPacket) -> Point3:
    q = packet.normalized()
    w, x, y, z = q.w, q.x, q.y, q.z
    px, py, pz = point

    # Quaternion rotation: v' = q * v * conjugate(q), expanded to a matrix.
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return (
        (1 - 2 * (yy + zz)) * px + 2 * (xy - wz) * py + 2 * (xz + wy) * pz,
        2 * (xy + wz) * px + (1 - 2 * (xx + zz)) * py + 2 * (yz - wx) * pz,
        2 * (xz - wy) * px + 2 * (yz + wx) * py + (1 - 2 * (xx + yy)) * pz,
    )


def project(point: Point3, width: int, height: int) -> Point2:
    x, y, z = point
    camera_distance = 4.2
    scale = min(width, height) * 0.36
    perspective = camera_distance / (camera_distance + y)
    screen_x = int(width * 0.5 + x * scale * perspective)
    screen_y = int(height * 0.53 - z * scale * perspective)
    return (screen_x, screen_y)


def render_frame(packet: QuaternionPacket, width: int, height: int) -> bytes:
    pixels = bytearray([245, 241, 232] * width * height)
    points = [project(rotate_point(vertex, packet), width, height) for vertex in VERTICES]

    draw_grid(pixels, width, height)
    for start, end in EDGES:
        color = (35, 56, 92)
        if (start, end) == (8, 9):
            color = (226, 71, 57)
        if (start, end) == (10, 11):
            color = (42, 148, 80)
        draw_line(pixels, width, height, points[start], points[end], color, thickness=5)

    return ppm_bytes(pixels, width, height)


def draw_grid(pixels: bytearray, width: int, height: int) -> None:
    horizon = int(height * 0.76)
    for x in range(0, width, 48):
        draw_line(pixels, width, height, (x, horizon), (width // 2, int(height * 0.55)), (214, 206, 190), 1)
    for offset in range(0, 220, 28):
        draw_line(
            pixels,
            width,
            height,
            (0, horizon + offset),
            (width, horizon + offset),
            (218, 210, 194),
            1,
        )


def draw_line(
    pixels: bytearray,
    width: int,
    height: int,
    start: Point2,
    end: Point2,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    x0, y0 = start
    x1, y1 = end
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for index in range(steps + 1):
        t = index / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        radius = thickness // 2
        for yy in range(y - radius, y + radius + 1):
            for xx in range(x - radius, x + radius + 1):
                if math.hypot(xx - x, yy - y) <= radius:
                    set_pixel(pixels, width, height, xx, yy, color)


def set_pixel(
    pixels: bytearray,
    width: int,
    height: int,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    index = (y * width + x) * 3
    pixels[index : index + 3] = bytes(color)


def ppm_bytes(pixels: bytearray, width: int, height: int) -> bytes:
    return f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(pixels)


def render_demo_video(output: Path, width: int, height: int, fps: int, seconds: float) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required to render the demo video")

    output.parent.mkdir(parents=True, exist_ok=True)
    frame_count = int(fps * seconds)
    with tempfile.TemporaryDirectory(prefix="imu-demo-frames-") as tmp:
        frame_dir = Path(tmp)
        for frame in range(frame_count):
            packet = simulated_packet_at(frame / fps)
            frame_path = frame_dir / f"frame-{frame:04d}.ppm"
            frame_path.write_bytes(render_frame(packet, width, height))

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(frame_dir / "frame-%04d.ppm"),
                "-vf",
                "format=yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the hardware-free demo video.")
    parser.add_argument("--output", type=Path, default=Path("docs/demo.mp4"))
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--seconds", type=float, default=4.0)
    args = parser.parse_args()
    render_demo_video(args.output, args.width, args.height, args.fps, args.seconds)


if __name__ == "__main__":
    main()
