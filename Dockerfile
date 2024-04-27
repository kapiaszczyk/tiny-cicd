FROM python:3.9-alpine

WORKDIR /app

ENV DEPLOYMENTS_DIR=/app/deployments

COPY requirements.txt .

RUN apk update && \
    apk add --no-cache git openssh-client && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5050

CMD ["python", "tiny_cicd.py"]