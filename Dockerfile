# --- STAGE 1: Build Frontend ---
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# We set this to empty for relative API calls on the same host
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

# --- STAGE 2: Build/Run Backend ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
# Copy the built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Set environment variables
ENV MOCK_SERVICES=false
ENV PORT=8002

# Expose the single port
EXPOSE 8002

# Run the unified server
CMD ["python", "backend/main.py"]
