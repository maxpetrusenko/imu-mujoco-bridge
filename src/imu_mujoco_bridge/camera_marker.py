from __future__ import annotations

import argparse
import json
import math
import socket
from pathlib import Path

from .packet import QuaternionPacket


def rotation_matrix_to_quaternion(matrix: list[list[float]]) -> tuple[float, float, float, float]:
    m00, m01, m02 = matrix[0]
    m10, m11, m12 = matrix[1]
    m20, m21, m22 = matrix[2]
    trace = m00 + m11 + m22

    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2
        return (0.25 * s, (m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s)
    if m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        return ((m21 - m12) / s, 0.25 * s, (m01 + m10) / s, (m02 + m20) / s)
    if m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        return ((m02 - m20) / s, (m01 + m10) / s, 0.25 * s, (m12 + m21) / s)

    s = math.sqrt(1.0 + m22 - m00 - m11) * 2
    return ((m10 - m01) / s, (m02 + m20) / s, (m12 + m21) / s, 0.25 * s)


def load_json_vector(value: str) -> list[float]:
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("expected JSON list")
    return [float(item) for item in parsed]


def make_camera_matrix(width: int, height: int, focal_px: float | None = None) -> list[list[float]]:
    focal = focal_px or float(width)
    return [[focal, 0.0, width / 2.0], [0.0, focal, height / 2.0], [0.0, 0.0, 1.0]]


def send_marker_camera_packets(
    camera_index: int,
    host: str,
    port: int,
    marker_length_m: float,
    marker_id: int | None,
    focal_px: float | None,
    max_packets: int | None,
    show: bool,
) -> int:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise SystemExit("Install camera support first: python -m pip install '.[camera]'") from exc

    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    detector = aruco.ArucoDetector(dictionary, aruco.DetectorParameters())
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise SystemExit(f"Could not open camera index {camera_index}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = 0
    try:
        while max_packets is None or sent < max_packets:
            ok, frame = capture.read()
            if not ok:
                continue

            height, width = frame.shape[:2]
            corners, ids, _rejected = detector.detectMarkers(frame)
            if ids is None:
                if show:
                    cv2.imshow("imu-camera-marker", frame)
                    if cv2.waitKey(1) == 27:
                        break
                continue

            camera_matrix = np.array(make_camera_matrix(width, height, focal_px), dtype=np.float64)
            dist_coeffs = np.zeros((5, 1), dtype=np.float64)
            object_points = np.array(
                [
                    [-marker_length_m / 2, marker_length_m / 2, 0],
                    [marker_length_m / 2, marker_length_m / 2, 0],
                    [marker_length_m / 2, -marker_length_m / 2, 0],
                    [-marker_length_m / 2, -marker_length_m / 2, 0],
                ],
                dtype=np.float64,
            )

            for marker_corners, detected_id in zip(corners, ids.flatten(), strict=False):
                if marker_id is not None and int(detected_id) != marker_id:
                    continue
                image_points = marker_corners.reshape((4, 2)).astype(np.float64)
                success, rvec, _tvec = cv2.solvePnP(
                    object_points,
                    image_points,
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE,
                )
                if not success:
                    continue
                rotation, _jacobian = cv2.Rodrigues(rvec)
                q = rotation_matrix_to_quaternion(rotation.tolist())
                packet = QuaternionPacket(*q, calibration=(3, 3, 3, 3)).normalized()
                sock.sendto(packet.as_csv().encode("utf-8"), (host, port))
                sent += 1
                if show:
                    aruco.drawDetectedMarkers(frame, corners, ids)
                break

            if show:
                cv2.imshow("imu-camera-marker", frame)
                if cv2.waitKey(1) == 27:
                    break
    finally:
        sock.close()
        capture.release()
        if show:
            cv2.destroyAllWindows()
    return sent


def write_marker(output: Path, marker_id: int, size_px: int) -> None:
    try:
        import cv2
    except ImportError as exc:
        raise SystemExit("Install camera support first: python -m pip install '.[camera]'") from exc

    marker = cv2.aruco.generateImageMarker(
        cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),
        marker_id,
        size_px,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), marker)


def main() -> None:
    parser = argparse.ArgumentParser(description="Use a webcam ArUco marker as the pose source.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--marker-length-m", type=float, default=0.08)
    parser.add_argument("--marker-id", type=int)
    parser.add_argument("--focal-px", type=float)
    parser.add_argument("--max-packets", type=int)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--make-marker", type=Path)
    parser.add_argument("--marker-size-px", type=int, default=800)
    args = parser.parse_args()

    if args.make_marker:
        write_marker(args.make_marker, args.marker_id or 0, args.marker_size_px)
        return

    send_marker_camera_packets(
        camera_index=args.camera_index,
        host=args.host,
        port=args.port,
        marker_length_m=args.marker_length_m,
        marker_id=args.marker_id,
        focal_px=args.focal_px,
        max_packets=args.max_packets,
        show=args.show,
    )


if __name__ == "__main__":
    main()

