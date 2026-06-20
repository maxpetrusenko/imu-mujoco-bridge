import math
import unittest

from imu_mujoco_bridge.camera_marker import make_camera_matrix, rotation_matrix_to_quaternion


class CameraMarkerTests(unittest.TestCase):
    def test_rotation_matrix_to_quaternion_identity(self) -> None:
        q = rotation_matrix_to_quaternion(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        )
        self.assertEqual(q, (1.0, 0.0, 0.0, 0.0))

    def test_rotation_matrix_to_quaternion_z_90(self) -> None:
        q = rotation_matrix_to_quaternion(
            [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
        )
        self.assertAlmostEqual(q[0], math.sqrt(0.5))
        self.assertAlmostEqual(q[3], math.sqrt(0.5))

    def test_default_camera_matrix_uses_frame_center(self) -> None:
        matrix = make_camera_matrix(width=1280, height=720)
        self.assertEqual(matrix[0][2], 640)
        self.assertEqual(matrix[1][2], 360)


if __name__ == "__main__":
    unittest.main()

