# Scraper Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
# Create a dummy README to satisfy pip install -e
RUN touch README.md
RUN pip install --no-cache-dir .

# Copy source code
COPY src/ ./src/

# Default command (runs the API server)
CMD ["python", "-m", "src.server"]
