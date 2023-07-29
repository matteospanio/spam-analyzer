FROM python:3.10.6-slim-buster

LABEL maintainer="Matteo Spanio"

ENV TERM xterm

WORKDIR /app

COPY . /app

RUN apt update && apt install -y nano

RUN pip install /app --no-cache-dir

ENTRYPOINT ["spam-analyzer"]

CMD ["--help"]