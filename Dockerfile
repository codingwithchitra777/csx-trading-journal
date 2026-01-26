# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY firebase/ ./firebase/
COPY main.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Cloud Run requires container to listen on port specified by PORT env var
# We'll use a simple HTTP server wrapper for health checks
EXPOSE 8080

# Start the bot
CMD exec python main.py

