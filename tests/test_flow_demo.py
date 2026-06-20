import unittest

from imu_mujoco_bridge.flow_demo import collect_udp_flow_packets
from imu_mujoco_bridge.virtual_device import VirtualDeviceConfig


class FlowDemoTests(unittest.TestCase):
    def test_collects_packets_through_udp_loop(self) -> None:
        packets = collect_udp_flow_packets(VirtualDeviceConfig(packets=5, noise=0.0))
        self.assertEqual(len(packets), 5)
        self.assertEqual(packets[0].calibration, (0, 0, 0, 0))
        self.assertEqual(packets[-1].timestamp_ms, 66)


if __name__ == "__main__":
    unittest.main()

