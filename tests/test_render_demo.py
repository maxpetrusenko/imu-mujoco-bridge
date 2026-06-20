import unittest

from imu_mujoco_bridge.demo import simulated_packet_at
from imu_mujoco_bridge.render_demo import project, render_frame, rotate_point


class RenderDemoTests(unittest.TestCase):
    def test_identity_rotation_keeps_x_axis(self) -> None:
        packet = simulated_packet_at(0.0)
        x, y, z = rotate_point((1.0, 0.0, 0.0), packet)
        self.assertAlmostEqual(x, 1.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)

    def test_projection_stays_inside_frame_for_origin(self) -> None:
        x, y = project((0.0, 0.0, 0.0), width=960, height=540)
        self.assertGreater(x, 0)
        self.assertLess(x, 960)
        self.assertGreater(y, 0)
        self.assertLess(y, 540)

    def test_render_frame_outputs_ppm(self) -> None:
        frame = render_frame(simulated_packet_at(0.5), width=160, height=90)
        self.assertTrue(frame.startswith(b"P6\n160 90\n255\n"))
        self.assertGreater(len(frame), 160 * 90 * 3)


if __name__ == "__main__":
    unittest.main()

