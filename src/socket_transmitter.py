"""
Simple Radio Transmitter Script to control RF Plugs
"""
import argparse
import logging
import socket

# Socket
import sys
import time

from RPi import GPIO

DEFAULT_IP_ADDRESS = "0.0.0.0"
DEFAULT_PORT_NUM = 60000

# RF transmission Variables
NUM_ATTEMPTS = 10
DEFAULT_TRANSMIT_PIN = 11
RETRY_TIME = 0.001  # s
log = logging.getLogger('Transmitter Logger')


parser = argparse.ArgumentParser(
    prog="RF Transmitter",
    description="TCP RF Transmitter program, that transmits the byte sent over tcp via RF",
    epilog="This could be of more help"
)
parser.add_argument("-p", "--port_number",default=DEFAULT_PORT_NUM, type=int, required=False, help="Port number")
parser.add_argument("-ip", "--ip_address",default= DEFAULT_IP_ADDRESS,type=str, required=False, help="IP address")
parser.add_argument("-pin", "--pin_number",default=DEFAULT_TRANSMIT_PIN, type=int, required=False, help="TF Transmitter Pin number")
args = parser.parse_args()


def main(ip_addr: str = DEFAULT_IP_ADDRESS, port_num:int = DEFAULT_PORT_NUM, transmit_pin:int = DEFAULT_TRANSMIT_PIN)-> None:
    """
    The main application of the program
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
                log.info("Listening on Port: {0} at {1}".format(port_num,ip_addr))
                log.info("Transmitting on Pin: {0}".format(transmit_pin))
                conn, _ = sock.accept()
                log.info("Accepted Connection")
                sock_file = conn.makefile()

                # Decode Message and perform selected operation
                while True:
                    message = sock_file.readline()
                    log.debug(message)
                    message = message.strip()
                    strings = message.split(':')
                    log.info("Decoding String")
                    log.info(message)
                    try:
                        transmit_rf_code(strings[0], float(strings[1]), float(strings[2]),transmit_pin)
                    except IndexError:
                        logging.error("Received malformed data packet, abandoning socket")
                        sock.shutdown(1)
                        sock.close()
                        break


        finally:
            sock.close()
            GPIO.cleanup()


def transmit_rf_code(code, short_delay, long_delay, trsmt_pin:int) -> None:
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
        log.debug("Attempt: %s", str(t))
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
                log.critical("Received invalid Code: %s", str(code))
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
    setup_logging()
    log.info("RF Smart Transmitter Booting")
    log.info("Arguments Received:\n {0}".format(args))
    main(args.ip_address, args.port_number, args.pin_number)
