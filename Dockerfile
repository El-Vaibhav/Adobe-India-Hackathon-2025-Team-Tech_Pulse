# Use Python slim base image with amd64 compatibility
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy everything into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point to run main.py
CMD ["python", "main.py"]
