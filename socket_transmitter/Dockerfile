FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && \
	apt-get install -y --no-install-recommends curl ca-certificates build-essential && \
	rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:${PATH}"

COPY . .
RUN uv sync --locked

ENV TSMT_PIN_NUMBER=11
ENV PORT_NUMBER=60000

EXPOSE ${PORT_NUMBER}
CMD ["sh", "-c", "uv run socket_transmitter.py --port_number ${PORT_NUMBER} --pin_number ${TSMT_PIN_NUMBER}"]
