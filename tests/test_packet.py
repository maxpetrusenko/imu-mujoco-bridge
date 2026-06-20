import unittest

from imu_mujoco_bridge.demo import packet_to_json, simulated_packets
from imu_mujoco_bridge.packet import parse_packet


class PacketTests(unittest.TestCase):
    def test_parse_csv_minimal(self) -> None:
        packet = parse_packet("1,0,0,0")
        self.assertEqual(packet.as_mujoco_qpos(), (1.0, 0.0, 0.0, 0.0))

    def test_parse_csv_with_calibration_and_timestamp(self) -> None:
        packet = parse_packet("2,0,0,0,3,3,2,1,123")
        self.assertEqual(packet.as_mujoco_qpos(), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(packet.calibration, (3, 3, 2, 1))
        self.assertEqual(packet.timestamp_ms, 123)

    def test_parse_json(self) -> None:
        packet = parse_packet('{"qw":1,"qx":0,"qy":0,"qz":0,"t_ms":7}')
        self.assertEqual(packet.as_mujoco_qpos(), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(packet.timestamp_ms, 7)

    def test_simulated_packet_json_roundtrip(self) -> None:
        packet = next(simulated_packets(rate_hz=1000))
        parsed = parse_packet(packet_to_json(packet))
        self.assertAlmostEqual(parsed.as_mujoco_qpos()[0], packet.as_mujoco_qpos()[0])

    def test_reject_zero_quaternion(self) -> None:
        packet = parse_packet("0,0,0,0")
        with self.assertRaises(ValueError):
            packet.as_mujoco_qpos()


if __name__ == "__main__":
    unittest.main()

