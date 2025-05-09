#!/bin/bash

# Install necessary dependencies
apt-get update && \
apt-get install -y ffmpeg libcairo2 xvfb

# Run FastAPI app with headless display (make sure to specify the correct location of main.py)
xvfb-run uvicorn manim-render-api.main:app --host 0.0.0.0 --port 8000
