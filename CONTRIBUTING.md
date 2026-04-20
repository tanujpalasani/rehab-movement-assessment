# Contributing Guide

Thank you for contributing to this rehabilitation movement assessment project.

This guide is written for beginners so you can make safe changes without breaking existing behavior.

## Project Goal

Build and improve a computer vision system that analyzes rehabilitation exercise movement quality using:

- Live pose detection
- Joint angle estimation
- Range of motion (ROM) tracking
- Real-time feedback

## Before You Start

1. Read README.md fully.
2. Set up the project environment.
3. Run tests once before making any changes.
4. Understand which module your change belongs to.

## Local Setup

### 1) Clone and enter project

```bash
git clone <repository-url>
cd <repository-folder>/rehab_project
```

### 2) Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

macOS/Linux:

```bash
python3 -m venv .venv
```

### 3) Activate virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Run app

```bash
streamlit run ui/streamlit_app.py
```

### 6) Run tests

```bash
python -m unittest discover -s tests -v
```

## Branch and Commit Workflow

Use this simple workflow for every change:

1. Pull latest changes from main branch.
2. Create a new branch for your task.
3. Make small, focused commits.
4. Push branch and open a Pull Request.

Suggested branch name formats:

- feature/<short-topic>
- fix/<short-topic>
- docs/<short-topic>
- test/<short-topic>

Suggested commit style:

- feat: add shoulder exercise calibration option
- fix: handle missing right_wrist landmark safely
- docs: improve setup instructions for windows
- test: add evaluator rep counting edge case

## Code Organization Rules

Keep module responsibilities clear.

- pose/: Only pose detection and landmark extraction logic.
- angle/: Only geometric angle helpers.
- movement/: Exercise configs, evaluation logic, ROM and rep logic.
- ui/: Rendering and Streamlit interaction only.
- tests/: Unit tests and logic validation.

Do not move business logic into UI callbacks unless absolutely necessary.

## Coding Standards

- Keep code readable and beginner-friendly.
- Prefer descriptive names over short abbreviations.
- Keep functions small and focused.
- Reuse existing dataclasses and config patterns.
- Avoid magic numbers in logic; place thresholds in exercise config where possible.
- Preserve backward-compatible wrappers unless full import refactor is completed.
- Add comments only when code is not self-explanatory.

## Exercise and Threshold Changes

When editing exercise behavior in movement/exercises.py:

1. Explain why thresholds changed.
2. Verify effects on status, ROM feedback, and rep counting.
3. Add or update tests in tests/test_exercise_logic.py.
4. Update README.md if behavior visible to users changed.

## Testing Expectations

Minimum checks before opening a PR:

1. Run all tests.
2. Start Streamlit app and verify camera starts and stops.
3. Confirm selected exercise updates correctly.
4. Confirm Angle, ROM, Reps, Status, and Hint are visible.

Optional but recommended:

- Verify behavior in different lighting.
- Verify behavior when no person is in frame.
- Verify behavior after changing exercises during runtime.

## Pull Request Checklist

Copy this checklist into your PR description.

- [ ] My branch is up to date with main.
- [ ] I kept changes focused to one problem.
- [ ] I ran tests locally and they pass.
- [ ] I manually verified the app starts and camera works.
- [ ] I updated tests for logic changes.
- [ ] I updated documentation for user-visible changes.
- [ ] I did not break existing module boundaries.
- [ ] I added clear notes for reviewers.

## Review Guidelines

When reviewing code, prioritize:

1. Correctness and safety of exercise evaluation logic.
2. Regressions in pose detection and runtime stability.
3. Clear user feedback and usability.
4. Test coverage for changed behavior.
5. Code readability for future student contributors.

## Common Mistakes to Avoid

- Hardcoding exercise thresholds in UI code.
- Changing rep counting logic without tests.
- Mixing old legacy flow and Streamlit flow in one feature.
- Ignoring camera failure and no-detection states.
- Making large unrelated refactors in a single PR.

## Documentation Rules

If your change affects setup, behavior, or outputs:

- Update README.md.
- Add short notes in PR explaining what changed and why.
- Keep wording simple so new contributors can follow.

## Safety and Scope Note

This project is a technical assistance tool for movement assessment. It is not a medical diagnosis system.

Avoid claims of clinical accuracy unless validated by proper clinical studies.

## Need Help

If you are unsure where to place a change, start by opening an issue or draft PR and ask for module-level guidance before implementing a large refactor.
