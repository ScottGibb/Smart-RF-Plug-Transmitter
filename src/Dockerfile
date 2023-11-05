FROM debian:latest


RUN apt-get update -y
RUN apt-get install -y build-essential
RUN apt-get install python3-pip -y

COPY socket_transmitter.py /
COPY requirements.txt /

RUN pip3 install -r requirements.txt

ARG TSMT_PIN_NUMBER=10

EXPOSE 60000
ENTRYPOINT ["python3"]
CMD ["-u","socket_transmitter.py 0.0.0.0 60000 ${TSMT_PIN_NUMBER}"]
