FROM python:3.9 as compile-image
COPY requirements.txt .
RUN apt-get update && \
    apt-get install python3-pip -y && \
    pip install --target=/app/dependencies -r requirements.txt && \
    rm -rf requirements.txt static Dockerfile
WORKDIR /app
COPY . .
ENTRYPOINT [ "python3", "app.py" ]

FROM python:alpine3.14
WORKDIR /app
COPY --from=compile-image /app .
ENV PYTHONPATH="${PYTHONPATH}:/app/dependencies"
ENTRYPOINT [ "python3", "app.py" ]