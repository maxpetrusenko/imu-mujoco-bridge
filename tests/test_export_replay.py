import unittest

from imu_mujoco_bridge.export_replay import build_replay
from imu_mujoco_bridge.virtual_device import VirtualDeviceConfig


class ExportReplayTests(unittest.TestCase):
    def test_build_replay_uses_udp_flow_packets(self) -> None:
        frames = build_replay(VirtualDeviceConfig(rate_hz=10, packets=3, noise=0.0))
        self.assertEqual(len(frames), 3)
        self.assertEqual(frames[0]["timestampMs"], 0)
        self.assertEqual(frames[0]["calibration"], [0, 0, 0, 0])
        self.assertIn("csv", frames[0])


if __name__ == "__main__":
    unittest.main()

