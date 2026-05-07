FROM python:3.12-slim

RUN useradd --create-home --shell /bin/false runner && \
    mkdir -p /code && chown runner:runner /code

COPY run.py /usr/local/bin/run.py

USER runner
WORKDIR /code

ENTRYPOINT ["python", "/usr/local/bin/run.py"]
