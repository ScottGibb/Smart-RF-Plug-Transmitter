FROM raspbian/stretch

RUN apt-get update -y
RUN apt-get install -y build-essential
RUN apt-get install python3-pip -y

COPY socket_transmitter.py /
COPY requirements.txt /

RUN pip3 install -r requirements.txt

EXPOSE 60000
ENTRYPOINT ["python3"]
CMD ["-u","socket_transmitter.py"]
