@echo off
REM Script to install MediaPipe with correct version for Windows

echo Installing MediaPipe 0.10.9...

REM Uninstall existing version if any
pip uninstall -y mediapipe

REM Install MediaPipe (latest 0.10.x version)
pip install "mediapipe>=0.10.30,<0.11.0"

REM Install protobuf with version constraint (separate command for Windows)
pip install "protobuf>=3.20.0,<5.0.0"

REM Verify installation
python -c "import mediapipe as mp; print('✅ MediaPipe version:', mp.__version__); print('✅ Solutions available:', hasattr(mp, 'solutions'))"

echo Done!
pause

