"""
Simple Radio Transmitter Script to control RF Plugs
"""
import argparse
import json
import logging
import os
import socket

# Socket
import sys
import time

import paho.mqtt.client as mqtt
try:
    from RPi import GPIO
except ModuleNotFoundError:  # pragma: no cover - allows non-RPi development/testing
    class _MockGPIO:
        BOARD = 11
        OUT = 1

        @staticmethod
        def setmode(_mode: int) -> None:
            return

        @staticmethod
        def setup(_pin: int, _mode: int) -> None:
            return

        @staticmethod
        def output(_pin: int, _value: int) -> None:
            return

        @staticmethod
        def cleanup() -> None:
            return

    GPIO = _MockGPIO()

from plug_codes.easy_on_easy_off_plugs import (
    A_OFF,
    A_ON,
    B_OFF,
    B_ON,
    C_OFF,
    C_ON,
    D_OFF,
    D_ON,
    LONG_DELAY,
    SHORT_DELAY,
)

DEFAULT_IP_ADDRESS = "0.0.0.0"
DEFAULT_PORT_NUM = 60000
DEFAULT_TRANSPORT = "tcp"
DEFAULT_MQTT_HOST = "localhost"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_COMMAND_TOPIC = "smart-rf-plug/command"
DEFAULT_HA_DISCOVERY_PREFIX = "homeassistant"
DEFAULT_HA_TOPIC_PREFIX = "smart-rf-plug"
DEFAULT_HA_DEVICE_ID = "smart_rf_plug_transmitter"

# RF transmission Variables
NUM_ATTEMPTS = 10
DEFAULT_TRANSMIT_PIN = 11
RETRY_TIME = 0.001  # s
log = logging.getLogger('Transmitter Logger')
HA_COMMAND_CODES = {
    "A": {"ON": A_ON, "OFF": A_OFF},
    "B": {"ON": B_ON, "OFF": B_OFF},
    "C": {"ON": C_ON, "OFF": C_OFF},
    "D": {"ON": D_ON, "OFF": D_OFF},
}


def get_transport() -> str:
    """
    Get transport mode from environment.
    """
    return os.getenv("RF_TRANSPORT", DEFAULT_TRANSPORT).strip().lower()


def get_mqtt_host() -> str:
    """
    Get mqtt host from environment.
    """
    return os.getenv("MQTT_HOST", DEFAULT_MQTT_HOST).strip()


def get_mqtt_port() -> int:
    """
    Get mqtt port from environment.
    """
    return int(os.getenv("MQTT_PORT", str(DEFAULT_MQTT_PORT)).strip())


def get_mqtt_command_topic() -> str:
    """
    Get mqtt command topic from environment.
    """
    return os.getenv("MQTT_COMMAND_TOPIC", DEFAULT_MQTT_COMMAND_TOPIC).strip()


def get_ha_discovery_prefix() -> str:
    """
    Get home assistant discovery prefix from environment.
    """
    return os.getenv("HA_DISCOVERY_PREFIX", DEFAULT_HA_DISCOVERY_PREFIX).strip()


def get_ha_topic_prefix() -> str:
    """
    Get home assistant topic prefix from environment.
    """
    return os.getenv("HA_TOPIC_PREFIX", DEFAULT_HA_TOPIC_PREFIX).strip()


def get_ha_device_id() -> str:
    """
    Get home assistant device id from environment.
    """
    return os.getenv("HA_DEVICE_ID", DEFAULT_HA_DEVICE_ID).strip()


def get_packet(packet: str) -> tuple[str, float, float] | None:
    """
    Parse and validate code packet.
    """
    strings = packet.strip().split(':')
    try:
        return strings[0], float(strings[1]), float(strings[2])
    except (IndexError, ValueError):
        return None


def handle_packet(packet: str, transmit_pin: int) -> bool:
    """
    Handle and transmit packet.
    """
    message = get_packet(packet)
    if message is None:
        return False
    transmit_rf_code(message[0], message[1], message[2], transmit_pin)
    return True


def handle_ha_switch_command(topic: str, payload: str, transmit_pin: int) -> bool:
    """
    Handle Home Assistant switch commands.
    """
    topic_prefix = get_ha_topic_prefix().strip("/")
    message = payload.strip().upper()
    if not topic.startswith(f"{topic_prefix}/") or not topic.endswith("/set"):
        return False
    topic_parts = topic.split("/")
    if len(topic_parts) != 3:
        return False
    switch_name = topic_parts[1].upper()
    if switch_name not in HA_COMMAND_CODES or message not in HA_COMMAND_CODES[switch_name]:
        return False
    transmit_rf_code(HA_COMMAND_CODES[switch_name][message], SHORT_DELAY, LONG_DELAY, transmit_pin)
    return True


def publish_ha_discovery(client: mqtt.Client) -> None:
    """
    Publish Home Assistant auto discovery.
    """
    discovery_prefix = get_ha_discovery_prefix().strip("/")
    topic_prefix = get_ha_topic_prefix().strip("/")
    device_id = get_ha_device_id()
    for switch_name in HA_COMMAND_CODES:
        discovery_topic = f"{discovery_prefix}/switch/{device_id}_{switch_name.lower()}/config"
        discovery_payload = json.dumps(
            {
                "name": f"RF Plug {switch_name}",
                "uniq_id": f"{device_id}_{switch_name.lower()}",
                "command_topic": f"{topic_prefix}/{switch_name.lower()}/set",
                "payload_on": "ON",
                "payload_off": "OFF",
                "device": {
                    "identifiers": [device_id],
                    "name": "Smart RF Plug Transmitter",
                    "manufacturer": "ScottGibb",
                },
            }
        )
        client.publish(discovery_topic, discovery_payload, retain=True)
        log.info(f"Published Home Assistant discovery for RF Plug {switch_name}")


def run_tcp_listener(ip_addr: str, port_num: int, transmit_pin: int) -> None:
    """
    Run tcp listener for RF packets.
    """
    while True:
        sock = None
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(transmit_pin, GPIO.OUT)

            while True:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((ip_addr, port_num))
                sock.listen()
                log.info(f"Listening on Port: {port_num} at {ip_addr}")
                log.info(f"Transmitting on Pin: {transmit_pin}")
                conn, _ = sock.accept()
                log.info("Accepted Connection")
                sock_file = conn.makefile()

                # Decode Message and perform selected operation
                while True:
                    message = sock_file.readline()
                    if not message:
                        break
                    log.debug(message)
                    log.info("Decoding String")
                    if not handle_packet(message, transmit_pin):
                        logging.error("Received malformed data packet, abandoning socket")
                        sock.shutdown(1)
                        sock.close()
                        break

        finally:
            if sock is not None:
                sock.close()
            GPIO.cleanup()


def run_mqtt_listener(transmit_pin: int) -> None:
    """
    Run mqtt listener for RF packets and HA commands.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(transmit_pin, GPIO.OUT)
    host = get_mqtt_host()
    port = get_mqtt_port()
    command_topic = get_mqtt_command_topic()
    ha_topic_prefix = get_ha_topic_prefix().strip("/")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    if username:
        client.username_pw_set(username, password)

    def on_connect(
        mqtt_client: mqtt.Client,
        _userdata: object,
        _flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: mqtt.Properties | None,
    ) -> None:
        if reason_code.is_failure:
            log.error(f"MQTT connection failed: {reason_code}")
            return
        log.info(f"Connected to MQTT broker {host}:{port}")
        mqtt_client.subscribe(command_topic)
        mqtt_client.subscribe(f"{ha_topic_prefix}/+/set")
        log.info(f"Subscribed to MQTT command topics: {command_topic}, {ha_topic_prefix}/+/set")
        publish_ha_discovery(mqtt_client)

    def on_message(
        _mqtt_client: mqtt.Client,
        _userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        payload = message.payload.decode("utf-8").strip()
        log.info(f"Received MQTT message on topic {message.topic}")
        if handle_ha_switch_command(message.topic, payload, transmit_pin):
            return
        if not handle_packet(payload, transmit_pin):
            log.error("Received malformed MQTT packet")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port)
    client.loop_forever()


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return CLI parser.
    """
    parser = argparse.ArgumentParser(
        prog="RF Transmitter",
        description="RF transmitter that receives commands over TCP or MQTT",
        epilog="This could be of more help"
    )
    parser.add_argument("-p", "--port_number", default=DEFAULT_PORT_NUM, type=int, help="Port number")
    parser.add_argument("-ip", "--ip_address", default=DEFAULT_IP_ADDRESS, type=str, help="IP address")
    parser.add_argument("-pin", "--pin_number", default=DEFAULT_TRANSMIT_PIN, type=int, help="RF Transmitter Pin number")
    parser.add_argument(
        "-t",
        "--transport",
        default=None,
        choices=["tcp", "mqtt"],
        help="Transport to use. Defaults to RF_TRANSPORT environment variable.",
    )
    return parser


def main(
    ip_addr: str = DEFAULT_IP_ADDRESS,
    port_num: int = DEFAULT_PORT_NUM,
    transmit_pin: int = DEFAULT_TRANSMIT_PIN,
    transport: str | None = None,
) -> None:
    """
    The main application of the program
    """
    selected_transport = (transport or get_transport()).strip().lower()
    log.info(f"Using transport: {selected_transport}")
    if selected_transport == "mqtt":
        run_mqtt_listener(transmit_pin)
        return
    run_tcp_listener(ip_addr, port_num, transmit_pin)


def transmit_rf_code(code: str, short_delay: float, long_delay: float, trsmt_pin: int) -> None:
    """
    Using the parameters and the GPIO pin associated with TRANSMIT_PIN the GPIO pin is turned on and off representing
    the signal to be transmitted using the RF Module
    :param code: The str object containing the bit sequence to be transmitted using the RF module
    :param short_delay: the delay in seconds of the long pulse
    :param long_delay: the delay in seconds of the short pulse
    :param logging: the log object
    """
    log.info("Transmitting")
    for t in range(NUM_ATTEMPTS):
        log.debug(f"Attempt: {t}")
        for i in code:
            if i == '1':
                GPIO.output(trsmt_pin, 1)
                time.sleep(short_delay)
                GPIO.output(trsmt_pin, 0)
                time.sleep(long_delay)
            elif i == '0':
                GPIO.output(trsmt_pin, 1)
                time.sleep(long_delay)
                GPIO.output(trsmt_pin, 0)
                time.sleep(short_delay)
            else:
                log.critical(("Received invalid Code: %s", str(code)))
        GPIO.output(trsmt_pin, 0)
        time.sleep(RETRY_TIME)
    time.sleep(0.5)


def setup_logging() -> None:
    """
    Sets up the Logger object log for use throughout the script
    """
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    log.addHandler(ch)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    setup_logging()
    log.info("RF Smart Transmitter Booting")
    log.info(f"Arguments Received:\n ,{args}")
    main(args.ip_address, args.port_number, args.pin_number, args.transport)
