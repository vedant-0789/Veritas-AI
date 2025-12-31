#!/bin/bash
# Script to install MediaPipe with correct version

echo "Installing MediaPipe 0.10.30+..."

# Uninstall existing version if any
pip uninstall -y mediapipe

# Install latest 0.10.x version
pip install "mediapipe>=0.10.30,<0.11.0"

# Verify installation
python -c "import mediapipe as mp; print('✅ MediaPipe version:', mp.__version__); print('✅ Solutions available:', hasattr(mp, 'solutions'))"

echo "Done!"

