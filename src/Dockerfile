FROM debian:latest


RUN apt-get update -y
RUN apt-get install -y build-essential
RUN apt-get install python3-pip -y
COPY requirements.txt /
RUN pip3 install -r requirements.txt --break-system-package

ARG TSMT_PIN_NUMBER=11
COPY *.py /

EXPOSE 60000
CMD ["/bin/sh", "-c","python3 socket_transmitter.py", "0.0.0.0", "60000", "${TSMT_PIN_NUMBER}"]
