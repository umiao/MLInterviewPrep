# Backend Dockerfile for MLE Interview Prep
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ src/

# Create data directory for SQLite volume mount
RUN mkdir -p /app/data

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
