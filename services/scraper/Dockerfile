FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY services/scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and configuration
COPY services/scraper/src/config.toml ./
COPY services/scraper/src/ ./src/

# Run consumer
CMD ["python", "src/main.py"]
