



FROM python:3.10-slim

# Light-weight Nginx installation aur unwanted cache cleaning
RUN apt-get update && apt-get install -y nginx --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Strict Security: Non-privileged user banana taaki root exploit na ho sake
RUN useradd -u 1001 -m garud_user && chown -R garud_user:garud_user /app

# Files ko secure permissions ke sath copy karna
COPY --chown=garud_user:garud_user . .

# Dependencies installation bina root warning ke
RUN pip install --no-cache-dir flask pinecone gunicorn --quiet
RUN pip install --no-cache-dir flask pinecone gunicorn --quiet requests

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Container ko non-root user ke context me switch karna

# Daemon-off process execution matrix
CMD ["gunicorn", "--workers", "3", "--bind", "127.0.0.1:8080", "garud_web:app"]
