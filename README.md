# Rehabilitation Movement Range Assessment (Computer Vision)

This project is a real-time rehabilitation assistant that uses a webcam and computer vision to evaluate movement quality and range of motion (ROM).

It is designed so a therapist, student, or developer can monitor exercise posture with immediate on-screen feedback.

## 1. Project Overview

### What this project does

The system captures live camera frames, detects body landmarks, computes joint angles, tracks ROM, and gives feedback for selected rehabilitation exercises.

### Real-world use case (rehabilitation therapy)

In rehabilitation, patients are often asked to perform repeated movements (for example elbow flexion or squats) while maintaining proper posture and sufficient movement range.

This project helps by:

- Providing instant visual feedback while the user is exercising
- Showing measurable values (angle, ROM, repetition count)
- Highlighting whether current posture is correct or incorrect
- Giving a simple corrective hint in plain language

### End-to-end pipeline

Video Input -> Pose Detection -> Angle Calculation -> ROM Tracking -> Feedback

Detailed meaning:

- Video Input: Webcam provides frame-by-frame video
- Pose Detection: MediaPipe detects key body landmarks (shoulder, elbow, hip, knee, ankle, etc.)
- Angle Calculation: Joint angle is computed from three landmark points
- ROM Tracking: Minimum and maximum observed angles are tracked to compute ROM
- Feedback: Status, ROM quality, and corrective hints are displayed in UI

## 2. Current Project Status

### Implemented and working

- Streamlit application with navigation pages:
	- Home
	- Start Exercise
	- Instructions
- Live camera runtime with a threaded worker
- Pose detection using MediaPipe Pose (when backend is available)
- Joint angle computation using geometric angle function
- ROM tracking over time (min/max angle based)
- Repetition counting using phase transitions (low angle <-> high angle)
- Exercise-specific evaluation for:
	- Elbow Flexion
	- Squat
	- Shoulder Raise
- On-frame and panel feedback:
	- Angle
	- ROM
	- Repetitions
	- Correct/Incorrect status
	- ROM quality message
	- Hint text
- Basic automated tests for core exercise logic and imports

### Partially implemented / legacy paths

- A separate OpenCV window runner exists in main.py (legacy path) and is simpler than the Streamlit flow
- feedback/feedback.py provides generic ROM text bands, while the main Streamlit flow uses evaluator-based feedback logic
- Wrapper modules (for example pose_module.py, angle_module.py, analysis_module.py, visualization_module.py) exist mainly for backward compatibility
- config/ folder exists but is currently empty

## 3. Project Structure

Top-level project tree:

```text
rehab_project/
	main.py
	README.md
	requirements.txt
	angle/
	config/
	feedback/
	movement/
	pose/
	tests/
	ui/
```

### Module-by-module explanation

- main.py
	- Legacy OpenCV loop runner (camera + pose + angle + simple feedback)
	- Useful for quick debugging without Streamlit

- pose/pose.py
	- Core pose detector class (PoseDetector)
	- Handles MediaPipe initialization, landmark extraction, visibility filtering, and safe recovery

- pose/pose_module.py
	- Re-export wrapper for PoseDetector (compatibility import path)

- angle/angle.py
	- calculate_joint_angle(point_a, point_b, point_c): generic angle utility
	- calculate_angle(coords): backward-compatible helper for right elbow keys

- angle/angle_module.py
	- Re-export wrapper for angle functions

- movement/analysis.py
	- MovementAnalyzer class for min/max angle tracking and ROM computation

- movement/evaluator.py
	- ExerciseEvaluator class that combines:
		- Angle calculation
		- ROM tracking
		- Rep counting
		- Status and hint generation
	- ExerciseMetrics dataclass for structured results

- movement/exercises.py
	- ExerciseConfig dataclass
	- Static configurations and thresholds for each exercise

- movement/analysis_module.py
	- Re-export wrapper for movement classes/configs

- feedback/feedback.py
	- Legacy generic feedback based on ROM bands

- ui/streamlit_app.py
	- Main app entry point for day-to-day use
	- Includes navigation pages, camera worker lifecycle, and live metric rendering

- ui/ui.py
	- OpenCV frame overlay drawing utilities

- ui/visualization_module.py
	- Re-export wrapper for UI overlay utilities

- tests/test_pose.py
	- Unit tests for angle helper compatibility and feedback bands

- tests/test_exercise_logic.py
	- Unit tests for evaluator status, ROM feedback progression, and repetition counting

- tests/test_camera.py
	- Basic test to ensure OpenCV camera interface exists

- config/
	- Reserved for future external configuration files (currently empty)

## 4. Setup Instructions

Follow these steps exactly from a terminal.

### Step 1: Clone repository

```bash
git clone <repository-url>
cd <repository-folder>/rehab_project
```

### Step 2: Create virtual environment

On Windows (PowerShell):

```powershell
python -m venv .venv
```

On macOS/Linux:

```bash
python3 -m venv .venv
```

### Step 3: Activate virtual environment

On Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows (CMD):

```bat
.venv\Scripts\activate.bat
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Streamlit app

```bash
streamlit run ui/streamlit_app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

### Step 6 (optional): Run tests

```bash
python -m unittest discover -s tests -v
```

### Recommended Python version

Use Python 3.11 for best MediaPipe Pose compatibility in this project.

## 5. How the System Works (Technical Flow)

### 1) Video frame capture

- CameraWorker opens webcam with OpenCV VideoCapture
- Frames are read continuously in a worker thread
- Frame size and buffer settings are tuned for stable live display

### 2) Pose detection with MediaPipe

- Each selected frame is passed to PoseDetector.get_pose()
- Frame is converted from BGR to RGB
- MediaPipe Pose predicts landmark locations
- Landmarks with low visibility are filtered out
- Named coordinate dictionary is built (for example right_shoulder, right_elbow, right_wrist)

### 3) Angle calculation

- For the active exercise, three landmark names (triplet) are read from ExerciseConfig
- The angle at the middle joint is computed with calculate_joint_angle

### 4) ROM computation

- MovementAnalyzer tracks min_angle and max_angle observed so far
- ROM is computed as:

```text
ROM = max_angle - min_angle
```

### 5) Feedback and rep counting

- ExerciseEvaluator compares current angle with target ranges
- Status is set to Correct or Incorrect
- Hint text is generated (too low / too high / good posture)
- ROM quality is categorized (incomplete / try more / good)
- Repetitions are counted by low-to-high phase transitions

### 6) UI update

- Processed frame is rendered with overlay text
- Streamlit page displays:
	- Live camera image
	- Angle, ROM, reps
	- Status, ROM feedback, hint

## 6. Features Implemented

- Live pose detection from webcam
- Exercise-specific angle measurement
- Continuous ROM tracking
- Real-time feedback and posture hinting
- Repetition counting
- Streamlit UI with page navigation
- Start/Stop detection controls
- On-frame overlay visualization
- Basic unit tests for core logic

## 7. How to Use the Application

### For end users (patient / trainer / demo user)

1. Start the app using Streamlit command.
2. Open the app in browser.
3. Go to Start Exercise page.
4. Select one exercise from sidebar.
5. Click Start Detection.
6. Stand around 1.5 to 2 meters from camera.
7. Keep your full right side visible (shoulder to ankle).
8. Perform movement slowly and smoothly.
9. Watch Angle, ROM, Reps, Status, and Hint values.
10. Click Stop Detection when done.

### Positioning tips

- Use good front lighting
- Keep camera stable
- Avoid cluttered background
- Keep full body segment for selected exercise inside frame

## 8. Known Issues / Limitations

- Accuracy depends on camera quality, lighting, occlusion, and user orientation
- Current exercise definitions are right-side dominant (right-side landmarks)
- No patient profile, history storage, or progress database yet
- No therapist dashboard or report export yet
- Camera access can fail due to OS permissions or occupied device
- MediaPipe backend behavior can vary across Python versions
- test_camera.py only verifies OpenCV interface availability, not actual hardware capture quality
- main.py and feedback/feedback.py represent a legacy path that may diverge from Streamlit logic over time

## 9. Future Work / TODO

- Add more rehabilitation exercise templates and per-exercise calibration
- Support left-side and mirrored movement analysis
- Add patient session logging and ROM progress charts
- Add result export (CSV/PDF) for therapist review
- Improve UI clarity (exercise demo media, onboarding prompts, progress widgets)
- Improve robustness for partial occlusion and different camera angles
- Add performance optimizations for lower-end devices
- Expand automated tests (integration tests, camera mock tests, UI tests)
- Move hardcoded thresholds to configurable external files under config/
- Add clinical safety guardrails and validation protocol documentation

## 10. Developer Guidelines

Follow these rules when contributing:

- Maintain the current module boundaries (pose, angle, movement, ui)
- Keep business logic in movement/ and pose/, not mixed into UI callbacks
- Reuse existing dataclasses and config structures instead of creating duplicate patterns
- Keep backward-compatible wrappers unless you also refactor all imports safely
- Add or update tests when changing evaluator, thresholds, or angle logic
- Run tests before pushing:

```bash
python -m unittest discover -s tests -v
```

- Avoid breaking existing Streamlit flow (start/stop runtime and session_state behavior)
- Keep user-facing hints simple and actionable
- Document any new thresholds or exercises in movement/exercises.py and this README

## 11. Requirements (Dependencies)

From requirements.txt:

- mediapipe>=0.10.9,<0.10.30; python_version < "3.13"
- mediapipe>=0.10.30; python_version >= "3.13"
- numpy>=1.26
- opencv-python>=4.8
- streamlit>=1.30

## 12. Notes

- If pose detection does not work, first verify Python version and MediaPipe compatibility
- Prefer Python 3.11 for smoother MediaPipe Pose usage in this project
- If camera feed is blank:
	- Close other apps using the webcam
	- Check OS camera permissions
	- Restart Streamlit app
- Keep all new documentation beginner-friendly and aligned with rehabilitation use cases
- Treat this as a technical-assistance tool, not a clinical diagnosis tool

---

If you are a new developer, start with these files in this order:

1. ui/streamlit_app.py
2. movement/evaluator.py
3. movement/exercises.py
4. pose/pose.py
5. angle/angle.py

This order helps you understand the complete runtime flow quickly.

For contributor workflow and pull request rules, see CONTRIBUTING.md.
