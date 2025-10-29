# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Render’s default port
EXPOSE 8000

# Start the app
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

