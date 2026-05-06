FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY vendor/pyasn1 /usr/local/lib/python3.12/site-packages/pyasn1
COPY vendor/pyasn1-0.6.3.dist-info /usr/local/lib/python3.12/site-packages/pyasn1-0.6.3.dist-info
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
