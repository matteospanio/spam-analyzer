FROM python:3.10.6-slim-buster

WORKDIR /app

COPY . /app

RUN pip install /app --no-cache-dir

ENTRYPOINT ["spam-analyzer"]

CMD ["--help"]