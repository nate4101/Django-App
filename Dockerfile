# Use Python image
FROM python:3.11-slim

# Prevent .pyc files and enable better logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Run Django using Gunicorn
CMD gunicorn my_duck_project.wsgi:application --bind 0.0.0.0:8080