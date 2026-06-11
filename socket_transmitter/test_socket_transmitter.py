import os
import sys
import types
import unittest
from unittest.mock import patch

fake_paho = types.ModuleType("paho")
fake_mqtt = types.ModuleType("paho.mqtt")
fake_client = types.ModuleType("paho.mqtt.client")
fake_client.CallbackAPIVersion = types.SimpleNamespace(VERSION2=2)
fake_client.Client = object
fake_client.ConnectFlags = object
fake_client.ReasonCode = object
fake_client.Properties = object
fake_client.MQTTMessage = object
fake_paho.mqtt = fake_mqtt
fake_mqtt.client = fake_client
sys.modules.setdefault("paho", fake_paho)
sys.modules.setdefault("paho.mqtt", fake_mqtt)
sys.modules.setdefault("paho.mqtt.client", fake_client)

fake_rpi = types.ModuleType("RPi")
fake_rpi.GPIO = types.SimpleNamespace(
    BOARD=11,
    OUT=1,
    setmode=lambda *args, **kwargs: None,
    setup=lambda *args, **kwargs: None,
    output=lambda *args, **kwargs: None,
    cleanup=lambda *args, **kwargs: None,
)
sys.modules.setdefault("RPi", fake_rpi)

import socket_transmitter as st


class SocketTransmitterTests(unittest.TestCase):
    def test_get_packet_valid(self) -> None:
        self.assertEqual(st.get_packet("1010:0.001:0.002"), ("1010", 0.001, 0.002))

    def test_get_packet_invalid(self) -> None:
        self.assertIsNone(st.get_packet("bad-packet"))

    def test_handle_packet_calls_transmitter(self) -> None:
        with patch.object(st, "transmit_rf_code") as mock_transmit:
            self.assertTrue(st.handle_packet("1010:0.001:0.002", 11))
            mock_transmit.assert_called_once_with("1010", 0.001, 0.002, 11)

    def test_handle_ha_switch_command_calls_transmitter(self) -> None:
        with patch.dict(os.environ, {"HA_TOPIC_PREFIX": "smart-rf-plug"}, clear=False):
            with patch.object(st, "transmit_rf_code") as mock_transmit:
                self.assertTrue(st.handle_ha_switch_command("smart-rf-plug/a/set", "ON", 13))
                mock_transmit.assert_called_once_with(st.A_ON, st.SHORT_DELAY, st.LONG_DELAY, 13)

    def test_handle_ha_switch_command_rejects_invalid_command(self) -> None:
        with patch.dict(os.environ, {"HA_TOPIC_PREFIX": "smart-rf-plug"}, clear=False):
            with patch.object(st, "transmit_rf_code") as mock_transmit:
                self.assertFalse(st.handle_ha_switch_command("smart-rf-plug/a/set", "UNKNOWN", 13))
                mock_transmit.assert_not_called()

    def test_get_mqtt_port_uses_default_for_invalid_value(self) -> None:
        with patch.dict(os.environ, {"MQTT_PORT": "invalid"}, clear=False):
            self.assertEqual(st.get_mqtt_port(), st.DEFAULT_MQTT_PORT)


if __name__ == "__main__":
    unittest.main()
