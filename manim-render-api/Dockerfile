FROM python:3.10-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2 \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project
COPY . .

# Make sure start.sh is executable (if you use it)
RUN chmod +x manim-render-api/start.sh

# Command to run your FastAPI app
CMD ["xvfb-run", "uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
