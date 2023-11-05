FROM debian:latest


RUN apt-get update -y
RUN apt-get install -y build-essential
RUN apt-get install python3-pip -y

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-package

ENV TSMT_PIN_NUMBER=11
ENV PORT_NUMBER=60000
COPY *.py .

EXPOSE ${PORT_NUMBER}
CMD ["sh", "-c", "python3 socket_transmitter.py --port_number ${PORT_NUMBER} --pin_number ${TSMT_PIN_NUMBER}"]
