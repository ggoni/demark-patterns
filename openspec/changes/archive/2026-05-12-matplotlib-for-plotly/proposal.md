## Why

The current implementation of plots in the project relies on Matplotlib, which lacks interactivity. This limits the ability to explore data dynamically, especially for users who need to zoom, pan, or hover over data points for detailed insights. Switching to Plotly will address these limitations by providing interactive plotting capabilities.

## What Changes

- Replace Matplotlib with Plotly for all plotting functionalities.
- Update existing plot generation code to use Plotly APIs.
- Ensure compatibility with current data processing pipelines.
- **BREAKING**: Remove Matplotlib dependencies from the project.

## Capabilities

### New Capabilities
- `interactive-plots`: Introduces interactive plotting capabilities using Plotly.

### Modified Capabilities
- `plot-output`: Update requirements to include interactivity features such as zooming, panning, and tooltips.

## Impact

- Affected code: All modules generating plots.
- Dependencies: Remove Matplotlib, add Plotly.
- Systems: Ensure Plotly works seamlessly with existing data processing and visualization workflows.