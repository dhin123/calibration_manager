# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY tag-service /app/tag-service
COPY tag-service/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY common_packages /app/common_packages


# Set Python path to include common packages
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/common_packages"

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5002/health || exit 1

# Run the application
CMD ["python", "tag-service/tag_app.py"]
