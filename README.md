# Rehab Movement Assessment

Computer-vision rehabilitation assistant for real-time movement range assessment with posture guidance.

## Features

- Modern Streamlit UI with sidebar navigation: Home, Start Exercise, Instructions
- Real-time pose tracking using MediaPipe
- Exercise support:
	- Elbow Flexion
	- Squat
	- Shoulder Raise
- Live metrics:
	- Joint Angle
	- ROM (range of motion)
	- Rep Count
	- Posture Status (Correct/Incorrect)
	- Corrective hint text
- Threaded camera pipeline for smoother continuous display on larger screens

## Project Structure (Key Modules)

- `pose/pose.py`: MediaPipe pose integration and landmark extraction
- `angle/angle.py`: Generic and backward-compatible angle calculation utilities
- `movement/exercises.py`: Exercise thresholds and posture configuration
- `movement/evaluator.py`: Posture evaluation, ROM update, and repetition counting
- `ui/streamlit_app.py`: Streamlit app, navigation, camera runtime worker
- `ui/ui.py`: Frame overlay rendering

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run ui/streamlit_app.py
```

4. Optional: run tests

```bash
python -m unittest discover -s tests -v
```

## Recommended Runtime on This Machine

For stable MediaPipe Pose support, use Python 3.11 environment:

```bash
..\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py --server.port 8503
```

## Notes for Users

- Keep full body side landmarks visible during exercise.
- Use a stable camera position and good front lighting.
- If detection drops, step back slightly and avoid cluttered backgrounds.
