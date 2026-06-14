# frontend/Dockerfile — image for the Vue dev server (Vite).
# Build context is ./frontend (see docker-compose.yml).
#
# Hot reload: docker-compose mounts the host ./frontend into the container and Vite runs
# in dev mode with polling, so editing a .vue file updates the browser live.

FROM node:20-alpine

WORKDIR /app

# Install deps first (cached layer — only re-runs when package.json changes).
COPY package*.json ./
RUN npm install

# Copy the rest of the source (overridden by the bind mount at runtime).
COPY . .

EXPOSE 5173
# --host 0.0.0.0 makes the dev server reachable from outside the container.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
