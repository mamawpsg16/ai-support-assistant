# backend/Dockerfile — image for the FastAPI API.
# Build context is the REPO ROOT (see docker-compose.yml), so paths are backend/...
#
# Hot reload: the entrypoint runs `uvicorn --reload`, and docker-compose mounts the host
# ./backend folder into the container, so editing a .py file restarts the server.

FROM python:3.12-slim

# PYTHONUNBUFFERED: logs appear immediately. PYTHONPATH: makes `backend` importable.
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install Python deps first (cached layer — only re-runs when requirements change).
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the backend package.
COPY backend /app/backend

# Put the entrypoint OUTSIDE the /app/backend bind-mount path so it stays executable
# even when docker-compose mounts the host source over /app/backend.
COPY backend/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
