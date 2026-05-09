FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create cache directory for models
RUN mkdir -p ~/.u2net

# Expose port
EXPOSE 7860

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]