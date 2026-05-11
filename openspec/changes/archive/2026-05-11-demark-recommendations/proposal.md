## Why

Users need clear, actionable signals (Buy, Hold, Sell) based on DeMark Sequential indicators rather than just interpreting counts manually. This simplifies decision-making for traders using the tool.

## What Changes

- **New Recommendation Engine**: Logic to translate TD Setup and TD Countdown counts into explicit Buy/Hold/Sell signals.
- **Enhanced CLI Output**: The analysis table and signal highlights will now include a clear "Action" recommendation for the latest bar and historical bars.
- **Visual Color Coding**: Recommendations will be color-coded in the terminal for better visibility (Green for Buy, Red for Sell, Yellow/Gray for Hold).

## Capabilities

### New Capabilities
- `recommendation-logic`: Defines the rules for translating TD counts into Buy, Hold, and Sell signals.
- `cli-signals`: Enhances the CLI interface to display actionable recommendations and status.

### Modified Capabilities
None.

## Impact

- `demark/engine.py`: Will be extended or used by the new recommendation engine.
- `demark/cli.py`: Will be updated to fetch and display recommendations.
