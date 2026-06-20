import unittest

from imu_mujoco_bridge.virtual_device import (
    VirtualDeviceConfig,
    calibration_at,
    virtual_bno055_packets,
)


class VirtualDeviceTests(unittest.TestCase):
    def test_calibration_ramps_to_ready(self) -> None:
        self.assertEqual(calibration_at(0.0, 2.0), (0, 0, 0, 0))
        self.assertEqual(calibration_at(3.0, 2.0), (3, 3, 3, 3))

    def test_virtual_packets_include_realistic_metadata(self) -> None:
        packets = list(virtual_bno055_packets(VirtualDeviceConfig(packets=4, noise=0.0)))
        self.assertEqual(len(packets), 4)
        self.assertEqual(packets[0].calibration, (0, 0, 0, 0))
        self.assertIsNotNone(packets[-1].timestamp_ms)
        self.assertAlmostEqual(sum(value * value for value in packets[-1].as_mujoco_qpos()), 1.0)

    def test_seeded_noise_is_deterministic(self) -> None:
        config = VirtualDeviceConfig(packets=2, noise=0.01, seed=123)
        first = [packet.as_csv() for packet in virtual_bno055_packets(config)]
        second = [packet.as_csv() for packet in virtual_bno055_packets(config)]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

