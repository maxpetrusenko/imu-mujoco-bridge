from __future__ import annotations

import socket
import threading
import time
import unittest

from imu_mujoco_bridge.udp import make_udp_socket, receive_packets_from_socket


class UdpTests(unittest.TestCase):
    def test_receive_one_packet_over_loopback(self) -> None:
        host = "127.0.0.1"
        sock = make_udp_socket(host, 0, timeout=1.0)
        port = sock.getsockname()[1]
        receiver = receive_packets_from_socket(sock)

        def send_packet() -> None:
            time.sleep(0.05)
            sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sender.sendto(b"1,0,0,0,3,3,3,3,42", (host, port))
            finally:
                sender.close()

        thread = threading.Thread(target=send_packet)
        thread.start()
        try:
            packet = next(receiver)
        finally:
            receiver.close()
            thread.join()

        self.assertEqual(packet.as_mujoco_qpos(), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(packet.calibration, (3, 3, 3, 3))
        self.assertEqual(packet.timestamp_ms, 42)


if __name__ == "__main__":
    unittest.main()
