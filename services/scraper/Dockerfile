FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and configuration
COPY src/config.toml ./
COPY src/ ./src/

# Run consumer
# CMD ["python", "src/main.py"]
CMD ["tail", "-f", "/dev/null"]

