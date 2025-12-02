FROM ghcr.io/astral-sh/uv:alpine3.22

WORKDIR /app

COPY socket_transmitter .
RUN uv sync --locked

ENV TSMT_PIN_NUMBER=11
ENV PORT_NUMBER=60000

EXPOSE ${PORT_NUMBER}
CMD ["uv", "run", "socket_transmitter.py --port_number ${PORT_NUMBER} --pin_number ${TSMT_PIN_NUMBER}"]
