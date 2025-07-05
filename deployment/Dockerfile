FROM python:3.9-slim

RUN useradd -ms /bin/bash appuser
USER appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/usr/local/bin/python", "-m", "bankometer"]