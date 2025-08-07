# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Copy application code
COPY calibration-service /app/calibration-service
COPY calibration-service/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY common_packages /app/common_packages

# Set Python path to include common packages
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/common_packages"

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# Run the application
CMD ["python", "calibration-service/calibration_app.py"]

