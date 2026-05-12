## 1. Dependency and Configuration Setup

- [x] 1.1 Add Plotly to project dependencies and remove Matplotlib where no longer needed.
- [x] 1.2 Define or confirm CLI options for plot output mode values: html, png, both.

## 2. Plot Rendering Refactor

- [x] 2.1 Refactor plot generation code to render Plotly figures from existing analysis data.
- [x] 2.2 Implement browser-compliant HTML export for Plotly figures in analysis outputs.
- [x] 2.3 Keep PNG output support and ensure mode-based generation behavior is enforced.

## 3. Artifact Persistence and Naming

- [x] 3.1 Persist HTML plot files in the existing analysis artifact location.
- [x] 3.2 Enforce deterministic naming for HTML and PNG artifacts across repeated runs.

## 4. Verification and Testing

- [x] 4.1 Add unit tests for output mode behavior (html only, png only, both).
- [x] 4.2 Add tests that validate HTML artifact creation and expected file paths.
- [x] 4.3 Behavior-validate by running the CLI and confirming generated HTML opens in a browser.

## 5. Documentation

- [x] 5.1 Update README/CLI docs to describe output modes and HTML artifact usage.
- [x] 5.2 Document compatibility expectations and any limitations for browser rendering.