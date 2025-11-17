# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for database
RUN mkdir -p instance

# Expose port 5000
EXPOSE 5000

# Initialize database and run the application
CMD ["sh", "-c", "flask --app app init-db && gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app"]

