FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["/bin/bash", "-c", "source venv/bin/activate && python -m bot"]
