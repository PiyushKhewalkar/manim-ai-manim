#!/bin/bash

apt-get update && \
apt-get install -y ffmpeg libcairo2 xvfb

# Run FastAPI app with headless display
xvfb-run uvicorn main:app --host=0.0.0.0 --port=10000
