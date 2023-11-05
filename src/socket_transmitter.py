"""
Simple Radio Transmitter Script to control RF Plugs
"""
import logging
import socket

# Socket
import sys
import time

from RPi import GPIO

IP_ADDRESS = "0.0.0.0"
PORT_NUM = 60000

# RF transmission Variables
NUM_ATTEMPTS = 10
TRANSMIT_PIN = 10
RETRY_TIME = 0.001  # s
log = logging.getLogger('Transmitter Logger')


def main():
    """
    The main application of the program
    """
    sock = None
    try:
        setup_logging()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(TRANSMIT_PIN, GPIO.OUT)

        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((IP_ADDRESS, PORT_NUM))
            sock.listen()
            log.info("Listening on Port 60000")
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
                    transmit_rf_code(strings[0], float(strings[1]), float(strings[2]))
                except IndexError:
                    logging.error("Received malformed data packet, abandoning socket")
                    sock.shutdown(1)
                    sock.close()
                    break


    finally:
        sock.close()
        GPIO.cleanup()


def transmit_rf_code(code, short_delay, long_delay):
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
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(short_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(long_delay)
            elif i == '0':
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(long_delay)
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(short_delay)
            else:
                log.critical("Received invalid Code: %s", str(code))
        GPIO.output(TRANSMIT_PIN, 0)
        time.sleep(RETRY_TIME)
    time.sleep(0.5)


def setup_logging():
    """
    Sets up the Logger object log for use throughout the script
    """
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    log.addHandler(ch)


if __name__ == '__main__':
    main()
