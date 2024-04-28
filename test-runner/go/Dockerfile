FROM golang:1.22.2 AS builder

WORKDIR /app

COPY . .

RUN go build -o myapp

CMD ["go", "test", "./..."]
