FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/false runner \
    && mkdir -p /code && chown runner:runner /code

COPY run.py /usr/local/bin/run.py

USER runner
WORKDIR /code

ENTRYPOINT ["python3", "/usr/local/bin/run.py"]
