# Project Report
## Movement Range Assessment for Rehabilitation Therapy

**Team**  
- Palasani Sai Venkata Tanuj (12315545)  
- Shivang Thakur (12317497)  
- Shashwat Vijayvergiya (12319062)

**Course**: INT345 - Computer Vision  
**Submission Type**: Major Project Report  
**Report Date**: May 12, 2026

---

## Table of Contents
1. Abstract  
2. Problem Statement  
3. Project Title and Objective Alignment  
4. Scope of the Project  
5. System Requirements  
6. Technology Stack  
7. Project Structure and File-Level Explanation  
8. End-to-End Working Pipeline  
9. Core Algorithms and Mathematical Foundation  
10. Exercise Modeling and Clinical Logic  
11. System Implementation Details  
12. User Interface Design and Flow  
13. Error Handling and Runtime Stability  
14. Testing Strategy and Results  
15. Results and Observations  
16. Limitations  
17. Future Enhancements  
18. Conclusion  
19. How to Run the Project  
20. GitHub Readiness and Release Notes  
21. Screenshot Placeholders Index  
22. Appendix

---

## 1. Abstract
This project presents a computer vision-based rehabilitation assistance system that evaluates joint movement quality and range of motion (ROM) in real time. The system captures live webcam video, detects body landmarks, computes exercise-specific joint angles, tracks ROM over time, evaluates movement quality, counts repetitions, and provides immediate visual feedback to the user.

The final implementation uses:
- Pose estimation (MediaPipe PoseLandmarker)
- Geometric angle computation
- ROM tracking through min-max progression with smoothing
- Classical motion tracking fallback (Lucas-Kanade optical flow) for short detection dropouts
- Real-time UI feedback through Streamlit

The project supports multiple bilateral exercises and is designed as a technical-assistance tool for rehabilitation monitoring, not as a medical diagnosis system.

**Screenshot Placeholder**  
- `[SS-01: Project home page with title and navigation]`

---

## 2. Problem Statement
In rehabilitation therapy, movement quality and joint range are often assessed manually. Manual assessment can be subjective and difficult to quantify over time. Patients performing exercises at home may also lack immediate corrective feedback.

This project addresses these issues by creating a real-time software tool that:
- Measures joint angles from camera frames
- Tracks ROM numerically
- Detects whether movement is within configured target ranges
- Provides instant correction hints
- Tracks repetition count using movement phases

**Screenshot Placeholder**  
- `[SS-02: Problem context slide / introductory project statement]`

---

## 3. Project Title and Objective Alignment
### Project Title
**Movement Range Assessment for Rehabilitation Therapy**

### Required Description
Create a system using computer vision to evaluate ROM during rehabilitation sessions, using motion tracking and geometric transformations.

### Alignment Summary
The delivered system matches the title and description by implementing:
1. **Computer vision**: Pose detection from live video  
2. **Geometric transformation/math**: Joint angle from 2D landmark triplets  
3. **Motion tracking**: Landmark continuity via optical flow fallback  
4. **ROM analysis**: Continuous min-max angle tracking  
5. **Rehabilitation feedback**: Status, ROM quality, hints, repetition count

---

## 4. Scope of the Project
### Included Scope
- Live webcam processing
- Exercise-specific angle computation
- ROM tracking in real time
- Real-time feedback UI
- Bilateral exercise support (left and right variants)
- Unit tests for core logic

### Excluded Scope
- Medical-grade diagnostic certification
- Patient data persistence/database
- Therapist dashboard and report export
- Multi-camera fusion
- Clinical validation study

---

## 5. System Requirements
### Hardware
- Laptop/Desktop with webcam
- Minimum 4 GB RAM (8 GB recommended)
- CPU capable of real-time webcam processing

### Software
- Windows/macOS/Linux (development validated mostly on Windows)
- Python 3.11 recommended
- Browser for Streamlit UI

### Python Dependencies
- `mediapipe`
- `opencv-python`
- `numpy`
- `streamlit`

**Screenshot Placeholder**  
- `[SS-03: requirements.txt file opened in IDE]`

---

## 6. Technology Stack
- **Language**: Python
- **Computer Vision**: OpenCV
- **Pose Estimation**: MediaPipe Tasks API (PoseLandmarker)
- **Numerical Ops**: NumPy
- **Frontend/UI**: Streamlit
- **Testing**: Python unittest
- **Version Control**: Git + GitHub

---

## 7. Project Structure and File-Level Explanation
```text
rehab_project/
  .gitignore
  CONTRIBUTING.md
  README.md
  PROJECT_REPORT.md
  main.py
  debug_pose.py
  run_app.ps1
  pose_landmarker.task
  requirements.txt
  angle/
    __init__.py
    angle.py
    angle_module.py
  feedback/
    __init__.py
    feedback.py
  movement/
    __init__.py
    analysis.py
    analysis_module.py
    evaluator.py
    exercises.py
  pose/
    __init__.py
    pose.py
    pose_module.py
  tests/
    __init__.py
    test_camera.py
    test_exercise_logic.py
    test_pose.py
  ui/
    __init__.py
    streamlit_app.py
    ui.py
    visualization_module.py
```

### Module Responsibilities
- `pose/pose.py`: pose detection and fallback motion tracking
- `angle/angle.py`: geometric angle math
- `movement/analysis.py`: ROM tracker
- `movement/evaluator.py`: exercise evaluation, feedback logic, rep counting
- `movement/exercises.py`: exercise thresholds and configs
- `ui/streamlit_app.py`: app runtime and camera worker
- `ui/ui.py`: frame overlays and visual dashboard rendering
- `tests/`: unit tests

**Screenshot Placeholders**  
- `[SS-04: Full project tree in IDE explorer]`  
- `[SS-05: Core modules side-by-side view]`

---

## 8. End-to-End Working Pipeline
1. Webcam frame is captured continuously.  
2. Frame is sent to PoseLandmarker for landmark detection.  
3. If fresh landmarks are absent, optical flow tracks previous landmarks temporarily.  
4. For selected exercise, required landmark triplet is extracted.  
5. Joint angle is computed at the middle point of triplet.  
6. Angle is fed to ROM tracker (smoothed, min-max updated).  
7. Evaluator computes:
   - Correct/Incorrect posture status
   - ROM quality band
   - Movement phase
   - Repetition count
8. UI overlays visuals and updates metrics in real time.

**Screenshot Placeholders**  
- `[SS-06: Pipeline block diagram]`  
- `[SS-07: Live frame with skeleton overlay]`  
- `[SS-08: Metrics panel with angle/ROM/reps]`

---

## 9. Core Algorithms and Mathematical Foundation
### 9.1 Joint Angle Calculation
For points A, B, C where B is joint center:
- Compute direction angles via `atan2`
- Subtract to obtain relative angle
- Normalize to `[0, 180]` degrees

This makes angle computation robust for exercise evaluation.

### 9.2 ROM Calculation
ROM is computed from tracked extrema:
`ROM = max_angle - min_angle`

### 9.3 Smoothing
Exponential smoothing reduces jitter in live angle progression:
`smoothed = alpha * current + (1 - alpha) * previous`

### 9.4 Repetition Counting
State machine approach:
- `Ready -> Phase A -> Phase B -> rep++ -> Ready`
- Direction-aware rules based on exercise configuration

### 9.5 Classical Tracking Fallback
Lucas-Kanade optical flow (`cv2.calcOpticalFlowPyrLK`) tracks known points when direct pose output is temporarily missing, improving continuity.

---

## 10. Exercise Modeling and Clinical Logic
Exercises are defined via `ExerciseConfig` with:
- title, side, description
- triplet landmarks
- target angle range (min, max)
- rep thresholds (`rep_low`, `rep_high`)
- phase labels
- speed and jerk thresholds

### Supported Exercises
- Right/Left Elbow Flexion
- Right/Left Shoulder Abduction
- Right/Left Knee Flexion (Squat)
- Right/Left Wrist Flexion
- Right/Left Hip Flexion

### Feedback Outputs
- Posture status: Correct / Incorrect
- ROM quality: Poor / Fair / Good
- Hint: exercise-specific guidance

**Screenshot Placeholders**  
- `[SS-09: exercises.py showing configured exercises]`  
- `[SS-10: Live shoulder exercise run]`  
- `[SS-11: Live squat exercise run]`

---

## 11. System Implementation Details
### 11.1 Camera Worker Design
`CameraWorker` uses a dedicated thread to avoid blocking Streamlit UI, with:
- start/stop lifecycle
- frame read failure handling
- periodic processing (`PROCESS_EVERY_N_FRAMES`)
- latest frame + metrics sharing via lock

### 11.2 Safety and Robustness
- Camera init failure checks
- Pose backend availability checks
- Safe handling for missing coordinates
- Safe joint point conversion before OpenCV draw
- Overlay exception guard to prevent worker death

### 11.3 Legacy Compatibility
Wrapper modules (`*_module.py`) and aliases preserve compatibility with older imports and test paths.

---

## 12. User Interface Design and Flow
### Pages
- Home
- Start Exercise
- Instructions

### Start Exercise Flow
1. Select exercise from sidebar
2. Start Detection
3. Observe frame + live metrics
4. Stop Detection

### Metrics Shown
- Exercise name
- Current angle
- ROM
- Reps
- Status
- ROM feedback
- Hint

**Screenshot Placeholders**  
- `[SS-12: Home page]`  
- `[SS-13: Start Exercise page before start]`  
- `[SS-14: Start Exercise page during active detection]`  
- `[SS-15: Instructions page]`

---

## 13. Error Handling and Runtime Stability
### Addressed Runtime Cases
- Camera not accessible
- No person in frame
- Low-visibility landmarks
- Exercise switch during active runtime
- Overlay drawing type safety
- Temporary landmark dropout through optical flow fallback

### Common Non-Fatal Runtime Warnings
- TFLite feedback manager warnings
- Streamlit fragment lifecycle warnings during reruns
- MediaPipe projection warnings

These warnings are generally informational and do not necessarily indicate project failure.

---

## 14. Testing Strategy and Results
### Test Framework
- `unittest` with module-level logic tests

### Tested Areas
- Angle function correctness
- ROM tracker correctness
- Feedback mapping
- Legacy alias resolution
- Repetition counting logic
- ROM feedback progression
- Evaluator config update/reset behavior
- OpenCV availability check (skips if unavailable)

### Latest Test Outcome
- All logic tests pass
- Camera availability test is environment-dependent and safely skipped when OpenCV is missing

**Screenshot Placeholder**  
- `[SS-16: Terminal screenshot of unittest output]`

---

## 15. Results and Observations
### Functional Results
- Real-time exercise monitoring is operational
- Angle and ROM values update live
- Repetition counting works with configured thresholds
- Feedback hints and posture status behave as expected

### Practical Observations
- Good lighting improves detection stability
- Side visibility strongly affects tracking quality
- Fast motion and occlusion reduce confidence

**Screenshot Placeholders**  
- `[SS-17: Correct posture state]`  
- `[SS-18: Incorrect posture state with hint]`  
- `[SS-19: ROM progression over reps]`

---

## 16. Limitations
- Not clinically validated for diagnosis
- No long-term session storage
- No exported reports (CSV/PDF) in current version
- Performance varies with hardware and lighting
- Single-camera viewpoint constraints

---

## 17. Future Enhancements
1. Patient profile and session history storage  
2. Automated report export (CSV/PDF)  
3. Therapist dashboard and trend charts  
4. Calibration per patient or joint condition  
5. More robust occlusion handling  
6. Multi-person filtering and user selection  
7. Integration with remote tele-rehab platform  
8. Formal clinical validation methodology

---

## 18. Conclusion
The project successfully delivers a complete computer vision-based rehabilitation movement range assessment system aligned with its title and stated objective. It combines pose estimation, geometric angle analysis, ROM computation, and tracking continuity techniques to provide practical live feedback for rehabilitation exercises.

The current implementation is technically strong for academic demonstration and further extension, while clearly separating its scope from medical diagnosis.

---

## 19. How to Run the Project
### Option A (Windows quick run)
```powershell
.\run_app.ps1
```

### Option B (manual)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run ui/streamlit_app.py
```

### Tests
```powershell
python -m unittest discover -s tests -v
```

---

## 20. GitHub Readiness and Release Notes
The repository is prepared with:
- Clean `.gitignore`
- Documentation updates (`README.md`, `CONTRIBUTING.md`)
- Runtime stability fixes
- Test updates and passing core suite
- GitHub push completed on `main`

Suggested release tags:
- `v1.0.0` for first stable academic submission

---

## 21. Screenshot Placeholders Index
Use this checklist while inserting final screenshots:
- `[SS-01]` Home page with project title
- `[SS-02]` Problem statement slide/section
- `[SS-03]` requirements.txt
- `[SS-04]` Full project tree
- `[SS-05]` Core modules in IDE
- `[SS-06]` Pipeline architecture diagram
- `[SS-07]` Live skeleton frame
- `[SS-08]` Live metrics panel
- `[SS-09]` exercises.py configuration
- `[SS-10]` Shoulder run
- `[SS-11]` Squat run
- `[SS-12]` Home UI
- `[SS-13]` Start page before detection
- `[SS-14]` Start page during detection
- `[SS-15]` Instructions page
- `[SS-16]` Test output terminal
- `[SS-17]` Correct status example
- `[SS-18]` Incorrect status example
- `[SS-19]` ROM progression example

---

## 22. Appendix
### A. Key Configuration Parameters
- `PROCESS_EVERY_N_FRAMES = 3`
- `WORKER_TARGET_FPS = 20`
- Landmark visibility threshold: `0.3`
- Pose confidence thresholds: `0.5` class defaults

### B. Ethical and Safety Note
This system is an educational and technical assistance tool. It is not a replacement for licensed clinical diagnosis or treatment planning.

### C. Suggested Viva/Presentation Talking Points
1. Why pose landmarks are sufficient for ROM tracking  
2. Why optical flow fallback was added  
3. How angle and ROM are mathematically derived  
4. How repetition counting works via phase transitions  
5. Practical deployment constraints and improvements

