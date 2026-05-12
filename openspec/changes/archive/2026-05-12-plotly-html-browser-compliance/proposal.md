## Why

Current plotting output is centered on PNG artifacts, which prevents browser-native interactivity and limits downstream sharing workflows. We need Plotly outputs that are HTML browser compliant so users can open charts directly in a browser with full interaction support.

## What Changes

- Add Plotly-based HTML output as a first-class plot artifact for analysis runs.
- Require generated HTML to be browser compliant and directly viewable in modern browsers without custom runtime setup.
- Keep PNG export as an optional static artifact for compatibility.
- Update CLI behavior and output expectations so users can request HTML output explicitly.

## Capabilities

### New Capabilities
- `interactive-html-plots`: Generate interactive Plotly charts as HTML files that can be opened in a browser.
- `plot-output-modes`: Support selectable output modes so runs can produce HTML, PNG, or both.

### Modified Capabilities
- None.

## Impact

- Affected code: plotting logic, CLI plot options, and artifact persistence paths.
- Dependencies: Plotly becomes required for interactive chart generation; static image path remains supported.
- Systems: local analysis workflows and browser-based artifact viewing behavior.